import yaml
from types import SimpleNamespace

class Config:
    def __init__(self,file='./config.yml'):

        with open(file,'r') as yamlfh:
            configs=yaml.load(yamlfh,Loader=yaml.FullLoader)

        self.hash={}

        for key in configs:
            val=configs[key]

            self.hash[key]=val
            setattr(self,key,val)

    def __iter__(self):
        return iter(self.hash.keys())


config=Config()
