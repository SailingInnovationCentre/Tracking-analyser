import os

def get_env_var(varname) : 
    if varname not in os.environ : 
        raise LookupError(f"Cannot find '{varname}' in environment variables.")

def find_data_dir() : 
    if 'DATA_DIR' in os.environ : 
        # For local development
        return os.environ['DATA_DIR']
    
    # In production environment (Docker)
    return "/data"

def find_blob_connection_string() :
    return get_env_var('BLOB_CONNECTION_STRING')

def find_db_connection_string() :
    return get_env_var('DB_CONNECTION_STRING')

# Later: credentials for SAP database? 

class Config : 

    def __init__ (self) : 
        self.data_dir = find_data_dir()
        self.base_url = 'http://www.sapsailing.com/sailingserver/api/v1/'
        self.blob_connection_string = find_blob_connection_string()
        self.db_connection_string = find_db_connection_string()


