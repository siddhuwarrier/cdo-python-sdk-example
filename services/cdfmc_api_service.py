import requests
from cdo_sdk_python import ApiClient, InventoryApi, DevicePage

from models.fmc import FmcAccessPolicy


class CdFmcApiService:
    def __init__(self, api_client: ApiClient):
        self.api_client = api_client
        inventory_api = InventoryApi(api_client)
        manager_page: DevicePage = inventory_api.get_device_managers(
            limit="1", offset="0", q="deviceType:CDFMC"
        )
        if len(manager_page.items) != 1:
            raise RuntimeError("CDFMC not found")
        self.cdfmc_domain_uid = manager_page.items[0].fmc_domain_uid

    def get_first_access_policy_uid(self) -> FmcAccessPolicy:
        url = (
            f"{self.api_client.configuration.host}/v1/cdfmc/api/fmc_config/v1/domain/"
            f"{self.cdfmc_domain_uid}/policy/accesspolicies"
        )
        headers = {
            "Authorization": f"Bearer {self.api_client.configuration.access_token}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        first_access_policy = response.json()["items"][0]
        return FmcAccessPolicy(
            name=first_access_policy["name"],
            id=first_access_policy["id"],
        )
