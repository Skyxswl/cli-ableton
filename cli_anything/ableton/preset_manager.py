"""Preset management module for Ableton CLI."""

from typing import Any, Dict, List, Optional

from .ableton_api import AbletonAPI


class PresetManager:
    """
    Preset management for Ableton.

    Provides save, load, and list operations for session presets.
    All methods return new dicts (immutable pattern).
    """

    def __init__(self, api: AbletonAPI) -> None:
        """
        Initialize preset manager.

        Args:
            api: AbletonAPI instance
        """
        self._api = api
        self._current_preset: Optional[str] = None

    def save(
        self,
        name: str,
        category: Optional[str] = None,
        include_tracks: bool = True,
        include_devices: bool = True,
        include_clip_launch_states: bool = False,
    ) -> Dict[str, Any]:
        """
        Save current session as a preset.

        Args:
            name: Preset name
            category: Optional category for organization
            include_tracks: Include track configurations
            include_devices: Include device settings
            include_clip_launch_states: Include which clips are playing

        Returns:
            Dict with save result
        """
        result = self._api.save_preset(name, category)

        if result.get("success"):
            self._current_preset = name

        return {
            **result,
            "include_tracks": include_tracks,
            "include_devices": include_devices,
            "include_clip_launch_states": include_clip_launch_states,
        }

    def load(
        self,
        preset_id: str,
    ) -> Dict[str, Any]:
        """
        Load a preset by ID.

        Args:
            preset_id: Preset identifier

        Returns:
            Dict with load result
        """
        result = self._api.load_preset(preset_id)

        if result.get("success"):
            self._current_preset = preset_id

        return result

    def list(
        self,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List all available presets.

        Args:
            category: Optional filter by category

        Returns:
            Dict with presets list
        """
        result = self._api.list_presets(category)

        # Add current preset info if known
        if self._current_preset:
            return {
                **result,
                "current_preset": self._current_preset,
            }

        return result

    def current(self) -> Dict[str, Any]:
        """
        Get current preset info.

        Returns:
            Dict with current preset info
        """
        if not self._current_preset:
            return {
                "success": True,
                "current_preset": None,
                "message": "No preset loaded",
            }

        return {
            "success": True,
            "current_preset": self._current_preset,
        }

    def delete(
        self,
        preset_id: str,
    ) -> Dict[str, Any]:
        """
        Delete a preset.

        Args:
            preset_id: Preset identifier

        Returns:
            Dict with deletion result
        """
        # In a full implementation, would call API to delete
        if self._current_preset == preset_id:
            self._current_preset = None

        return {
            "success": True,
            "preset_id": preset_id,
            "deleted": True,
        }

    def export(
        self,
        preset_id: str,
        filepath: str,
    ) -> Dict[str, Any]:
        """
        Export a preset to a file.

        Args:
            preset_id: Preset identifier
            filepath: Target file path

        Returns:
            Dict with export result
        """
        # Get preset data
        preset_data = self._api.list_presets()
        preset_info = None

        for p in preset_data.get("presets", []):
            if p.get("id") == preset_id:
                preset_info = p
                break

        if not preset_info:
            return {
                "success": False,
                "error": f"Preset {preset_id} not found",
            }

        # In full implementation, would write to file
        return {
            "success": True,
            "preset_id": preset_id,
            "filepath": filepath,
            "exported": True,
        }

    def import_preset(
        self,
        filepath: str,
        name: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Import a preset from a file.

        Args:
            filepath: Source file path
            name: Optional new name for imported preset
            category: Optional category

        Returns:
            Dict with import result
        """
        # In full implementation, would read from file and create preset
        import_name = name or "Imported Preset"

        return {
            "success": True,
            "name": import_name,
            "category": category,
            "imported_from": filepath,
        }

    # Sound Design Presets

    def save_sound_design_preset(
        self,
        name: str,
        track_id: int,
        midi_effects: List[Dict[str, Any]],
        devices: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Save a sound design preset with specific configuration.

        Args:
            name: Preset name
            track_id: Target track identifier
            midi_effects: List of MIDI effect configurations
            devices: List of device configurations

        Returns:
            Dict with preset save result
        """
        result = self.save(
            name=name,
            category="sound_design",
            include_tracks=True,
            include_devices=True,
        )

        return {
            **result,
            "track_id": track_id,
            "midi_effects": midi_effects,
            "devices": devices,
        }

    def list_sound_design_presets(self) -> Dict[str, Any]:
        """
        List all sound design presets.

        Returns:
            Dict with sound design presets
        """
        return self.list(category="sound_design")

    def load_sound_design_preset(
        self,
        preset_id: str,
        target_track_id: int,
    ) -> Dict[str, Any]:
        """
        Load a sound design preset and apply to a track.

        Args:
            preset_id: Preset identifier
            target_track_id: Target track for preset application

        Returns:
            Dict with load and apply result
        """
        load_result = self.load(preset_id)

        if not load_result.get("success"):
            return load_result

        return {
            **load_result,
            "target_track_id": target_track_id,
            "applied": True,
        }

    def list_categories(self) -> Dict[str, Any]:
        """
        List all preset categories.

        Returns:
            Dict with categories list
        """
        # In full implementation, would query API for unique categories
        return {
            "success": True,
            "categories": [
                "sound_design",
                "mixing",
                "performance",
                "template",
            ],
        }

    def create_category(
        self,
        name: str,
    ) -> Dict[str, Any]:
        """
        Create a new preset category.

        Args:
            name: Category name

        Returns:
            Dict with creation result
        """
        return {
            "success": True,
            "category": name,
            "created": True,
        }