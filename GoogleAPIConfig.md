# Google API Config

## 1. Start a new cloud console project

https://console.cloud.google.com/projectcreate

- Project Name: `gslide2media`  (or your choice)
- Location [Organization]: `No organization` (or your choice)

you should be able to access your project's dashboard at the following
link (if you used `gsslide2media` as the project name.)

```text
https://console.cloud.google.com/home/dashboard?project=gslide2media

# Otherwise insert your project name accordingly
https://console.cloud.google.com/home/dashboard?project=PROJECT_NAME

```

__*Note:*__ The rest of this guide will assume the use of `gslide2media` as the project name.  If you specified a different project name, change your links accordingly.

## 2. Enable the Google Drive API for your project

https://console.cloud.google.com/apis/library/drive.googleapis.com?project=gslide2media


## 3. Enable the Google Slides API for your project

https://console.cloud.google.com/apis/library/slides.googleapis.com?project=gslide2media

## 4. Create an OAuth Client Id for your project

https://console.cloud.google.com/apis/credentials/oauthclient?project=gslide2media

1. __Configure Consent Screen__
    - __*User Type:*__ `External`
2. __Provide App Information__
    - __*App Name:*__ `gslide2media`
    - __*User Support Email:*__ `Your Email Address`
    - __*Developer contact information:*__ `Your Email Address`
3. __Scopes Configuration__
    - __*non-sensitive scopes:*__ `No rows to display`
    - __*sensitive scopes:*__ `No rows to display`
    - __*restricted scopes:*__ `No rows to display`
4. __Add Test Users__
    - __*...add yourself as a test user*__
    - __*Test Users:*__ `Your Email Address`
4. __Create The Client Id__
    - https://console.cloud.google.com/apis/credentials/oauthclient?project=gslide2media
    - __*Application Type:*__ `Desktop App`
    - __*Application Name:*__ `gslide2media_desktop_client`
5. __Download Client Secret Json__
    - https://console.cloud.google.com/apis/credentials?project=gslide2media
    - __*Under OAuth 2.0 Client IDs*__
        - Click on the __Download icon__ (the bold down arrow on the right end of the row)
        - Click on `Download JSON`, save the file in your project's working/download directory.