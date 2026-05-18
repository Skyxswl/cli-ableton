"""Tests for TrackOperations."""

import pytest
from unittest.mock import Mock

from cli_anything.ableton.track_operations import TrackOperations
from cli_anything.ableton.ableton_api import AbletonAPI


class TestTrackOperations:
    """Test TrackOperations class."""

    @pytest.fixture
    def api(self):
        """Create mock API."""
        api = Mock(spec=AbletonAPI)
        return api

    @pytest.fixture
    def ops(self, api):
        """Create TrackOperations instance."""
        return TrackOperations(api)

    def test_list_tracks(self, ops, api):
        """Test list all tracks."""
        api.get_tracks.return_value = {
            "success": True,
            "tracks": [{"id": 1, "name": "Audio 1"}, {"id": 2, "name": "Audio 2"}]
        }

        result = ops.list()

        assert result["success"] is True
        assert len(result["tracks"]) == 2

    def test_list_tracks_filter_type(self, ops, api):
        """Test list tracks with type filter."""
        api.get_tracks.return_value = {
            "success": True,
            "tracks": [
                {"id": 1, "name": "Audio 1", "type": "audio"},
                {"id": 2, "name": "MIDI 1", "type": "midi"}
            ]
        }

        result = ops.list(filter_type="midi")

        assert result["success"] is True
        assert len(result["tracks"]) == 1
        assert result["tracks"][0]["type"] == "midi"

    def test_list_tracks_invalid_filter(self, ops, api):
        """Test list tracks with invalid filter."""
        result = ops.list(filter_type="invalid")

        assert result["success"] is False
        assert "Invalid filter type" in result["error"]

    def test_create_track(self, ops, api):
        """Test create track."""
        api.create_track.return_value = {"success": True, "track_id": 1, "track_name": "New Track"}

        result = ops.create(name="New Track", track_type="audio")

        assert result["success"] is True
        assert result["track_name"] == "New Track"

    def test_delete_track(self, ops, api):
        """Test delete track."""
        api.delete_track.return_value = {"success": True, "track_id": 1}

        result = ops.delete(track_id=1)

        assert result["success"] is True

    def test_select_track(self, ops, api):
        """Test select track."""
        api.select_track.return_value = {"success": True, "track_id": 1}

        result = ops.select(track_id=1)

        assert result["success"] is True

    def test_arm_track(self, ops, api):
        """Test arm track."""
        api.set_track_arm.return_value = {"success": True, "armed": True}

        result = ops.arm(track_id=1, armed=True)

        assert result["armed"] is True

    def test_mute_track(self, ops, api):
        """Test mute track."""
        api.set_track_mute.return_value = {"success": True, "muted": True}

        result = ops.mute(track_id=1, muted=True)

        assert result["muted"] is True

    def test_solo_track(self, ops, api):
        """Test solo track."""
        api.set_track_solo.return_value = {"success": True, "soloed": True}

        result = ops.solo(track_id=1, soloed=True)

        assert result["soloed"] is True

    def test_set_volume(self, ops, api):
        """Test set volume."""
        api.set_track_volume.return_value = {"success": True, "volume": 0.8}

        result = ops.volume(track_id=1, value=0.8)

        assert result["volume"] == 0.8

    def test_set_panning(self, ops, api):
        """Test set panning."""
        api.set_track_panning.return_value = {"success": True, "panning": 0.5}

        result = ops.panning(track_id=1, value=0.5)

        assert result["panning"] == 0.5

    def test_get_info(self, ops, api):
        """Test get track info."""
        api.get_tracks.return_value = {
            "success": True,
            "tracks": [{"id": 1, "name": "Audio 1"}]
        }

        result = ops.get_info(track_id=1)

        assert result["success"] is True
        assert result["track"]["name"] == "Audio 1"

    def test_get_info_not_found(self, ops, api):
        """Test get info for non-existent track."""
        api.get_tracks.return_value = {
            "success": True,
            "tracks": [{"id": 1, "name": "Audio 1"}]
        }

        result = ops.get_info(track_id=999)

        assert result["success"] is False

    def test_batch_create(self, ops, api):
        """Test batch create tracks."""
        api.create_track.side_effect = [
            {"success": True, "track_id": 1},
            {"success": True, "track_id": 2}
        ]

        result = ops.batch_create(names=["Track 1", "Track 2"])

        assert result["success"] is True
        assert result["created"] == 2
        assert result["failed"] == 0

    def test_duplicate_track(self, ops, api):
        """Test duplicate track."""
        api.get_tracks.return_value = {
            "success": True,
            "tracks": [{"id": 1, "name": "Original", "type": "audio"}]
        }
        api.create_track.return_value = {"success": True, "track_id": 2, "track_name": "Original Copy"}

        result = ops.duplicate(track_id=1)

        assert result["success"] is True
        assert "Copy" in result["track_name"]

    def test_duplicate_track_not_found(self, ops, api):
        """Test duplicate non-existent track."""
        api.get_tracks.return_value = {"success": False, "error": "Not found"}

        result = ops.duplicate(track_id=999)

        assert result["success"] is False