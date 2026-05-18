"""Tests for AbletonAPI."""

import pytest
from unittest.mock import Mock, patch

from cli_anything.ableton.ableton_api import AbletonAPI, Track, Clip, Device


class TestAbletonAPI:
    """Test AbletonAPI class."""

    @pytest.fixture
    def api(self):
        """Create API instance with mocked bridge."""
        with patch('cli_anything.ableton.ableton_api.AbletonOSCBridge') as mock_bridge:
            api = AbletonAPI(host="127.0.0.1", port=9001)
            api._bridge = Mock()
            return api

    def test_init(self, api):
        """Test API initialization."""
        assert api.bridge.host == "127.0.0.1"
        assert api.bridge.send_port == 9001

    def test_connect_success(self, api):
        """Test successful connection."""
        api._bridge.connect.return_value = Mock(success=True)
        api._connected = False

        result = api.connect()

        assert result.success is True
        assert api._connected is True

    def test_connect_failure(self, api):
        """Test failed connection."""
        api._bridge.connect.return_value = Mock(success=False, error="CONNECTION_FAILED")
        api._connected = False

        result = api.connect()

        assert result.success is False

    def test_health_check_connected(self, api):
        """Test health check when connected."""
        api._connected = True
        api._bridge.health_check.return_value = Mock(success=True, data={"status": "ok"})

        result = api.health_check()

        assert result.success is True

    def test_health_check_not_connected(self, api):
        """Test health check when not connected."""
        api._connected = False

        result = api.health_check()

        assert result.success is False
        assert result.error == "CONNECTION_FAILED"

    def test_get_tracks(self, api):
        """Test get tracks."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"tracks": [{"id": 1, "name": "Audio 1"}]}
        )

        result = api.get_tracks()

        assert result["success"] is True
        assert len(result["tracks"]) == 1

    def test_create_track_success(self, api):
        """Test create track success."""
        api._bridge.send_message.return_value = Mock(success=True, data={"track_id": 1})

        result = api.create_track("New Track", "audio")

        assert result["success"] is True
        assert result["track_name"] == "New Track"

    def test_create_track_invalid_type(self, api):
        """Test create track with invalid type."""
        result = api.create_track("Test", "invalid")

        assert result["success"] is False
        assert "Invalid track type" in result["error"]

    def test_delete_track(self, api):
        """Test delete track."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.delete_track(1)

        assert result["success"] is True
        assert result["track_id"] == 1

    def test_select_track(self, api):
        """Test select track."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.select_track(1)

        assert result["success"] is True

    def test_set_track_arm(self, api):
        """Test arm track."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.set_track_arm(1, True)

        assert result["success"] is True
        assert result["armed"] is True

    def test_set_track_mute(self, api):
        """Test mute track."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.set_track_mute(1, True)

        assert result["success"] is True
        assert result["muted"] is True

    def test_set_track_volume_invalid(self, api):
        """Test set volume with invalid value."""
        result = api.set_track_volume(1, 1.5)

        assert result["success"] is False
        assert "Volume must be between" in result["error"]

    def test_set_track_panning_invalid(self, api):
        """Test set panning with invalid value."""
        result = api.set_track_panning(1, 2.0)

        assert result["success"] is False
        assert "Panning must be between" in result["error"]

    def test_launch_clip(self, api):
        """Test launch clip."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.launch_clip(1, 2)

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["clip_index"] == 2

    def test_stop_clip(self, api):
        """Test stop clip."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.stop_clip(1, 2)

        assert result["success"] is True

    def test_launch_scene(self, api):
        """Test launch scene."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.launch_scene(0)

        assert result["success"] is True
        assert result["scene_index"] == 0

    def test_get_devices(self, api):
        """Test get devices."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"devices": [{"id": 1, "name": "Reverb"}]}
        )

        result = api.get_devices(1)

        assert result["success"] is True
        assert len(result["devices"]) == 1

    def test_get_device_param(self, api):
        """Test get device param."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"value": 0.5}
        )

        result = api.get_device_param(1, "Mix")

        assert result["success"] is True
        assert result["value"] == 0.5

    def test_set_device_param(self, api):
        """Test set device param."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.set_device_param(1, "Mix", 0.7)

        assert result["success"] is True
        assert result["value"] == 0.7

    def test_list_midi_effects(self, api):
        """Test list MIDI effects."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"midi_effects": [{"type": "arp", "enabled": True}]}
        )

        result = api.list_midi_effects(1)

        assert result["success"] is True
        assert len(result["midi_effects"]) == 1

    def test_set_midi_effect(self, api):
        """Test set MIDI effect."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.set_midi_effect(1, "arp", True, rate="1/8")

        assert result["success"] is True
        assert result["effect_type"] == "arp"

    def test_save_preset(self, api):
        """Test save preset."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.save_preset("My Preset", "sound_design")

        assert result["success"] is True
        assert result["preset_name"] == "My Preset"

    def test_load_preset(self, api):
        """Test load preset."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.load_preset("preset_123")

        assert result["success"] is True
        assert result["preset_id"] == "preset_123"

    def test_list_presets(self, api):
        """Test list presets."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"presets": [{"id": "1", "name": "Preset 1"}]}
        )

        result = api.list_presets()

        assert result["success"] is True
        assert len(result["presets"]) == 1

    def test_transport_play(self, api):
        """Test transport play."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.transport_play()

        assert result["success"] is True
        assert result["playing"] is True

    def test_transport_stop(self, api):
        """Test transport stop."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.transport_stop()

        assert result["success"] is True
        assert result["playing"] is False

    def test_transport_record(self, api):
        """Test transport record."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.transport_record(True)

        assert result["success"] is True
        assert result["recording"] is True


class TestImmutableDataclasses:
    """Test immutable data classes."""

    def test_track_immutable(self):
        """Test Track is immutable."""
        track = Track(id=1, name="Test")

        with pytest.raises(Exception):
            track.name = "Changed"

    def test_clip_immutable(self):
        """Test Clip is immutable."""
        clip = Clip(id="abc", name="Test", track_id=1, slot_index=0)

        with pytest.raises(Exception):
            clip.name = "Changed"

    def test_device_immutable(self):
        """Test Device is immutable."""
        device = Device(id=1, name="Reverb", type="audio")

        with pytest.raises(Exception):
            device.name = "Changed"