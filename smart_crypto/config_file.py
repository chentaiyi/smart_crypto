
import json
import os.path as path

def _readConfig(config_file: str) -> dict:
    if path.exists(config_file):
        with open(config_file, "r") as config_file_r:
            return json.loads(config_file_r.read())
    return {}


def _writeConfig(config_file: str, content: dict) -> None:
    # create config content before opening file not to clear file or json dump exception
    #config_content = configuration.dump_formatted_json(content)
    with open(config_file, "w+") as config_file_w:
        config_file_w.write(content)

def getConfigFile(path) ->dict:
    return _readConfig(path)

if __name__=="__main__":
     r=getConfigFile("config.json")
     print(r)