from .component import Service
import requests

class WellKnown(Service):
    def __init__(self, url: str, tenant: str):
        super().__init__(url, tenant)

    def get_schemas(self) -> requests.Response:
        url = f"{self.url}/v1/tenants/{self.tenant}/.well-known/openid-credential-issuer"
        return requests.get(url, verify=False)
