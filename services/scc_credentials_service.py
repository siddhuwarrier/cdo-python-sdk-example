# services/scc_credentials_service.py
import os
import yaml
from services.token_validation_service import TokenValidationService
from utils.region_mapping import get_scc_url


class SccCredentialsService:
    def __init__(self, region: str, api_token: str):
        self.region = region
        self.api_token = api_token
        self.base_url = self.map_region_to_base_url()
        if not TokenValidationService(self.base_url, self.api_token).validate_token():
            raise ValueError("The provided API token is invalid.")

    def map_region_to_base_url(self):
        base_url = get_scc_url(self.region)
        if not base_url:
            raise ValueError(f"Invalid region specified: {self.region}")
        return base_url

    def get_credentials(self):
        return self.api_token, self.base_url
