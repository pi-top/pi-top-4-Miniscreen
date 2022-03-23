from functools import partial
from getpass import getuser

from pitop.common.pt_os import is_pi_using_default_password

from pt_miniscreen.hotspots.icon_text_row import IconTextRow, Row
from pt_miniscreen.hotspots.info_page import InfoPage
from pt_miniscreen.utils import get_image_file_path


def get_user():
    user = getuser()
    return "pi" if user == "root" else user


def get_password():
    return "pi-top" if is_pi_using_default_password() is True else "********"


class LoginDetailsPage(InfoPage):
    def __init__(self, **kwargs):
        super().__init__(
            **kwargs,
            title="Login Details",
            Rows=[
                partial(
                    IconTextRow,
                    get_text=get_user,
                    icon_path=get_image_file_path(
                        "sys_info/networking/person-small.png"
                    ),
                ),
                partial(
                    IconTextRow,
                    get_text=get_password,
                    icon_path=get_image_file_path(
                        "sys_info/networking/padlock-small.png"
                    ),
                ),
                Row,
            ]
        )
