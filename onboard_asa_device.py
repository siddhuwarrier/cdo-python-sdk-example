from functools import partial
import os
import sys
import time
import click
from cdo_sdk_python import (
    ApiClient,
    InventoryApi,
    CdoTransaction,
    AsaCreateOrUpdateInput,
    TransactionsApi,
)

from cdo_api import execute_using_cdo_api


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
    "--device-address", help="Enter the ASA's management interface address", prompt=True
)
@click.option("--username", help="Enter the ASA username", prompt=True)
@click.option("--password", help="Enter the ASA password", prompt=True, hide_input=True)
@click.option(
    "--connector-type",
    help="Enter the connector type",
    prompt=True,
    type=click.Choice(["SDC", "CDG"], case_sensitive=True),
    default="CDG",
)
def onboard_asa_command(
    base_url: str,
    cdo_api_token: str,
    device_name: str,
    device_address: str,
    username: str,
    password: str,
    connector_type: str,
):
    execute_using_cdo_api(
        base_url,
        cdo_api_token,
        partial(
            onboard_asa_device,
            device_name,
            device_address,
            username,
            password,
            connector_type,
        ),
    )


def onboard_asa_device(
    device_name: str,
    device_address: str,
    username: str,
    password: str,
    connector_type: str,
    api_client: ApiClient,
):
    inventory_api_instance = InventoryApi(api_client)
    cdo_transaction: CdoTransaction = inventory_api_instance.onboard_asa_device(
        asa_create_or_update_input=AsaCreateOrUpdateInput(
            name=device_name,
            username=username,
            password=password,
            device_address=device_address,
            connector_type=connector_type,
        )
    )

    transaction_api_instance = TransactionsApi(api_client)
    while (
        cdo_transaction.cdo_transaction_status != "DONE"
        and cdo_transaction.cdo_transaction_status != "ERROR"
    ):
        cdo_transaction = transaction_api_instance.get_transaction(
            cdo_transaction.transaction_uid
        )
        print(f"CDO transaction status: {cdo_transaction.cdo_transaction_status}")
        time.sleep(3)

    if cdo_transaction.cdo_transaction_status == "ERROR":
        print(
            f"Error onboarding ASA device {cdo_transaction.entity_uid}: {cdo_transaction.error_message}"
        )
        sys.exit(1)
    else:
        print(
            f"Onboarding ASA device completed. Device UID: {cdo_transaction.entity_uid}"
        )


if __name__ == "__main__":
    onboard_asa_command()
