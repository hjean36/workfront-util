import asyncio
import time 
from datetime import datetime 
from pathlib import Path 
import math
import os 

#Local Library 
from services.creds import Env
from services.settings import Defaults, ENVSettings

#Third-party imports 
import pandas as pd
import requests
from tenacity import *
import ssl
import aiohttp 
from pandas.io.json import json_normalize
import json
import click

class Workfront:
    """
    Class that is used as a wrapper of the workfront API

    Attributes
    ----------
    version : str 
        API version to use; set in the the config file 
    apiKey : str 
        API key from workfront admin; set in the config file 
    env : str 
        Environment to use when making calls; prod, preview, sandbox set in config file" 

    Methods
    -------

    _process_filter(options)
        This function pulls out filter options from a dict and returns a string for creating requests url 
    
    search(options)
        This function makes a search request to the workfront api.

    """
    
    def __init__(self):
        self.env_settings = ENVSettings()
        self.apiKey = self.env_settings.api_key 

    def _process_filter(self, options):
        """
        This function pulls out filter options from a dict and returns a string for creating requests url 

        Parameters
        ----------

        """
        filter_string = ""
    
        if 'filter' in options and isinstance(options['filter'], dict): 
            "Handles a dictionary"
            filter_string =  "&".join(list({f"{parameter}={value}" for (parameter,value) in options['filter'].items()}))
        else: 
            filter_string = options.get('filter', "")
        
        return filter_string

    
    @retry(wait=wait_fixed(1), stop=stop_after_attempt(2))
    async def search(self, **options):
        """
        This function makes a search request to the workfront api. Code will execute 2 times if it fails
        
        Parameters
        ----------
        filter : dict 
            Filter options following the text mode / api explorer syntax'
        fields : str 
            Comma seperated string of fields to return from the search 
        limit : str 
            Max number of records to return per call. Maximum available from workfront is 2000. Deafult is 100. 
        first : str 
            Index number of the first record to return 
        """

        filter_string = self._process_filter(options)

        "Build the url link"
        url = self.env_settings.url
        search_url =  f"{url}/{options.get('objCode')}/search?{filter_string}&fields={options.get('fields')}"
        search_url = search_url + f"&apiKey={self.apiKey}&$$FIRST={options.get('first')}&$$LIMIT={options.get('limit')}"

        try: 
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, ssl=ssl.SSLContext()) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except Exception as e:
            raise(e) 
            

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(2))
    async def count(self, **options):
        """
        This function counts the number of obj given the options
        
        Parameters
        ----------
        filter : dict 
            Filter options following the text mode / api explorer syntax'
        fields : str 
            Comma seperated string of fields to return from the search 
        limit : str 
            Max number of records to return per call. Maximum available from workfront is 2000. Deafult is 100. 
        first : str 
            Index number of the first record to return 

        """
        filter_string = self._process_filter(options)
        url = self.env_settings.url
        search_url =  f"{url}/{options.get('objCode')}/count?{filter_string}&apiKey={self.apiKey}"
        try: 
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, ssl=ssl.SSLContext()) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except Exception as e:
            raise(e)


    async def return_counts(self, objCode, filter=None):
        """
        Returns the total number of records

        Parameters
        ----------

        objCode : str
            Object code from the api explorer
        filter : dict 
            Filter options following the text mode / api explorer syntax'
        """

        if filter:
           return await self.count(objCode=objCode, filter=filter)
        else: 
             return await self.count(objCode=objCode, filter=Defaults(self.objCode).obj_filter)

        
