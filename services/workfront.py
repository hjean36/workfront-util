import asyncio
import time 
from datetime import datetime 
from pathlib import Path 
import math
import os 

#Local Library 
from services.create_creds import Env
from services.settings import Defaults

#Third-party imports 
import pandas as pd
import requests
from tenacity import *
import ssl
import aiohttp 
from pandas.io.json import json_normalize
import json

"""
TODO: Refactor Classes

"""
class Workfront:
    
    def __init__(self, version, env):
        self.version = version
        self.apiKey =  Env().workfront_api_key
        self.env = env
 
    def __repr__(self): 
        return f"API Version: {self.version}, Env: {self.env}"

    def print_info(self): 
        return f"You are using api version {self.version}  in the {self.env} environment"
        
    def convert_to_str(alist): 
            """ Will convert custom values from model to be read by workfront API 
                Ex: de_program_reporting_requirements -> 'DE: Program Reporting Requirements'
            """ 
            converted =  str(alist).replace("de_", "DE:").replace('DE:program_reporting_requirements', 'DE:Program Reporting Requirements')
            return converted
   
    async def get(self, **options):
        url =  Env.create_url(self.env, self.version) 
        filter_string = ""

        if filter in options: 
            filter_string =  "&".join(list({f"{k}={v}" for (k,v) in options[filter].items()})).replace(" ", "")
        else:
            filter_string = options.get('filter')

        get_url = f"{url}/{options.get('objCode')}?ID={options.get('ID')}&fields={options.get('fields')}&apiKey={self.apiKey}&$$LIMIT={options.get('limit')}"

        async with aiohttp.ClientSession() as session:
                async with session.get(get_url) as resp:
                    resp.raise_for_status() 

                    return await resp

    async def search(self, **options):
        filter_string = ""
    
        if 'filter' in options and isinstance(options['filter'], dict): 
            filter_string =  "&".join(list({f"{parameter}={value}" for (parameter,value) in options['filter'].items()}))#Allows user to pass in a dict for a filter 
        else: 
            filter_string = options.get('filter')

        url = Env.create_url(self.env, self.version)
        search_url =  f"{url}/{options.get('objCode')}/search?{filter_string}&fields={options.get('fields')}&apiKey={self.apiKey}&$$FIRST={options.get('first')}&$$LIMIT={options.get('limit')}"
        
        try: 
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, ssl=ssl.SSLContext()) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except: 
            import pdb; pdb.set_trace()

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(2))
    async def count(self, **options):
        filter_string = ""
        # import pdb; pdb.set_trace()
        if 'filter_option' in options and isinstance(options['filter_option'], dict): 
            filter_string =  "&".join(list({f"{parameter}={value}" for (parameter,value) in options['filter_option'].items()}))#Allows user to pass in a dict for a filter 
        else: 
            filter_string = options.get('filter_option', "")

        url = Env.create_url(self.env, self.version)
        search_url =  f"{url}/{options.get('objCode')}/count?{filter_string}&apiKey={self.apiKey}"

        try: 
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, ssl=ssl.SSLContext()) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except:
            import pdb; pdb.set_trace()

    async def edit(self, **options):
        url = Env.create_url(self.env, self.version)
        edit_url = requests.post((f"{url}/{options.get('objCode')}?updates={options.get('updates')}&apiKey={self.apiKey}"))
    
        async with aiohttp.ClientSession() as session:
                async with session.get(edit_url) as resp:
                    resp.raise_for_status() 

                    return await resp

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(2))
    async def edit_users(self, objCode, ID, fields, *args,**options):
        
        def convert_to_str(adict): 
            """ Will convert custom values from model to be read by workfront API 
                Ex: de_program_reporting_requirements -> 'DE: Program Reporting Requirements'
            """ 
            converted =  str(adict).replace("de_", "DE:").replace('DE:program_reporting_requirements', 'DE:Program Reporting Requirements')
            return converted
    
        fields_string = ""
        # import pdb; pdb.set_trace()
        if fields and isinstance(fields, dict): 
            fields_string=  "&".join(list({f"{parameter}={value}" for (parameter,value) in fields.items()}))#Allows user to pass in a dict for a filter 
        else: 
            fields_string = options.get('filter')

        
        url = Env.create_url(self.env, self.version)
        edit_url = f"{url}/{objCode}/{ID}"
    
        edit_params = {'updates' : convert_to_str(fields) , 'apiKey' : self.apiKey}
        
        try: 
            async with aiohttp.ClientSession() as session:
                    async with session.put(edit_url, params=edit_params, ssl=ssl.SSLContext()) as resp:  
                        resp.raise_for_status() 
                        return await resp.json()
        except Exception as e:
            print(resp.status)
            import pdb; pdb.set_trace()
   
    #TODO: Add to the converter services... Better yet abstract into a utils library. 
    async def report(self, *args, **options):
        groups_string = ""
    
        if 'groups' in options and isinstance(options['groups'], dict): 
            groups_string =  "&".join(list({f"{parameter}={value}" for (parameter,value) in options['groups'].items()}))#Allows user to pass in a dict for a filter 
        else: 
            groups_string = options.get('groups')

        if 'agg_func' in options and isinstance(options['agg_func'], dict): 
            func_string = "".join(list({f"{parameter}={value}" for (parameter,value) in options['agg_func'].items()}))

        url = Env.create_url(self.env, self.version)
        report_url =  f"{url}/{options.get('objCode')}/report?{groups_string}&{func_string}&apiKey={self.apiKey}"
        
        #import pdb; pdb.set_trace()
        async with aiohttp.ClientSession() as session:
            async with session.get(report_url, ssl=ssl.SSLContext()) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def create(self, **options): 
        """ Use this to create a project in workfront 
        
            Takes options as a dictionary. 
            params: objCode - Obj code listed by workfront 
            params: create_params - Dict of fields to set when creation
            params: fields - Fields to return in the response body 
         """
        url = Env.create_url(self.env, self.version)
        create_params = ""
 
        if 'create_params' in options: 
            create_params =  "&".join(list({f"{k}={v}" for (k,v) in options['create_params'].items()})).replace(" ", "")
        
        else:
            create_params = options.get('create_params')
   
        post_url = f"{url}/{options.get('objCode')}?{create_params}&fields={options.get('fields')}&apiKey={self.apiKey}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(post_url, ssl=ssl.SSLContext()) as resp:
                
                resp.raise_for_status()
                return await resp.json()

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(2))
    async def create_bulk(self, create_dicts, fields,*args, **options):
        """
            Use this to create bulk objects in workfront
            Tasks options as a dictionary
            params: objCode  code listed by workfront 
            params: list of dicts to create  Ex : [{"name":"Test_Project_1"},{"name":"Test_Project_2"}]    
            params:fields to return 
        """
        
        url = Env.create_url(self.env, self.version)
        post_url = ""
        post_url = f"{url}/{options.get('objCode')}"
        
        if options.get('objCode') == 'proj':
            create_dicts = [obj for obj in create_dicts if obj['projectID']]
        else: 
            #TODO: Add handler code
            print('Warning: Obj Code not Project. Create Dicts Used') 
  
        
        params = {'updates' : self.convert_to_str(create_dicts) ,'method' : 'POST', 'apiKey' : self.apiKey, 'fields': fields}
        
        try: 
            async with aiohttp.ClientSession() as session:
                async with session.put(post_url, params=params, ssl=ssl.SSLContext()) as resp:  
                    resp.raise_for_status() 
                    return await resp.json()
        except Exception as e:
            print(resp.status)
            import pdb; pdb.set_trace()

            #DEBUG MODE
            #Look for bad strings 
            #TODO Write dict checker/validation code
            #Check search_url
            #print(convert_to_str(create_dicts))

