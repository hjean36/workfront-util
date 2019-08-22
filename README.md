# workfront-util
### Simple Python library that can be used to retrieve data from the workfront api. 
---

#### Easily return all data for any objCode from the workfront api. 
#### This library uses asyncio under the hood to batch requests and return a list of dicts. 
---
```
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
settings = ENVSettings

hour_api = WorkfrontObj(
    version = settings.api_version,
    env= settings.env,
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
settings = ENVSettings()

filter_option = {
                    "entryDate": "2019-07-01", 
                    "entryDate_Mod": "between", 
                    "entryDate_Range": "$$TODAYb"          
            }
            
hour_api = WorkfrontObj(
    version = settings.api_version,
    env= settings.env ,
    fields = "*"
    filter_option= filter_option, 
    objCode= 'hour')

hours = hour_api.return_all()

```

Return a flat pandas dataframe by passing flat=true

```
hours = hour_api.return_all(flat=True)
```


Set up Sqlite and MSSSQL Database Connections via the config file 
```
{
    "database" : {
        "sqlite_database_path" : "",   
        "sql_server": {
            "server" : "localhost", 
            "database" : "TestDB", 
            "username" : "sa", 
            "password" : "myStronGPassword"
        }
    }, 

```

Retrieve Data from the database 
```
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
```

 
