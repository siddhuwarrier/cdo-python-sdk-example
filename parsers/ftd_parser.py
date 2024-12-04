import csv
from typing import List

import questionary
from cdo_sdk_python import FtdCreateOrUpdateInput


class FtdParser:
    def __init__(self, fmc_access_policy_uid: str, ftd_csv_file: str):
        self.fmc_access_policy_uid = fmc_access_policy_uid
        self.ftd_csv_file = ftd_csv_file

    def get_ftds_to_onboard(
        self,
    ) -> List[FtdCreateOrUpdateInput]:
        return self._parse_csv()

    def _parse_csv(self) -> List[FtdCreateOrUpdateInput]:
        ftd_credentials = []
        with open(self.ftd_csv_file, mode="r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                licenses = row["licenses"].split(";")
                virtual = row["virtual"].lower() == "true"
                performance_tier = row.get("performance_tier")
                ftd_credentials.append(
                    FtdCreateOrUpdateInput(
                        name=row["name"],
                        licenses=licenses,
                        virtual=virtual,
                        performance_tier=performance_tier,
                        fmc_access_policy_uid=self.fmc_access_policy_uid,
                        device_type="CDFMC_MANAGED_FTD",
                    ),
                )
        return ftd_credentials
