from pathlib import Path
from re import match

from pitop.common.pt_os import get_pitopOS_info

from ..network.network_page_base import NetworkPageData
from ..network.network_page_base import Page as PageBase
from ..network.network_page_base import RowDataText


def get_package_version(package_name: str) -> str:
    try:
        from apt import Cache
    except ModuleNotFoundError:
        return ""
    apt_cache = Cache()
    package = apt_cache.get(package_name)
    if (
        package
        and hasattr(package, "installed")
        and hasattr(package.installed, "version")
    ):
        return package.installed.version
    return ""


def get_apt_repositories():
    def find_repo_in_file(file):
        for line in file:
            match_obj = match(
                r"^(.*)pi-top[.]com\/(?P<repository>[a-z-]*)\/debian(.*)$", line
            )
            if match_obj and match_obj.group("repository"):
                return match_obj.group("repository")

    repos = []
    sources_dir = Path("/etc/apt/sources.list.d")

    if not sources_dir.is_dir():
        return repos

    for filename in sources_dir.iterdir():
        with open(filename) as file:
            repo = find_repo_in_file(file)
            if repo:
                repos.append(repo)
    return repos


class SoftwarePageInfo:
    def __init__(self):
        self._info = get_pitopOS_info()
        self.os = ""
        if self._info:
            self.os = (
                f"pi-topOS {self._info.build_os_version}-{self._info.build_run_number}"
            )
        self.sdk_version = f"SDK {get_package_version('python3-pitop')}"
        self.pitopd_version = f"pi-topd {get_package_version('pi-topd')}"
        self.repos = f"Repos: {', '.join(get_apt_repositories())}"


class Page(PageBase):
    def __init__(self, size):
        info = SoftwarePageInfo()
        row_data = NetworkPageData(
            first_row=RowDataText(text=lambda: info.repos),
            second_row=RowDataText(text=lambda: info.sdk_version),
            third_row=RowDataText(text=lambda: info.pitopd_version),
        )
        title = info.os if len(info.os) > 0 else "OS Information"
        super().__init__(size=size, row_data=row_data, title=title)
