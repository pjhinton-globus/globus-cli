import uuid

from globus_cli.parsing import command
from globus_cli.services.search import get_search_client
from globus_cli.termio import FORMAT_TEXT_RECORD, formatted_print

from .._common import task_id_arg


def _format_state(x: dict):
    state = x["state"]
    desc = x["state_description"]
    return f"{state} ({desc})"


TASK_FIELDS = [
    ("State", _format_state),
    ("Index ID", "index_id"),
    ("Message", "message"),
    ("Creation Date", "creation_date"),
    ("Completion Date", "completion_date"),
]


@command("show")
@task_id_arg
def show_command(task_id: uuid.UUID):
    """Display a Task"""
    search_client = get_search_client()
    formatted_print(
        search_client.get_task(task_id),
        fields=TASK_FIELDS,
        text_format=FORMAT_TEXT_RECORD,
    )
