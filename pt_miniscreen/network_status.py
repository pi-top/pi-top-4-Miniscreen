import logging

from pitop.common.command_runner import run_command

logger = logging.getLogger(__name__)

READ_STATE = "nmcli -t -f CONNECTIVITY general"
CHECK_NOW = "nmcli networking connectivity check"

_last = {"portal": False}


def get_connectivity(check_now: bool = False) -> str:
    """NetworkManager's connectivity: full, portal, limited, none or unknown.

    check_now asks for a new check instead of reading the last result:
    behind a portal NetworkManager backs off to one check every 5 minutes.
    """
    try:
        value = run_command(
            CHECK_NOW if check_now else READ_STATE, timeout=15, log_errors=False
        ).strip()
    except Exception as e:
        logger.debug(f"Couldn't read connectivity: {e}")
        value = ""
    return value or "unknown"


def needs_sign_in(check_now: bool = False) -> bool:
    _last["portal"] = get_connectivity(check_now) == "portal"
    return _last["portal"]


def is_behind_portal() -> bool:
    """The app's last result, for pages that redraw often."""
    return _last["portal"]
