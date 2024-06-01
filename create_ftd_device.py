from functools import partial
import os
import sys
import click
import paramiko
from cdo_sdk_python import (
    ApiClient,
    InventoryApi,
    CdoTransaction,
    FtdCreateOrUpdateInput,
)

from cdo_api import execute_using_cdo_api
from transactions_api import wait_for_transaction_to_finish


def create_ftd_device(
    device_name: str,
    fmc_access_policy_uid: str,
    licenses: list[str],
    is_virtual: bool,
    performance_tier: str,
    api_client: ApiClient,
):
    inventory_api_instance = InventoryApi(api_client)
    cdo_transaction: CdoTransaction = inventory_api_instance.create_ftd_device(
        ftd_create_or_update_input=FtdCreateOrUpdateInput(
            name=device_name,
            licenses=licenses,
            fmc_access_policy_uid=fmc_access_policy_uid,
            device_type="CDFMC_MANAGED_FTD",
            virtual=is_virtual,
            performance_tier=(performance_tier if is_virtual else None),
        )
    )
    wait_for_transaction_to_finish(
        cdo_transaction,
        api_client,
        f"FTD device created.",
        f"Failed to create FTD device.",
    )
    print(f"FTD UID: {cdo_transaction.entity_uid}")
    print(
        f"Paste this into your FTD CLI: {inventory_api_instance.get_device(cdo_transaction.entity_uid).cd_fmc_info.cli_key}"
    )


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
@click.option("--device-name", help="Enter the ASA device name", prompt=True)
@click.option(
    "--fmc-access-policy-uid",
    help="Specify the unique identifier of the FMC Access Policy",
    prompt=True,
)
@click.option(
    "--licenses",
    help="Specify the licenses",
    multiple=True,
    default=["BASE"],
    prompt=True,
)
@click.option(
    "--is-virtual",
    help="Specify if this is a virtual device",
    default=True,
    prompt=True,
)
@click.option(
    "--performance-tier",
    help="Specify if this is a virtual device",
    default="FTDv5",
    prompt=True,
)
def create_ftd_command(
    base_url: str,
    cdo_api_token: str,
    device_name: str,
    fmc_access_policy_uid: str,
    licenses: list[str],
    is_virtual: bool,
    performance_tier: str,
):
    execute_using_cdo_api(
        base_url,
        cdo_api_token,
        partial(
            create_ftd_device,
            device_name,
            fmc_access_policy_uid,
            licenses,
            is_virtual,
            performance_tier,
        ),
    )


if __name__ == "__main__":
    create_ftd_command()
