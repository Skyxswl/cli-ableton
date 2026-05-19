"""Shared constants for Ableton CLI harness."""

from types import MappingProxyType
from enum import Enum

# Create immutable dict helper
def frozen_dict(d):
    return MappingProxyType(d)

# OSC Address prefixes
OSC_PREFIX = "/ableton"
TRACK_PREFIX = f"{OSC_PREFIX}/track"
CLIP_PREFIX = f"{OSC_PREFIX}/clip"
DEVICE_PREFIX = f"{OSC_PREFIX}/device"
MIDI_PREFIX = f"{OSC_PREFIX}/midi"
PRESET_PREFIX = f"{OSC_PREFIX}/preset"
SCENE_PREFIX = f"{OSC_PREFIX}/scene"

# Default connection settings
DEFAULT_HOST = "127.0.0.1"
DEFAULT_OSC_PORT = 11000
DEFAULT_RESPONSE_PORT = 11001
DEFAULT_LISTEN_PORT = DEFAULT_OSC_PORT
DEFAULT_TIMEOUT = 5.0

# MIDI effect types
class MIDIEffectType(str, Enum):
    ARPEGGIATOR = "arp"
    CHORD = "chord"
    SCALE = "scale"
    NOTE = "note"
    VELOCITY = "velocity"
    RANDOM = "random"
    PITCH = "pitch"
    ROTATE = "rotate"
    FLAM = "flam"

# MIDI effect parameters
MIDI_PARAMS = frozen_dict({
    "arp": ["rate", "gate", "direction", "octaves", "repeat"],
    "chord": ["chord", "strum", "spread", "voicing"],
    "scale": ["scale", "root", "octave", "wrap"],
    "note": ["length", "velocity", "position", "repeat"],
    "velocity": ["amount", "curve", "random"],
    "random": ["probability", "note_length", "velocity"],
    "pitch": ["amount", "auto", "range"],
    "rotate": ["amount", "step", "fade"],
    "flam": ["amount", "timing", "velocity"],
})

# Ableton OSC address mappings
OSC_ADDRESSES = frozen_dict({
    # Track operations
    "track_list": "/live/song/get/track_names",
    "track_create_audio": "/live/song/create_audio_track",
    "track_create_midi": "/live/song/create_midi_track",
    "track_create_return": "/live/song/create_return_track",
    "track_delete": "/live/song/delete_track",
    "track_select": "/live/toggle-brothers/track/select",
    "track_arm": "/live/track/set/arm",
    "track_mute": "/live/track/set/mute",
    "track_solo": "/live/track/set/solo",
    "track_volume": "/live/track/set/volume",
    "track_panning": "/live/track/set/panning",
    "track_input_routes": "/live/track/get/available_input_routing_types",
    "track_input_channels": "/live/track/get/available_input_routing_channels",
    "track_input_type": "/live/track/set/input_routing_type",
    "track_input_channel": "/live/track/set/input_routing_channel",
    "track_monitor": "/live/track/set/current_monitoring_state",

    # Clip operations
    "clip_launch": "/live/clip/fire",
    "clip_stop": "/live/clip/stop",
    "clip_record": "/live/toggle-brothers/clip/record",
    "clip_select": "/live/toggle-brothers/clip/select",
    "clip_slot_create": "/live/clip_slot/create_clip",
    "clip_slot_create_audio": "/live/clip_slot/create_audio_clip",
    "clip_add_notes": "/live/clip/add/notes",
    "clip_get_notes": "/live/clip/get/notes",

    # Scene operations
    "scene_count": "/live/song/get/num_scenes",
    "scene_create": "/live/song/create_scene",
    "scene_launch": "/live/toggle-brothers/scene/launch",
    "scene_stop": "/live/toggle-brothers/scene/stop",

    # Device operations
    "browser_instruments": "/live/browser/get/instruments",
    "browser_load_instrument": "/live/browser/load/instrument",
    "device_list": "/live/toggle-brothers/device/list",
    "device_select": "/live/toggle-brothers/device/select",
    "device_param_get": "/live/toggle-brothers/device/param/get",
    "device_param_set": "/live/toggle-brothers/device/param/set",
    "device_on_off": "/live/toggle-brothers/device/on_off",

    # MIDI effect operations
    "midi_effect_list": "/live/toggle-brothers/midi/effect/list",
    "midi_effect_set": "/live/toggle-brothers/midi/effect/set",
    "midi_effect_bypass": "/live/toggle-brothers/midi/effect/bypass",

    # Preset operations
    "preset_save": "/live/toggle-brothers/preset/save",
    "preset_load": "/live/toggle-brothers/preset/load",
    "preset_list": "/live/toggle-brothers/preset/list",

    # Transport
    "transport_play": "/live/song/start_playing",
    "transport_stop": "/live/song/stop_playing",
    "transport_record": "/live/song/trigger_session_record",
})

# Error codes
class ErrorCode(str, Enum):
    CONNECTION_FAILED = "CONNECTION_FAILED"
    TIMEOUT = "TIMEOUT"
    INVALID_TRACK = "INVALID_TRACK"
    INVALID_CLIP = "INVALID_CLIP"
    INVALID_DEVICE = "INVALID_DEVICE"
    INVALID_PARAM = "INVALID_PARAM"
    MIDI_EFFECT_NOT_FOUND = "MIDI_EFFECT_NOT_FOUND"
    PRESET_NOT_FOUND = "PRESET_NOT_FOUND"
    ABLETON_ERROR = "ABLETON_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

# Supported Ableton versions
SUPPORTED_VERSIONS = ["11", "12"]

# CLI output formats
class OutputFormat(str, Enum):
    JSON = "json"
    HUMAN = "human"
