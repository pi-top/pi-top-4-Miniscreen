import logging
from functools import partial
from os import environ
from pathlib import Path
from re import match, search
from shlex import split
from subprocess import run
from threading import Thread

from pitop.common.pt_os import get_pitopOS_info

from pt_miniscreen.components.info_page import InfoPage
from pt_miniscreen.core.components.marquee_text import MarqueeText

logger = logging.getLogger(__name__)


def get_package_version(pkg_name):
    def __get_env():
        env = environ.copy()
        # Print output of commands in english
        env["LANG"] = "en_US.UTF-8"
        return env

    try:
        resp = run(
            split(f"apt-cache policy {pkg_name}"),
            check=False,
            capture_output=True,
            timeout=5,
            env=__get_env(),
        )
        output = str(resp.stdout, "utf8")
        match = search("Installed: (.*)", output)
        return match.group(1) if match else ""

    except Exception as e:
        logger.warning(f"get_package_version {pkg_name} failed: {e}")
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
