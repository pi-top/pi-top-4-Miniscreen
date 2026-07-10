from functools import partial
from getpass import getuser
import os

from pitop.common.pt_os import is_pi_using_default_password

from pt_miniscreen.components.icon_text_row import IconTextRow, Row
from pt_miniscreen.components.info_page import InfoPage
from pt_miniscreen.utils import get_image_file_path


def get_user():
    # Check for override env var first
    override_user = os.environ.get("PT_MINISCREEN_USER")
    if override_user:
        return override_user

    user = getuser()
    return "pi" if user == "root" else user


def get_password():
    # Check for override env var first
    override_pass = os.environ.get("PT_MINISCREEN_PASS")
    if override_pass:
        return override_pass

    return "pi-top" if is_pi_using_default_password() is True else "********"


class LoginDetailsPage(InfoPage):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            title="Login Details",
            Rows=[
                partial(
                    IconTextRow,
                    text=get_user(),
                    get_text=get_user,
                    icon_path=get_image_file_path(
                        "sys_info/networking/person-small.png"
                    ),
                ),
                partial(
                    IconTextRow,
                    text=get_password(),
                    get_text=get_password,
                    text_vertical_align="bottom",
                    icon_path=get_image_file_path(
                        "sys_info/networking/padlock-small.png"
                    ),
                ),
                Row,
            ]
        )
