from functools import partial
from pathlib import Path
from re import match
from threading import Thread

from pitop.common.pt_os import get_pitopOS_info

from pt_miniscreen.components.info_page import InfoPage
from pt_miniscreen.core.components.marquee_text import MarqueeText

# creating apt_cache locks app even when done in a thread, do it at app import
# so it does not impact performance while user is interacting with the device.
try:
    from apt import Cache

    apt_cache = Cache()
except ModuleNotFoundError:
    apt_cache = None


def get_package_version(package_name: str) -> str:
    if apt_cache is None:
        return ""

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


class SoftwarePage(InfoPage):
    sdk = ""
    pitopd = ""
    repos = ""
    os = "OS Information"

    def __init__(self, **kwargs):
        Row = partial(MarqueeText, font_size=10, vertical_align="center")

        super().__init__(
            **kwargs,
            title=SoftwarePage.os,
            Rows=[
                partial(Row, text=SoftwarePage.repos or "Loading..."),
                partial(Row, text=SoftwarePage.sdk),
                partial(Row, text=SoftwarePage.pitopd),
            ],
        )

        def update_info():
            try:
                SoftwarePage.sdk = f"SDK: {get_package_version('python3-pitop')}"
                SoftwarePage.pitopd = f"pi-topd: {get_package_version('pi-topd')}"
                SoftwarePage.repos = f"Repos: {', '.join(get_apt_repositories())}"
                os_info = get_pitopOS_info()

                if os_info:
                    SoftwarePage.os = f"pi-topOS {os_info.build_os_version}-{os_info.build_run_number}"
                    self.title.state.update({"text": SoftwarePage.os})

                self.list.rows[0].state.update({"text": SoftwarePage.repos})
                self.list.rows[1].state.update({"text": SoftwarePage.sdk})
                self.list.rows[2].state.update({"text": SoftwarePage.pitopd})

            except Exception:
                pass

        Thread(target=update_info, daemon=True).start()
