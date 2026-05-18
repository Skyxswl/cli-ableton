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
