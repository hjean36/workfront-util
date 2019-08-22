import json
import pathlib as Path



class Settings:
    def __init__(self): 
        self._settings_file = "workfront_util_settings.json" 

    def _load_settings_file(self): 
        with open(self._settings_file) as json_data_file:
            data = json.load(json_data_file) 
            return data 

class ENVSettings(Settings):
    def __init__(self):
        Settings.__init__(self)
        self.data = Settings._load_settings_file(self)
    
    @property
    def api_version(self):
        api_version = self.data.get("workfront").get('api_version')
        return api_version
    
    @property
    def env(self):
        env = self.data.get("workfront").get('environment')
        return env
    
class Defaults(Settings):
    def __init__(self, objCode):
        Settings.__init__(self)
        self.objCode = objCode
        self.data = Settings._load_settings_file(self)
        self._filters =  self.data.get("workfront").get('filters')
        self._fields =   self.data.get("workfront").get('fields')
    
    @property
    def obj_filter(self):
        return self._filters[self.objCode]

    @property
    def obj_fields(self):
        return self._fields[self.objCode]

class DatabaseConfig(Settings):
    def __init__(self):
        Settings.__init__(self)
        self.data = Settings._load_settings_file(self)
       

    @property
    def connection_string(self):
        return self.data.get("database").get("connection_string")

    @property
    def sqlite_default(self): 
        return self.data.get("database").get("sqlite_default")
    
    @property
    def server(self): 
        return self.data.get("database").get("sql_server").get("server")

    @property
    def username(self): 
        return self.data.get("database").get("sql_server").get("username")

    @property
    def password(self): 
        return self.data.get("database").get("sql_server").get("password")

    @property
    def database(self): 
        return self.data.get("database").get("sql_server").get("database")


    


if __name__ == "__main__":
    ENVSettings()
    Defaults()
    DatabaseConfig()
