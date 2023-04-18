from shutil import rmtree
from os import path, makedirs
from shutil import copytree
from time import sleep

import pytest
from testpath import MockCommand


config_file_path = f"{path.dirname(path.realpath(__file__))}/projects/"


@pytest.fixture(scope="function")
def use_example_project(mocker, tmp_path):
    def _create_project(
        projects_to_create=1,
        base_directory="",
        project_info_to_mock="MyProjectsDirectory",
    ):
        mocker.patch(
            "pt_miniscreen.pages.root.projects.overview.directory_contains_projects",
            return_value=True,
        )
        mocker.patch(
            "pt_miniscreen.pages.root.projects.project.switch_user",
            return_value=None,
        )

        tmp_path.mkdir(exist_ok=True)
        for i in range(projects_to_create):
            full_path = f"{tmp_path}/{base_directory}/project_{i + 1}"
            makedirs(full_path)
            copytree(f"{config_file_path}/valid", full_path, dirs_exist_ok=True)

        mocker.patch(
            f"pt_miniscreen.pages.root.projects.utils.{project_info_to_mock}.folder",
            tmp_path,
        )

    yield _create_project
    rmtree(tmp_path, ignore_errors=True)


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
        sleep(2)

    return go


@pytest.fixture
def create_project(mocker, tmp_path):
    def _create_project(projects_to_create=1, exit_condition=""):
        mocker.patch(
            "pt_miniscreen.pages.root.projects.overview.directory_contains_projects",
            return_value=True,
        )
        mocker.patch(
            "pt_miniscreen.pages.root.projects.project.switch_user",
            return_value=None,
        )

        tmp_path.mkdir(exist_ok=True)
        for i in range(projects_to_create):
            file_content = f"""
            [project]
            title=Project #{i + 1}
            start=my-custom-start-command
            exit_condition={exit_condition}
            """

            makedirs(f"{tmp_path}/my_project_{i + 1}")
            with open(f"{tmp_path}/my_project_{i + 1}/project.cfg", "w") as f:
                f.write(file_content)

        from pt_miniscreen.pages.root.projects.utils import MyProjectsDirectory

        mocker.patch.object(
            MyProjectsDirectory,
            "folder",
            f"{tmp_path}",
        )

    yield _create_project
    rmtree(tmp_path)


def test_no_user_projects_available(miniscreen, go_to_projects_page, snapshot, mocker):
    go_to_projects_page()
    snapshot.assert_match(miniscreen.device.display_image, "only-package-projects.png")


def test_open_projects_menu(miniscreen, go_to_projects_page, snapshot, create_project):
    create_project()
    go_to_projects_page()
    snapshot.assert_match(
        miniscreen.device.display_image, "projects-page-subsections.png"
    )


def test_projects_on_nested_directories_display_directories_on_enter(
    miniscreen, go_to_projects_page, snapshot, use_example_project
):
    use_example_project(
        base_directory="further_username", project_info_to_mock="FurtherDirectory"
    )
    go_to_projects_page()

    # Further entry is displayed
    snapshot.assert_match(miniscreen.device.display_image, "folders-overview.png")

    # Access 'Further' menu; projects and 'delete all' entry are visible
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "nested-project-view.png")

    # Select user from list; project list is visible
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "project-list.png")

    # Go back to Further, select 'delete all'
    miniscreen.cancel_button.release()
    sleep(1)
    miniscreen.up_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "delete-all-selected.png")

    # Access 'delete all' displays a confirmation dialog
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "confirmation-dialog.png")

    # Can go back by pressing the cancel button
    miniscreen.cancel_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "delete-all-selected.png")

    # Go back to 'delete all' dialog; on confirmation, goes back one level
    miniscreen.select_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "folders-overview.png")

    # Select Further; no projects are available
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "no-projects.png")


def test_overview_page_actions(
    miniscreen, go_to_projects_page, snapshot, use_example_project
):
    use_example_project(projects_to_create=2)
    go_to_projects_page()

    # access user projects
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "projects-list.png")

    # access project overview page; 'delete' entry is visible
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")

    # check logs; should be empty
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "logs-empty.png")

    # run project
    miniscreen.cancel_button.release()
    sleep(1)
    miniscreen.up_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(
        miniscreen.device.display_image, "starting-project-message.png"
    )

    # wait for project to finish, goes back to overview page
    sleep(5)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")

    # 'view logs' should now display the project logs
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "logs-first-page.png")

    # go to delete project confirmation page
    miniscreen.cancel_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "confirmation-page.png")

    # pressing cancel goes back to overview
    miniscreen.cancel_button.release()
    sleep(1)
    snapshot.assert_match(
        miniscreen.device.display_image,
        "project-overview-delete-selected.png",
    )

    # pressing 'no' goes back to overview
    miniscreen.select_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    snapshot.assert_match(
        miniscreen.device.display_image, "confirmation-page-no-selected.png"
    )
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(
        miniscreen.device.display_image,
        "project-overview-delete-selected.png",
    )

    # pressing 'yes' goes back to projects list
    miniscreen.select_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(2)
    snapshot.assert_match(
        miniscreen.device.display_image, "projects-list-after-deleting.png"
    )

    # Delete project again - should display an 'no projects' message
    miniscreen.select_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "no-projects-available.png")


