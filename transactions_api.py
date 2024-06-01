import sys
import time
from cdo_sdk_python import (
    ApiClient,
    CdoTransaction,
    TransactionsApi,
)


def wait_for_transaction_to_finish(
    cdo_transaction: CdoTransaction, api_client: ApiClient, success_msg, failure_message
):
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
        print(failure_message)
        sys.exit(1)
    else:
        print(success_msg)
