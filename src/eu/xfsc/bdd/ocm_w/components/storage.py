import json

import requests

from .component import Service


class Storage(Service):
    def __init__(self, url: str, tenant: str):
        super().__init__(url, tenant)

    def get_credentials(self, user_id: str, search: str) -> requests.Response:
        url = f"{self.url}/v1/tenants/{self.tenant}/storage/{user_id}/credentials"
        headers = {
            "Content-Type": "application/json"
        }
        return requests.post(url, headers=headers, data=json.dumps(self.__get_credential_filter(search)), verify=False)

    def get_presentations(self, user_id: str) -> requests.Response:
        url = f"{self.url}/v1/tenants/{self.tenant}/storage/{user_id}/presentations"
        headers = {
            "Content-Type": "application/json"
        }
        return requests.post(url, headers=headers, verify=False)


    @staticmethod
    def __get_credential_filter(search: str) -> dict[str, object]:
        return {
            "input_descriptors": [
                {
                    "constraints": {"fields": [{
                        "path": ["$.credentialSubject"],
                        "filter": {
                            "pattern": search,
                        }
                    }]
                    }
                }
            ]
        }

    @staticmethod
    def drop_proofs(credentials_data):
        for item in credentials_data["groups"]:
            for cred in item["credentials"].values():
                del cred["proof"]