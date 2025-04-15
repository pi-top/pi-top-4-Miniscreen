import pytest
import uuid
from pathlib import Path
from pt_miniscreen.state import StateManager


@pytest.fixture
def state_manager():
    # Generate a random name for the state file to avoid conflicts with concurrent tests
    name = f"test_package_{uuid.uuid4()}"
    # Use testing=True to use /tmp directory
    manager = StateManager(name, testing=True)
    yield manager

    # Cleanup after tests
    state_file = Path(f"/tmp/{name}/state.cfg")
    if state_file.exists():
        state_file.unlink()
    if state_file.parent.exists():
        state_file.parent.rmdir()


def test_singleton_pattern():
    manager1 = StateManager("test_package", testing=True)
    manager2 = StateManager("test_package", testing=True)
    assert manager1 is manager2


def test_state_file_creation(state_manager):
    state_file = Path("/tmp/test_package/state.cfg")
    assert state_file.exists()


def test_set_and_get(state_manager):
    state_manager.set("test_section", "test_key", "test_value")
    assert state_manager.get("test_section", "test_key") == "test_value"


def test_get_with_fallback(state_manager):
    fallback_value = "default"
    value = state_manager.get("nonexistent", "nonexistent", fallback_value)
    assert value == fallback_value


def test_get_nonexistent_raises(state_manager):
    with pytest.raises(Exception):
        state_manager.get("nonexistent", "nonexistent")


def test_remove_key(state_manager):
    state_manager.set("test_section", "test_key", "test_value")
    state_manager.remove("test_section", "test_key")

    with pytest.raises(Exception):
        state_manager.get("test_section", "test_key")


def test_remove_section(state_manager):
    state_manager.set("test_section", "test_key", "test_value")
    state_manager.remove("test_section")

    with pytest.raises(Exception):
        state_manager.get("test_section", "test_key")


def test_exists():
    # Test non-existent state
    assert not StateManager.exists("nonexistent_package", testing=True)

    # Create state and test again
    StateManager("test_package", testing=True)
    assert StateManager.exists("test_package", testing=True)


def test_persistence(state_manager):
    # Set a value
    state_manager.set("test_section", "test_key", "test_value")

    # Create a new instance (should load existing state)
    new_manager = StateManager("test_package", testing=True)
    assert new_manager.get("test_section", "test_key") == "test_value"


def test_set_creates_section(state_manager):
    # Test that set() creates a new section if it doesn't exist
    state_manager.set("new_section", "key", "value")
    assert state_manager.get("new_section", "key") == "value"


def test_set_raises_on_invalid_input(state_manager):
    # Test that set() raises an exception with invalid input
    with pytest.raises(Exception):
        state_manager.set(None, "key", "value")


def test_remove_nonexistent(state_manager):
    # Test removing non-existent section and key
    # Should not raise exceptions
    state_manager.remove("nonexistent_section")
    state_manager.remove("nonexistent_section", "nonexistent_key")


def test_multiple_values_in_section(state_manager):
    # Test handling multiple key-value pairs in the same section
    state_manager.set("test_section", "key1", "value1")
    state_manager.set("test_section", "key2", "value2")
    assert state_manager.get("test_section", "key1") == "value1"
    assert state_manager.get("test_section", "key2") == "value2"
