"""Track operations module for Ableton CLI."""

from typing import Any, Dict, List, Optional

from .ableton_api import AbletonAPI
from .constants import ErrorCode


class TrackOperations:
    """
    Track management operations for Ableton.

    Provides track CRUD operations and track state control.
    All methods return new dicts (immutable pattern).
    """

    def __init__(self, api: AbletonAPI) -> None:
        """
        Initialize track operations.

        Args:
            api: AbletonAPI instance
        """
        self._api = api

    def list(self, filter_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List all tracks, optionally filtered by type.

        Args:
            filter_type: Optional filter ('audio', 'midi', 'return')

        Returns:
            Dict with filtered track list
        """
        result = self._api.get_tracks()

        if filter_type and result.get("success"):
            valid_types = {"audio", "midi", "return"}
            if filter_type not in valid_types:
                return {
                    "success": False,
                    "error": f"Invalid filter type: {filter_type}",
                    "tracks": [],
                }

            filtered = [
                t for t in result["tracks"]
                if t.get("type") == filter_type
            ]
            return {**result, "tracks": filtered}

        return result

    def create(
        self,
        name: str,
        track_type: str = "audio",
        color: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a new track.

        Args:
            name: Track name
            track_type: Track type ('audio', 'midi', 'return')
            color: Optional track color (hex)

        Returns:
            Dict with created track info
        """
        result = self._api.create_track(name, track_type)

        if result.get("success") and color:
            # Color can be set separately if needed
            return {**result, "color": color}

        return result

    def delete(self, track_id: int) -> Dict[str, Any]:
        """
        Delete a track by ID.

        Args:
            track_id: Track identifier

        Returns:
            Dict with deletion result
        """
        return self._api.delete_track(track_id)

    def select(self, track_id: int) -> Dict[str, Any]:
        """
        Select a track for editing.

        Args:
            track_id: Track identifier

        Returns:
            Dict with selection result
        """
        return self._api.select_track(track_id)

    def arm(self, track_id: int, armed: bool = True) -> Dict[str, Any]:
        """
        Arm or disarm a track for recording.

        Args:
            track_id: Track identifier
            armed: True to arm, False to disarm

        Returns:
            Dict with arm state result
        """
        return self._api.set_track_arm(track_id, armed)

    def mute(self, track_id: int, muted: bool = True) -> Dict[str, Any]:
        """
        Mute or unmute a track.

        Args:
            track_id: Track identifier
            muted: True to mute, False to unmute

        Returns:
            Dict with mute state result
        """
        return self._api.set_track_mute(track_id, muted)

    def solo(self, track_id: int, soloed: bool = True) -> Dict[str, Any]:
        """
        Solo or unsolo a track.

        Args:
            track_id: Track identifier
            soloed: True to solo, False to unsolo

        Returns:
            Dict with solo state result
        """
        return self._api.set_track_solo(track_id, soloed)

    def volume(self, track_id: int, value: float) -> Dict[str, Any]:
        """
        Set track volume.

        Args:
            track_id: Track identifier
            value: Volume level (0.0 to 1.0)

        Returns:
            Dict with volume result
        """
        return self._api.set_track_volume(track_id, value)

    def panning(self, track_id: int, value: float) -> Dict[str, Any]:
        """
        Set track panning.

        Args:
            track_id: Track identifier
            value: Pan position (-1.0 to 1.0)

        Returns:
            Dict with panning result
        """
        return self._api.set_track_panning(track_id, value)

    def get_info(self, track_id: int) -> Dict[str, Any]:
        """
        Get detailed track information.

        Args:
            track_id: Track identifier

        Returns:
            Dict with track details
        """
        result = self._api.get_tracks()

        if result.get("success"):
            for track in result.get("tracks", []):
                if track.get("id") == track_id:
                    return {
                        "success": True,
                        "track": track,
                    }

        return {
            "success": False,
            "error": f"Track {track_id} not found",
            "track": None,
        }

    def batch_create(
        self,
        names: List[str],
        track_type: str = "audio",
    ) -> Dict[str, Any]:
        """
        Create multiple tracks in batch.

        Args:
            names: List of track names
            track_type: Track type for all tracks

        Returns:
            Dict with batch creation results
        """
        results = []
        for name in names:
            result = self._api.create_track(name, track_type)
            results.append(result)

        success_count = sum(1 for r in results if r.get("success"))

        return {
            "success": success_count == len(names),
            "created": success_count,
            "failed": len(names) - success_count,
            "results": results,
        }

    def duplicate(self, track_id: int) -> Dict[str, Any]:
        """
        Duplicate an existing track.

        Args:
            track_id: Track to duplicate

        Returns:
            Dict with duplicate result
        """
        # Get track info first
        info = self.get_info(track_id)

        if not info.get("success"):
            return {
                "success": False,
                "error": f"Track {track_id} not found",
            }

        track = info.get("track", {})
        new_name = f"{track.get('name', 'Track')} Copy"

        return self._api.create_track(new_name, track.get("type", "audio"))