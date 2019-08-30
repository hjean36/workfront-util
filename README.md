# workfront-util
### Simple Python library that can be used to retrieve data from the workfront api. 
---

#### Easily return all data for any objCode from the workfront api. 
#### This library uses asyncio under the hood to batch requests and return a list of dicts. 
---
```
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
api = WorkfrontAPI(objCode= 'hour')
hours = api.return_all()
```
---
Control the results by configuring a workfront_util_settings.json file.  

```
{
  "workfront" : {
        "environment": "prod", 
        "api_version": "9.0", 
        "filters": {
            "hour" : {
                    "entryDate": "2019-07-01", 
                    "entryDate_Mod": "between", 
                    "entryDate_Range": "$$TODAYb"          
            }
        }, 
        "fields" : {
            "hour" : "*"

        }

}
```
---
OR Add your filter options and field selections inline if preferred. 

```
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
settings = ENVSettings()

filter_option = {
                    "entryDate": "2019-07-01", 
                    "entryDate_Mod": "between", 
                    "entryDate_Range": "$$TODAYb"          
            }
            
api = WorkfrontAPI(
    version = settings.api_version,
    env= settings.env ,
    fields = "*"
    filter_option= filter_option, 
    objCode= 'hour')

hours = api.return_all()

```

Return a flat pandas dataframe by passing flat=true

```
hours = api.return_all(flat=True)
```


Run a CLI 

```
Usage: workfrontutil [OPTIONS]

Options:
  --make_config TEXT  Generate config file
  --config_path TEXT  location of config file
  --objCode TEXT      Target objCode
  --fields TEXT       Target objCode fields to return
  --filter TEXT       Target objCode filter to use
  --edit_config TEXT  Update Config file
  --save_obj TEXT     Save all objCode data to DB
  --help              Show this message and exit.

```

#Getting Started

Install the package 
```
pip install workforntutil
```

Run from the cli or import into your script

```
from workfrontutil import WorkfrontAPI
```




