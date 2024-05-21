from typing import Callable
from cdo_sdk_python import Configuration, ApiClient

def execute_using_cdo_api(base_url: str, bearer_token: str, function_to_execute: Callable[[ApiClient], None]):
  configuration = Configuration(host=f"{base_url}/api/rest")
  configuration.access_token = bearer_token
  with ApiClient(configuration) as api_client:
    function_to_execute(api_client)