"""Tests for ClipControl."""

import pytest
from unittest.mock import Mock

from cli_anything.ableton.clip_control import ClipControl
from cli_anything.ableton.ableton_api import AbletonAPI


class TestClipControl:
    """Test ClipControl class."""

    @pytest.fixture
    def api(self):
        """Create mock API."""
        return Mock(spec=AbletonAPI)

    @pytest.fixture
    def ctrl(self, api):
        """Create ClipControl instance."""
        return ClipControl(api)

    def test_launch_clip(self, ctrl, api):
        """Test launch clip."""
        api.launch_clip.return_value = {"success": True, "track_id": 1, "clip_index": 2}

        result = ctrl.launch(track_id=1, clip_index=2)

        assert result["success"] is True
        assert result["clip_index"] == 2

    def test_stop_clip(self, ctrl, api):
        """Test stop clip."""
        api.stop_clip.return_value = {"success": True}

        result = ctrl.stop(track_id=1, clip_index=2)

        assert result["success"] is True

    def test_create_clip(self, ctrl, api):
        """Test creating a MIDI clip."""
        api.create_midi_clip.return_value = {"success": True, "length": 4.0}

        result = ctrl.create(track_id=1, clip_index=2, length=4.0)

        assert result["success"] is True
        assert result["length"] == 4.0
        api.create_midi_clip.assert_called_once_with(1, 2, 4.0)

    def test_add_note(self, ctrl, api):
        """Test adding a MIDI note to a clip."""
        api.add_midi_note.return_value = {"success": True, "pitch": 60}

        result = ctrl.add_note(
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
        api.add_midi_note.assert_called_once_with(1, 2, 60, 0.0, 0.25, 100, False)

    def test_record_start(self, ctrl, api):
        """Test start recording."""
        api.record_clip.return_value = {"success": True, "recording": True}

        result = ctrl.record(track_id=1, clip_index=2, enable=True)

        assert result["recording"] is True

    def test_record_stop(self, ctrl, api):
        """Test stop recording."""
        api.record_clip.return_value = {"success": True, "recording": False}

        result = ctrl.record(track_id=1, clip_index=2, enable=False)

        assert result["recording"] is False

    def test_stop_all_success(self, ctrl, api):
        """Test stop all clips successfully."""
        api.get_tracks.return_value = {
            "success": True,
            "tracks": [{"id": 1}, {"id": 2}]
        }
        api.stop_clip.return_value = {"success": True}

        result = ctrl.stop_all()

        assert result["success"] is True
        assert len(result["stopped"]) == 2

    def test_stop_all_with_failures(self, ctrl, api):
        """Test stop all with some failures."""
        api.get_tracks.return_value = {
            "success": True,
            "tracks": [{"id": 1}, {"id": 2}]
        }
        api.stop_clip.side_effect = [
            {"success": True},
            {"success": False}
        ]

        result = ctrl.stop_all()

        assert result["success"] is False
        assert len(result["stopped"]) == 1
        assert len(result["failed"]) == 1

    def test_launch_scene(self, ctrl, api):
        """Test launch scene."""
        api.launch_scene.return_value = {"success": True, "scene_index": 0}

        result = ctrl.launch_scene(scene_index=0)

        assert result["success"] is True

    def test_stop_scene(self, ctrl, api):
        """Test stop scene."""
        api.stop_scene.return_value = {"success": True}

        result = ctrl.stop_scene(scene_index=0)

        assert result["success"] is True

    def test_batch_launch_success(self, ctrl, api):
        """Test batch launch all success."""
        api.launch_clip.return_value = {"success": True}

        result = ctrl.batch_launch(clips=[(1, 0), (1, 1), (2, 0)])

        assert result["success"] is True
        assert result["launched"] == 3

    def test_batch_launch_partial(self, ctrl, api):
        """Test batch launch with partial failure."""
        api.launch_clip.side_effect = [
            {"success": True},
            {"success": False},
            {"success": True}
        ]

        result = ctrl.batch_launch(clips=[(1, 0), (1, 1), (2, 0)])

        assert result["success"] is False
        assert result["launched"] == 2
        assert result["failed"] == 1

    def test_trigger_clip_by_name_found(self, ctrl, api):
        """Test trigger clip by name when found."""
        api.get_tracks.return_value = {
            "success": True,
            "tracks": [{"id": 1, "name": "Synth"}]
        }
        api.launch_clip.return_value = {"success": True}

        result = ctrl.trigger_clip_by_name(track_name="Synth", clip_name="Section A")

        assert result["success"] is True

    def test_trigger_clip_by_name_not_found(self, ctrl, api):
        """Test trigger clip by name when track not found."""
        api.get_tracks.return_value = {
            "success": True,
            "tracks": [{"id": 1, "name": "Synth"}]
        }

        result = ctrl.trigger_clip_by_name(track_name="Drums", clip_name="Beat")

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_get_playing_clips(self, ctrl, api):
        """Test get playing clips."""
        api.get_tracks.return_value = {
            "success": True,
            "tracks": [{"id": 1, "name": "Synth"}]
        }

        result = ctrl.get_playing_clips()

        assert result["success"] is True
        assert "playing_clips" in result
