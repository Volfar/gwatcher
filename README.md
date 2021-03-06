![title](https://github.com/Volfar/gwatcher/blob/logo/logo/logo.png)

GWatcher will harvest all files on your Google Drive with their permissions in convenient csv format so you would be able easy to check **WHO** has access to **WHAT**.

## Prerequisites
To be able to run this tool you need to do following steps:
1. Go to [APIs Console](https://console.developers.google.com/iam-admin/projects) and make your own project. You will see notification that your project has been created. Click there and you will be moved to your project main dashboard.
2. Search for ‘Google Drive API’, select the entry, and click ‘Enable’.
3. Select ‘Credentials’ from the left menu, click ‘Create Credentials’, select ‘OAuth client ID’.
4. Now, the product name and consent screen need to be set -> click ‘Configure consent screen’ and follow the instructions. Once finished:
   * Select ‘Application type’ to be Other.
   * Enter an appropriate name.
   * Click ‘Save’.
   * Click ‘Download JSON’ on the right side of Client ID to download client_secret_<really long ID>.json.

The downloaded file has all authentication information. Rename the file to “client_secrets.json” and place it in GWatcher directory.

5. Install needed dependencies with pip

```pip install -r requirements.txt```

For best experience I recommend to use virtualenv.<br />
```virtualenv -p python3 env```<br />
```source env/bin/activate```<br />
And then install dependencies with command in number 5.


## Usage
Simply run tool and you will be prompted to enter your Google credentials and requested access to Google Drive

```python3 gwatcher.py```

## Report Example
![alt text](https://github.com/Volfar/gwatcher/blob/logo/logo/screenshot.png)
