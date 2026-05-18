# Ableton Integration Notes

`cli-ableton` talks to Ableton Live through
[ideoforms/AbletonOSC](https://github.com/ideoforms/AbletonOSC).

## Architecture

```text
CLI command -> OSC UDP message -> AbletonOSC remote script -> Ableton Live
```

## Ports

The supported AbletonOSC version listens on port `11000` and sends replies to
port `11001`. These are the package defaults.

## Known Working Flow

```bash
cli-ableton --json status
cli-ableton --json track list
cli-ableton clip create 0 0 --length 4
cli-ableton midi note 0 0 --pitch 60 --start 0 --duration 0.5 --velocity 100
cli-ableton clip launch 0 0
cli-ableton clip stop 0 0
```

## Current Coverage

Confirmed against Ableton Live 12 with AbletonOSC:

- Connectivity check through `/live/test`
- Track names through `/live/song/get/track_names`
- Transport play/stop through `/live/song/start_playing` and
  `/live/song/stop_playing`
- MIDI clip creation through `/live/clip_slot/create_clip`
- MIDI note insertion through `/live/clip/add/notes`
- Clip launch/stop through `/live/clip/fire` and `/live/clip/stop`

Legacy commands for devices, presets, scenes, and MIDI effects still need full
mapping against the current AbletonOSC API.
