import csv
import os
import time
from datetime import datetime
from multiprocessing import Manager, Pool, Process, Queue

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def AuthGoogle(credentials):
    """Connects to GoogleDrive

    Args:
        credentials: path to file with credentials(string)
    Returns:    
        GoogleDrive object
    """
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(credentials)
    if gauth.credentials is None:
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        gauth.Refresh()
    else:
        gauth.Authorize()
    gauth.SaveCredentialsFile(credentials)
    return GoogleDrive(gauth)


def CollectPermissions(file):
    """Analyse permissions for file

    Args: GoogleDrive file (dict)
    Returns: dict with collected information
    """
    for j in range(3):
        try:
            if file["mimeType"] == "application/vnd.google-apps.folder":
                folders.append(file["id"])
                if file["parents"]:
                    parent_dir[file["id"]] = "{0}{1}/".format(
                        parent_dir.get(file["parents"][0]["id"], "/"),
                        file["title"]
                    )
                else:
                    parent_dir[file["id"]] = "/{0}/".format(
                        file["title"]
                    )
            watch = {}
            for perm in file.GetPermissions():
                if perm.get("emailAddress") is not None:
                    emailAddress = perm.get("emailAddress")
                else:
                    emailAddress = ""
                if perm.get("type") == "anyone":
                    watch["anyone"] = perm.get("role")
                elif perm.get("type") == "user":
                    if emailAddress not in fieldnames:
                        fields.append(emailAddress)
                        watch[emailAddress] = perm.get("role")
                    else:
                        watch[emailAddress] = perm.get("role")
            if not file["parents"]:
                watch['Path'] = "/{0}".format(file["title"])
            else:
                watch['Path'] = "{0}{1}".format(parent_dir.get(file["parents"][0]["id"], "/"),
                                                file["title"])
            watch['FileType'] = file["mimeType"].split(".")[-1]
            watch['Owner'] = file["ownerNames"][0]
            watch['CreatedDate'] = file["createdDate"]
            watch['ModifiedDate'] = file["modifiedDate"]
            watch['AlternateLink'] = file["alternateLink"]
            time.sleep(0.1)
            return watch
        except Exception as e:
            print("Error parsing:{0}, {1}".format(file["title"], e))
            time.sleep(1)


def GenerateReport():
    """Moves header to the top and deletes tempfile
    """
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


if __name__ == '__main__':
    delta = datetime.now()
    drive = AuthGoogle("mycreds.txt")
    gwatcher = open('tmp.csv', 'w')
    results = []
    manager = Manager()
    folders = manager.list()
    parent_dir = manager.dict()
    fields = manager.list()
    file_count = 0
    fieldnames = ['Path', 'FileType', 'Owner', 'CreatedDate',
                  'ModifiedDate', 'AlternateLink', 'anyone']
    writer = csv.DictWriter(gwatcher, fieldnames=fieldnames)
    writer.writeheader()
    pool = Pool()
    for i in range(3):
        try:
            RootDirectory = drive.ListFile(
                {'q': '"root" in parents'}).GetList()
            break
        except:
            time.sleep(10)
    parent_dir.update({RootDirectory[0]['parents'][0]["id"]: "/"})
    p = pool.map_async(CollectPermissions, RootDirectory)
    for i in (p.get()):
        results.append(i)
        file_count += 1
        print("File:{0}".format(file_count))
    for i in range(3):
        try:
            SharedFiles = drive.ListFile({'q': 'sharedWithMe'}).GetList()
            break
        except:
            time.sleep(10)
    p = pool.map_async(CollectPermissions, SharedFiles)
    for i in (p.get()):
        results.append(i)
        file_count += 1
        print("File:{0}".format(file_count))
    try:
        while folders:
            for id in folders:
                time.sleep(0.1)
                for i in range(3):
                    try:
                        folder = drive.ListFile(
                            {'q': '"{0}" in parents'.format(id)}).GetList()
                        break
                    except:
                        time.sleep(10)
                p = pool.map_async(CollectPermissions, folder)
                for i in p.get():
                    results.append(i)
                    file_count += 1
                    print("File:{0}".format(file_count))
                folders.remove(id)
    except:
        print("Error")
    finally:
        for field in fields:
            if field not in fieldnames:
                fieldnames.append(field)
        time.sleep(1)

        for i in results:
            try:
                writer.writerow(i)
            except AttributeError as e:
                print(e)
        writer.writeheader()
        gwatcher.close()
        GenerateReport()
        print("Total time:{0}".format((datetime.now()-delta)))
