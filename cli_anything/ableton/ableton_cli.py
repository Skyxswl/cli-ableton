"""Main CLI entry point for Ableton CLI harness."""

import json
import logging
from typing import Any, Dict, Optional

import click

from .ableton_api import AbletonAPI
from .track_operations import TrackOperations
from .midi_processor import MIDIProcessor
from .clip_control import ClipControl
from .device_control import DeviceControl
from .preset_manager import PresetManager
from .constants import DEFAULT_HOST, DEFAULT_LISTEN_PORT, DEFAULT_RESPONSE_PORT, OutputFormat


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def output_result(result, json_output: bool) -> None:
    """
    Output result in specified format.

    Args:
        result: Result dictionary or OSCResponse
        json_output: If True, output JSON; otherwise human-readable
    """
    # Handle OSCResponse object
    if hasattr(result, 'success'):
        result = {
            "success": result.success,
            "data": result.data,
            "error": result.error,
        }

    if json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        if result.get("success"):
            click.echo("OK")
        else:
            error_msg = result.get("error", "Unknown error")
            click.echo(f"Error: {error_msg}", err=True)

    if not result.get("success"):
        raise click.exceptions.Exit(1)


def output_list(items: list, json_output: bool, item_name: str = "item") -> None:
    """
    Output a list of items.

    Args:
        items: List of items
        json_output: If True, output JSON
        item_name: Name of item type for human output
    """
    if json_output:
        click.echo(json.dumps(items, indent=2))
    else:
        if items:
            for item in items:
                click.echo(f"  - {item}")
        else:
            click.echo(f"No {item_name}s found")


@click.group()
@click.option("--host", default=DEFAULT_HOST, help="AbletonOSC server host")
@click.option("--port", default=DEFAULT_LISTEN_PORT, help="AbletonOSC server port")
@click.option("--response-port", default=DEFAULT_RESPONSE_PORT, help="AbletonOSC response port")
@click.option("--json", "json_output", is_flag=True, help="Output JSON format")
@click.pass_context
def cli(ctx: click.Context, host: str, port: int, response_port: int, json_output: bool) -> None:
    """
    Ableton CLI - Control Ableton Live from command line.

    Connects to AbletonOSC server running in Ableton Live to provide
    CLI control over tracks, clips, devices, MIDI effects, and presets.
    """
    ctx.ensure_object(dict)
    ctx.obj["host"] = host
    ctx.obj["port"] = port
    ctx.obj["response_port"] = response_port
    ctx.obj["json_output"] = json_output

    # Create API instance
    api = AbletonAPI(host=host, port=port, response_port=response_port)
    ctx.obj["api"] = api

    # Create operation instances
    ctx.obj["track_ops"] = TrackOperations(api)
    ctx.obj["midi_processor"] = MIDIProcessor(api)
    ctx.obj["clip_control"] = ClipControl(api)
    ctx.obj["device_control"] = DeviceControl(api)
    ctx.obj["preset_manager"] = PresetManager(api)


# Connection Commands

@cli.command()
@click.pass_context
def connect(ctx: click.Context) -> None:
    """Connect to Ableton Live."""
    api = ctx.obj["api"]
    result = api.connect()
    output_result(result, ctx.obj["json_output"])


@cli.command()
@click.pass_context
def disconnect(ctx: click.Context) -> None:
    """Disconnect from Ableton Live."""
    api = ctx.obj["api"]
    api.disconnect()
    result = {"success": True, "message": "Disconnected"}
    output_result(result, ctx.obj["json_output"])


