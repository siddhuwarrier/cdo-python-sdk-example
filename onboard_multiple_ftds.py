import re
from typing import List

import click
from rich.console import Console
from cdo_sdk_python import ApiClient, Configuration, FtdCreateOrUpdateInput
from click_option_group import MutuallyExclusiveOptionGroup, AllOptionGroup, optgroup

from parsers.ftd_parser import FtdParser
from services.cdfmc_api_service import CdFmcApiService
from services.inventory_api_service import InventoryApiService
from services.scc_credentials_service import SccCredentialsService
from utils.region_mapping import supported_regions
from validators.ftd_csv_validator import FtdCsvValidator
from validators.ftd_ztp_csv_validator import FtdZtpCsvValidator


UUID_REGEX = re.compile(
    r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
)


def validate_uuid(ctx: click.Context, param: click.Parameter, value: str) -> str | None:
    if value is not None and not UUID_REGEX.match(value):
        raise click.BadParameter(f"{param.name} must be a valid UUID.")
    return value


def validate_ftd_csv_file(
    _ctx: click.Context, _param: click.Parameter, value: str
) -> str:
    if value:
        validator = FtdCsvValidator(value)
        if not validator.validate():
            raise click.BadParameter(f"CSV file {value} is invalid.")
    return value


def validate_ztp_ftd_csv_file(
    _ctx: click.Context, _param: click.Parameter, value: str
) -> str:
    if value:
        validator = FtdZtpCsvValidator(value)
        if not validator.validate():
            raise click.BadParameter(f"CSV file {value} is invalid.")
    return value


@click.command(
    help="Onboard FTDs to an MSP managed tenant. You need a super-admin API token generated using the Cisco Security Cloud Control MSSP portal to use this script."
)
@click.option(
    "--fmc-access-policy-id",
    type=str,
    callback=validate_uuid,
    help="The ID of the access policy to apply to this device when onboarded.",
)
@click.option(
    "--ftd-csv-file",
    required=True,
    type=str,
    callback=validate_ftd_csv_file,
    help="Path to the CSV file with FTD information. The CSV file should contain the FTD address, username, password, licenses, and performance tier if the FTD is virtual.",
)
@click.option(
    "--region",
    help="The region for the API.",
    type=click.Choice(supported_regions),
    required=True,
)
@click.option("--api-token", type=str, help="The API token.", required=True)
def main(
    ftd_csv_file: str, region: str, api_token: str, fmc_access_policy_id: str
) -> None:
    console = Console()
    api_token, base_url = SccCredentialsService(
        region=region, api_token=api_token
    ).get_credentials()
    with ApiClient(Configuration(host=base_url, access_token=api_token)) as api_client:
        if fmc_access_policy_id is None:
            cdfmc_api_service = CdFmcApiService(api_client)
            fmc_access_policy = cdfmc_api_service.get_first_access_policy_uid()
            fmc_access_policy_id = fmc_access_policy.id
            console.print(
                f'[orange]Using FMC Access Policy "{fmc_access_policy.name}" (UID: {fmc_access_policy_id})...[/orange]'
            )

        ftd_parser = FtdParser(
            fmc_access_policy_uid=fmc_access_policy_id, ftd_csv_file=ftd_csv_file
        )
        ftd_inputs: List[FtdCreateOrUpdateInput] = ftd_parser.get_ftds_to_onboard()
        console.print(f"[orange]Onboarding {len(ftd_inputs)} FTD(s)...[/orange]")

        inventory_api_service = InventoryApiService(api_client=api_client)
        for ftd_input in ftd_inputs:
            inventory_api_service.onboard_ftd_device(ftd_input)


if __name__ == "__main__":
    main()
