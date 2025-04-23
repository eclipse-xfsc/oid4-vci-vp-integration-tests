from abc import ABC
import requests


class Service(ABC):
    def __init__(self, url: str, tenant: str):
        self.url = url
        self.tenant = tenant

    def is_healthy(self) -> bool:
        url = f"{self.url}/v1/metrics/health"
        res = requests.get(url)
        return res.ok
