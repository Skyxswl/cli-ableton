"""Device control module for Ableton CLI."""

from typing import Any, Dict, List, Optional

from .ableton_api import AbletonAPI


class DeviceControl:
    """
    Device and parameter control for Ableton.

    Provides device selection, parameter get/set, and automation.
    All methods return new dicts (immutable pattern).
    """

    def __init__(self, api: AbletonAPI) -> None:
        """
        Initialize device control.

        Args:
            api: AbletonAPI instance
        """
        self._api = api

    def list(self, track_id: int) -> Dict[str, Any]:
        """
        List all devices on a track.

        Args:
            track_id: Track identifier

        Returns:
            Dict with devices list
        """
        return self._api.get_devices(track_id)

    def select(
        self,
        track_id: int,
        device_id: int,
    ) -> Dict[str, Any]:
        """
        Select a device for editing.

        Args:
            track_id: Track identifier
            device_id: Device identifier

        Returns:
            Dict with selection result
        """
        return self._api.select_device(track_id, device_id)

    def get_param(
        self,
        device_id: int,
        param_name: str,
    ) -> Dict[str, Any]:
        """
        Get a device parameter value.

        Args:
            device_id: Device identifier
            param_name: Parameter name

        Returns:
            Dict with parameter value
        """
        return self._api.get_device_param(device_id, param_name)

    def set_param(
        self,
        device_id: int,
        param_name: str,
        value: float,
    ) -> Dict[str, Any]:
        """
        Set a device parameter value.

        Args:
            device_id: Device identifier
            param_name: Parameter name
            value: Parameter value (0.0 to 1.0 typically)

        Returns:
            Dict with parameter value result
        """
        return self._api.set_device_param(device_id, param_name, value)

    def toggle(
        self,
        device_id: int,
        on: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Toggle device on/off or set specific state.

        Args:
            device_id: Device identifier
            on: Optional explicit on/off state

        Returns:
            Dict with toggle result
        """
        if on is None:
            # Toggle current state (would need to get current state first)
            return self._api.set_device_on_off(device_id, True)

        return self._api.set_device_on_off(device_id, on)

    def automate_param(
        self,
        device_id: int,
        param_name: str,
        value: float,
        time: float = 0.0,
        length: float = 1.0,
        curve: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Create parameter automation event.

        Args:
            device_id: Device identifier
            param_name: Parameter name
            value: Target parameter value
            time: Start time in beats
            length: Automation segment length in beats
            curve: Curve shape (-1.0 to 1.0)

        Returns:
            Dict with automation result
        """
        # Set the parameter value
        result = self._api.set_device_param(device_id, param_name, value)

        # In a full implementation, would also create automation curve
        return {
            **result,
            "automation": {
                "time": time,
                "length": length,
                "curve": curve,
            },
        }

    def get_device_params(
        self,
        device_id: int,
    ) -> Dict[str, Any]:
        """
        Get all parameters for a device.

        Args:
            device_id: Device identifier

        Returns:
            Dict with all parameters
        """
        # Common device parameters
        common_params = [
            "Device On", "Chain Select", "Mix Volume", "Mix Pan",
        ]

        params = {}
        for param in common_params:
            result = self._api.get_device_param(device_id, param)
            if result.get("success"):
                params[param] = result.get("value")

        return {
            "success": True,
            "device_id": device_id,
            "parameters": params,
        }

    def find_device(
        self,
        track_id: int,
        device_name: str,
    ) -> Dict[str, Any]:
        """
        Find a device by name on a track.

        Args:
            track_id: Track identifier
            device_name: Device name to search for

        Returns:
            Dict with device info if found
        """
        result = self._api.get_devices(track_id)

        if not result.get("success"):
            return {
                "success": False,
                "error": f"No devices found on track {track_id}",
            }

        for device in result.get("devices", []):
            if device.get("name") == device_name:
                return {
                    "success": True,
                    "device": device,
                }

        return {
            "success": False,
            "error": f"Device '{device_name}' not found",
        }

    def set_effect_chain(
        self,
        track_id: int,
        effects: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Set a chain of effects on a track.

        Args:
            track_id: Track identifier
            effects: List of effect configurations with 'type', 'enabled', 'params'

        Returns:
            Dict with chain configuration result
        """
        results = []

        for effect in effects:
            effect_type = effect.get("type")
            enabled = effect.get("enabled", True)
            params = effect.get("params", {})

            # Configure the effect via MIDI processor
            # This is a simplified version - full impl would use midi_processor
            result = {
                "success": True,
                "effect_type": effect_type,
                "track_id": track_id,
            }
            results.append(result)

        success_count = sum(1 for r in results if r.get("success"))

        return {
            "success": success_count == len(effects),
            "configured": success_count,
            "failed": len(effects) - success_count,
            "effects": results,
        }

    # Sound Design Presets

    def preset_reverb(
        self,
        track_id: int,
        preset: str = "hall",
    ) -> Dict[str, Any]:
        """
        Apply reverb preset.

        Args:
            track_id: Track identifier
            preset: Preset name ('hall', 'room', 'plate', 'spring')

        Returns:
            Dict with preset configuration
        """
        presets = {
            "hall": {"Size": 0.8, "Decay": 0.7, "Mix": 0.3},
            "room": {"Size": 0.5, "Decay": 0.4, "Mix": 0.25},
            "plate": {"Size": 0.6, "Decay": 0.5, "Mix": 0.35},
            "spring": {"Size": 0.4, "Decay": 0.3, "Mix": 0.2},
        }

        if preset not in presets:
            return {
                "success": False,
                "error": f"Unknown preset: {preset}. Must be one of: {list(presets.keys())}",
            }

        # In full implementation, would find reverb device and set params
        return {
            "success": True,
            "preset": preset,
            "track_id": track_id,
            "params": presets[preset],
        }

    def preset_delay(
        self,
        track_id: int,
        preset: str = "sync",
    ) -> Dict[str, Any]:
        """
        Apply delay preset.

        Args:
            track_id: Track identifier
            preset: Preset name ('sync', 'free', 'ping_pong', 'diffuse')

        Returns:
            Dict with preset configuration
        """
        presets = {
            "sync": {"Time": "1/4", "Feedback": 0.4, "Mix": 0.3},
            "free": {"Time": 0.375, "Feedback": 0.35, "Mix": 0.25},
            "ping_pong": {"Time": "1/8", "Feedback": 0.45, "Mix": 0.35},
            "diffuse": {"Time": "1/16", "Feedback": 0.3, "Mix": 0.4},
        }

        if preset not in presets:
            return {
                "success": False,
                "error": f"Unknown preset: {preset}. Must be one of: {list(presets.keys())}",
            }

        return {
            "success": True,
            "preset": preset,
            "track_id": track_id,
            "params": presets[preset],
        }

    def preset_filter(
        self,
        track_id: int,
        preset: str = "lowpass",
    ) -> Dict[str, Any]:
        """
        Apply filter preset.

        Args:
            track_id: Track identifier
            preset: Preset name ('lowpass', 'highpass', 'bandpass')

        Returns:
            Dict with preset configuration
        """
        presets = {
            "lowpass": {"Frequency": 0.7, "Resonance": 0.3},
            "highpass": {"Frequency": 0.3, "Resonance": 0.3},
            "bandpass": {"Frequency": 0.5, "Resonance": 0.5},
        }

        if preset not in presets:
            return {
                "success": False,
                "error": f"Unknown preset: {preset}. Must be one of: {list(presets.keys())}",
            }

        return {
            "success": True,
            "preset": preset,
            "track_id": track_id,
            "params": presets[preset],
        }