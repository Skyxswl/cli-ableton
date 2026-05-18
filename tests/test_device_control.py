"""Tests for DeviceControl."""

import pytest
from unittest.mock import Mock

from cli_anything.ableton.device_control import DeviceControl
from cli_anything.ableton.ableton_api import AbletonAPI


class TestDeviceControl:
    """Test DeviceControl class."""

    @pytest.fixture
    def api(self):
        """Create mock API."""
        return Mock(spec=AbletonAPI)

    @pytest.fixture
    def ctrl(self, api):
        """Create DeviceControl instance."""
        return DeviceControl(api)

    def test_list_devices(self, ctrl, api):
        """Test list devices."""
        api.get_devices.return_value = {
            "success": True,
            "devices": [{"id": 1, "name": "Reverb"}]
        }

        result = ctrl.list(track_id=1)

        assert result["success"] is True
        assert len(result["devices"]) == 1

    def test_select_device(self, ctrl, api):
        """Test select device."""
        api.select_device.return_value = {"success": True, "device_id": 1}

        result = ctrl.select(track_id=1, device_id=1)

        assert result["success"] is True

    def test_get_param(self, ctrl, api):
        """Test get device param."""
        api.get_device_param.return_value = {
            "success": True,
            "device_id": 1,
            "param_name": "Mix",
            "value": 0.5
        }

        result = ctrl.get_param(device_id=1, param_name="Mix")

        assert result["value"] == 0.5

    def test_set_param(self, ctrl, api):
        """Test set device param."""
        api.set_device_param.return_value = {
            "success": True,
            "device_id": 1,
            "param_name": "Mix",
            "value": 0.8
        }

        result = ctrl.set_param(device_id=1, param_name="Mix", value=0.8)

        assert result["value"] == 0.8

    def test_toggle_on(self, ctrl, api):
        """Test toggle device on."""
        api.set_device_on_off.return_value = {"success": True, "on": True}

        result = ctrl.toggle(device_id=1, on=True)

        assert result["on"] is True

    def test_toggle_off(self, ctrl, api):
        """Test toggle device off."""
        api.set_device_on_off.return_value = {"success": True, "on": False}

        result = ctrl.toggle(device_id=1, on=False)

        assert result["on"] is False

    def test_automate_param(self, ctrl, api):
        """Test automate parameter."""
        api.set_device_param.return_value = {"success": True}

        result = ctrl.automate_param(device_id=1, param_name="Filter", value=0.7,
                                     time=1.0, length=2.0, curve=0.5)

        assert result["success"] is True
        assert "automation" in result

    def test_get_device_params(self, ctrl, api):
        """Test get all device parameters."""
        api.get_device_param.return_value = {
            "success": True,
            "value": 0.5
        }

        result = ctrl.get_device_params(device_id=1)

        assert result["success"] is True
        assert "parameters" in result

    def test_find_device_found(self, ctrl, api):
        """Test find device when found."""
        api.get_devices.return_value = {
            "success": True,
            "devices": [{"id": 1, "name": "Reverb"}, {"id": 2, "name": "Delay"}]
        }

        result = ctrl.find_device(track_id=1, device_name="Delay")

        assert result["success"] is True
        assert result["device"]["name"] == "Delay"

    def test_find_device_not_found(self, ctrl, api):
        """Test find device when not found."""
        api.get_devices.return_value = {
            "success": True,
            "devices": [{"id": 1, "name": "Reverb"}]
        }

        result = ctrl.find_device(track_id=1, device_name="Chorus")

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_set_effect_chain(self, ctrl, api):
        """Test set effect chain."""
        effects = [
            {"type": "reverb", "enabled": True, "params": {"size": 0.5}},
            {"type": "delay", "enabled": True, "params": {"time": 0.25}}
        ]

        result = ctrl.set_effect_chain(track_id=1, effects=effects)

        assert result["success"] is True
        assert result["configured"] == 2

    def test_preset_reverb_valid(self, ctrl, api):
        """Test reverb preset with valid preset."""
        result = ctrl.preset_reverb(track_id=1, preset="hall")

        assert result["success"] is True
        assert result["preset"] == "hall"

    def test_preset_reverb_invalid(self, ctrl, api):
        """Test reverb preset with invalid preset."""
        result = ctrl.preset_reverb(track_id=1, preset="invalid")

        assert result["success"] is False
        assert "Unknown preset" in result["error"]

    def test_preset_delay_valid(self, ctrl, api):
        """Test delay preset with valid preset."""
        result = ctrl.preset_delay(track_id=1, preset="ping_pong")

        assert result["success"] is True
        assert result["preset"] == "ping_pong"

    def test_preset_delay_invalid(self, ctrl, api):
        """Test delay preset with invalid preset."""
        result = ctrl.preset_delay(track_id=1, preset="invalid")

        assert result["success"] is False
        assert "Unknown preset" in result["error"]

    def test_preset_filter_valid(self, ctrl, api):
        """Test filter preset with valid preset."""
        result = ctrl.preset_filter(track_id=1, preset="lowpass")

        assert result["success"] is True
        assert result["preset"] == "lowpass"

    def test_preset_filter_invalid(self, ctrl, api):
        """Test filter preset with invalid preset."""
        result = ctrl.preset_filter(track_id=1, preset="invalid")

        assert result["success"] is False
        assert "Unknown preset" in result["error"]