class WorkfrontAPI(Workfront): 
    """
    This class works as a higher level interface. 
    Basic bussines logic is wrapped here as functions to return all data for workfront objects
    Functions should be used in views and other background tasks 

    Attributes 
    ----------
    version : str 
        API version to use 
    env : str
        Environment to use when making calls; prod, preview, sandbox set in config file" 
    objCode : str 
        Workfront object code 
    fields : str 
        Comma seperated string of fields to return from the search 
    filter : dict 
        Filter options following the text mode / api explorer syntax'
    count : int 
        Number of records to return; Default to 0 will indicate for workfront to return the max 
    first : int 
        Index number of the first record to return 
    sems : int
        Number of semaphores to use for the token bucket algorithm; Default to 10 is optimal for most 
        requests sizes
    """
    def __init__(self, objCode,  fields=None, filter=None, count=0, first=0, sems=10): 
        self.objCode = objCode
        self.first = first
        self.count_of_objects = count
        self.fields = fields 
        self.filter = filter
        self.callSemaphore = asyncio.BoundedSemaphore(value=sems)
        self.response_data = []
        self.request_tasks = []
        super(WorkfrontAPI, self).__init__()

    def _return_filters(self, objCode=None):
        """
        Checks if a filter was passed. If not default is carried over from settings 

        Parameters
        ----------

        objCode : str
            Object code from the api explorer
        """
        try:
            if self.filter: 
                return self.filter
            elif self.objCode:
                self.filter = Defaults(self.objCode).obj_filter
                return self.filter
        except Exception as e: 
            import pdb ; pdb.set_trace()
            raise Exception('Check filter options')

    def _return_fields(self, objCode=None): 
        """
        Checks if a list of fields was given. If not default is carried over from settings 

        Paremeters
        ----------

        objCode : str
            Object code from the api explorer
        """
        try:
            if self.fields: 
                return ",".join(self.fields)
            elif self.objCode:
                self.fields = Defaults(self.objCode).obj_fields
                return self.fields
        except Exception as e: 
            raise Exception('Check Fields')
        
    async def _search_obj(self, first, limit, semaphore=None):
        """
        Async return data from workfront as a list of dicts

        Parameters
        ---------

        first : int 
            Index number of the first record to return 
        limit : int 
            Max number of records to return
        semaphore  : object
            function to use for the token bucket algorithm;
        """
   
        if semaphore is None: 
            semaphore = self.callSemaphore
        await semaphore.acquire()
    
        response = await super(WorkfrontAPI,self).search(objCode=self.objCode, 
                                            filter=self._return_filters(self.objCode), 
                                            fields=self._return_fields(self.objCode), 
                                            first=first, limit=limit)
      
        self.response_data.extend(response.get('data')) 
        semaphore.release()
      

    def _collect_requests(self):
        """
        Async requests collected to be run on the async loop
        """
        loop = asyncio.get_event_loop()
        
        counts = loop.run_until_complete((super(WorkfrontAPI, self).return_counts(
            objCode=self.objCode, 
            filter= self._return_filters(self.objCode)
            )))
        if self.count_of_objects is 0: 
            self.count_of_objects = counts.get("data").get("count")

        if self.count_of_objects > 2000: 
            #Collect the number of requests that should be made 
            number_of_requests = math.ceil(self.count_of_objects / 2000.0)
            request_list = list(range(1, number_of_requests))

            #Append the first call
            first = self.first
            limit=2000
            self.request_tasks.append(self._search_obj(first=first, limit=limit, semaphore=self.callSemaphore))

            #Append all calls except the first & last one 
            for n in request_list[:-1]:
                first += 2000
                self.request_tasks.append(self._search_obj(first=first, limit=limit, semaphore=self.callSemaphore))

            #Append the final call
            first = (self.count_of_objects + self.first) - 2000   
            limit = 2000 if self.count_of_objects % 2000 ==  0 else self.count_of_objects % 2000
            self.request_tasks.append(self._search_obj(first=first, limit=limit, semaphore=self.callSemaphore))
        else: 
            self.request_tasks.append(self._search_obj(first=0, limit=self.count_of_objects, semaphore=self.callSemaphore))
    

    def populate_data(self):
        """
        This function runs the async loop to collect data into the response data list 
        """
        self._collect_requests()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(self.request_tasks))

    def return_all(self, flat=False):
        """
        Returns all data for a Obj based on the initalized filters as a pandas dataframe
        """
        if flat: 
            self.populate_data()
            data_df  = json_normalize(json.loads(json.dumps(self.response_data)))
            return data_df
        else: 
            self.populate_data()
            return self.response_data
        
    
if __name__ == "__main__":
    WorkfrontAPI()
    Workfront_Api()
    Workfront()