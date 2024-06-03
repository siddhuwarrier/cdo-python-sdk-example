from functools import partial
import os
import click
from cdo_sdk_python import (
    ApiClient,
    InventoryApi,
    AIAssistantApi,
    AiQuestion,
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
    "--question",
    help="Enter the question you want to ask the AI Assistant",
    prompt=True,
)
def ask_ai_assistant_question_cmd(base_url: str, cdo_api_token: str, question: str):
    execute_using_cdo_api(
        base_url,
        cdo_api_token,
        partial(ask_ai_assistant_question, question),
    )


def ask_ai_assistant_question(question: str, api_client: str):
    ai_assistant_api = AIAssistantApi(api_client)
    cdo_transaction = ai_assistant_api.ask_ai_assistant(
        ai_question=AiQuestion(content=question)
    )
    wait_for_transaction_to_finish(
        cdo_transaction,
        api_client,
        "Received answer from AI Assistant",
        "Failed to get answer from AI assistant",
    )

    messages = ai_assistant_api.get_ai_assistant_conversation_messages(
        cdo_transaction.entity_uid
    )
    request = [message for message in messages if message.content == question][0]
    response = [message for message in messages if message.in_reply_to == request.uid][0]
    print(f"The AI assistant said {response.content}")


if __name__ == "__main__":
    ask_ai_assistant_question_cmd()
