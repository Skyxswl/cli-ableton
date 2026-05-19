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

## External MIDI Input Test

Use this when testing a controller such as Touch Me as the MIDI source:

```bash
cli-ableton --json input routes 0
cli-ableton --json input route "Touch Me" 0 --monitor 1 --arm
```

Then record or capture MIDI into a clip in Ableton and verify the clip:

```bash
cli-ableton --json input check 0 0
```

If `input routes` does not include the device name, Ableton has not exposed it
to the track yet. Enable the device's `Track` input under `Settings > Link,
Tempo & MIDI > MIDI Ports`.

## Current Coverage

Confirmed against Ableton Live 12 with AbletonOSC:

- Connectivity check through `/live/test`
- Track names through `/live/song/get/track_names`
- Transport play/stop through `/live/song/start_playing` and
  `/live/song/stop_playing`
- MIDI clip creation through `/live/clip_slot/create_clip`
- MIDI note insertion through `/live/clip/add/notes`
- Clip launch/stop through `/live/clip/fire` and `/live/clip/stop`
- Track input route listing through
  `/live/track/get/available_input_routing_types`
- Track input routing, monitoring, and arm through
  `/live/track/set/input_routing_type`,
  `/live/track/set/current_monitoring_state`, and `/live/track/set/arm`
- MIDI note inspection through `/live/clip/get/notes`

Legacy commands for devices, presets, scenes, and MIDI effects still need full
mapping against the current AbletonOSC API.
