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
        self.cursor = DatabaseConfig().init_db_connection(database="TestDB")
        self.cursor.execute("CREATE TABLE test_table ( value1 int, value2 int)")
        self.cursor.execute("INSERT INTO test_table VALUES (1, 3)")
   
    def tearDown(self): 
        self.cursor.execute("DROP TABLE test_table")
        

    def test_connect_to_sql_database(self):   
            self.cursor.execute("SELECT * FROM [dbo].[test_table]") 
            row = self.cursor.fetchone() 
            self.assertIsNotNone(row)
                


if __name__ == "__main__":
    unittest.main() 