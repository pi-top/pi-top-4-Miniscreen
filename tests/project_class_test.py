from functools import partial
from time import sleep
from unittest.mock import Mock, patch

import pytest
from testpath import MockCommand


@pytest.fixture
def create_project_object():
    from pt_miniscreen.pages.root.projects import ProjectConfig, Project

    config = ProjectConfig(
        file="/tmp/config.cfg",
        title="Project #0",
        start="my-custom-start-command",
        image="",
        exit_condition="POWER_BUTTON_FLICKER",
    )
    return partial(Project, config)


def test_project_cls_instance(create_project_object):
    from pt_miniscreen.pages.root.projects import ProjectConfig

    project = create_project_object()
    assert isinstance(project.config, ProjectConfig)


def test_project_cls_run_method(create_project_object):
    project = create_project_object()

    with MockCommand("my-custom-start-command") as start_command:
        project.run()
        sleep(1)

    assert len(start_command.get_calls()) == 1

    project.stop()
    assert project.process is None


def test_project_cls_as_context_manager(create_project_object):
    with create_project_object() as project:
        with MockCommand("my-custom-start-command") as start_command:
            project.run()
            sleep(1)

    assert len(start_command.get_calls()) == 1

    assert project.process is None
    assert project.subscribe_client is None


@patch("pt_miniscreen.pages.root.projects.PTDMSubscribeClient")
def test_project_cls_subscribes_to_exit_condition_events(
    subscribe_client, create_project_object
):
    project = create_project_object()
    with MockCommand("my-custom-start-command"):
        project.run()
        sleep(1)

    project.subscribe_client.initialise.assert_called_once()


@patch("pt_miniscreen.pages.root.projects.PTDMSubscribeClient")
def test_project_cls_callback_for_exit_condition_flicker(
    subscribe_client, create_project_object
):
    project = create_project_object()
    with MockCommand("my-custom-start-command"):
        project.run()
        sleep(1)

    initialise_args = project.subscribe_client.initialise.call_args_list[0]
    callbacks = list(initialise_args.args[0].values())
    assert len(callbacks) == 1
    assert callbacks[0] == project.stop


@patch("pt_miniscreen.pages.root.projects.PTDMSubscribeClient")
def test_project_cls_callbacks_for_exit_condition_hold_x(
    subscribe_client, create_project_object, mocker
):
    project = create_project_object()
    project.config.exit_condition = "HOLD_X"

    with MockCommand("my-custom-start-command"):
        project.run()
        sleep(1)

    initialise_args = project.subscribe_client.initialise.call_args_list[0]
    callbacks = list(initialise_args.args[0].values())
    assert len(callbacks) == 2
    on_cancel_button_press = callbacks[0]
    on_cancel_button_release = callbacks[1]

    project.stop = Mock()

    on_cancel_button_press()
    assert project.stop.call_count == 0
    sleep(3)
    on_cancel_button_release()
    assert project.stop.call_count == 1


@patch("pt_miniscreen.pages.root.projects.PTDMSubscribeClient")
def test_project_cls_no_ptdm_subscribe_on_invalid_exit_condition(
    subscribe_client, create_project_object, mocker
):
    project = create_project_object()
    project.config.exit_condition = "INVALID_EXIT_CONDITION"

    with MockCommand("my-custom-start-command"):
        project.run()
        sleep(1)

    assert subscribe_client.call_count == 0
