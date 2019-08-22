import unittest 
import asyncio 
from pathlib import Path
import glob
import datetime
import os
import pyodbc


#Third Party Imports 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,  create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import pandas as pd

#Local Imports 
from services.workfront import WorkfrontAPI 
from services.settings import ENVSettings, DatabaseConfig, Defaults
from services.db_util import DBU

class TestDatabase(unittest.TestCase): 

    def setUp(self): 
        #TODO: Create test db 
        #TODO:  Create Test Table 
        #TODO; Create test values
        pass 

    def tearDown(self): 
        #Delete Test Tables 
        pass 

    def test_connect_to_sql_database(self): 
            #TODO: Import test values
            database_settings = DatabaseConfig()
            server = dataabse_settings.server
            database = dataabse_settings.database
            username = dataabse_settings.username
            password =  dataabse_settings.password
            cnxn = pyodbc.connect('driver={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
            cursor = cnxn.cursor()

            cursor.execute("SELECT * FROM [dbo].[test_table]") 
            row = cursor.fetchone() 
            while row: 
                print(row[0])
                row = cursor.fetchone()


if __name__ == "__main__":
    unittest.main() 