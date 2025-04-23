from .component import Service
import requests


class StatusList(Service):
    def __init__(self, url: str, tenant: str):
        super().__init__(url, tenant)

    def get_status_list(self, user_id: str) -> requests.Response:
        url = f"{self.url}/v1/tenants/tenant_space/status/{user_id}"
        headers = {
            "x-group": user_id
        }
        return requests.get(url, headers=headers, verify=False)

    def revoke_credential(self, list_id: str, index: int) -> requests.Response:
        url = f"{self.url}/v1/tenants/tenant_space/status/{list_id}/revoke/{index}"
        return requests.post(url, verify=False)