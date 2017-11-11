from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import csv
import os

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


def write_results(perm, watch, emailAddress):
    if str(perm.get("type")) == 'anyone':
        watch['anyone'] = str(perm.get("role"))
    elif str(perm.get("type")) == 'user':
        if emailAddress not in fieldnames:
            fieldnames.append(emailAddress)
            writer = csv.DictWriter(gwatcher, fieldnames=fieldnames)
            watch[emailAddress] = str(perm.get("role"))
        else:
            watch[emailAddress] = str(perm.get("role"))        
    return watch


def lets_godeeper(id,writer,watch, level):
    for file in drive.ListFile({'q': "'"+id+"' in parents"}).GetList():
        for perm in file.GetPermissions():
            if perm.get('emailAddress') is not None:
                emailAddress = str(perm.get("emailAddress"))
            else:
                emailAddress = ""
            write_results(perm, watch, emailAddress)
        watch['Path'] = ("/" + str(level) + str(file["title"]))
        watch['FileType'] = str(file["mimeType"].split(".")[-1])
        watch['Owner'] = str(file["ownerNames"][0])
        watch['CreatedDate'] = str(file["createdDate"])
        watch['ModifiedDate'] = str(file["modifiedDate"])
        watch['AlternateLink'] = str(file["alternateLink"])
        writer.writerow(watch)
        watch.clear()
        if file["mimeType"] == "application/vnd.google-apps.folder":
            lets_godeeper(file["id"],writer, watch,level + file['title'] + "/")



def file_enum(writer, query):
    root_dir = drive.ListFile(
    {'q': query}).GetList()

    for root_file in root_dir:
        watch = {}
        for perm in root_file.GetPermissions():
            if perm.get('emailAddress') is not None:
                emailAddress = str(perm.get("emailAddress"))
            else:
                emailAddress = ""
            write_results(perm, watch, emailAddress)
        watch['Path'] = ("/" + str(root_file["title"]))
        watch['FileType'] = str(root_file["mimeType"].split(".")[-1])
        watch['Owner'] = str(root_file["ownerNames"][0])
        watch['CreatedDate'] = str(root_file["createdDate"])
        watch['ModifiedDate'] = str(root_file["modifiedDate"])
        watch['AlternateLink'] = str(root_file["alternateLink"])
        writer.writerow(watch)
        watch.clear()
        if root_file["mimeType"] == "application/vnd.google-apps.folder":
            lets_godeeper(root_file["id"],writer,watch, root_file['title'] + "/")


            


with open('tmp.csv', 'w') as gwatcher:
    fieldnames = ['Path', 'FileType', 'Owner', 'CreatedDate',
                  'ModifiedDate',  'AlternateLink', 'anyone']
    writer = csv.DictWriter(gwatcher, fieldnames=fieldnames)
    writer.writeheader()
    file_enum(writer,"'root' in parents and trashed=false")
    file_enum(writer, "sharedWithMe=True")
    writer.writeheader()
    gwatcher.close()

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
