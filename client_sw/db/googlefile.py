from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaFileUpload,MediaIoBaseDownload
from apiclient import errors
import os
import io
import json
import logging
# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive'
class googlefile():
    
    def __init__(self, log):
        self.logger = log
        logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        self.pcname = os.environ['COMPUTERNAME']
        self.filename = self.pcname + '_prize.json'
        self.folder_id = None
        self.file_id = None
        self.network = False
        if os.path.isfile(self.filename) and os.access(self.filename, os.R_OK):
            print ("Local file exists and is readable")
        else:
            with io.open(self.filename, 'w') as db_file:
                db_file.write(json.dumps({}))             
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        try:    
            self.service = build('drive', 'v3', http=creds.authorize(Http()), cache_discovery=False)
        except Exception as e:
            self.logger.log(logging.ERROR,"No networkconnection google")
            print("No networkconnection", e)
            self.network = False
            return None     
        # Call the Drive v3 API
        results = self.service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        self.network = True
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))
                if item['name'] == self.pcname:
                    self.folder_id = item['id']
                if item['name'] == self.filename:
                    self.file_id = item['id']
          
                    

        if self.folder_id == None:
            print("Create Folder")
            self.createFolder(self.pcname)
        if self.file_id == None:
            print("Create File")
            self.uploadFile()
	
    
    def createFolder(self,folderName):
        file_metadata = {
                        'name': folderName,
                        'mimeType': 'application/vnd.google-apps.folder'
                        }

        file = self.service.files().create(body=file_metadata,
                                    fields='id').execute()
        print ('Folder ID: %s' % file.get('id')	)
        self.folder_id = file.get('id')  
        self.uploadFile()
  
    
    def uploadFile(self):
        
        file_metadata = {
                    'name': self.filename,
                    'parents': [self.folder_id]
                        }
        media = MediaFileUpload(self.filename,
                        mimetype='text/plain',
                        resumable=True)
        file = self.service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id').execute()
        print ('File ID: %s' % file.get('id'))
        self.file_id = file.get('id')
    
    def update_file(self, file_path, fileId):

        mimetype='text/plain'
        media_body = MediaFileUpload(file_path, mimetype, resumable=True)

        results = self.service.files().update(
            fileId=fileId, media_body=media_body, fields="id").execute()

        return results  
  
    def print_file_content(self, file_id):
        """Print a file's content.
    
          Args:
            service: Drive API service instance.
            file_id: ID of the file.
    
          Returns:
            File's content if successful, None otherwise.
          """
        try:
            print (self.service.files().get_media(fileId=file_id).execute())
        except Exception as e:
            print ('An error occurred: %s' % e) 
    
    def download_googledocs(self, file_id):
        request = self.service.files().export_media(fileId=file_id,
                                             mimeType='text/plain')
        fh = io.FileIO(self.filename, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            try:
                status, done = downloader.next_chunk()
                print ("Download %d%%." % int(status.progress() * 100))
            except:
                print ('An error occurred, when downloading google docs file:')
                return
            
            
            
    def download_file(self):
      """Download a Drive file's content to the local filesystem.
    
      Args:
        service: Drive API Service instance.
        file_id: ID of the Drive file that will downloaded.
        local_fd: io.Base or file object, the stream that the Drive file's
            contents will be written to.
      """
      request = self.service.files().get_media(fileId=self.file_id)
      local_fd = io.FileIO(self.filename, 'wb')
      media_request = MediaIoBaseDownload(local_fd, request)
    
      while True:
        try:
          download_progress, done = media_request.next_chunk()
        except (errors.HttpError):
          print ('An error occurred, when downloading plain file: %s' , errors.HttpError)
          return
        if download_progress:
          print ('Download Progress: %d%%' % int(download_progress.progress() * 100))
        if done:
          print ('Download Complete')
          return 

    def ReadFile(self):
        data = None
        try:
            jsonFile = open(self.filename, "r") # Open the JSON file for reading
            data = json.load(jsonFile) # Read the JSON into the buffer
        except Exception as e:
            print('Json read error: ' , e)
        finally:   
            jsonFile.close() # Close the JSON file
        return data     
      
    def SaveFile(self,data):
        ## Save our changes to JSON file
        jsonFile = open(self.filename, "w+")
        jsonFile.write(json.dumps(data))
        jsonFile.close()
        if self.network:
            self.update_file(self.filename,self.file_id)
        
if __name__ == '__main__':
    gf = googlefile()
    #gf.ReadFile()
    # gf.print_file_content(gf.file_id)
    gf.download_file(gf.file_id)
    #gf.download_googledocs(gf.file_id)
    #gf.update_file(gf.filename, gf.file_id)
  