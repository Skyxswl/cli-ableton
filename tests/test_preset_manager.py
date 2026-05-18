"""Tests for PresetManager."""

import pytest
from unittest.mock import Mock

from cli_anything.ableton.preset_manager import PresetManager
from cli_anything.ableton.ableton_api import AbletonAPI


class TestPresetManager:
    """Test PresetManager class."""

    @pytest.fixture
    def api(self):
        """Create mock API."""
        return Mock(spec=AbletonAPI)

    @pytest.fixture
    def mgr(self, api):
        """Create PresetManager instance."""
        return PresetManager(api)

    def test_save_preset(self, mgr, api):
        """Test save preset."""
        api.save_preset.return_value = {"success": True, "preset_name": "My Preset"}

        result = mgr.save(name="My Preset", category="sound_design")

        assert result["success"] is True
        assert result["preset_name"] == "My Preset"

    def test_save_updates_current(self, mgr, api):
        """Test save updates current preset."""
        api.save_preset.return_value = {"success": True}

        mgr.save(name="New Preset")

        assert mgr._current_preset == "New Preset"

    def test_load_preset(self, mgr, api):
        """Test load preset."""
        api.load_preset.return_value = {"success": True, "preset_id": "abc123"}

        result = mgr.load(preset_id="abc123")

        assert result["success"] is True

    def test_load_updates_current(self, mgr, api):
        """Test load updates current preset."""
        api.load_preset.return_value = {"success": True}

        mgr.load(preset_id="abc123")

        assert mgr._current_preset == "abc123"

    def test_list_presets(self, mgr, api):
        """Test list presets."""
        api.list_presets.return_value = {
            "success": True,
            "presets": [{"id": "1", "name": "Preset 1"}]
        }

        result = mgr.list()

        assert result["success"] is True
        assert len(result["presets"]) == 1

    def test_list_presets_with_category(self, mgr, api):
        """Test list presets with category filter."""
        api.list_presets.return_value = {
            "success": True,
            "presets": []
        }

        result = mgr.list(category="sound_design")

        assert result["success"] is True

    def test_list_includes_current(self, mgr, api):
        """Test list includes current preset info."""
        api.list_presets.return_value = {"success": True, "presets": []}
        mgr._current_preset = "Test Preset"

        result = mgr.list()

        assert "current_preset" in result
        assert result["current_preset"] == "Test Preset"

    def test_current_with_preset(self, mgr, api):
        """Test current when preset is loaded."""
        mgr._current_preset = "My Preset"

        result = mgr.current()

        assert result["success"] is True
        assert result["current_preset"] == "My Preset"

    def test_current_without_preset(self, mgr, api):
        """Test current when no preset loaded."""
        result = mgr.current()

        assert result["success"] is True
        assert result["current_preset"] is None

    def test_delete_clears_current(self, mgr, api):
        """Test delete clears current if deleted."""
        mgr._current_preset = "To Delete"

        result = mgr.delete("To Delete")

        assert result["success"] is True
        assert mgr._current_preset is None

    def test_delete_preset(self, mgr, api):
        """Test delete preset."""
        result = mgr.delete("preset_123")

        assert result["success"] is True
        assert result["deleted"] is True

    def test_export(self, mgr, api):
        """Test export preset."""
        api.list_presets.return_value = {
            "success": True,
            "presets": [{"id": "1", "name": "Export Me"}]
        }

        result = mgr.export(preset_id="1", filepath="/path/to/preset.json")

        assert result["success"] is True
        assert result["exported"] is True

    def test_export_not_found(self, mgr, api):
        """Test export when preset not found."""
        api.list_presets.return_value = {
            "success": True,
            "presets": []
        }

        result = mgr.export(preset_id="nonexistent", filepath="/path/to/file.json")

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_import_preset(self, mgr, api):
        """Test import preset."""
        result = mgr.import_preset(filepath="/path/to/preset.json", name="Imported")

        assert result["success"] is True
        assert result["name"] == "Imported"

    def test_import_preset_with_category(self, mgr, api):
        """Test import with category."""
        result = mgr.import_preset(
            filepath="/path/to/preset.json",
            name="Imported",
            category="custom"
        )

        assert result["success"] is True
        assert result["category"] == "custom"

    def test_save_sound_design_preset(self, mgr, api):
        """Test save sound design preset."""
        api.save_preset.return_value = {"success": True}

        midi_effects = [{"type": "arp", "enabled": True}]
        devices = [{"name": "Reverb", "params": {"size": 0.5}}]

        result = mgr.save_sound_design_preset(
            name="Ambient Arp",
            track_id=1,
            midi_effects=midi_effects,
            devices=devices
        )

        assert result["success"] is True
        assert result["track_id"] == 1

    def test_list_sound_design_presets(self, mgr, api):
        """Test list sound design presets."""
        api.list_presets.return_value = {"success": True, "presets": []}

        result = mgr.list_sound_design_presets()

        assert result["success"] is True

    def test_load_sound_design_preset(self, mgr, api):
        """Test load sound design preset."""
        api.load_preset.return_value = {"success": True}

        result = mgr.load_sound_design_preset(preset_id="123", target_track_id=1)

        assert result["success"] is True
        assert result["applied"] is True

    def test_load_sound_design_preset_failure(self, mgr, api):
        """Test load sound design preset failure."""
        api.load_preset.return_value = {"success": False, "error": "Not found"}

        result = mgr.load_sound_design_preset(preset_id="nonexistent", target_track_id=1)

        assert result["success"] is False

    def test_list_categories(self, mgr, api):
        """Test list categories."""
        result = mgr.list_categories()

        assert result["success"] is True
        assert "categories" in result

    def test_create_category(self, mgr, api):
        """Test create category."""
        result = mgr.create_category(name="custom_category")

        assert result["success"] is True
        assert result["created"] is True