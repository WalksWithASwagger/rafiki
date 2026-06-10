"""CLI subcommand modules extracted from the generate.py dispatcher.

Each module holds one command group moved verbatim from generate.py.
generate.py imports handlers from here and keeps the dispatch table,
so `generate._cmd_*` stays importable for tests and other callers.
"""

from lib.commands.archive_cmds import (
    _cmd_approve,
    _cmd_archive_health,
    _cmd_archive_thumbnails,
    _cmd_clean,
    _parse_days,
)
from lib.commands.billing_cmds import _cmd_billing
from lib.commands.registry_cmds import _cmd_registry, _refresh_registry_after_mutation

__all__ = [
    "_cmd_approve",
    "_parse_days",
    "_cmd_archive_health",
    "_cmd_archive_thumbnails",
    "_cmd_billing",
    "_cmd_clean",
    "_cmd_registry",
    "_refresh_registry_after_mutation",
]