#TODO Bug fix move function up into workfront or down into WorkfrontObj
class Workfront_Api(Workfront): 
    def __init__(self, version, env): 
        super(Workfront_Api, self).__init__(version, env)

    async def return_counts(self, objCode, filter_option=None):
        if filter_option:
           return await super(Workfront_Api, self).count(objCode=objCode, filter_option=filter_option)
        else: 
             return await super(Workfront_Api, self).count(objCode=objCode, filter_option=Defaults(self.objCode).obj_filter)

        
class WorkfrontObj(Workfront_Api): 
    """
    Native async supported class works as a higher level interface to the Workfront base class
    Basic bussines logic is wrapped here as functions to return all data for objs
    Functions should be used apporiately in views and other background tasks 
    """
    def __init__(self, version, env, objCode,  fields=None, filter_option=None, count=0, first=0, sems=10): 
        self.objCode = objCode
        self.first = first
        self.count_of_objects = count
        self.fields = fields 
        self.filter_option = filter_option
        self.callSemaphore = asyncio.BoundedSemaphore(value=sems)
        self.response_data = []
        self.request_tasks = []
        super(WorkfrontObj, self).__init__(version, env)

    def _return_filters(self, objCode=None):
        """
        Checks if a filter was passed. If not default is carried over from settings 
        """
        try:
            if self.filter_option: 
                return self.filter_option
            elif self.objCode:
                self.filter_option = Defaults(self.objCode).obj_filter
                return self.filter_option
        except Exception as e: 
            import pdb ; pdb.set_trace()
            raise Exception('Check filter options')

    def _return_fields(self, objCode=None): 
        """
        Checks if a list of fields was given. If not default is carried over from settings 
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
        Return data from workfront as a list of dicts
        """
   
        if semaphore is None: 
            semaphore = self.callSemaphore
        await semaphore.acquire()
    
        response = await super(WorkfrontObj,self).search(objCode=self.objCode, 
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
        
        counts = loop.run_until_complete((super(WorkfrontObj, self).return_counts(
            objCode=self.objCode, 
            filter_option= self._return_filters(self.objCode)
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

    def to_csv(self, dir, filename):
        self.populate_data()
        data_df  = json_normalize(json.loads(json.dumps(self.response_data)))
        try: 
            data_df.to_csv(Path(f"{dir}/{filename}.csv"))
        except Exception as e: 
            return e 

        return True 
        
    
if __name__ == "__main__":
    WorkfrontObj()
    Workfront_Api()
    Workfront()