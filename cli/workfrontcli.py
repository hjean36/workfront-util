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
import click
import click

#Local Imports 
from services.workfront import WorkfrontAPI 
from services.settings import ENVSettings, DatabaseConfig, Defaults
from services.db_util import DBU
from cli.tools import WorkfrontConfig

@click.command()
@click.option('--make_config', help="Generate config files")
@click.option('--objCode', help="Target objCode")
@click.option('--fields', help="Target objCode fields to return")
@click.option('--filter', help="Target objCode filter to use")
@click.option('--add_default_fields', help="Add a default fields for objCode")
@click.option('--add_default_filter', help="Add a default filter for objCode")
@click.option('--use_fields', help="Use fields for objCode")
@click.option('--use_filter', help="Use filter for objCode")
@click.option('--add_api_key', help="WF API Key")
@click.option('--server', help="Database Server")
@click.option('--table_name', help="Table output")
@click.option('--db_password', help='DB password')
def main(**kwargs):
    if kwargs.get('make_config'):
        wf_conf = WorkfrontConfig()
        wf_conf.gen_config()

    

    
            



if __name__ == "__main__":
    main()