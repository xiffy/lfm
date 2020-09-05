
class Config:
    def __init__(self, ap_base_url=None, api_key=None):
        self.api_base_url = api_base_url if  ap_base_url != None else 'https://ws.audioscrobbler.com/2.0/'
        self.api_key = api_key if api_key != None else '4c2ab2b69e38701ff36698fc0a319159'