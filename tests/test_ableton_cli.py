"""Tests for the Ableton CLI entry point."""

import json
from unittest.mock import Mock, patch

from click.testing import CliRunner

from cli_anything.ableton.ableton_cli import cli


def test_status_json_failure_exits_nonzero():
    """A failed status check should be script-detectable."""
    runner = CliRunner()

    with patch("cli_anything.ableton.ableton_cli.AbletonAPI") as api_cls:
        api = api_cls.return_value
        api.health_check.return_value = Mock(
            success=False,
            data=None,
            error="CONNECTION_FAILED",
        )

        result = runner.invoke(cli, ["--json", "status"])

    assert result.exit_code == 1
    assert json.loads(result.output) == {
        "success": False,
        "data": None,
        "error": "CONNECTION_FAILED",
    }


def test_status_json_success_exits_zero():
    """A successful status check should preserve the normal zero exit code."""
    runner = CliRunner()

    with patch("cli_anything.ableton.ableton_cli.AbletonAPI") as api_cls:
        api = api_cls.return_value
        api.health_check.return_value = Mock(
            success=True,
            data={"status": "ok"},
            error=None,
        )

        result = runner.invoke(cli, ["--json", "status"])

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "success": True,
        "data": {"status": "ok"},
        "error": None,
    }


def test_track_list_failure_exits_nonzero():
    """Operation failures routed through output_result should exit non-zero."""
    runner = CliRunner()

    with patch("cli_anything.ableton.ableton_cli.TrackOperations") as ops_cls:
        ops = ops_cls.return_value
        ops.list.return_value = {
            "success": False,
            "error": "CONNECTION_FAILED",
            "tracks": [],
        }

        result = runner.invoke(cli, ["--json", "track", "list"])

    assert result.exit_code == 1
    assert json.loads(result.output) == {
        "success": False,
        "error": "CONNECTION_FAILED",
        "tracks": [],
    }


def test_clip_create_command_outputs_json():
    """The CLI should expose MIDI clip creation."""
    runner = CliRunner()

    with patch("cli_anything.ableton.ableton_cli.ClipControl") as ctrl_cls:
        ctrl = ctrl_cls.return_value
        ctrl.create.return_value = {
            "success": True,
            "track_id": 1,
            "clip_index": 2,
            "length": 4.0,
        }

        result = runner.invoke(cli, ["--json", "clip", "create", "1", "2", "--length", "4"])

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "success": True,
        "track_id": 1,
        "clip_index": 2,
        "length": 4.0,
    }
    ctrl.create.assert_called_once_with(1, 2, 4.0)


def test_midi_note_command_outputs_json():
    """The CLI should expose adding a MIDI note to a clip."""
    runner = CliRunner()

    with patch("cli_anything.ableton.ableton_cli.ClipControl") as ctrl_cls:
        ctrl = ctrl_cls.return_value
        ctrl.add_note.return_value = {
            "success": True,
            "track_id": 1,
            "clip_index": 2,
            "pitch": 60,
        }

        result = runner.invoke(
            cli,
            [
                "--json",
                "midi",
                "note",
                "1",
                "2",
                "--pitch",
                "60",
                "--start",
                "0",
                "--duration",
                "0.25",
                "--velocity",
                "100",
            ],
        )

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "success": True,
        "track_id": 1,
        "clip_index": 2,
        "pitch": 60,
    }
    ctrl.add_note.assert_called_once_with(1, 2, 60, 0.0, 0.25, 100, False)


def test_input_routes_command_outputs_json():
    """The CLI should expose available MIDI input routing types."""
    runner = CliRunner()

    with patch("cli_anything.ableton.ableton_cli.AbletonAPI") as api_cls:
        api = api_cls.return_value
        api.get_track_input_routes.return_value = {
            "success": True,
            "track_id": 0,
            "inputs": ["Touch Me", "Ext. In"],
        }

        result = runner.invoke(cli, ["--json", "input", "routes", "0"])

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "success": True,
        "track_id": 0,
        "inputs": ["Touch Me", "Ext. In"],
    }
    api.get_track_input_routes.assert_called_once_with(0)


def test_input_route_command_outputs_json():
    """The CLI should route a track to a named MIDI input source."""
    runner = CliRunner()

    with patch("cli_anything.ableton.ableton_cli.AbletonAPI") as api_cls:
        api = api_cls.return_value
        api.route_midi_input.return_value = {
            "success": True,
            "track_id": 0,
            "source": "Touch Me",
            "channel": "All Channels",
            "monitor": 0,
            "armed": True,
        }

        result = runner.invoke(
            cli,
            [
                "--json",
                "input",
                "route",
                "Touch Me",
                "0",
                "--channel",
                "All Channels",
                "--monitor",
                "0",
                "--arm",
            ],
        )

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "success": True,
        "track_id": 0,
        "source": "Touch Me",
        "channel": "All Channels",
        "monitor": 0,
        "armed": True,
    }
    api.route_midi_input.assert_called_once_with(0, "Touch Me", "All Channels", 0, True)


def test_input_check_command_outputs_json():
    """The CLI should check whether a clip captured MIDI notes."""
    runner = CliRunner()

    with patch("cli_anything.ableton.ableton_cli.AbletonAPI") as api_cls:
        api = api_cls.return_value
        api.check_midi_input.return_value = {
            "success": True,
            "track_id": 0,
            "clip_index": 1,
            "note_count": 1,
            "notes": [{"pitch": 60}],
        }

        result = runner.invoke(cli, ["--json", "input", "check", "0", "1"])

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "success": True,
        "track_id": 0,
        "clip_index": 1,
        "note_count": 1,
        "notes": [{"pitch": 60}],
    }
    api.check_midi_input.assert_called_once_with(0, 1)


def test_instrument_list_command_outputs_json():
    """The CLI should list loadable instruments."""
    runner = CliRunner()

    with patch("cli_anything.ableton.ableton_cli.AbletonAPI") as api_cls:
        api = api_cls.return_value
        api.get_available_instruments.return_value = {
            "success": True,
            "instruments": ["Operator", "Wavetable"],
        }

        result = runner.invoke(cli, ["--json", "instrument", "list"])

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "success": True,
        "instruments": ["Operator", "Wavetable"],
    }
    api.get_available_instruments.assert_called_once_with()


def test_instrument_load_command_outputs_json():
    """The CLI should load an instrument onto a track."""
    runner = CliRunner()

    with patch("cli_anything.ableton.ableton_cli.AbletonAPI") as api_cls:
        api = api_cls.return_value
        api.load_instrument.return_value = {
            "success": True,
            "track_id": 0,
            "instrument": "Operator",
        }

        result = runner.invoke(cli, ["--json", "instrument", "load", "0", "Operator"])

    assert result.exit_code == 0
    assert json.loads(result.output) == {
        "success": True,
        "track_id": 0,
        "instrument": "Operator",
    }
    api.load_instrument.assert_called_once_with(0, "Operator")
