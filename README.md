# cli-ableton

Control Ableton Live from the command line through
[AbletonOSC](https://github.com/ideoforms/AbletonOSC).

This project is a small Python CLI for agent-driven Ableton workflows. It can
connect to Ableton Live, inspect tracks, control transport, create MIDI clips,
write MIDI notes, and launch/stop clips.

## Requirements

- Python 3.10+
- Ableton Live 11 or 12
- [ideoforms/AbletonOSC](https://github.com/ideoforms/AbletonOSC) installed as a
  Live control surface

## Install

```bash
pip install -e .
```

This installs two command names:

```bash
cli-ableton --help
ableton --help
```

## AbletonOSC Setup

Install AbletonOSC following its upstream instructions. On macOS the recommended
location is:

```text
~/Music/Ableton/User Library/Remote Scripts/AbletonOSC
```

Restart Ableton Live, then select `AbletonOSC` from:

```text
Settings > Link, Tempo & MIDI > Control Surface
```

AbletonOSC defaults to:

- OSC listen port: `11000`
- OSC response port: `11001`

Those are the CLI defaults.

## Quick Start

```bash
cli-ableton --json status
cli-ableton --json track list
cli-ableton transport play
cli-ableton transport stop
```

Create a MIDI clip, add a note, and launch it:

```bash
cli-ableton clip create 0 0 --length 4
cli-ableton midi note 0 0 --pitch 60 --start 0 --duration 0.5 --velocity 100
cli-ableton clip launch 0 0
cli-ableton clip stop 0 0
```

MIDI does not produce sound by itself. Put an instrument, Drum Rack, Simpler,
Sampler, or plugin on the target MIDI track before expecting audible output.

## Test An External MIDI Input

First check which MIDI inputs Ableton exposes for the target track:

```bash
cli-ableton --json input routes 0
```

If your controller appears as `Touch Me`, route track 0 to it, enable monitor,
and arm the track:

```bash
cli-ableton --json input route "Touch Me" 0 --monitor 0 --arm
```

`--monitor 0` forces Ableton's monitor mode to `In`, which is the right setting
for real-time playing:

```bash
cli-ableton --json input route "Touch Me" 0 --monitor 0 --arm
```

Record or capture MIDI into a clip in Ableton, then check whether notes were
recorded:

```bash
cli-ableton --json input check 0 0
```

If `Touch Me` does not appear in `input routes`, enable it in Ableton:

```text
Settings > Link, Tempo & MIDI > MIDI Ports > Touch Me > Track: On
```

## Load An Instrument From The Terminal

The `instrument` commands require the browser extension described in
`ABLETON.md`.

List loadable instruments:

```bash
cli-ableton --json instrument list
```

Load `Operator` onto track 0 and play the recorded clip:

```bash
cli-ableton --json instrument load 0 Operator
cli-ableton clip launch 0 0
```

## Commands

- `status` - Check AbletonOSC connectivity
- `track list` - List tracks
- `track create` - Create audio, MIDI, or return tracks
- `clip create` - Create a MIDI clip in a clip slot
- `clip launch` / `clip stop` - Trigger or stop clips
- `midi note` - Add a MIDI note to an existing clip
- `input routes` - List input sources available to a track
- `input route` - Route a track to an external MIDI input
- `input check` - Check whether a clip contains recorded MIDI notes
- `instrument list` - List loadable instruments exposed by the Ableton browser
- `instrument load` - Load an instrument onto a MIDI track
- `transport play` / `transport stop` / `transport record` - Control playback

Some legacy device, preset, and MIDI-effect commands are still present but need
further mapping work against the newer AbletonOSC API.

## Configuration

```bash
cli-ableton --host 127.0.0.1 --port 11000 --response-port 11001 --json status
```

## Development

```bash
pip install -r requirements-dev.txt
pytest -q
```

## License

Apache-2.0
