import os
from cdo_sdk_python import ApiClient, InventoryApi, DevicePage

from cdo_api import execute_using_cdo_api

def list_devices(api_client: ApiClient):
  api_instance = InventoryApi(api_client)
  api_response: DevicePage = api_instance.get_devices()
  print(f"Number of devices: {api_response.count}")
  print(f"Devices: {api_response.items}")

execute_using_cdo_api("https://www.defenseorchestrator.com", os.environ["BEARER_TOKEN"], list_devices)