"""MIDI processor module for Ableton CLI - MIDI effectors and sound design."""

from typing import Any, Dict, Optional

from .ableton_api import AbletonAPI
from .constants import MIDIEffectType, MIDI_PARAMS


class MIDIProcessor:
    """
    MIDI effects processor for Ableton.

    Provides control over all MIDI effect types including:
    - Arpeggiator
    - Chord
    - Scale
    - Note
    - Velocity
    - Random
    - Pitch
    - Rotate
    - Flam

    All methods return new dicts (immutable pattern).
    """

    def __init__(self, api: AbletonAPI) -> None:
        """
        Initialize MIDI processor.

        Args:
            api: AbletonAPI instance
        """
        self._api = api

    def list_effects(self, track_id: int) -> Dict[str, Any]:
        """
        List MIDI effects on a track.

        Args:
            track_id: Track identifier

        Returns:
            Dict with MIDI effects list
        """
        return self._api.list_midi_effects(track_id)

    def configure(
        self,
        track_id: int,
        effect_type: str,
        enabled: bool = True,
        **params,
    ) -> Dict[str, Any]:
        """
        Configure a MIDI effect.

        Args:
            track_id: Track identifier
            effect_type: MIDI effect type
            enabled: True to enable, False to bypass
            **params: Effect-specific parameters

        Returns:
            Dict with configuration result
        """
        # Validate effect type
        valid_types = [e.value for e in MIDIEffectType]
        if effect_type not in valid_types:
            return {
                "success": False,
                "error": f"Invalid effect type: {effect_type}. "
                         f"Must be one of: {valid_types}",
            }

        # Validate parameters for effect type
        expected_params = MIDI_PARAMS.get(effect_type, [])
        for param_name in params:
            if param_name not in expected_params:
                return {
                    "success": False,
                    "error": f"Invalid parameter '{param_name}' for {effect_type}. "
                             f"Expected: {expected_params}",
                }

        return self._api.set_midi_effect(track_id, effect_type, enabled, **params)

    def bypass(self, track_id: int, effect_type: str, bypassed: bool = True) -> Dict[str, Any]:
        """
        Bypass or enable a MIDI effect.

        Args:
            track_id: Track identifier
            effect_type: MIDI effect type
            bypassed: True to bypass, False to enable

        Returns:
            Dict with bypass state result
        """
        return self._api.set_midi_effect_bypass(track_id, effect_type, bypassed)

    # Arpeggiator

    def arpeggiator(
        self,
        track_id: int,
        enabled: bool = True,
        rate: str = "1/4",
        gate: float = 1.0,
        direction: str = "up",
        octaves: int = 2,
        repeat: int = 0,
    ) -> Dict[str, Any]:
        """
        Configure arpeggiator effect.

        Args:
            track_id: Track identifier
            enabled: Effect enabled state
            rate: Note rate ('1/4', '1/8', '1/16', etc.)
            gate: Gate time (0.0 to 1.0)
            direction: Direction ('up', 'down', 'updown', 'random')
            octaves: Number of octaves (1-4)
            repeat: Repeat count (0-4)

        Returns:
            Dict with configuration result
        """
        valid_rates = ["1/4", "1/8", "1/16", "1/32", "1/4T", "1/8T", "1/16T"]
        valid_directions = ["up", "down", "updown", "downup", "random", "order"]

        if rate not in valid_rates:
            return {
                "success": False,
                "error": f"Invalid rate: {rate}. Must be one of: {valid_rates}",
            }

        if direction not in valid_directions:
            return {
                "success": False,
                "error": f"Invalid direction: {direction}. Must be one of: {valid_directions}",
            }

        if not 1 <= octaves <= 4:
            return {
                "success": False,
                "error": f"Octaves must be between 1 and 4, got {octaves}",
            }

        return self.configure(
            track_id=track_id,
            effect_type=MIDIEffectType.ARPEGGIATOR.value,
            enabled=enabled,
            rate=rate,
            gate=gate,
            direction=direction,
            octaves=octaves,
            repeat=repeat,
        )

    # Chord

    def chord(
        self,
        track_id: int,
        enabled: bool = True,
        chord: str = "maj",
        strum: float = 0.0,
        spread: float = 0.5,
        voicing: str = "close",
    ) -> Dict[str, Any]:
        """
        Configure chord effect.

        Args:
            track_id: Track identifier
            enabled: Effect enabled state
            chord: Chord type ('maj', 'min', 'dim', 'aug', etc.)
            strum: Strum time (0.0 to 1.0)
            spread: Stereo spread (0.0 to 1.0)
            voicing: Voicing type ('close', 'open', 'wide')

        Returns:
            Dict with configuration result
        """
        valid_chords = ["maj", "min", "dim", "aug", "sus2", "sus4", "maj7", "min7", "dom7"]
        valid_voicings = ["close", "open", "wide", "block"]

        if chord not in valid_chords:
            return {
                "success": False,
                "error": f"Invalid chord: {chord}. Must be one of: {valid_chords}",
            }

        if voicing not in valid_voicings:
            return {
                "success": False,
                "error": f"Invalid voicing: {voicing}. Must be one of: {valid_voicings}",
            }

        return self.configure(
            track_id=track_id,
            effect_type=MIDIEffectType.CHORD.value,
            enabled=enabled,
            chord=chord,
            strum=strum,
            spread=spread,
            voicing=voicing,
        )

    # Scale

    def scale(
        self,
        track_id: int,
        enabled: bool = True,
        scale: str = "chromatic",
        root: int = 0,
        octave: int = 0,
        wrap: bool = True,
    ) -> Dict[str, Any]:
        """
        Configure scale effect.

        Args:
            track_id: Track identifier
            enabled: Effect enabled state
            scale: Scale type ('chromatic', 'major', 'minor', 'pentatonic', etc.)
            root: Root note (0-11, where 0=C)
            octave: Octave offset (-2 to 2)
            wrap: Wrap notes within scale

        Returns:
            Dict with configuration result
        """
        valid_scales = [
            "chromatic", "major", "minor", "harmonic_minor",
            "melodic_minor", "pentatonic_major", "pentatonic_minor",
            "blues", "whole_note", "diminished", "mixolydian", "dorian",
        ]

        if scale not in valid_scales:
            return {
                "success": False,
                "error": f"Invalid scale: {scale}. Must be one of: {valid_scales}",
            }

        if not 0 <= root <= 11:
            return {
                "success": False,
                "error": f"Root must be between 0 and 11, got {root}",
            }

        return self.configure(
            track_id=track_id,
            effect_type=MIDIEffectType.SCALE.value,
            enabled=enabled,
            scale=scale,
            root=root,
            octave=octave,
            wrap=wrap,
        )

    # Note

    def note(
        self,
        track_id: int,
        enabled: bool = True,
        length: float = 0.5,
        velocity: int = 100,
        position: float = 0.0,
        repeat: int = 0,
    ) -> Dict[str, Any]:
        """
        Configure note effect.

        Args:
            track_id: Track identifier
            enabled: Effect enabled state
            length: Note length (0.0 to 1.0)
            velocity: Note velocity (1-127)
            position: Note position (0.0 to 1.0)
            repeat: Repeat count (0-8)

        Returns:
            Dict with configuration result
        """
        if not 1 <= velocity <= 127:
            return {
                "success": False,
                "error": f"Velocity must be between 1 and 127, got {velocity}",
            }

        return self.configure(
            track_id=track_id,
            effect_type=MIDIEffectType.NOTE.value,
            enabled=enabled,
            length=length,
            velocity=velocity,
            position=position,
            repeat=repeat,
        )

    # Velocity

    def velocity(
        self,
        track_id: int,
        enabled: bool = True,
        amount: float = 0.0,
        curve: float = 0.0,
        random: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Configure velocity effect.

        Args:
            track_id: Track identifier
            enabled: Effect enabled state
            amount: Velocity offset (-127 to 127)
            curve: Velocity curve (-1.0 to 1.0)
            random: Random amount (0.0 to 1.0)

        Returns:
            Dict with configuration result
        """
        return self.configure(
            track_id=track_id,
            effect_type=MIDIEffectType.VELOCITY.value,
            enabled=enabled,
            amount=amount,
            curve=curve,
            random=random,
        )

    # Random

    def random(
        self,
        track_id: int,
        enabled: bool = True,
        probability: float = 0.5,
        note_length: float = 0.5,
        velocity: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Configure random effect.

        Args:
            track_id: Track identifier
            enabled: Effect enabled state
            probability: Trigger probability (0.0 to 1.0)
            note_length: Note length variance (0.0 to 1.0)
            velocity: Velocity variance (0.0 to 1.0)

        Returns:
            Dict with configuration result
        """
        return self.configure(
            track_id=track_id,
            effect_type=MIDIEffectType.RANDOM.value,
            enabled=enabled,
            probability=probability,
            note_length=note_length,
            velocity=velocity,
        )

    # Pitch

    def pitch(
        self,
        track_id: int,
        enabled: bool = True,
        amount: float = 0.0,
        auto: bool = False,
        range_max: float = 12.0,
    ) -> Dict[str, Any]:
        """
        Configure pitch effect.

        Args:
            track_id: Track identifier
            enabled: Effect enabled state
            amount: Pitch shift in semitones (-24 to 24)
            auto: Auto pitch correction
            range_max: Maximum pitch shift

        Returns:
            Dict with configuration result
        """
        if not -24 <= amount <= 24:
            return {
                "success": False,
                "error": f"Amount must be between -24 and 24, got {amount}",
            }

        return self.configure(
            track_id=track_id,
            effect_type=MIDIEffectType.PITCH.value,
            enabled=enabled,
            amount=amount,
            auto=auto,
            range=range_max,
        )

    # Rotate

    def rotate(
        self,
        track_id: int,
        enabled: bool = True,
        amount: int = 0,
        step: int = 1,
        fade: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Configure rotate effect.

        Args:
            track_id: Track identifier
            enabled: Effect enabled state
            amount: Rotation amount (-12 to 12)
            step: Rotation step size
            fade: Crossfade amount (0.0 to 1.0)

        Returns:
            Dict with configuration result
        """
        return self.configure(
            track_id=track_id,
            effect_type=MIDIEffectType.ROTATE.value,
            enabled=enabled,
            amount=amount,
            step=step,
            fade=fade,
        )

    # Flam

    def flam(
        self,
        track_id: int,
        enabled: bool = True,
        amount: float = 0.25,
        timing: float = 0.0,
        velocity: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Configure flam effect.

        Args:
            track_id: Track identifier
            enabled: Effect enabled state
            amount: Flam offset time (0.0 to 1.0)
            timing: Timing offset (-0.5 to 0.5)
            velocity: Velocity offset (-127 to 127)

        Returns:
            Dict with configuration result
        """
        return self.configure(
            track_id=track_id,
            effect_type=MIDIEffectType.FLAM.value,
            enabled=enabled,
            amount=amount,
            timing=timing,
            velocity=velocity,
        )

    # Sound Design Helpers

    def preset_arp(
        self,
        track_id: int,
        preset: str = "tight",
    ) -> Dict[str, Any]:
        """
        Apply arpeggiator preset for sound design.

        Args:
            track_id: Track identifier
            preset: Preset name ('tight', 'loose', 'fantasy', 'rapid')

        Returns:
            Dict with preset configuration
        """
        presets = {
            "tight": dict(rate="1/8", gate=1.0, direction="up", octaves=1),
            "loose": dict(rate="1/8", gate=0.7, direction="updown", octaves=2),
            "fantasy": dict(rate="1/16", gate=0.8, direction="updown", octaves=3),
            "rapid": dict(rate="1/32", gate=0.9, direction="up", octaves=2),
        }

        if preset not in presets:
            return {
                "success": False,
                "error": f"Unknown preset: {preset}. Must be one of: {list(presets.keys())}",
            }

        return self.arpeggiator(track_id, enabled=True, **presets[preset])

    def preset_chord(
        self,
        track_id: int,
        preset: str = "spacious",
    ) -> Dict[str, Any]:
        """
        Apply chord preset for sound design.

        Args:
            track_id: Track identifier
            preset: Preset name ('spacious', 'tight', 'strummed', 'shimmer')

        Returns:
            Dict with preset configuration
        """
        presets = {
            "spacious": dict(chord="maj", spread=1.0, voicing="wide"),
            "tight": dict(chord="maj", spread=0.0, voicing="close"),
            "strummed": dict(chord="min", strum=0.5, voicing="open"),
            "shimmer": dict(chord="aug", spread=0.8, voicing="wide"),
        }

        if preset not in presets:
            return {
                "success": False,
                "error": f"Unknown preset: {preset}. Must be one of: {list(presets.keys())}",
            }

        return self.chord(track_id, enabled=True, **presets[preset])