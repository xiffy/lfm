# Configuration settings
# api_base_url, defaults to: https://ws.audioscrobbler.com/2.0/
# api_key: no default
# base_url: domain which hosts the webpage, defauls to


class Config:
    def __init__(self, api_base_url=None, api_key=None, base_url=None):
        self.api_base_url = (
            api_base_url
            if api_base_url is not None
            else "https://ws.audioscrobbler.com/2.0/"
        )
        self.api_key = api_key if api_key is not None else "<YOUR API_KEY HERE>"
        self.base_url = base_url if base_url is not None else "/"
