"""Tests for MIDIProcessor."""

import pytest
from unittest.mock import Mock

from cli_anything.ableton.midi_processor import MIDIProcessor
from cli_anything.ableton.ableton_api import AbletonAPI
from cli_anything.ableton.constants import MIDIEffectType


class TestMIDIProcessor:
    """Test MIDIProcessor class."""

    @pytest.fixture
    def api(self):
        """Create mock API."""
        return Mock(spec=AbletonAPI)

    @pytest.fixture
    def proc(self, api):
        """Create MIDIProcessor instance."""
        return MIDIProcessor(api)

    def test_list_effects(self, proc, api):
        """Test list MIDI effects."""
        api.list_midi_effects.return_value = {
            "success": True,
            "midi_effects": [{"type": "arp", "enabled": True}]
        }

        result = proc.list_effects(track_id=1)

        assert result["success"] is True
        assert len(result["midi_effects"]) == 1

    def test_configure_valid_effect(self, proc, api):
        """Test configure valid MIDI effect."""
        api.set_midi_effect.return_value = {"success": True}

        result = proc.configure(track_id=1, effect_type="arp", enabled=True, rate="1/8")

        assert result["success"] is True

    def test_configure_invalid_effect_type(self, proc, api):
        """Test configure invalid effect type."""
        result = proc.configure(track_id=1, effect_type="invalid", enabled=True)

        assert result["success"] is False
        assert "Invalid effect type" in result["error"]

    def test_configure_invalid_param(self, proc, api):
        """Test configure with invalid parameter."""
        result = proc.configure(track_id=1, effect_type="arp", enabled=True, invalid_param=1)

        assert result["success"] is False
        assert "Invalid parameter" in result["error"]

    def test_bypass(self, proc, api):
        """Test bypass MIDI effect."""
        api.set_midi_effect_bypass.return_value = {"success": True, "bypassed": True}

        result = proc.bypass(track_id=1, effect_type="arp", bypassed=True)

        assert result["bypassed"] is True

    def test_arpeggiator_valid(self, proc, api):
        """Test arpeggiator with valid params."""
        api.set_midi_effect.return_value = {"success": True}

        result = proc.arpeggiator(track_id=1, enabled=True, rate="1/8", gate=0.8,
                                  direction="up", octaves=2)

        assert result["success"] is True

    def test_arpeggiator_invalid_rate(self, proc, api):
        """Test arpeggiator with invalid rate."""
        result = proc.arpeggiator(track_id=1, rate="invalid")

        assert result["success"] is False
        assert "Invalid rate" in result["error"]

    def test_arpeggiator_invalid_direction(self, proc, api):
        """Test arpeggiator with invalid direction."""
        result = proc.arpeggiator(track_id=1, direction="invalid")

        assert result["success"] is False
        assert "Invalid direction" in result["error"]

    def test_arpeggiator_invalid_octaves(self, proc, api):
        """Test arpeggiator with invalid octaves."""
        result = proc.arpeggiator(track_id=1, octaves=5)

        assert result["success"] is False
        assert "Octaves must be between" in result["error"]

    def test_chord_valid(self, proc, api):
        """Test chord with valid params."""
        api.set_midi_effect.return_value = {"success": True}

        result = proc.chord(track_id=1, chord="maj", strum=0.5, spread=0.8, voicing="wide")

        assert result["success"] is True

    def test_chord_invalid_chord(self, proc, api):
        """Test chord with invalid chord type."""
        result = proc.chord(track_id=1, chord="invalid")

        assert result["success"] is False
        assert "Invalid chord" in result["error"]

    def test_chord_invalid_voicing(self, proc, api):
        """Test chord with invalid voicing."""
        result = proc.chord(track_id=1, voicing="invalid")

        assert result["success"] is False
        assert "Invalid voicing" in result["error"]

    def test_scale_valid(self, proc, api):
        """Test scale with valid params."""
        api.set_midi_effect.return_value = {"success": True}

        result = proc.scale(track_id=1, scale="major", root=0, octave=0)

        assert result["success"] is True

    def test_scale_invalid_scale(self, proc, api):
        """Test scale with invalid scale type."""
        result = proc.scale(track_id=1, scale="invalid")

        assert result["success"] is False
        assert "Invalid scale" in result["error"]

    def test_scale_invalid_root(self, proc, api):
        """Test scale with invalid root."""
        result = proc.scale(track_id=1, root=15)

        assert result["success"] is False
        assert "Root must be between" in result["error"]

    def test_note_valid(self, proc, api):
        """Test note with valid params."""
        api.set_midi_effect.return_value = {"success": True}

        result = proc.note(track_id=1, length=0.5, velocity=100)

        assert result["success"] is True

    def test_note_invalid_velocity(self, proc, api):
        """Test note with invalid velocity."""
        result = proc.note(track_id=1, velocity=200)

        assert result["success"] is False
        assert "Velocity must be between" in result["error"]

    def test_velocity_valid(self, proc, api):
        """Test velocity with valid params."""
        api.set_midi_effect.return_value = {"success": True}

        result = proc.velocity(track_id=1, amount=10.0, curve=0.5)

        assert result["success"] is True

    def test_random_valid(self, proc, api):
        """Test random with valid params."""
        api.set_midi_effect.return_value = {"success": True}

        result = proc.random(track_id=1, probability=0.5)

        assert result["success"] is True

    def test_pitch_valid(self, proc, api):
        """Test pitch with valid params."""
        api.set_midi_effect.return_value = {"success": True}

        result = proc.pitch(track_id=1, amount=5.0, auto=False)

        assert result["success"] is True

    def test_pitch_invalid_amount(self, proc, api):
        """Test pitch with invalid amount."""
        result = proc.pitch(track_id=1, amount=30.0)

        assert result["success"] is False
        assert "Amount must be between" in result["error"]

    def test_rotate_valid(self, proc, api):
        """Test rotate with valid params."""
        api.set_midi_effect.return_value = {"success": True}

        result = proc.rotate(track_id=1, amount=5, step=1)

        assert result["success"] is True

    def test_flam_valid(self, proc, api):
        """Test flam with valid params."""
        api.set_midi_effect.return_value = {"success": True}

        result = proc.flam(track_id=1, amount=0.25, timing=0.0)

        assert result["success"] is True

    def test_preset_arp_valid(self, proc, api):
        """Test arp preset with valid preset name."""
        api.set_midi_effect.return_value = {"success": True}

        result = proc.preset_arp(track_id=1, preset="tight")

        assert result["success"] is True

    def test_preset_arp_invalid(self, proc, api):
        """Test arp preset with invalid preset name."""
        result = proc.preset_arp(track_id=1, preset="invalid")

        assert result["success"] is False
        assert "Unknown preset" in result["error"]

    def test_preset_chord_valid(self, proc, api):
        """Test chord preset with valid preset name."""
        api.set_midi_effect.return_value = {"success": True}

        result = proc.preset_chord(track_id=1, preset="spacious")

        assert result["success"] is True

    def test_preset_chord_invalid(self, proc, api):
        """Test chord preset with invalid preset name."""
        result = proc.preset_chord(track_id=1, preset="invalid")

        assert result["success"] is False
        assert "Unknown preset" in result["error"]