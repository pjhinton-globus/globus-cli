import click

from globus_cli.parsing.command_state import CommandState


def outformat_is_json():
    """
    Only safe to call within a click context.
    """
    ctx = click.get_current_context()
    state = ctx.ensure_object(CommandState)
    return state.outformat_is_json()


def outformat_is_text():
    """
    Only safe to call within a click context.
    """
    ctx = click.get_current_context()
    state = ctx.ensure_object(CommandState)
    return state.outformat_is_text()