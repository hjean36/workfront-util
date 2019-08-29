import json
import pathlib as Path
import pyodbc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,  create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os

CONFIG_FILE = ""

class Settings:
    def __init__(self): 
        self._settings_file = CONFIG_FILE

    def _load_settings_file(self): 
        with open(self._settings_file) as json_data_file:
            data = json.load(json_data_file) 
            return data 

class ENVSettings(Settings):
    def __init__(self):
        Settings.__init__(self)
        self.data = Settings._load_settings_file(self)
    
    @property
    def api_version(self):
        api_version = self.data.get("workfront").get('api_version')
        return api_version
    
    @property
    def env(self):
        env = self.data.get("workfront").get('environment')
        return env

    @property
    def api_key(self): 
        api_key = self.data.get("workfront").get("api_key")
        return api_key
    
class Defaults(Settings):
    def __init__(self, objCode):
        Settings.__init__(self)
        self.objCode = objCode
        self.data = Settings._load_settings_file(self)
        self._filters =  self.data.get("workfront").get('filters')
        self._fields =   self.data.get("workfront").get('fields')
    
    @property
    def obj_filter(self):
        return self._filters[self.objCode]

    @property
    def obj_fields(self):
        return self._fields[self.objCode]

class DatabaseConfig(Settings):
    def __init__(self):
        Settings.__init__(self)
        self.data = Settings._load_settings_file(self)
        self.server = self.data.get("database").get("sql_server").get("server")
        self.username = self.data.get("database").get("sql_server").get("username")
        self.password = self.data.get("database").get("sql_server").get("password")
        self.prod_database = self.data.get("database").get("sql_server").get("prod_database")
        self.test_database = self.data.get("database").get("sql_server").get("test_database")
        self.init_db_dir_path = ""
        self.database = ""
        self.engine = ""
        self.Base = declarative_base()
        self.metadata = self.Base.metadata
        self.session = scoped_session(sessionmaker())
    
    @property
    def sqlite_connection_string(self):
        return self.data.get("database").get("sqlite_connection_string")

    @property
    def sqlite_default(self): 
        return self.data.get("database").get("sqlite_default")

    def set_up_sqlite(self): 
        if not self.sqlite_connection_string:
            if os.name == 'nt':
                self.init_db_dir_path = os.path.join(os.environ['temp'], 'workfront')
            else:
                self.init_db_dir_path  = os.path.join(os.environ['TMPDIR'], 'workfront')
            
            if not os.path.exists(self.init_db_dir_path ):
                os.makedirs(self.init_db_dir_path )

            self.database = os.path.join(self.init_db_dir_path , 'test.db')
            self.engine = create_engine(f"sqlite:///{self.database}", echo=False)
        self.session.remove()
        self.session.configure(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.metadata.drop_all(self.engine)
        self.metadata.create_all(self.engine)
        return self.engine
    
    def init_db_connection(self, test=False, sqlite=False, database=None):
        if sqlite: 
            engine = self.set_up_sqlite()
            return engine

        if database and not test: 
            self.database = database
        elif database and test: 
            self.database = self.test_database
        elif not database and not test: 
            raise Exception("Indicate which database to use or pass test=True")

        cxn = pyodbc.connect('driver={ODBC Driver 17 for SQL Server};SERVER='+self.server+';DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
        
        return cxn.cursor()


    


if __name__ == "__main__":
    ENVSettings()
    Defaults()
    DatabaseConfig()
