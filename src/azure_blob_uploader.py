import os
import json
from azure.storage.blob import BlobServiceClient

class AzureBlobUploader : 

    def __init__(self, secrets_file = None) : 
        if secrets_file is None : 
            if "BLOB_CONNECTION_STRING" not in os.environ :
                raise LookupError("Cannot find key 'BLOB_CONNECTION_STRING' in environment variables.")
            self.blob_connection_string = os.environ['BLOB_CONNECTION_STRING']
        else : 
            with open(secrets_file) as f : 
                data = json.load(f)
            if "BLOB_CONNECTION_STRING" not in data :
                raise LookupError("Cannot find key 'BLOB_CONNECTION_STRING' in secrets file.")
            
            self.blob_connection_string = data['BLOB_CONNECTION_STRING']
        
        self.service = BlobServiceClient.from_connection_string(conn_str = self.blob_connection_string)

    def upload(self, container_name, blob_name, data) : 
        container_client = self._get_container_client(container_name)
        container_client.upload_blob(blob_name, data)

    def _get_container_client(self, container_name) :
        self._create_container_if_not_exists(container_name)
        return self.service.get_container_client(container_name)

    def _create_container_if_not_exists(self, container_name) :
        container_names = [ x['name'] for x in list(self.service.list_containers()) ]
        if container_name not in container_names : 
            self.service.create_container(container_name)