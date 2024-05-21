import os
from typing import Dict
from functools import partial
from cdo_sdk_python import Configuration, ApiClient, UsersApi
from cdo_sdk_python.models.user_create_or_update_input import UserCreateOrUpdateInput

from cdo_api import execute_using_cdo_api

configuration = Configuration(host="https://www.defenseorchestrator.com/api/rest")
configuration.access_token = os.environ["BEARER_TOKEN"]

users = {
    "londo.mollari@babylon5.universe": "ROLE_SUPER_ADMIN",
    "delenn@babylon5.universe": "ROLE_READ_ONLY",
    "susan.ivanova@babylon5.universe": "ROLE_ADMIN",
    "john.sheridan@babylon5.universe": "ROLE_SUPER_ADMIN",
}

def create_users(users: Dict[str, str], api_client):
   api_instance = UsersApi(api_client)
   for username, role in users.items():
     user_api_response = api_instance.create_user(
         user_create_or_update_input=UserCreateOrUpdateInput(
             name=username, role=role, api_only_user=False
         )
     )
     print(f"User {username} created with role {role}. Response: {user_api_response}")

execute_using_cdo_api("https://www.defenseorchestrator.com", os.environ["BEARER_TOKEN"], partial(create_users, users))
