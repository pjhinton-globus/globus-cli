import click
import pytest

from globus_cli.parsing.param_types.guest_activity_notify_param import (
    GCSGuestActivityNotificationParamType,
    TransferGuestActivityNotificationParamType,
)


@click.command()
@click.option(
    "--activity-notifications",
    type=TransferGuestActivityNotificationParamType(),
)
def activity_notifications_cmd(activity_notifications):
    if not activity_notifications:
        click.echo("activity_notifications=None")
        return
    click.echo(f"len(activity_notifications)={len(activity_notifications)}")
    for k in sorted(activity_notifications):
        click.echo(f"activity_notifications.{k}={activity_notifications[k]}")


def test_activity_notifications_no_opts(runner):
    result = runner.invoke(activity_notifications_cmd)
    assert result.exit_code == 0
    assert result.output == "activity_notifications=None\n"


def test_notify_opt_empty(runner):
    result = runner.invoke(activity_notifications_cmd, ["--activity-notifications", ""])
    assert result.exit_code == 0
    assert result.output == "activity_notifications=None\n"


@pytest.mark.parametrize("arg", ("all,failed",))
def test_notify_opt_mutually_exclusive(runner, arg):
    result = runner.invoke(
        activity_notifications_cmd, ["--activity-notifications", arg]
    )
    assert result.exit_code == 2
    assert (
        result.output
        == """\
Usage: activity-notifications-cmd [OPTIONS]
Try 'activity-notifications-cmd --help' for help.

Error: --activity-notifications cannot accept "all" with other values
"""
    )


def test_notify_opt_invalid(runner):

    arg = "foo,Bar,BAZ"

    result = runner.invoke(
        activity_notifications_cmd, ["--activity-notifications", arg]
    )
    assert result.exit_code == 2
    assert (
        result.output
        == """\
Usage: activity-notifications-cmd [OPTIONS]
Try 'activity-notifications-cmd --help' for help.

Error: --activity-notifications received these invalid values: \
['bar', 'baz', 'foo']
"""
    )


@pytest.mark.parametrize("arg", ("all", "All", "ALL"))
def test_notify_opt_all(runner, arg):
    result = runner.invoke(
        activity_notifications_cmd, ["--activity-notifications", arg]
    )
    assert result.exit_code == 0
    assert (
        result.output
        == """\
len(activity_notifications)=2
activity_notifications.status=['FAILED', 'SUCCEEDED']
activity_notifications.transfer_use=['destination', 'source']
"""
    )


@pytest.mark.parametrize("arg", ("failed", "Failed", "FAILED"))
def test_notify_opt_failed(runner, arg):
    result = runner.invoke(
        activity_notifications_cmd, ["--activity-notifications", arg]
    )
    assert result.exit_code == 0
    assert (
        result.output
        == """\
len(activity_notifications)=2
activity_notifications.status=['FAILED']
activity_notifications.transfer_use=['destination', 'source']
"""
    )


@pytest.mark.parametrize("arg", ("succeeded", "Succeeded", "SUCCEEDED"))
def test_notify_opt_succeeded(runner, arg):
    result = runner.invoke(
        activity_notifications_cmd, ["--activity-notifications", arg]
    )
    assert result.exit_code == 0
    assert (
        result.output
        == """\
len(activity_notifications)=2
activity_notifications.status=['SUCCEEDED']
activity_notifications.transfer_use=['destination', 'source']
"""
    )


@pytest.mark.parametrize("arg", ("destination", "Destination", "DESTINATION"))
def test_notify_opt_destination(runner, arg):
    result = runner.invoke(
        activity_notifications_cmd, ["--activity-notifications", arg]
    )
    assert result.exit_code == 0
    assert (
        result.output
        == """\
len(activity_notifications)=2
activity_notifications.status=['FAILED', 'SUCCEEDED']
activity_notifications.transfer_use=['destination']
"""
    )


@pytest.mark.parametrize("arg", ("source", "Source", "SOURCE"))
def test_notify_opt_source(runner, arg):
    result = runner.invoke(
        activity_notifications_cmd, ["--activity-notifications", arg]
    )
    assert result.exit_code == 0
    assert (
        result.output
        == """\
len(activity_notifications)=2
activity_notifications.status=['FAILED', 'SUCCEEDED']
activity_notifications.transfer_use=['source']
"""
    )


@pytest.mark.parametrize(
    "arg,expected",
    (
        ["source,succeeded", {"status": ["SUCCEEDED"], "transfer_use": ["source"]}],
        ["failed,destination", {"status": ["FAILED"], "transfer_use": ["destination"]}],
        [
            "failed,source,destination",
            {"status": ["FAILED"], "transfer_use": ["destination", "source"]},
        ],
        [
            "failed,source,succeeded",
            {"status": ["FAILED", "SUCCEEDED"], "transfer_use": ["source"]},
        ],
        [
            "destination,failed,source,succeeded",
            {
                "status": ["FAILED", "SUCCEEDED"],
                "transfer_use": ["destination", "source"],
            },
        ],
        [
            "destination, failed,source, succeeded",
            {
                "status": ["FAILED", "SUCCEEDED"],
                "transfer_use": ["destination", "source"],
            },
        ],
        [
            "source, destination",
            {
                "status": ["FAILED", "SUCCEEDED"],
                "transfer_use": ["destination", "source"],
            },
        ],
    ),
)
def test_notify_opt_mixed(runner, arg, expected):
    result = runner.invoke(
        activity_notifications_cmd, ["--activity-notifications", arg]
    )
    assert result.exit_code == 0
    assert (
        result.output
        == f"""\
len(activity_notifications)=2
activity_notifications.status={expected["status"]}
activity_notifications.transfer_use={expected["transfer_use"]}
"""
    )


@pytest.mark.parametrize(
    "incomplete_value, expected_completions",
    (
        ("", {"all", "destination", "failed", "source", "succeeded"}),
        ("a", {"all"}),
        ("al", {"all"}),
        ("all", {"all"}),
        ("dest", {"destination"}),
        ("destination", {"destination"}),
        ("s", {"source", "succeeded"}),
        ("so", {"source"}),
        ("su", {"succeeded"}),
        ("destination,succ", {"destination,succeeded"}),
        ("destination,succeeded", {"destination,succeeded"}),
        (
            "succeeded,",
            {"succeeded,destination", "succeeded,failed", "succeeded,source"},
        ),
        (
            ",,succeeded,",
            {"succeeded,destination", "succeeded,failed", "succeeded,source"},
        ),
        (",,succeeded,,f", {"succeeded,failed"}),
        (",", {"destination", "failed", "source", "succeeded"}),
        (
            "succeeded,failed,destination,source,",
            {"succeeded,failed,destination,source"},
        ),
        (",,,succeeded,,,,failed,source,", {"succeeded,failed,source,destination"}),
        ("succeeded,UNKNOWN", {"succeeded,UNKNOWN"}),
        (",,succeeded,UNKNOWN", {"succeeded,UNKNOWN"}),
    ),
)
def test_notify_shell_complete(runner, incomplete_value, expected_completions):
    param_type = GCSGuestActivityNotificationParamType()
    param = click.Option(["--activity-notifications"], type=param_type)
    completions = param_type.shell_complete(
        click.Context(activity_notifications_cmd), param, incomplete_value
    )
    got_values = {c.value for c in completions}
    assert got_values == expected_completions


def test_notify_metavar_in_help(runner):
    # running `--help` should show the custom metavar for `--notify`
    result = runner.invoke(activity_notifications_cmd, ["--help"])
    assert result.exit_code == 0
    assert "{all,succeeded,failed,source,destination}" in result.output
