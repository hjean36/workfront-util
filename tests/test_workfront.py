import unittest 
import asyncio 
from pathlib import Path
import glob
import datetime
import os

#Third Party Imports 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,  create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import pandas as pd

#Local Imports 
from services.workfront import WorkfrontAPI 
from services.settings import ENVSettings, DatabaseConfig, Defaults
from services.db_util import DBU



class TestWorkfrontInterface(unittest.TestCase): 
   
    def setUp(self): 
        self._helper = DBU()
        self.files_processed = False            
        self.init_db_dir_path = ""
        self.database = ""
        self.engine = ""
        self.Base = declarative_base()
        self.metadata = self.Base.metadata
        self.session = scoped_session(sessionmaker())


    def tearDown(self):
        if self.database:
            os.remove(self.database)
        
    def test_set_up_database_no_sqlite_connection_string(self): 
        #Import database settings 
        self.database_settings = DatabaseConfig() 

        #Check if user passed a connection string
        if not self.database_settings.sqlite_connection_string:
            if os.name == 'nt':
                self.init_db_dir_path = os.path.join(os.environ['temp'], 'workfront')
            else:
                self.init_db_dir_path  = os.path.join(os.environ['TMPDIR'], 'workfront')
            
            if not os.path.exists(self.init_db_dir_path ):
                os.makedirs(self.init_db_dir_path )

            self.database = os.path.join(self.init_db_dir_path , 'test.db')
            self.engine = create_engine(f"sqlite:///{self.database}", echo=False)
            
        #Create a workfront temp dir for the database 
        self.session.remove()
        self.session.configure(bind=self.engine, autoflush=False, expire_on_commit=False)
        self.metadata.drop_all(self.engine)
        self.metadata.create_all(self.engine)

        self.assertTrue(os.path.isfile(self.database))
        
        
    def test_settings(self):
        filter = Defaults("hour").obj_filter
        self.assertIsNotNone(filter)
        hour_options = {
            "entryDate": "2019-07-01", 
            "entryDate_Mod": "between", 
            "entryDate_Range": "$$TODAYb"
            }
        self.assertEqual(filter, hour_options)

    def test_hours_save(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        #Accepts parameters for fields and filter option for all data
        hour_api = WorkfrontAPI(objCode= 'hour')
        hours = hour_api.return_all()
        self.assertEqual(len(hours) ,  hour_api.count_of_objects)

if __name__ == '__main__': 
    unittest.main() 