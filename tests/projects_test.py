from functools import partial
from os import path
from time import sleep

import pytest

config_file_path = f"{path.dirname(path.realpath(__file__))}/projects/"


@pytest.fixture
def internal_ip(mocker):
    return lambda page, interface, ip: mocker.patch(
        f"pt_miniscreen.pages.network.{page}.get_internal_ip",
        lambda iface: ip if interface == iface else "No IP address",
    )


@pytest.fixture
def go_to_projects_page(miniscreen):
    def go():
        # enter projects menu
        miniscreen.down_button.release()
        sleep(1)
        miniscreen.down_button.release()
        sleep(1)
        miniscreen.down_button.release()
        sleep(1)
        miniscreen.select_button.release()
        sleep(1)

    return go


@pytest.fixture
def create_project(mocker):
    def create_project_rows(project_number):
        from pt_miniscreen.pages.root.projects import ProjectConfig, ProjectRow

        pages = []
        for project in range(project_number):
            config = ProjectConfig(
                title=f"Project #{project + 1}", start="", image="", exit_condition=""
            )
            pages.append(partial(ProjectRow, config))
        return pages

    def mock_project_rows(projects_to_create):
        mocker.patch(
            "pt_miniscreen.pages.root.projects.ProjectList.load_project_rows",
            side_effect=lambda: create_project_rows(projects_to_create),
        )

    return mock_project_rows


def test_no_projects_available(miniscreen, go_to_projects_page, snapshot, mocker):
    go_to_projects_page()
    snapshot.assert_match(miniscreen.device.display_image, "no-projects.png")


def test_selecting_no_projects_message_does_nothing(
    miniscreen, go_to_projects_page, snapshot, mocker
):
    go_to_projects_page()
    snapshot.assert_match(miniscreen.device.display_image, "no-projects.png")
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "no-projects.png")


def test_open_project_page(miniscreen, go_to_projects_page, snapshot, create_project):
    create_project(1)
    go_to_projects_page()
    snapshot.assert_match(miniscreen.device.display_image, "1-project-row.png")

    # access project page
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "project-page.png")


def test_first_item_is_selected_by_default(
    miniscreen, go_to_projects_page, snapshot, create_project
):
    create_project(3)
    go_to_projects_page()
    snapshot.assert_match(
        miniscreen.device.display_image, "first-project-is-selected.png"
    )


def test_load_project_config_from_valid_file():
    from pt_miniscreen.pages.root.projects import ProjectConfig

    config = ProjectConfig.from_file(f"{config_file_path}/valid/valid_project.cfg")
    assert config.title == "my project"
    assert config.start == "python3 project.py"
    assert config.exit_condition == "?"


def test_load_project_config_raises_on_invalid_file():
    from pt_miniscreen.pages.root.projects import InvalidConfigFile, ProjectConfig

    with pytest.raises(InvalidConfigFile):
        ProjectConfig.from_file(f"{config_file_path}/invalid/invalid_project.cfg")


def test_project_list_loads_projects_from_directories(mocker, create_component):
    mocker.patch(
        "pt_miniscreen.pages.root.projects.ProjectList.PROJECT_DIRECTORIES",
        [f"{config_file_path}"],
    )
    from pt_miniscreen.pages.root.projects import ProjectList

    project_list = create_component(ProjectList)
    assert len(project_list.rows) == 1
    selected_row = project_list.selected_row
    assert selected_row.page is not None


def test_project_list_doesnt_add_project_page_when_projects_not_found(
    mocker, create_component
):
    from pt_miniscreen.pages.root.projects import ProjectList

    project_list = create_component(ProjectList)
    assert len(project_list.rows) == 1
    selected_row = project_list.selected_row
    assert selected_row.page is None
