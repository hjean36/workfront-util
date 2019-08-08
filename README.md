# workfront-util
Simple Python library that can be used to retrieve data from the workfront api. 


### Easily return all data for any objCode from the workfront api. 
### This library uses asyncio under the hood to batch requests and return a list of dicts. 
---
```
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

hour_api = WorkfrontObj(
    version = ObjConstants().api_version,
    env= ObjConstants().env,
    objCode= 'hour')

hours = hour_api.return_all()
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
OR Add your filter options and field selections inline if preffered. 

```
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

filter_option = {
                    "entryDate": "2019-07-01", 
                    "entryDate_Mod": "between", 
                    "entryDate_Range": "$$TODAYb"          
            }
            
hour_api = WorkfrontObj(
    version = "9.0",
    env= "prod" ,
    fields = "*"
    filter_option= filter_option, 
    objCode= 'hour')

hours = hour_api.return_all()

```


 
