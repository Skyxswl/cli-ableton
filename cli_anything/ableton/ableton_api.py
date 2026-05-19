"""Ableton API wrapper - high-level interface to Ableton functionality."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .osc_bridge import AbletonOSCBridge, OSCResponse
from .constants import (
    OSC_ADDRESSES,
    ErrorCode,
    DEFAULT_HOST,
    DEFAULT_LISTEN_PORT,
    DEFAULT_RESPONSE_PORT,
    DEFAULT_TIMEOUT,
)


@dataclass(frozen=True)
class Track:
    """Immutable track representation."""
    id: int
    name: str
    color: Optional[str] = None
    armed: bool = False
    muted: bool = False
    soloed: bool = False
    volume: float = 0.0
    panning: float = 0.0


@dataclass(frozen=True)
class Clip:
    """Immutable clip representation."""
    id: str
    name: str
    track_id: int
    slot_index: int
    playing: bool = False


@dataclass(frozen=True)
class Device:
    """Immutable device representation."""
    id: int
    name: str
    type: str
    parameters: Dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class MIDIEffect:
    """Immutable MIDI effect representation."""
    type: str
    enabled: bool
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Preset:
    """Immutable preset representation."""
    id: str
    name: str
    category: Optional[str] = None


@dataclass(frozen=True)
class TransportState:
    """Immutable transport state representation."""
    playing: bool
    recording: bool
    tempo: float
    time: float


class AbletonAPI:
    """
    High-level API wrapper for Ableton Live.

    All methods return JSON-serializable dicts and never mutate
    internal state. Implements immutable data patterns.
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_LISTEN_PORT,
        response_port: int = DEFAULT_RESPONSE_PORT,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Initialize the Ableton API.

        Args:
            host: AbletonOSC server host
            port: AbletonOSC server port
            timeout: Response timeout in seconds
        """
        self._bridge = AbletonOSCBridge(
            host=host,
            send_port=port,
            recv_port=response_port,
            timeout=timeout,
        )
        self._connected = False

    @property
    def bridge(self) -> AbletonOSCBridge:
        """Get the underlying OSC bridge."""
        return self._bridge

    @property
    def is_connected(self) -> bool:
        """Check if API is connected to Ableton."""
        return self._connected

    def connect(self) -> OSCResponse:
        """
        Connect to Ableton Live.

        Returns:
            OSCResponse with connection status
        """
        response = self._bridge.connect()
        self._connected = response.success
        return response

    def disconnect(self) -> None:
        """Disconnect from Ableton Live."""
        self._bridge.disconnect()
        self._connected = False

    def health_check(self) -> OSCResponse:
        """
        Check connection health.

        Returns:
            OSCResponse with health status
        """
        return self._bridge.health_check()

    # Track Operations

    def get_tracks(self) -> Dict[str, Any]:
        """
        Get all tracks in the current session.

        Returns:
            Dict with 'tracks' key containing list of track dicts
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["track_list"]
        )

        if not response.success:
            return {
                "success": False,
                "error": response.error,
                "tracks": [],
            }

        if response.data and "params" in response.data:
            return {
                "success": True,
                "tracks": [
                    {"id": index, "name": name}
                    for index, name in enumerate(response.data["params"])
                ],
            }

        # Return immutable track list
        return {
            "success": True,
            "tracks": response.data or [],
        }

    def create_track(self, name: str, type: str = "audio") -> Dict[str, Any]:
        """
        Create a new track.

        Args:
            name: Track name
            type: Track type ('audio', 'midi', 'return')

        Returns:
            Dict with track creation result
        """
        valid_types = {"audio", "midi", "return"}
        if type not in valid_types:
            return {
                "success": False,
                "error": f"Invalid track type: {type}. Must be one of {valid_types}",
            }

        address_by_type = {
            "audio": OSC_ADDRESSES["track_create_audio"],
            "midi": OSC_ADDRESSES["track_create_midi"],
            "return": OSC_ADDRESSES["track_create_return"],
        }
        address = address_by_type[type]
        args = () if type == "return" else (-1,)

        response = self._bridge.send_message(address, *args, wait_for_response=False)

        return {
            "success": response.success,
            "track_id": None,
            "track_name": name,
            "track_type": type,
        }

    def delete_track(self, track_id: int) -> Dict[str, Any]:
        """
        Delete a track by ID.

        Args:
            track_id: Track identifier

        Returns:
            Dict with deletion result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["track_delete"],
            track_id,
            wait_for_response=False,
        )

        return {
            "success": response.success,
            "track_id": track_id,
        }

    def select_track(self, track_id: int) -> Dict[str, Any]:
        """
        Select a track for editing.

        Args:
            track_id: Track identifier

        Returns:
            Dict with selection result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["track_select"],
            track_id,
            wait_for_response=False,
        )

        return {
            "success": response.success,
            "track_id": track_id,
        }

    def set_track_arm(self, track_id: int, armed: bool) -> Dict[str, Any]:
        """
        Arm or disarm a track for recording.

        Args:
            track_id: Track identifier
            armed: True to arm, False to disarm

        Returns:
            Dict with arm state result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["track_arm"],
            track_id,
            1 if armed else 0,
            wait_for_response=False,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "armed": armed,
        }

    def set_track_mute(self, track_id: int, muted: bool) -> Dict[str, Any]:
        """
        Mute or unmute a track.

        Args:
            track_id: Track identifier
            muted: True to mute, False to unmute

        Returns:
            Dict with mute state result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["track_mute"],
            track_id,
            1 if muted else 0,
            wait_for_response=False,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "muted": muted,
        }

    def set_track_solo(self, track_id: int, soloed: bool) -> Dict[str, Any]:
        """
        Solo or unsolo a track.

        Args:
            track_id: Track identifier
            soloed: True to solo, False to unsolo

        Returns:
            Dict with solo state result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["track_solo"],
            track_id,
            1 if soloed else 0,
            wait_for_response=False,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "soloed": soloed,
        }

    def set_track_volume(self, track_id: int, volume: float) -> Dict[str, Any]:
        """
        Set track volume (0.0 to 1.0).

        Args:
            track_id: Track identifier
            volume: Volume level (0.0-1.0)

        Returns:
            Dict with volume result
        """
        if not 0.0 <= volume <= 1.0:
            return {
                "success": False,
                "error": f"Volume must be between 0.0 and 1.0, got {volume}",
            }

        response = self._bridge.send_message(
            OSC_ADDRESSES["track_volume"],
            track_id,
            volume,
            wait_for_response=False,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "volume": volume,
        }

    def set_track_panning(self, track_id: int, panning: float) -> Dict[str, Any]:
        """
        Set track panning (-1.0 to 1.0).

        Args:
            track_id: Track identifier
            panning: Pan position (-1.0 = left, 0.0 = center, 1.0 = right)

        Returns:
            Dict with panning result
        """
        if not -1.0 <= panning <= 1.0:
            return {
                "success": False,
                "error": f"Panning must be between -1.0 and 1.0, got {panning}",
            }

        response = self._bridge.send_message(
            OSC_ADDRESSES["track_panning"],
            track_id,
            panning,
            wait_for_response=False,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "panning": panning,
        }

    def get_track_input_routes(self, track_id: int) -> Dict[str, Any]:
        """
        List input routing types available to a track.

        AbletonOSC returns the queried track id as the first param; this method
        strips it and returns only route display names.
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["track_input_routes"],
            track_id,
        )
        if not response.success:
            return {
                "success": False,
                "error": response.error,
                "track_id": track_id,
                "inputs": [],
            }

        params = response.data.get("params", []) if response.data else []
        inputs = list(params)
        if inputs and inputs[0] == track_id:
            inputs = inputs[1:]

        return {
            "success": True,
            "track_id": track_id,
            "inputs": inputs,
        }

    def route_midi_input(
        self,
        track_id: int,
        source: str,
        channel: Optional[str] = None,
        monitor: int = 0,
        arm: bool = True,
    ) -> Dict[str, Any]:
        """
        Configure a track to receive MIDI from a named Ableton input route.
        """
        routes = self.get_track_input_routes(track_id)
        if not routes["success"]:
            return routes

        available_inputs = routes["inputs"]
        source_match = next(
            (item for item in available_inputs if item.lower() == source.lower()),
            None,
        )
        if source_match is None:
            return {
                "success": False,
                "error": f"Input source not found: {source}",
                "track_id": track_id,
                "available_inputs": available_inputs,
            }

        route_response = self._bridge.send_message(
            OSC_ADDRESSES["track_input_type"],
            track_id,
            source_match,
            wait_for_response=False,
        )
        if not route_response.success:
            return {
                "success": False,
                "error": route_response.error,
                "track_id": track_id,
                "source": source_match,
            }

        if channel is not None:
            channel_response = self._bridge.send_message(
                OSC_ADDRESSES["track_input_channel"],
                track_id,
                channel,
                wait_for_response=False,
            )
            if not channel_response.success:
                return {
                    "success": False,
                    "error": channel_response.error,
                    "track_id": track_id,
                    "source": source_match,
                    "channel": channel,
                }

        monitor_response = self._bridge.send_message(
            OSC_ADDRESSES["track_monitor"],
            track_id,
            monitor,
            wait_for_response=False,
        )
        if not monitor_response.success:
            return {
                "success": False,
                "error": monitor_response.error,
                "track_id": track_id,
                "source": source_match,
                "channel": channel,
            }

        if arm:
            arm_response = self._bridge.send_message(
                OSC_ADDRESSES["track_arm"],
                track_id,
                1,
                wait_for_response=False,
            )
            if not arm_response.success:
                return {
                    "success": False,
                    "error": arm_response.error,
                    "track_id": track_id,
                    "source": source_match,
                    "channel": channel,
                    "monitor": monitor,
                }

        return {
            "success": True,
            "track_id": track_id,
            "source": source_match,
            "channel": channel,
            "monitor": monitor,
            "armed": arm,
        }

    # Clip Operations

    def launch_clip(self, track_id: int, clip_index: int) -> Dict[str, Any]:
        """
        Launch a clip.

        Args:
            track_id: Track identifier
            clip_index: Clip slot index

        Returns:
            Dict with launch result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["clip_launch"],
            track_id,
            clip_index,
            wait_for_response=False,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "clip_index": clip_index,
        }

    def stop_clip(self, track_id: int, clip_index: int) -> Dict[str, Any]:
        """
        Stop a clip.

        Args:
            track_id: Track identifier
            clip_index: Clip slot index

        Returns:
            Dict with stop result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["clip_stop"],
            track_id,
            clip_index,
            wait_for_response=False,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "clip_index": clip_index,
        }

    def create_midi_clip(
        self,
        track_id: int,
        clip_index: int,
        length: float,
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
        if length <= 0:
            return {
                "success": False,
                "error": f"Clip length must be positive, got {length}",
            }

        scene_count = self._bridge.send_message(OSC_ADDRESSES["scene_count"])
        if scene_count.success and scene_count.data and "params" in scene_count.data:
            current_scenes = int(scene_count.data["params"][0])
            for _ in range(current_scenes, clip_index + 1):
                self._bridge.send_message(
                    OSC_ADDRESSES["scene_create"],
                    -1,
                    wait_for_response=False,
                )

        response = self._bridge.send_message(
            OSC_ADDRESSES["clip_slot_create"],
            track_id,
            clip_index,
            length,
            wait_for_response=False,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "clip_index": clip_index,
            "length": length,
        }

    def add_midi_note(
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
        Add a MIDI note to an existing MIDI clip.

        Args:
            track_id: Track identifier
            clip_index: Clip slot index
            pitch: MIDI note number (0-127)
            start: Note start time in beats
            duration: Note duration in beats
            velocity: MIDI velocity (0-127)
            mute: Whether the note is muted

        Returns:
            Dict with note insertion result
        """
        if not 0 <= pitch <= 127:
            return {"success": False, "error": f"Pitch must be 0-127, got {pitch}"}
        if start < 0:
            return {"success": False, "error": f"Start must be non-negative, got {start}"}
        if duration <= 0:
            return {"success": False, "error": f"Duration must be positive, got {duration}"}
        if not 0 <= velocity <= 127:
            return {"success": False, "error": f"Velocity must be 0-127, got {velocity}"}

        response = self._bridge.send_message(
            OSC_ADDRESSES["clip_add_notes"],
            track_id,
            clip_index,
            pitch,
            start,
            duration,
            velocity,
            mute,
            wait_for_response=False,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "clip_index": clip_index,
            "pitch": pitch,
            "start": start,
            "duration": duration,
            "velocity": velocity,
            "mute": mute,
        }

    def get_clip_notes(self, track_id: int, clip_index: int) -> Dict[str, Any]:
        """
        Read MIDI notes from an existing clip.
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["clip_get_notes"],
            track_id,
            clip_index,
        )
        if not response.success:
            return {
                "success": False,
                "error": response.error,
                "track_id": track_id,
                "clip_index": clip_index,
                "notes": [],
                "note_count": 0,
            }

        if response.data and response.data.get("address") == "/live/error":
            params = response.data.get("params", [])
            return {
                "success": False,
                "error": params[0] if params else ErrorCode.ABLETON_ERROR.value,
                "track_id": track_id,
                "clip_index": clip_index,
                "notes": [],
                "note_count": 0,
            }

        params = response.data.get("params", []) if response.data else []
        if len(params) % 5 == 2:
            params = params[2:]
        if len(params) % 5 != 0:
            return {
                "success": False,
                "error": f"Unexpected note payload length: {len(params)}",
                "track_id": track_id,
                "clip_index": clip_index,
                "notes": [],
                "note_count": 0,
            }

        notes = []
        for offset in range(0, len(params), 5):
            pitch, start, duration, velocity, mute = params[offset:offset + 5]
            notes.append({
                "pitch": int(pitch),
                "start": float(start),
                "duration": float(duration),
                "velocity": int(velocity),
                "mute": bool(mute),
            })

        return {
            "success": True,
            "track_id": track_id,
            "clip_index": clip_index,
            "notes": notes,
            "note_count": len(notes),
        }

    def check_midi_input(self, track_id: int, clip_index: int) -> Dict[str, Any]:
        """Check whether a clip contains recorded MIDI notes."""
        result = self.get_clip_notes(track_id, clip_index)
        if not result["success"]:
            return result
        if result["note_count"] == 0:
            return {
                **result,
                "success": False,
                "error": f"No MIDI notes recorded in clip {clip_index} on track {track_id}",
            }
        return result

    def get_available_instruments(self) -> Dict[str, Any]:
        """List instruments exposed by the AbletonOSC browser extension."""
        response = self._bridge.send_message(OSC_ADDRESSES["browser_instruments"])
        if not response.success:
            return {
                "success": False,
                "error": response.error,
                "instruments": [],
            }
        if response.data and response.data.get("address") == "/live/error":
            params = response.data.get("params", [])
            return {
                "success": False,
                "error": params[0] if params else ErrorCode.ABLETON_ERROR.value,
                "instruments": [],
            }

        params = response.data.get("params", []) if response.data else []
        return {
            "success": True,
            "instruments": list(params),
        }

    def load_instrument(self, track_id: int, instrument: str) -> Dict[str, Any]:
        """Load an instrument onto a MIDI track through the browser extension."""
        response = self._bridge.send_message(
            OSC_ADDRESSES["browser_load_instrument"],
            track_id,
            instrument,
        )
        if not response.success:
            return {
                "success": False,
                "error": response.error,
                "track_id": track_id,
                "instrument": instrument,
            }
        if response.data and response.data.get("address") == "/live/error":
            params = response.data.get("params", [])
            return {
                "success": False,
                "error": params[0] if params else ErrorCode.ABLETON_ERROR.value,
                "track_id": track_id,
                "instrument": instrument,
            }

        params = response.data.get("params", []) if response.data else []
        loaded_track = int(params[0]) if params else track_id
        loaded_instrument = str(params[1]) if len(params) > 1 else instrument
        return {
            "success": True,
            "track_id": loaded_track,
            "instrument": loaded_instrument,
        }

    def import_audio_clip(
        self,
        track_id: int,
        clip_index: int,
        file_path: str,
    ) -> Dict[str, Any]:
        """Import an audio file into an audio clip slot."""
        response = self._bridge.send_message(
            OSC_ADDRESSES["clip_slot_create_audio"],
            track_id,
            clip_index,
            file_path,
        )
        if not response.success:
            return {
                "success": False,
                "error": response.error,
                "track_id": track_id,
                "clip_index": clip_index,
                "file_path": file_path,
            }
        if response.data and response.data.get("address") == "/live/error":
            params = response.data.get("params", [])
            return {
                "success": False,
                "error": params[0] if params else ErrorCode.ABLETON_ERROR.value,
                "track_id": track_id,
                "clip_index": clip_index,
                "file_path": file_path,
            }

        params = response.data.get("params", []) if response.data else []
        imported_track = int(params[0]) if params else track_id
        imported_clip = int(params[1]) if len(params) > 1 else clip_index
        imported_path = str(params[2]) if len(params) > 2 else file_path
        return {
            "success": True,
            "track_id": imported_track,
            "clip_index": imported_clip,
            "file_path": imported_path,
        }

    def record_clip(self, track_id: int, clip_index: int, enable: bool) -> Dict[str, Any]:
        """
        Start or stop clip recording.

        Args:
            track_id: Track identifier
            clip_index: Clip slot index
            enable: True to start recording, False to stop

        Returns:
            Dict with recording result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["clip_record"],
            track_id,
            clip_index,
            1 if enable else 0,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "clip_index": clip_index,
            "recording": enable,
        }

    # Scene Operations

    def launch_scene(self, scene_index: int) -> Dict[str, Any]:
        """
        Launch a scene.

        Args:
            scene_index: Scene index

        Returns:
            Dict with launch result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["scene_launch"],
            scene_index,
        )

        return {
            "success": response.success,
            "scene_index": scene_index,
        }

    def stop_scene(self, scene_index: int) -> Dict[str, Any]:
        """
        Stop a scene.

        Args:
            scene_index: Scene index

        Returns:
            Dict with stop result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["scene_stop"],
            scene_index,
        )

        return {
            "success": response.success,
            "scene_index": scene_index,
        }

    # Device Operations

    def get_devices(self, track_id: int) -> Dict[str, Any]:
        """
        Get all devices on a track.

        Args:
            track_id: Track identifier

        Returns:
            Dict with 'devices' key containing list of device dicts
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["device_list"],
            track_id,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "devices": response.data.get("devices", []) if response.success else [],
        }

    def select_device(self, track_id: int, device_id: int) -> Dict[str, Any]:
        """
        Select a device for editing.

        Args:
            track_id: Track identifier
            device_id: Device identifier

        Returns:
            Dict with selection result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["device_select"],
            track_id,
            device_id,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "device_id": device_id,
        }

    def get_device_param(self, device_id: int, param_name: str) -> Dict[str, Any]:
        """
        Get a device parameter value.

        Args:
            device_id: Device identifier
            param_name: Parameter name

        Returns:
            Dict with parameter value
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["device_param_get"],
            device_id,
            param_name,
        )

        return {
            "success": response.success,
            "device_id": device_id,
            "param_name": param_name,
            "value": response.data.get("value") if response.success else None,
        }

    def set_device_param(self, device_id: int, param_name: str, value: float) -> Dict[str, Any]:
        """
        Set a device parameter value.

        Args:
            device_id: Device identifier
            param_name: Parameter name
            value: Parameter value

        Returns:
            Dict with parameter value result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["device_param_set"],
            device_id,
            param_name,
            value,
        )

        return {
            "success": response.success,
            "device_id": device_id,
            "param_name": param_name,
            "value": value,
        }

    def set_device_on_off(self, device_id: int, on: bool) -> Dict[str, Any]:
        """
        Toggle device on/off.

        Args:
            device_id: Device identifier
            on: True to turn on, False to turn off

        Returns:
            Dict with on/off result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["device_on_off"],
            device_id,
            1 if on else 0,
        )

        return {
            "success": response.success,
            "device_id": device_id,
            "on": on,
        }

    # MIDI Effect Operations

    def list_midi_effects(self, track_id: int) -> Dict[str, Any]:
        """
        List MIDI effects on a track.

        Args:
            track_id: Track identifier

        Returns:
            Dict with 'midi_effects' key containing list of MIDI effect dicts
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["midi_effect_list"],
            track_id,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "midi_effects": response.data.get("midi_effects", []) if response.success else [],
        }

    def set_midi_effect(self, track_id: int, effect_type: str, enabled: bool, **params) -> Dict[str, Any]:
        """
        Configure a MIDI effect.

        Args:
            track_id: Track identifier
            effect_type: MIDI effect type ('arp', 'chord', 'scale', etc.)
            enabled: True to enable, False to bypass
            **params: Effect-specific parameters

        Returns:
            Dict with effect configuration result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["midi_effect_set"],
            track_id,
            effect_type,
            1 if enabled else 0,
            *sum([[k, v] for k, v in params.items()], [])
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "effect_type": effect_type,
            "enabled": enabled,
            "parameters": params,
        }

    def set_midi_effect_bypass(self, track_id: int, effect_type: str, bypassed: bool) -> Dict[str, Any]:
        """
        Bypass or enable a MIDI effect.

        Args:
            track_id: Track identifier
            effect_type: MIDI effect type
            bypassed: True to bypass, False to enable

        Returns:
            Dict with bypass state result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["midi_effect_bypass"],
            track_id,
            effect_type,
            1 if bypassed else 0,
        )

        return {
            "success": response.success,
            "track_id": track_id,
            "effect_type": effect_type,
            "bypassed": bypassed,
        }

    # Preset Operations

    def save_preset(self, name: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Save current state as a preset.

        Args:
            name: Preset name
            category: Optional preset category

        Returns:
            Dict with save result
        """
        args = [name]
        if category:
            args.append(category)

        response = self._bridge.send_message(
            OSC_ADDRESSES["preset_save"],
            *args
        )

        return {
            "success": response.success,
            "preset_name": name,
            "category": category,
        }

    def load_preset(self, preset_id: str) -> Dict[str, Any]:
        """
        Load a preset by ID.

        Args:
            preset_id: Preset identifier

        Returns:
            Dict with load result
        """
        response = self._bridge.send_message(
            OSC_ADDRESSES["preset_load"],
            preset_id,
        )

        return {
            "success": response.success,
            "preset_id": preset_id,
        }

    def list_presets(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        List available presets.

        Args:
            category: Optional filter by category

        Returns:
            Dict with 'presets' key containing list of preset dicts
        """
        args = []
        if category:
            args.append(category)

        response = self._bridge.send_message(
            OSC_ADDRESSES["preset_list"],
            *args
        )

        return {
            "success": response.success,
            "presets": response.data.get("presets", []) if response.success else [],
        }

    # Transport Operations

    def transport_play(self) -> Dict[str, Any]:
        """Start playback."""
        response = self._bridge.send_message(OSC_ADDRESSES["transport_play"], wait_for_response=False)
        return {"success": response.success, "playing": True}

    def transport_stop(self) -> Dict[str, Any]:
        """Stop playback."""
        response = self._bridge.send_message(OSC_ADDRESSES["transport_stop"], wait_for_response=False)
        return {"success": response.success, "playing": False}

    def transport_record(self, enable: bool) -> Dict[str, Any]:
        """
        Start or stop recording.

        Args:
            enable: True to start recording, False to stop

        Returns:
            Dict with recording state
        """
        response = self._bridge.send_message(OSC_ADDRESSES["transport_record"], wait_for_response=False)
        return {
            "success": response.success,
            "recording": enable,
        }

    def __repr__(self) -> str:
        return f"AbletonAPI(host={self._bridge.host}, port={self._bridge.send_port})"