@cli.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Check connection status."""
    api = ctx.obj["api"]
    result = api.health_check()
    # Convert OSCResponse to dict for JSON serialization
    result_dict = {
        "success": result.success,
        "data": result.data,
        "error": result.error,
    }
    if ctx.obj["json_output"]:
        click.echo(json.dumps(result_dict, indent=2))
    else:
        if result.success:
            click.echo("Connected to Ableton Live")
        else:
            click.echo("Not connected", err=True)

    if not result.success:
        raise click.exceptions.Exit(1)


# Track Commands

@cli.group()
def track() -> None:
    """Track operations."""
    pass


@track.command(name="list")
@click.option("--type", "track_type", help="Filter by type (audio, midi, return)")
@click.pass_context
def track_list(ctx: click.Context, track_type: Optional[str]) -> None:
    """List all tracks."""
    ops = ctx.obj["track_ops"]
    result = ops.list(filter_type=track_type)
    output_result(result, ctx.obj["json_output"])


@track.command(name="create")
@click.option("--name", required=True, help="Track name")
@click.option("--type", "track_type", default="audio", help="Track type (audio, midi)")
@click.pass_context
def track_create(ctx: click.Context, name: str, track_type: str) -> None:
    """Create a new track."""
    ops = ctx.obj["track_ops"]
    result = ops.create(name=name, track_type=track_type)
    output_result(result, ctx.obj["json_output"])


@track.command(name="delete")
@click.argument("track_id", type=int)
@click.pass_context
def track_delete(ctx: click.Context, track_id: int) -> None:
    """Delete a track by ID."""
    ops = ctx.obj["track_ops"]
    result = ops.delete(track_id)
    output_result(result, ctx.obj["json_output"])


@track.command(name="select")
@click.argument("track_id", type=int)
@click.pass_context
def track_select(ctx: click.Context, track_id: int) -> None:
    """Select a track for editing."""
    ops = ctx.obj["track_ops"]
    result = ops.select(track_id)
    output_result(result, ctx.obj["json_output"])


@track.command(name="arm")
@click.argument("track_id", type=int)
@click.option("--on/--off", default=True, help="Arm state")
@click.pass_context
def track_arm(ctx: click.Context, track_id: int, on: bool) -> None:
    """Arm or disarm a track."""
    ops = ctx.obj["track_ops"]
    result = ops.arm(track_id, armed=on)
    output_result(result, ctx.obj["json_output"])


@track.command(name="mute")
@click.argument("track_id", type=int)
@click.option("--on/--off", default=True, help="Mute state")
@click.pass_context
def track_mute(ctx: click.Context, track_id: int, on: bool) -> None:
    """Mute or unmute a track."""
    ops = ctx.obj["track_ops"]
    result = ops.mute(track_id, muted=on)
    output_result(result, ctx.obj["json_output"])


@track.command(name="solo")
@click.argument("track_id", type=int)
@click.option("--on/--off", default=True, help="Solo state")
@click.pass_context
def track_solo(ctx: click.Context, track_id: int, on: bool) -> None:
    """Solo or unsolo a track."""
    ops = ctx.obj["track_ops"]
    result = ops.solo(track_id, soloed=on)
    output_result(result, ctx.obj["json_output"])


@track.command(name="volume")
@click.argument("track_id", type=int)
@click.argument("value", type=float)
@click.pass_context
def track_volume(ctx: click.Context, track_id: int, value: float) -> None:
    """Set track volume (0.0 to 1.0)."""
    ops = ctx.obj["track_ops"]
    result = ops.volume(track_id, value)
    output_result(result, ctx.obj["json_output"])


@track.command(name="panning")
@click.argument("track_id", type=int)
@click.argument("value", type=float)
@click.pass_context
def track_panning(ctx: click.Context, track_id: int, value: float) -> None:
    """Set track panning (-1.0 to 1.0)."""
    ops = ctx.obj["track_ops"]
    result = ops.panning(track_id, value)
    output_result(result, ctx.obj["json_output"])


# Clip Commands

@cli.group()
def clip() -> None:
    """Clip control operations."""
    pass


@clip.command(name="launch")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@click.pass_context
def clip_launch(ctx: click.Context, track_id: int, clip_index: int) -> None:
    """Launch a clip."""
    ctrl = ctx.obj["clip_control"]
    result = ctrl.launch(track_id, clip_index)
    output_result(result, ctx.obj["json_output"])


@clip.command(name="stop")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@click.pass_context
def clip_stop(ctx: click.Context, track_id: int, clip_index: int) -> None:
    """Stop a clip."""
    ctrl = ctx.obj["clip_control"]
    result = ctrl.stop(track_id, clip_index)
    output_result(result, ctx.obj["json_output"])


@clip.command(name="create")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@click.option("--length", type=float, default=4.0, help="Clip length in beats")
@click.pass_context
def clip_create(ctx: click.Context, track_id: int, clip_index: int, length: float) -> None:
    """Create a MIDI clip."""
    ctrl = ctx.obj["clip_control"]
    result = ctrl.create(track_id, clip_index, length)
    output_result(result, ctx.obj["json_output"])


@clip.command(name="record")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@click.option("--on/--off", default=True, help="Recording state")
@click.pass_context
def clip_record(ctx: click.Context, track_id: int, clip_index: int, on: bool) -> None:
    """Start or stop clip recording."""
    ctrl = ctx.obj["clip_control"]
    result = ctrl.record(track_id, clip_index, enable=on)
    output_result(result, ctx.obj["json_output"])


@clip.command(name="stop-all")
@click.pass_context
def clip_stop_all(ctx: click.Context) -> None:
    """Stop all playing clips."""
    ctrl = ctx.obj["clip_control"]
    result = ctrl.stop_all()
    output_result(result, ctx.obj["json_output"])


# Scene Commands

@cli.group()
def scene() -> None:
    """Scene operations."""
    pass


@scene.command(name="launch")
@click.argument("scene_index", type=int)
@click.pass_context
def scene_launch(ctx: click.Context, scene_index: int) -> None:
    """Launch a scene."""
    ctrl = ctx.obj["clip_control"]
    result = ctrl.launch_scene(scene_index)
    output_result(result, ctx.obj["json_output"])


@scene.command(name="stop")
@click.argument("scene_index", type=int)
@click.pass_context
def scene_stop(ctx: click.Context, scene_index: int) -> None:
    """Stop a scene."""
    ctrl = ctx.obj["clip_control"]
    result = ctrl.stop_scene(scene_index)
    output_result(result, ctx.obj["json_output"])


# MIDI Effect Commands

@cli.group()
def midi() -> None:
    """MIDI effect operations."""
    pass


@midi.command(name="list")
@click.argument("track_id", type=int)
@click.pass_context
def midi_list(ctx: click.Context, track_id: int) -> None:
    """List MIDI effects on a track."""
    proc = ctx.obj["midi_processor"]
    result = proc.list_effects(track_id)
    output_result(result, ctx.obj["json_output"])


@midi.command(name="note")
@click.argument("track_id", type=int)
@click.argument("clip_index", type=int)
@click.option("--pitch", type=int, required=True, help="MIDI pitch (0-127)")
@click.option("--start", type=float, default=0.0, help="Note start time in beats")
@click.option("--duration", type=float, default=0.25, help="Note duration in beats")
@click.option("--velocity", type=int, default=100, help="MIDI velocity (0-127)")
@click.option("--mute", is_flag=True, help="Add the note muted")
@click.pass_context
def midi_note(ctx: click.Context, track_id: int, clip_index: int, pitch: int,
              start: float, duration: float, velocity: int, mute: bool) -> None:
    """Add a MIDI note to a clip."""
    ctrl = ctx.obj["clip_control"]
    result = ctrl.add_note(track_id, clip_index, pitch, start, duration, velocity, mute)
    output_result(result, ctx.obj["json_output"])


@midi.command(name="arp")
@click.argument("track_id", type=int)
@click.option("--enable/--disable", default=True, help="Effect enabled state")
@click.option("--rate", default="1/4", help="Arpeggiator rate")
@click.option("--gate", type=float, default=1.0, help="Gate time (0.0-1.0)")
@click.option("--direction", default="up", help="Direction (up, down, updown, random)")
@click.option("--octaves", type=int, default=2, help="Number of octaves")
@click.pass_context
def midi_arp(ctx: click.Context, track_id: int, enable: bool, rate: str,
             gate: float, direction: str, octaves: int) -> None:
    """Configure arpeggiator effect."""
    proc = ctx.obj["midi_processor"]
    result = proc.arpeggiator(track_id, enabled=enable, rate=rate, gate=gate,
                              direction=direction, octaves=octaves)
    output_result(result, ctx.obj["json_output"])


@midi.command(name="chord")
@click.argument("track_id", type=int)
@click.option("--enable/--disable", default=True, help="Effect enabled state")
@click.option("--chord", default="maj", help="Chord type")
@click.option("--strum", type=float, default=0.0, help="Strum time")
@click.option("--spread", type=float, default=0.5, help="Stereo spread")
@click.option("--voicing", default="close", help="Voicing type")
@click.pass_context
def midi_chord(ctx: click.Context, track_id: int, enable: bool, chord: str,
               strum: float, spread: float, voicing: str) -> None:
    """Configure chord effect."""
    proc = ctx.obj["midi_processor"]
    result = proc.chord(track_id, enabled=enable, chord=chord, strum=strum,
                        spread=spread, voicing=voicing)
    output_result(result, ctx.obj["json_output"])


@midi.command(name="scale")
@click.argument("track_id", type=int)
@click.option("--enable/--disable", default=True, help="Effect enabled state")
@click.option("--scale", default="chromatic", help="Scale type")
@click.option("--root", type=int, default=0, help="Root note (0-11)")
@click.option("--octave", type=int, default=0, help="Octave offset")
@click.pass_context
def midi_scale(ctx: click.Context, track_id: int, enable: bool, scale: str,
               root: int, octave: int) -> None:
    """Configure scale effect."""
    proc = ctx.obj["midi_processor"]
    result = proc.scale(track_id, enabled=enable, scale=scale, root=root,
                        octave=octave)
    output_result(result, ctx.obj["json_output"])


@midi.command(name="velocity")
@click.argument("track_id", type=int)
@click.option("--enable/--disable", default=True, help="Effect enabled state")
@click.option("--amount", type=float, default=0.0, help="Velocity offset")
@click.option("--curve", type=float, default=0.0, help="Velocity curve")
@click.pass_context
def midi_velocity(ctx: click.Context, track_id: int, enable: bool,
                  amount: float, curve: float) -> None:
    """Configure velocity effect."""
    proc = ctx.obj["midi_processor"]
    result = proc.velocity(track_id, enabled=enable, amount=amount, curve=curve)
    output_result(result, ctx.obj["json_output"])


@midi.command(name="pitch")
@click.argument("track_id", type=int)
@click.option("--enable/--disable", default=True, help="Effect enabled state")
@click.option("--amount", type=float, default=0.0, help="Pitch shift in semitones")
@click.option("--auto", is_flag=True, help="Auto pitch correction")
@click.pass_context
def midi_pitch(ctx: click.Context, track_id: int, enable: bool,
               amount: float, auto: bool) -> None:
    """Configure pitch effect."""
    proc = ctx.obj["midi_processor"]
    result = proc.pitch(track_id, enabled=enable, amount=amount, auto=auto)
    output_result(result, ctx.obj["json_output"])


# Device Commands

@cli.group()
def device() -> None:
    """Device control operations."""
    pass


@device.command(name="list")
@click.argument("track_id", type=int)
@click.pass_context
def device_list(ctx: click.Context, track_id: int) -> None:
    """List devices on a track."""
    ctrl = ctx.obj["device_control"]
    result = ctrl.list(track_id)
    output_result(result, ctx.obj["json_output"])


@device.command(name="select")
@click.argument("track_id", type=int)
@click.argument("device_id", type=int)
@click.pass_context
def device_select(ctx: click.Context, track_id: int, device_id: int) -> None:
    """Select a device for editing."""
    ctrl = ctx.obj["device_control"]
    result = ctrl.select(track_id, device_id)
    output_result(result, ctx.obj["json_output"])


@device.command(name="get-param")
@click.argument("device_id", type=int)
@click.argument("param_name", type=str)
@click.pass_context
def device_get_param(ctx: click.Context, device_id: int, param_name: str) -> None:
    """Get a device parameter value."""
    ctrl = ctx.obj["device_control"]
    result = ctrl.get_param(device_id, param_name)
    output_result(result, ctx.obj["json_output"])


@device.command(name="set-param")
@click.argument("device_id", type=int)
@click.argument("param_name", type=str)
@click.argument("value", type=float)
@click.pass_context
def device_set_param(ctx: click.Context, device_id: int, param_name: str, value: float) -> None:
    """Set a device parameter value."""
    ctrl = ctx.obj["device_control"]
    result = ctrl.set_param(device_id, param_name, value)
    output_result(result, ctx.obj["json_output"])


@device.command(name="on")
@click.argument("device_id", type=int)
@click.pass_context
def device_on(ctx: click.Context, device_id: int) -> None:
    """Turn device on."""
    ctrl = ctx.obj["device_control"]
    result = ctrl.toggle(device_id, on=True)
    output_result(result, ctx.obj["json_output"])


@device.command(name="off")
@click.argument("device_id", type=int)
@click.pass_context
def device_off(ctx: click.Context, device_id: int) -> None:
    """Turn device off."""
    ctrl = ctx.obj["device_control"]
    result = ctrl.toggle(device_id, on=False)
    output_result(result, ctx.obj["json_output"])


# Preset Commands

@cli.group()
def preset() -> None:
    """Preset management operations."""
    pass


@preset.command(name="save")
@click.argument("name", type=str)
@click.option("--category", help="Preset category")
@click.pass_context
def preset_save(ctx: click.Context, name: str, category: Optional[str]) -> None:
    """Save current state as a preset."""
    mgr = ctx.obj["preset_manager"]
    result = mgr.save(name, category)
    output_result(result, ctx.obj["json_output"])


@preset.command(name="load")
@click.argument("preset_id", type=str)
@click.pass_context
def preset_load(ctx: click.Context, preset_id: str) -> None:
    """Load a preset by ID."""
    mgr = ctx.obj["preset_manager"]
    result = mgr.load(preset_id)
    output_result(result, ctx.obj["json_output"])


@preset.command(name="list")
@click.option("--category", help="Filter by category")
@click.pass_context
def preset_list(ctx: click.Context, category: Optional[str]) -> None:
    """List all presets."""
    mgr = ctx.obj["preset_manager"]
    result = mgr.list(category)
    output_result(result, ctx.obj["json_output"])


@preset.command(name="current")
@click.pass_context
def preset_current(ctx: click.Context) -> None:
    """Get current preset info."""
    mgr = ctx.obj["preset_manager"]
    result = mgr.current()
    output_result(result, ctx.obj["json_output"])


# Transport Commands

@cli.group()
def transport() -> None:
    """Transport control operations."""
    pass


@transport.command(name="play")
@click.pass_context
def transport_play(ctx: click.Context) -> None:
    """Start playback."""
    api = ctx.obj["api"]
    result = api.transport_play()
    output_result(result, ctx.obj["json_output"])


@transport.command(name="stop")
@click.pass_context
def transport_stop(ctx: click.Context) -> None:
    """Stop playback."""
    api = ctx.obj["api"]
    result = api.transport_stop()
    output_result(result, ctx.obj["json_output"])


@transport.command(name="record")
@click.option("--on/--off", default=True, help="Recording state")
@click.pass_context
def transport_record(ctx: click.Context, on: bool) -> None:
    """Start or stop recording."""
    api = ctx.obj["api"]
    result = api.transport_record(on)
    output_result(result, ctx.obj["json_output"])


if __name__ == "__main__":
    cli()
