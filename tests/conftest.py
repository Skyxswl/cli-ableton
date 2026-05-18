"""Pytest configuration and fixtures."""

import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_bridge():
    """Create mock OSC bridge."""
    bridge = Mock()
    bridge.connect.return_value = Mock(success=True)
    bridge.disconnect.return_value = None
    bridge.health_check.return_value = Mock(success=True, data={"status": "ok"})
    bridge.send_message.return_value = Mock(success=True, data={})
    return bridge


@pytest.fixture
def mock_api(mock_bridge):
    """Create mock AbletonAPI with mocked bridge."""
    with patch('cli_anything.ableton.ableton_api.AbletonOSCBridge') as MockBridge:
        from cli_anything.ableton.ableton_api import AbletonAPI
        api = AbletonAPI()
        api._bridge = mock_bridge
        api._connected = True
        return api


@pytest.fixture
def sample_tracks():
    """Sample track data for testing."""
    return [
        {"id": 1, "name": "Audio 1", "type": "audio", "armed": False, "muted": False},
        {"id": 2, "name": "MIDI 1", "type": "midi", "armed": True, "muted": False},
        {"id": 3, "name": "Return 1", "type": "return", "armed": False, "muted": True},
    ]


@pytest.fixture
def sample_devices():
    """Sample device data for testing."""
    return [
        {"id": 1, "name": "Reverb", "type": "audio"},
        {"id": 2, "name": "Delay", "type": "audio"},
        {"id": 3, "name": "Chorus", "type": "midi"},
    ]


@pytest.fixture
def sample_midi_effects():
    """Sample MIDI effect data for testing."""
    return [
        {"type": "arp", "enabled": True, "parameters": {"rate": "1/8"}},
        {"type": "chord", "enabled": True, "parameters": {"chord": "maj"}},
        {"type": "scale", "enabled": False, "parameters": {"scale": "minor"}},
    ]


@pytest.fixture
def sample_presets():
    """Sample preset data for testing."""
    return [
        {"id": "1", "name": "Ambient Pad", "category": "sound_design"},
        {"id": "2", "name": "Fat Bass", "category": "synthesis"},
        {"id": "3", "name": "Clean Guitar", "category": "mixing"},
    ]


@pytest.fixture
def sample_clip_data():
    """Sample clip data for testing."""
    return {
        "id": "clip_abc123",
        "name": "Section A",
        "track_id": 1,
        "slot_index": 0,
        "playing": True,
        "length": 4.0,
    }