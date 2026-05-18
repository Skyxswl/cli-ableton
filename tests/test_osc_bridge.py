"""Tests for OSC Bridge."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import socket

from cli_anything.ableton.osc_bridge import AbletonOSCBridge, OSCMessage, OSCResponse


class TestOSCMessage:
    """Test OSCMessage dataclass."""

    def test_create(self):
        """Test creating OSC message."""
        msg = OSCMessage(address="/test", args=(1, 2, "hello"))

        assert msg.address == "/test"
        assert msg.args == (1, 2, "hello")

    def test_immutable(self):
        """Test OSC message is immutable."""
        msg = OSCMessage(address="/test", args=(1,))

        with pytest.raises(Exception):
            msg.address = "/other"


class TestOSCResponse:
    """Test OSCResponse dataclass."""

    def test_success_response(self):
        """Test success response."""
        resp = OSCResponse(success=True, data={"tracks": []})

        assert resp.success is True
        assert resp.data == {"tracks": []}
        assert resp.error is None

    def test_failure_response(self):
        """Test failure response."""
        resp = OSCResponse(success=False, error="CONNECTION_FAILED")

        assert resp.success is False
        assert resp.error == "CONNECTION_FAILED"

    def test_immutable(self):
        """Test OSC response is immutable."""
        resp = OSCResponse(success=True, data={})

        with pytest.raises(Exception):
            resp.success = False


class TestAbletonOSCBridge:
    """Test AbletonOSCBridge class."""

    @pytest.fixture
    def bridge(self):
        """Create bridge instance."""
        return AbletonOSCBridge(host="127.0.0.1", send_port=9001, recv_port=9001)

    def test_init(self, bridge):
        """Test bridge initialization."""
        assert bridge.host == "127.0.0.1"
        assert bridge.send_port == 9001
        assert bridge.recv_port == 9001
        assert bridge.timeout == 5.0
        assert bridge.is_connected is False

    def test_properties(self, bridge):
        """Test bridge properties."""
        assert bridge.host == "127.0.0.1"
        assert bridge.send_port == 9001
        assert bridge.recv_port == 9001
        assert bridge.timeout == 5.0

    @patch('socket.socket')
    def test_connect_success(self, mock_socket_class, bridge):
        """Test successful connection."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        mock_socket.recvfrom.return_value = (b'/alive 1', ('127.0.0.1', 9001))

        result = bridge.connect()

        assert result.success is True

    @patch('socket.socket')
    def test_connect_timeout(self, mock_socket_class, bridge):
        """Test connection timeout."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recvfrom.side_effect = socket.timeout()

        result = bridge.connect()

        assert result.success is False
        assert result.error == "TIMEOUT"

    @patch('socket.socket')
    def test_disconnect(self, mock_socket_class, bridge):
        """Test disconnect."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        bridge.connect()
        bridge.disconnect()

        assert bridge.is_connected is False
        mock_socket.close.assert_called_once()

    @patch('socket.socket')
    def test_send_message_not_connected(self, mock_socket_class, bridge):
        """Test send message lazily opens a socket."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recvfrom.side_effect = socket.timeout()

        result = bridge.send_message("/test", "arg")

        assert result.success is False
        assert result.error == "TIMEOUT"
        mock_socket.bind.assert_called_once()

    @patch('socket.socket')
    def test_health_check_not_connected(self, mock_socket_class, bridge):
        """Test health check lazily opens a socket."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.recvfrom.side_effect = socket.timeout()

        result = bridge.health_check()

        assert result.success is False
        assert result.error == "TIMEOUT"
        mock_socket.bind.assert_called_once()

    def test_repr(self, bridge):
        """Test string representation."""
        repr_str = repr(bridge)

        assert "127.0.0.1" in repr_str
        assert "9001" in repr_str

    def test_build_osc_message_with_string(self, bridge):
        """Test building OSC message with string argument."""
        msg = bridge._build_osc_message("/test", ("hello",))

        assert len(msg) > 0
        assert b"/test" in msg

    def test_build_osc_message_with_int(self, bridge):
        """Test building OSC message with integer argument."""
        msg = bridge._build_osc_message("/test", (42,))

        assert len(msg) > 0

    def test_build_osc_message_with_float(self, bridge):
        """Test building OSC message with float argument."""
        msg = bridge._build_osc_message("/test", (3.14,))

        assert len(msg) > 0

    def test_build_osc_message_with_no_args(self, bridge):
        """Test building OSC message with no arguments."""
        msg = bridge._build_osc_message("/test", ())

        assert len(msg) > 0

    def test_build_osc_message_with_many_args_is_parseable(self, bridge):
        """Test messages with 4-byte-aligned type tags are null-terminated."""
        from pythonosc.osc_message import OscMessage

        msg = bridge._build_osc_message(
            "/live/clip/add/notes",
            (0, 0, 60, 0.0, 0.5, 100, False),
        )

        parsed = OscMessage(msg)
        assert parsed.address == "/live/clip/add/notes"
        assert parsed.params == [0, 0, 60, 0.0, 0.5, 100, False]

    def test_parse_response_with_address(self, bridge):
        """Test parsing response with OSC address."""
        data = b'/alive 1'
        result = bridge._parse_response(data)

        assert result.success is True
        assert result.data is not None
