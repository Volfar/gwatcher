from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import csv
import os
from multiprocessing import Manager, Queue, Pool
from datetime import datetime
import time


gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("mycreds.txt")
drive = GoogleDrive(gauth)


def writeResults(file):
    if file["mimeType"] == "application/vnd.google-apps.folder":
        folders.append(file["id"])
        if file["parents"]:
            parent_dir[file["id"]] = (parent_dir[file["parents"][0]["id"]] + str(file["title"] + "/"))
        else:
            parent_dir[file["id"]] = ("/" + str(file["title"] + "/"))
    watch = {}
    for perm in file.GetPermissions():
        if perm.get('emailAddress') is not None:
            emailAddress = str(perm.get("emailAddress"))
        else:
            emailAddress = ""
        if str(perm.get("type")) == 'anyone':
            watch['anyone'] = str(perm.get("role"))
        elif str(perm.get("type")) == 'user':
            if emailAddress not in fields:
                fields.append(emailAddress)
                watch[emailAddress] = str(perm.get("role"))
            else:
                watch[emailAddress] = str(perm.get("role"))
    if not file["parents"]:
         watch['Path'] = ("/" + str(file["title"]))
    else:
         watch['Path'] = (str(parent_dir[file["parents"][0]["id"]]) + str(file["title"]))
    watch['FileType'] = str(file["mimeType"].split(".")[-1])
    watch['Owner'] = str(file["ownerNames"][0])
    watch['CreatedDate'] = str(file["createdDate"])
    watch['ModifiedDate'] = str(file["modifiedDate"])
    watch['AlternateLink'] = str(file["alternateLink"])
    q.put(watch)
    progress.append("0")
    print("Total files checked:" + str(len(progress)))


if __name__ == '__main__':
    startTime = datetime.now()
    gwatcher = open('tmp.csv', 'w')
    fieldnames = ['Path', 'FileType', 'Owner', 'CreatedDate',
                  'ModifiedDate', 'AlternateLink', 'anyone']
    writer = csv.DictWriter(gwatcher, fieldnames=fieldnames)
    writer.writeheader()
    q = Queue()
    manager = Manager()
    folders = manager.list()
    fields = manager.list()
    progress = manager.list()
    parent_dir = manager.dict()
    files = drive.ListFile({'q':'"root" in parents'}).GetList()
    pool = Pool()
    parent_dir[files[0]['parents'][0]["id"]] = "/"
    p = pool.map_async(writeResults, files)
    p.wait()
    filesShared = drive.ListFile({'q': 'sharedWithMe'}).GetList()
    p = pool.map_async(writeResults, filesShared)
    p.wait()
    while folders:
        time.sleep(0.1)
        for id in folders:
            time.sleep(0.1)
            files = drive.ListFile({'q': "'" + str(id) + "' in parents"}).GetList()
            p = pool.map_async(writeResults, files)
            folders.remove(id)
    p.wait()

    for field in fields:
        if field not in fieldnames:
            fieldnames.append(field)

    while not q.empty():
        writer.writerow(q.get())

    q.close()
    q.join_thread()
    writer.writeheader()
    gwatcher.close()
    print(datetime.now()-startTime)
    with open("tmp.csv", "r") as file:
        lines = file.readlines()
        lines[0] = lines[-1]
        lines = lines[:-1]
        file.close()

    with open("gwatcher.csv", "w") as file:
        for line in lines:
            file.write(line)
        file.close()
        os.remove("tmp.csv")
