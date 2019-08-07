import json
import pathlib as Path



class Settings:
    def __init__(self): 
        self._settings_file = "workfront_util_settings.json" 

    def _load_settings_file(self): 
        with open(self._settings_file) as json_data_file:
            data = json.load(json_data_file) 
            return data 

class ObjConstants(Settings):
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


if __name__ == "__main__":
    ObjConstants()
    Defaults()
