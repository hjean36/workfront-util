import json
from pathlib import Path 
import os 
from services import settings

os.environ["CONFIG_FILE"] = ""

class WorkfrontConfig:
    def __init__(self): 
        pass

    def return_db_type(self, db_option):
        while db_option not in ["1","2"]:
            db_option = input("Enter `1`  for  MSSQL or `2` for Sqlite3 : ") 
             
        if db_option is '1': 
            server = input("Server : ")
            prod_databse = input("Prod Database : ")
            test_database = input("Test Database : ")
            username = input("Username :")
            password = input("Password :  ")
            return [server, prod_databse, test_database, username, password]
        elif db_option is  '2':
            sqlite_database_path = input("Provide database path : ")
            return sqlite_database_path

    def _create_config(self, wf_env, api_key, api_version, db_option, db_settings):
        try: 
            config = {}
            db_keys = ["server", "prod_database", "test_database", "username", "password"]
            sql_server_options = dict(zip(db_keys, db_settings))
            if db_option is "1":
                config =   {
                    "database" : {
                        "sql_server": sql_server_options
                    },  
                    "workfront" : {
                        "environment": wf_env, 
                        "api_version": api_version, 
                        "api_key" :  api_key
                    }
                } 
                return config                
            elif db_option is "2": 
                config =  {
                            "database" : {
                                "sqlite_database_path" : db_settings   
                            },  
                            "workfront" : {
                                "environment": wf_env, 
                                "api_version": api_version, 
                                "api_key" :  api_key
                            }
                        }
                return config
            elif db_option is "": 
                config = {
                    "workfront" : {
                                "environment": wf_env, 
                                "api_version": api_version, 
                                "api_key" :  api_key
                            }
                    }
                return config

        except Exception as e:
            print(e)
            raise Exception("Error creating config file")   

    def _create_config_file(self):
        config_dir_path = ""
        if os.name == 'nt':
            config_dir_path = os.path.join(os.environ['temp'], 'workfront')
        else: 
            config_dir_path = os.path.join(os.environ['TMPDIR'], 'workfront')

        if not os.path.exists(config_dir_path):
            os.makedirs(config_dir_path)

        config_path = os.path.join(config_dir_path , 'wf_config.json')
        with open(config_path, 'w') as outfile:
            json.dump({}, outfile) 

        return config_path

    def gen_config(self):
        config = input("Generate Config? Y/n : ")
        config_path = ""
        if config is "n": 
            config_path = input("Provide config file location : ")
            while not os.path.exists(config_path):
                config_path = input("Could not find file. Provide config file location : ")
        else: 
            api_key = input("Enter your API Key : ")
            api_version = input("API Version : ")
            wf_env = input("Environment : ")
            base_url = input("Provide your Base Url : ")
            db = input("Using a database ? Y/n : ") 
            db_option = ""
            db_settings= ""
            
            if db is "Y":
                print("Only MSSQL/Sqlite3 is supported - Make sure you can connect to the DB")
                db_option= input("Enter `1`  for  MSSQL or `2` for Sqlite3 : ")
                db_settings = self.return_db_type(db_option)
            elif db is "n": 
                db_option = ""
            else: 
                raise Exception("Invalid Db Option")
            
            #Set up files 
            config_json = self._create_config(wf_env, api_key, api_version, db_option, db_settings)
            if not config_path: 
                config_path = self._create_config_file()
            
            #Dump the new config file 
            with open(config_path, 'w') as outfile:
                json.dump(config_json, outfile)   
            
            print(f"Config file Generatated : {config_path}") 
            os.environ["CONFIG_FILE"] = config_path      
            settings.config_file = config_path 
            return config_path
            



if __name__ == "__main__":
    WorkfrontConfig