import asyncio 
from pathlib import Path
import glob
import datetime
import os
import glob
from sys import platform
import asyncio

#Third Party Imports 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String,  create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import pandas as pd
import click


#Local Imports 
from services.workfront import WorkfrontAPI 
from services import settings
from services.db_util import DBU
from cli.tools import WorkfrontConfig

class Config(object):
                def __init__(self, home=None, debug=False):
                        self.config_file = ""
@click.command()
@click.option('--make_config', help="Generate config files")
@click.option('--config_path', help="location of config file")
@click.option('--objCode', help="Target objCode")
@click.option('--fields', help="Target objCode fields to return")
@click.option('--filter', help="Target objCode filter to use")
@click.option('--edit_config', help="Update Config file")
@click.option('--save_obj', help="Save all objCode data to DB")
def main(**kwargs):
        if kwargs.get('make_config'):
                wf_conf = WorkfrontConfig()
                wf_conf.gen_config()

        """if not settings.config_file:
                path = click.echo("Generate Config file before adding additional defalts. Run --make_config")"""
       
        if kwargs.get('edit_config'):
                config_dir_path = ""
                if os.name == 'nt':
                        config_dir_path = os.path.join(os.environ['temp'], 'workfront')
                else: 
                        config_dir_path = os.path.join(os.environ['TMPDIR'], 'workfront')
                config_json =  os.path.join(config_dir_path , 'wf_config.json')
                
                if platform == "darwin":
                        my_cmd = f"Open /Applications/TextEdit.app {config_json}"
                        os.system(my_cmd)
                elif platform == "win32":
                        my_cmd = f"open {config_json}"
                        os.system(my_cmd)
        
        if kwargs.get("save_obj"): 
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                api = WorkfrontAPI(objCode= kwargs.get("save_obj"))
                obj_df = api.return_all(flat=True)
                engine = settings.DatabaseConfig(db_name="workfront.db").init_db_connection(sqlite=True)
                obj_df.to_sql(kwargs.get("save_obj"), con=engine,  if_exists='replace')
                obj = kwargs.get("save_obj")
                print(f"{obj} Object Saved!")
                
if __name__ == "__main__":
    main()