from functools import partial
import os
import click
from cdo_sdk_python import (
    ApiClient,
    InventoryApi,
    CdoTransaction,
    FtdCreateOrUpdateInput,
    FtdRegistrationInput,
)

from cdo_api import execute_using_cdo_api
from transactions_api import wait_for_transaction_to_finish


@click.command()
@click.option(
    "--base-url",
    help="Enter the CDO Base URL",
    prompt=True,
    type=click.Choice(
        [
            "https://www.defenseorchestrator.com",
            "https://apj.cdo.cisco.com",
            "https://www.defenseorchestator.eu",
            "https://au.cdo.cisco.com",
            "https://in.cdo.cisco.com",
        ],
        case_sensitive=True,
    ),
    default="https://www.defenseorchestrator.com",
)
@click.option(
    "--cdo-api-token",
    help="Enter the CDO API token",
    prompt=True,
    hide_input=True,
    default=lambda: os.environ.get("CDO_API_TOKEN"),
    show_default="CDO_API_TOKEN environment variable",
)
@click.option(
    "--ftd-uid",
    help="Specify the unique identifier of the FTD to register",
    prompt=True,
)
def register_ftd_command(base_url: str, cdo_api_token: str, ftd_uid: str):
    execute_using_cdo_api(
        base_url,
        cdo_api_token,
        partial(
            register_ftd,
            ftd_uid,
        ),
    )


def register_ftd(ftd_uid: str, api_client: ApiClient):
    inventory_api_instance = InventoryApi(api_client)
    cdo_transaction: CdoTransaction = (
        inventory_api_instance.finish_onboarding_ftd_device(
            ftd_registration_input=FtdRegistrationInput(ftd_uid=ftd_uid)
        )
    )
    wait_for_transaction_to_finish(
        cdo_transaction,
        api_client,
        f"FTD device onboarded.",
        f"Failed to onboarded FTD device.",
    )


if __name__ == "__main__":
    register_ftd_command()
