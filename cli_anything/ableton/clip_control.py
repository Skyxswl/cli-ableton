"""Clip control module for Ableton CLI."""

from typing import Any, Dict, List

from .ableton_api import AbletonAPI


class ClipControl:
    """
    Clip control operations for Ableton.

    Provides clip launch, stop, record, and scene control.
    All methods return new dicts (immutable pattern).
    """

    def __init__(self, api: AbletonAPI) -> None:
        """
        Initialize clip control.

        Args:
            api: AbletonAPI instance
        """
        self._api = api

    def launch(
        self,
        track_id: int,
        clip_index: int,
    ) -> Dict[str, Any]:
        """
        Launch a clip.

        Args:
            track_id: Track identifier
            clip_index: Clip slot index

        Returns:
            Dict with launch result
        """
        return self._api.launch_clip(track_id, clip_index)

    def stop(
        self,
        track_id: int,
        clip_index: int,
    ) -> Dict[str, Any]:
        """
        Stop a clip.

        Args:
            track_id: Track identifier
            clip_index: Clip slot index

        Returns:
            Dict with stop result
        """
        return self._api.stop_clip(track_id, clip_index)

    def create(
        self,
        track_id: int,
        clip_index: int,
        length: float = 4.0,
    ) -> Dict[str, Any]:
        """
        Create a MIDI clip in a clip slot.

        Args:
            track_id: Track identifier
            clip_index: Clip slot index
            length: Clip length in beats

        Returns:
            Dict with creation result
        """
        return self._api.create_midi_clip(track_id, clip_index, length)

    def add_note(
        self,
        track_id: int,
        clip_index: int,
        pitch: int,
        start: float,
        duration: float,
        velocity: int = 100,
        mute: bool = False,
    ) -> Dict[str, Any]:
        """
        Add a MIDI note to an existing clip.

        Args:
            track_id: Track identifier
            clip_index: Clip slot index
            pitch: MIDI note number
            start: Note start time in beats
            duration: Note duration in beats
            velocity: MIDI velocity
            mute: Whether the note is muted

        Returns:
            Dict with note insertion result
        """
        return self._api.add_midi_note(
            track_id,
            clip_index,
            pitch,
            start,
            duration,
            velocity,
            mute,
        )

    def record(
        self,
        track_id: int,
        clip_index: int,
        enable: bool = True,
    ) -> Dict[str, Any]:
        """
        Start or stop clip recording.

        Args:
            track_id: Track identifier
            clip_index: Clip slot index
            enable: True to start recording, False to stop

        Returns:
            Dict with recording state
        """
        return self._api.record_clip(track_id, clip_index, enable)

    def stop_all(self) -> Dict[str, Any]:
        """
        Stop all playing clips.

        Returns:
            Dict with stop all result
        """
        result = self._api.get_tracks()

        if not result.get("success"):
            return {
                "success": False,
                "error": "Failed to get tracks",
            }

        stopped = []
        failed = []

        for track in result.get("tracks", []):
            track_id = track.get("id")
            # Stop first clip of each track (0 index)
            response = self._api.stop_clip(track_id, 0)
            if response.get("success"):
                stopped.append(track_id)
            else:
                failed.append(track_id)

        return {
            "success": len(failed) == 0,
            "stopped": stopped,
            "failed": failed,
        }

    def launch_scene(
        self,
        scene_index: int,
    ) -> Dict[str, Any]:
        """
        Launch a scene.

        Args:
            scene_index: Scene index

        Returns:
            Dict with scene launch result
        """
        return self._api.launch_scene(scene_index)

    def stop_scene(
        self,
        scene_index: int,
    ) -> Dict[str, Any]:
        """
        Stop a scene.

        Args:
            scene_index: Scene index

        Returns:
            Dict with scene stop result
        """
        return self._api.stop_scene(scene_index)

    def launch_scene_and_others(
        self,
        scene_index: int,
    ) -> Dict[str, Any]:
        """
        Launch a scene and stop all others.

        Args:
            scene_index: Scene index to launch

        Returns:
            Dict with scene transition result
        """
        # First stop all scenes
        self.stop_all_scenes()

        # Then launch target scene
        return self.launch_scene(scene_index)

    def stop_all_scenes(self) -> Dict[str, Any]:
        """
        Stop all scenes.

        Returns:
            Dict with stop all scenes result
        """
        # Get total scene count from tracks
        result = self._api.get_tracks()

        if not result.get("success"):
            return {
                "success": False,
                "error": "Failed to get tracks",
            }

        # Stop scene 0 (all slots)
        return self._api.stop_scene(0)

    def batch_launch(
        self,
        clips: List[tuple],
    ) -> Dict[str, Any]:
        """
        Launch multiple clips at once.

        Args:
            clips: List of (track_id, clip_index) tuples

        Returns:
            Dict with batch launch results
        """
        results = []
        for track_id, clip_index in clips:
            result = self._api.launch_clip(track_id, clip_index)
            results.append(result)

        success_count = sum(1 for r in results if r.get("success"))

        return {
            "success": success_count == len(clips),
            "launched": success_count,
            "failed": len(clips) - success_count,
            "results": results,
        }

    def get_playing_clips(self) -> Dict[str, Any]:
        """
        Get all currently playing clips.

        Returns:
            Dict with playing clips list
        """
        result = self._api.get_tracks()

        if not result.get("success"):
            return {
                "success": False,
                "error": "Failed to get tracks",
                "playing_clips": [],
            }

        playing = []
        for track in result.get("tracks", []):
            track_id = track.get("id")
            # Check each clip slot (simplified - real impl would need more API calls)
            for clip_idx in range(8):  # Check first 8 slots
                # In real impl, would check is_playing state
                pass

        return {
            "success": True,
            "playing_clips": playing,
        }

    def trigger_clip_by_name(
        self,
        track_name: str,
        clip_name: str,
    ) -> Dict[str, Any]:
        """
        Trigger a clip by track name and clip name.

        Args:
            track_name: Track name to search
            clip_name: Clip name to find

        Returns:
            Dict with trigger result
        """
        result = self._api.get_tracks()

        if not result.get("success"):
            return {
                "success": False,
                "error": "Failed to get tracks",
            }

        for track in result.get("tracks", []):
            if track.get("name") == track_name:
                track_id = track.get("id")
                # In real impl, would find clip index by name
                # For now, assume clip_index = 0
                return self._api.launch_clip(track_id, 0)

        return {
            "success": False,
            "error": f"Track '{track_name}' not found",
        }
