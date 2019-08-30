import asyncio 
import sys
import sqlite3
from sqlite3 import Error
import os
import time
import sqlite3
from datetime import datetime

#Third party Imports 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,  create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import pandas as pd
from pandas.io.json import json_normalize
import json
from pathlib import Path

#Local Imports
from services.workfront import WorkfrontAPI
from services.settings import ENVSettings, Defaults


"""
TODO: Read in database settings for db name, connection string and location


"""
class DBU:
    def __init__(self, engine=None):
        #TODO: Get input from settings file for self.dir
        self.Base = declarative_base()
        self.metadata = self.Base.metadata
        self.session = scoped_session(sessionmaker())
        self.engine = engine
        self.database = ""


    def _init_db(self, database_name, sqlite_connection_string):
        init_db_dir_path = ""
        
        #Create a workfront temp dir for the compliance database 
        if os.name == 'nt':
                init_db_dir_path = os.path.join(os.environ['temp'], 'workfront')
        
        if not os.path.exists(init_db_dir_path ):
            os.makedirs(init_db_dir_path)
        
        #Set up the database
        self.database = os.path.join(init_db_dir_path , database_name)
        self.engine = create_engine(sqlite_connection_string, echo=False)
        self.session.remove()
        self.session.configure(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.metadata.drop_all(self.engine)
        self.metadata.create_all(self.engine)


        def _save_data_to_db(self, objCode, count=None, filter=None):
            self._init_db()
            start = time.time()
    
            if count is None:
                count = 0 #Workfront Obj will go find the max count 
            print("Fetching Data....")
            obj_api = WorkfrontAPI(objCode = objCode) 
            obj_data = obj_api.return_all(flat=True)   
            print("Saving data....")
            obj_data.to_sql(objCode, con=self.engine,  if_exists='replace')
            duration = time.time() - start
            print('SQLAlchemy Core - total time: {:.2f} seconds'.format(duration))


if __name__ == "__main__":
    DBU()