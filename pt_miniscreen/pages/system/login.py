from getpass import getuser

from pitop.common.pt_os import is_pi_using_default_password

from ..network.network_page_base import NetworkPageData
from ..network.network_page_base import Page as PageBase
from ..network.network_page_base import RowDataText


class Page(PageBase):
    def __init__(self, size):
        row_data = NetworkPageData(
            first_row=RowDataText(
                icon_path="sys_info/networking/person.png",
                text=self.get_user,
            ),
            second_row=RowDataText(
                icon_path="sys_info/networking/padlock-small.png",
                text=self.get_password,
            ),
        )
        super().__init__(size=size, row_data=row_data, title="Login Details")

    def get_user(self):
        user = getuser()
        return "pi" if user == "root" else user

    def get_password(self):
        return "pi-top" if is_pi_using_default_password() is True else "********"
