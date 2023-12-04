from __future__ import annotations

import dataclasses

from .entity_type import EntityType


@dataclasses.dataclass
class ShouldUse:
    command: str
    if_types: tuple[EntityType, ...]
    src_commands: tuple[str, ...]


# listed in precedence order; matching uses `if_types`+`src_commands`
SHOULD_USE_MAPPINGS = (
    # update [gcp]
    ShouldUse(
        command="globus gcp update mapped",
        if_types=(EntityType.GCP_MAPPED,),
        src_commands=("globus collection update", "globus gcs collection update"),
    ),
    ShouldUse(
        command="globus gcp update guest",
        if_types=(EntityType.GCP_GUEST,),
        src_commands=("globus collection update", "globus gcs collection update"),
    ),
    # update [gcsv4 endpoints (host/share)]
    ShouldUse(
        command="globus endpoint update",
        if_types=EntityType.traditional_endpoints(),
        src_commands=("globus collection update", "globus gcs collection update"),
    ),
    # update [gcsv5 collections]
    ShouldUse(
        command="globus gcs collection update",
        src_commands=("globus endpoint update",),
        if_types=EntityType.gcsv5_collections(),
    ),
    # delete [gcsv4 endpoints (host/share)]
    ShouldUse(
        command="globus endpoint delete",
        src_commands=("globus collection delete", "globus gcs collection delete"),
        if_types=EntityType.traditional_endpoints(),
    ),
    # delete [gcsv5 collections]
    ShouldUse(
        command="globus gcs collection delete",
        src_commands=("globus endpoint delete",),
        if_types=EntityType.gcsv5_collections(),
    ),
    # show [gcsv4 endpoints (host/share) + gcp + gcsv5 endpoint]
    ShouldUse(
        command="globus endpoint show",
        src_commands=("globus collection show", "globus gcs collection show"),
        if_types=EntityType.non_gcsv5_collection_types(),
    ),
    # show [gcsv5 collections]
    ShouldUse(
        command="globus gcs collection show",
        src_commands=("globus endpoint show",),
        if_types=EntityType.gcsv5_collections(),
    ),
)


class WrongEntityTypeError(ValueError):
    def __init__(
        self,
        from_command: str,
        endpoint_id: str,
        actual_type: EntityType,
        expected_types: tuple[EntityType, ...],
    ) -> None:
        self.from_command = from_command
        self.endpoint_id = str(endpoint_id)
        self.actual_type = actual_type
        self.expected_types = expected_types
        self.expected_message = self._get_expected_message()
        self.actual_message = self._get_actual_message()
        super().__init__(f"{self.expected_message} {self.actual_message}")

    def _get_expected_message(self) -> str:
        expect_str = ", ".join(EntityType.nice_name(x) for x in self.expected_types)
        if len(self.expected_types) == 1:
            expect_str = f"a {expect_str}"
        else:
            expect_str = f"one of [{expect_str}]"
        return f"Expected {self.endpoint_id} to be {expect_str}."

    def _get_actual_message(self) -> str:
        actual_str = EntityType.nice_name(self.actual_type)
        return f"Instead, found it was of type '{actual_str}'."

    def should_use_command(self) -> str | None:
        for should_use_data in SHOULD_USE_MAPPINGS:
            if (
                self.from_command in should_use_data.src_commands
                and self.actual_type in should_use_data.if_types
            ):
                return should_use_data.command
        return None


class ExpectedCollectionError(WrongEntityTypeError):
    def _get_expected_message(self) -> str:
        return f"Expected {self.endpoint_id} to be a collection ID."


class ExpectedEndpointError(WrongEntityTypeError):
    def _get_expected_message(self) -> str:
        return f"Expected {self.endpoint_id} to be an endpoint ID."
