import click

from globus_cli.constants import ExplicitNullType


class GCSGuestActivityNotificationParamType(click.ParamType):

    VALID_STATUSES = {
        "succeeded",
        "failed",
    }

    VALID_TRANSFER_USES = {
        "source",
        "destination",
    }

    VALID_NOTIFICATION_VALUES = VALID_TRANSFER_USES.copy()
    VALID_NOTIFICATION_VALUES |= VALID_STATUSES

    def get_metavar(self, param: click.Parameter) -> str:
        return "{all,succeeded,failed,source,destination}"

    def convert(
        self, value: str, param: click.Parameter | None, ctx: click.Context | None
    ) -> dict[str, list[str]] | ExplicitNullType:

        if value == "":
            return {
                "status": [],
                "transfer_use": [],
            }

        if value.lower() == "all":
            return {
                "status": sorted(self.VALID_STATUSES),
                "transfer_use": sorted(self.VALID_TRANSFER_USES),
            }

        policy: dict[str, list[str]] = {
            "status": [],
            "transfer_use": [],
        }

        # ignore white space, parse input sans case-sensitivity
        lowercase_vals: set[str] = {s.strip().lower() for s in value.split(",")}

        if "all" in lowercase_vals:
            raise click.UsageError(
                '--activity-notifications cannot accept "all" with other values'
            )

        val: str
        if lowercase_vals <= self.VALID_NOTIFICATION_VALUES:
            for val in lowercase_vals:
                if val in self.VALID_TRANSFER_USES:
                    policy["transfer_use"].append(val)
                else:
                    policy["status"].append(val)
        else:
            invalid_values = sorted(lowercase_vals - self.VALID_NOTIFICATION_VALUES)
            raise click.UsageError(
                "--activity-notifications received these invalid values: "
                f"{invalid_values}"
            )

        # Fill in implied values.
        k: str
        v: list[str]
        for k, v in policy.items():
            if k == "transfer_use" and not v:
                v = list(self.VALID_TRANSFER_USES)
            elif k == "status" and not v:
                v = list(self.VALID_STATUSES)
            # Ensure deterministic ordering for testability.
            policy[k] = sorted(v)

        return policy


class TransferGuestActivityNotificationParamType(GCSGuestActivityNotificationParamType):

    def convert(
        self, value: str, param: click.Parameter | None, ctx: click.Context | None
    ) -> dict[str, list[str]] | ExplicitNullType:

        policy: dict[str, list[str]] | ExplicitNullType = super().convert(
            value, param, ctx
        )

        if isinstance(policy, dict):
            if not (policy["status"] and policy["transfer_use"]):
                return ExplicitNullType()
            policy["status"] = [x.upper() for x in policy["status"]]

        return policy