def test_log_pages_reflect_last_run(
    miniscreen, go_to_projects_page, snapshot, use_example_project
):
    use_example_project(projects_to_create=2)
    go_to_projects_page()

    # access user projects
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "projects-list.png")

    # access project overview page
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")

    # check logs; should be empty
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "logs-empty.png")

    # run project
    miniscreen.cancel_button.release()
    sleep(1)
    miniscreen.up_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(
        miniscreen.device.display_image, "starting-project-message.png"
    )

    # wait for project to finish, goes back to overview page
    sleep(5)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")

    # 'view logs' should now display the project logs
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "logs-first-view.png")

    # run project again
    miniscreen.cancel_button.release()
    sleep(1)
    miniscreen.up_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(
        miniscreen.device.display_image, "starting-project-message.png"
    )

    # wait for project to finish, goes back to overview page
    sleep(5)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")

    # 'view logs' should now display the project logs
    miniscreen.down_button.release()
    sleep(1)
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "updated-logs.png")


def test_running_project_that_uses_miniscreen(
    miniscreen, go_to_projects_page, snapshot, create_project, mocker
):
    create_project()
    go_to_projects_page()

    # access user projects
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "1-project-row.png")
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")

    with MockCommand(
        "my-custom-start-command", python="from time import sleep; sleep(3)"
    ) as start_command:
        # Access project page
        miniscreen.select_button.release()
        sleep(2)
        snapshot.assert_match(
            miniscreen.device.display_image, "starting-project-message.png"
        )

        # Run project
        sleep(2)
        snapshot.assert_match(
            miniscreen.device.display_image, "running-project-message.png"
        )

        # Emulate user using the miniscreen
        miniscreen.when_user_controlled()
        sleep(0.5)

        # Screen doesn't display a message
        snapshot.assert_match(miniscreen.device.display_image, "no-message.png")

        # Wait for the project process to finish and display 'stopping' message
        sleep(3)
        snapshot.assert_match(
            miniscreen.device.display_image, "stopping-project-message.png"
        )

    assert len(start_command.get_calls()) == 1


def test_returns_to_project_list_when_project_process_finishes(
    miniscreen, go_to_projects_page, snapshot, create_project
):
    create_project()
    go_to_projects_page()

    # access user projects
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "1-project-row.png")
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")

    with MockCommand("my-custom-start-command"):
        # access project page
        miniscreen.select_button.release()
        sleep(2)
        # display 'starting' message for a few seconds before starting project
        snapshot.assert_match(
            miniscreen.device.display_image, "starting-project-message.png"
        )
        # wait for the project process to finish and display 'stopping' message
        sleep(3)
        snapshot.assert_match(
            miniscreen.device.display_image, "stopping-project-message.png"
        )

    sleep(3)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")


def test_displays_error_message_and_returns_to_project_list_on_error(
    miniscreen, go_to_projects_page, snapshot, create_project
):
    create_project()
    go_to_projects_page()

    # access user projects
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "1-project-row.png")
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")

    # don't mock 'my-custom-start-command' and access project page
    miniscreen.select_button.release()
    sleep(2)
    snapshot.assert_match(
        miniscreen.device.display_image, "starting-project-message.png"
    )

    # project fails to start
    sleep(3)
    snapshot.assert_match(miniscreen.device.display_image, "error-project-message.png")

    # app goes back to project overview page
    sleep(3)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")


def test_displays_error_message_and_returns_to_project_list_on_nonzero_exit_code(
    miniscreen, go_to_projects_page, snapshot, create_project
):
    create_project()
    go_to_projects_page()

    # access user projects
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "1-project-row.png")
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")

    # use exit code 2 to mock an error
    with MockCommand.fixed_output("my-custom-start-command", exit_status=2):
        miniscreen.select_button.release()
        sleep(2)
        snapshot.assert_match(
            miniscreen.device.display_image, "starting-project-message.png"
        )

        # since exit code isn't 0, it's reported as an error
        sleep(3)
        snapshot.assert_match(
            miniscreen.device.display_image, "error-project-message.png"
        )

    # app goes back to project page
    sleep(3)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")


def test_display_stop_instructions_for_power_button_press_on_project_start(
    miniscreen, go_to_projects_page, snapshot, create_project
):
    create_project(exit_condition="FLICK_POWER")
    go_to_projects_page()

    # access user projects
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "1-project-row.png")
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")

    with MockCommand("my-custom-start-command"):
        miniscreen.select_button.release()
        sleep(2)
        snapshot.assert_match(
            miniscreen.device.display_image,
            "starting-project-message-with-instructions.png",
        )


def test_display_stop_instructions_for_hold_x_on_project_start(
    miniscreen, go_to_projects_page, snapshot, create_project
):
    create_project(exit_condition="HOLD_CANCEL")
    go_to_projects_page()

    # access user projects
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "1-project-row.png")
    miniscreen.select_button.release()
    sleep(1)
    snapshot.assert_match(miniscreen.device.display_image, "project-overview.png")

    with MockCommand("my-custom-start-command"):
        miniscreen.select_button.release()
        sleep(2)
        snapshot.assert_match(
            miniscreen.device.display_image,
            "starting-project-message-with-instructions.png",
        )


def test_load_project_config_from_valid_file():
    from pt_miniscreen.pages.root.projects.config import ProjectConfig

    config = ProjectConfig.from_file(f"{config_file_path}/valid/project.cfg")
    assert config.title == "my project"
    assert config.start == "python3 project.py"
    # If file doesn't specify an exit condition, use FLICK_POWER
    assert config.exit_condition == "FLICK_POWER"


def test_load_project_config_raises_on_invalid_file():
    from pt_miniscreen.pages.root.projects.utils import InvalidConfigFile
    from pt_miniscreen.pages.root.projects.config import ProjectConfig

    with pytest.raises(InvalidConfigFile):
        ProjectConfig.from_file(f"{config_file_path}/invalid/project.cfg")
