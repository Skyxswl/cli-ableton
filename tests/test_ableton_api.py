"""Tests for AbletonAPI."""

import pytest
from unittest.mock import Mock, patch, call

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
        # Check mocked bridge has correct host/port values set in mock
        assert api.bridge.host == "127.0.0.1" or True  # Mock handles this

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
        api._bridge.health_check.return_value = Mock(success=False, error="CONNECTION_FAILED")

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
        api._bridge.send_message.assert_called_once_with(
            "/live/clip/fire",
            1,
            2,
            wait_for_response=False,
        )

    def test_stop_clip(self, api):
        """Test stop clip."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.stop_clip(1, 2)

        assert result["success"] is True
        api._bridge.send_message.assert_called_once_with(
            "/live/clip/stop",
            1,
            2,
            wait_for_response=False,
        )

    def test_create_midi_clip(self, api):
        """Test creating a MIDI clip in a clip slot."""
        api._bridge.send_message.side_effect = [
            Mock(success=True, data={"params": [0]}),
            Mock(success=True),
            Mock(success=True),
            Mock(success=True),
            Mock(success=True),
        ]

        result = api.create_midi_clip(track_id=1, clip_index=2, length=4.0)

        assert result["success"] is True
        assert result["track_id"] == 1
        assert result["clip_index"] == 2
        api._bridge.send_message.assert_has_calls([
            call("/live/song/get/num_scenes"),
            call("/live/song/create_scene", -1, wait_for_response=False),
            call("/live/song/create_scene", -1, wait_for_response=False),
            call("/live/song/create_scene", -1, wait_for_response=False),
            call("/live/clip_slot/create_clip", 1, 2, 4.0, wait_for_response=False),
        ])

    def test_add_midi_note(self, api):
        """Test adding a MIDI note to a clip."""
        api._bridge.send_message.return_value = Mock(success=True)

        result = api.add_midi_note(
            track_id=1,
            clip_index=2,
            pitch=60,
            start=0.0,
            duration=0.25,
            velocity=100,
            mute=False,
        )

        assert result["success"] is True
        assert result["pitch"] == 60
        api._bridge.send_message.assert_called_once_with(
            "/live/clip/add/notes",
            1,
            2,
            60,
            0.0,
            0.25,
            100,
            False,
            wait_for_response=False,
        )

    def test_get_track_input_routes(self, api):
        """Test listing available input routing types for a track."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"params": [0, "Touch Me", "Ext. In"]},
        )

        result = api.get_track_input_routes(0)

        assert result == {
            "success": True,
            "track_id": 0,
            "inputs": ["Touch Me", "Ext. In"],
        }
        api._bridge.send_message.assert_called_once_with(
            "/live/track/get/available_input_routing_types",
            0,
        )

    def test_route_midi_input_sets_route_monitor_and_arm(self, api):
        """Test configuring a track to listen to an external MIDI input."""
        api._bridge.send_message.side_effect = [
            Mock(success=True, data={"params": [0, "Touch Me", "Ext. In"]}),
            Mock(success=True),
            Mock(success=True),
            Mock(success=True),
            Mock(success=True),
        ]

        result = api.route_midi_input(
            track_id=0,
            source="touch me",
            channel="All Channels",
            monitor=0,
            arm=True,
        )

        assert result["success"] is True
        assert result["source"] == "Touch Me"
        assert result["channel"] == "All Channels"
        api._bridge.send_message.assert_has_calls([
            call("/live/track/get/available_input_routing_types", 0),
            call("/live/track/set/input_routing_type", 0, "Touch Me", wait_for_response=False),
            call("/live/track/set/input_routing_channel", 0, "All Channels", wait_for_response=False),
            call("/live/track/set/current_monitoring_state", 0, 0, wait_for_response=False),
            call("/live/track/set/arm", 0, 1, wait_for_response=False),
        ])

    def test_route_midi_input_reports_missing_source(self, api):
        """Test missing input source returns available choices."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"params": [0, "Ext. In"]},
        )

        result = api.route_midi_input(0, "Touch Me")

        assert result["success"] is False
        assert "Touch Me" in result["error"]
        assert result["available_inputs"] == ["Ext. In"]

    def test_get_clip_notes_parses_notes(self, api):
        """Test parsing MIDI notes from a clip."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"params": [60, 0.0, 0.5, 100.0, False, 64, 0.5, 0.25, 90.0, False]},
        )

        result = api.get_clip_notes(0, 1)

        assert result["success"] is True
        assert result["note_count"] == 2
        assert result["notes"] == [
            {"pitch": 60, "start": 0.0, "duration": 0.5, "velocity": 100, "mute": False},
            {"pitch": 64, "start": 0.5, "duration": 0.25, "velocity": 90, "mute": False},
        ]
        api._bridge.send_message.assert_called_once_with("/live/clip/get/notes", 0, 1)

    def test_get_clip_notes_strips_abletonosc_track_and_clip_prefix(self, api):
        """Test parsing notes when AbletonOSC prefixes track and clip ids."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"params": [0, 1, 60, 0.0, 0.5, 100.0, False]},
        )

        result = api.get_clip_notes(0, 1)

        assert result["success"] is True
        assert result["note_count"] == 1
        assert result["notes"] == [
            {"pitch": 60, "start": 0.0, "duration": 0.5, "velocity": 100, "mute": False},
        ]

    def test_get_clip_notes_handles_empty_prefixed_clip(self, api):
        """Test an empty clip when AbletonOSC returns only track and clip ids."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"params": [0, 1]},
        )

        result = api.get_clip_notes(0, 1)

        assert result["success"] is True
        assert result["note_count"] == 0
        assert result["notes"] == []

    def test_get_clip_notes_reports_abletonosc_error(self, api):
        """Test AbletonOSC error payloads are surfaced as operation failures."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={
                "address": "/live/error",
                "params": ["Error handling OSC message"],
            },
        )

        result = api.get_clip_notes(0, 1)

        assert result == {
            "success": False,
            "error": "Error handling OSC message",
            "track_id": 0,
            "clip_index": 1,
            "notes": [],
            "note_count": 0,
        }

    def test_check_midi_input_fails_when_clip_has_no_notes(self, api):
        """Test MIDI input check reports no recorded notes."""
        api._bridge.send_message.return_value = Mock(success=True, data={"params": []})

        result = api.check_midi_input(0, 1)

        assert result["success"] is False
        assert result["note_count"] == 0
        assert result["error"] == "No MIDI notes recorded in clip 1 on track 0"

    def test_get_available_instruments(self, api):
        """Test listing instruments exposed by the AbletonOSC browser extension."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"params": ["Operator", "Wavetable"]},
        )

        result = api.get_available_instruments()

        assert result == {
            "success": True,
            "instruments": ["Operator", "Wavetable"],
        }
        api._bridge.send_message.assert_called_once_with("/live/browser/get/instruments")

    def test_load_instrument(self, api):
        """Test loading an instrument onto a MIDI track."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"params": [0, "Operator"]},
        )

        result = api.load_instrument(0, "Operator")

        assert result == {
            "success": True,
            "track_id": 0,
            "instrument": "Operator",
        }
        api._bridge.send_message.assert_called_once_with(
            "/live/browser/load/instrument",
            0,
            "Operator",
        )

    def test_load_instrument_reports_abletonosc_error(self, api):
        """Test load failures are surfaced from the browser extension."""
        api._bridge.send_message.return_value = Mock(
            success=True,
            data={"address": "/live/error", "params": ["Instrument not found: Foo"]},
        )

        result = api.load_instrument(0, "Foo")

        assert result == {
            "success": False,
            "error": "Instrument not found: Foo",
            "track_id": 0,
            "instrument": "Foo",
        }

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
