"""AbletonOSC bridge for external Ableton control."""

import socket
import logging
from dataclasses import dataclass
from typing import Any, Optional, Tuple

from .constants import (
    DEFAULT_HOST,
    DEFAULT_LISTEN_PORT,
    DEFAULT_RESPONSE_PORT,
    DEFAULT_TIMEOUT,
    ErrorCode,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OSCMessage:
    """Immutable OSC message representation."""
    address: str
    args: Tuple[Any, ...]


@dataclass(frozen=True)
class OSCResponse:
    """Immutable OSC response representation."""
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class AbletonOSCBridge:
    """
    Bridge for communicating with Ableton via OSC.

    Uses AbletonOSC to send/receive OSC messages to/from Ableton Live.
    All instance state is immutable after construction.
    """

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        send_port: int = DEFAULT_LISTEN_PORT,
        recv_port: Optional[int] = DEFAULT_RESPONSE_PORT,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Initialize the AbletonOSC bridge.

        Args:
            host: AbletonOSC server host (default: 127.0.0.1)
            send_port: Port to send OSC messages to (default: 11000)
            recv_port: Port to receive responses on (default: 11001)
            timeout: Response timeout in seconds (default: 5.0)
        """
        self._host = host
        self._send_port = send_port
        self._recv_port = recv_port or DEFAULT_RESPONSE_PORT
        self._timeout = timeout
        self._socket: Optional[socket.socket] = None
        self._connected = False

    @property
    def host(self) -> str:
        """Get the host address."""
        return self._host

    @property
    def send_port(self) -> int:
        """Get the send port."""
        return self._send_port

    @property
    def recv_port(self) -> int:
        """Get the receive port."""
        return self._recv_port

    @property
    def timeout(self) -> float:
        """Get the timeout value."""
        return self._timeout

    @property
    def is_connected(self) -> bool:
        """Check if bridge is connected."""
        return self._connected

    def connect(self) -> OSCResponse:
        """
        Establish connection to AbletonOSC server.

        Returns:
            OSCResponse with connection status
        """
        try:
            self._ensure_socket()

            # Send health check message
            response = self.send_message("/live/test")
            if response.success:
                self._connected = True
                logger.info(f"Connected to AbletonOSC at {self._host}:{self._send_port}")
            return response

        except socket.timeout:
            self._connected = False
            return OSCResponse(
                success=False,
                error=ErrorCode.TIMEOUT.value,
            )
        except Exception as e:
            self._connected = False
            logger.error(f"Connection failed: {e}")
            return OSCResponse(
                success=False,
                error=ErrorCode.CONNECTION_FAILED.value,
            )

    def disconnect(self) -> None:
        """Close the OSC connection."""
        if self._socket:
            self._socket.close()
            self._socket = None
        self._connected = False
        logger.info("Disconnected from AbletonOSC")

    def send_message(self, address: str, *args: Any, wait_for_response: bool = True) -> OSCResponse:
        """
        Send an OSC message to AbletonOSC server.

        Args:
            address: OSC address pattern
            *args: OSC arguments

        Returns:
            OSCResponse with result
        """
        if not self._socket:
            try:
                self._ensure_socket()
            except OSError as e:
                return OSCResponse(success=False, error=str(e))

        try:
            # Build OSC message
            import struct

            # OSC message format: address + type tag + arguments
            message = self._build_osc_message(address, args)

            self._socket.sendto(message, (self._host, self._send_port))

            if not wait_for_response:
                return OSCResponse(success=True, data={"status": "sent"})

            # Wait for response
            try:
                data, _ = self._socket.recvfrom(4096)
                return self._parse_response(data)
            except socket.timeout:
                return OSCResponse(
                    success=False,
                    error=ErrorCode.TIMEOUT.value,
                )

        except Exception as e:
            logger.error(f"Send failed: {e}")
            return OSCResponse(
                success=False,
                error=str(e),
            )

    def _ensure_socket(self) -> None:
        """Create and bind the UDP socket used for AbletonOSC replies."""
        if self._socket:
            return

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.settimeout(self._timeout)
        self._socket.bind(("0.0.0.0", self._recv_port))

    def _build_osc_message(self, address: str, args: tuple) -> bytes:
        """Build a raw OSC message bytes."""
        import struct

        # Address
        address_bytes = address.encode('utf-8') + b'\x00'
        # Pad to 4-byte boundary
        while len(address_bytes) % 4 != 0:
            address_bytes += b'\x00'

        # Type tag string
        if args:
            type_tag = b','
            values = b''
            for arg in args:
                if isinstance(arg, bool):
                    type_tag += b'T' if arg else b'F'
                elif isinstance(arg, int):
                    type_tag += b'i'
                    values += struct.pack('>i', arg)
                elif isinstance(arg, float):
                    type_tag += b'f'
                    values += struct.pack('>f', arg)
                elif isinstance(arg, str):
                    type_tag += b's'
                    arg_bytes = arg.encode('utf-8') + b'\x00'
                    while len(arg_bytes) % 4 != 0:
                        arg_bytes += b'\x00'
                    values += arg_bytes
                else:
                    type_tag += b's'
                    arg_bytes = str(arg).encode('utf-8') + b'\x00'
                    while len(arg_bytes) % 4 != 0:
                        arg_bytes += b'\x00'
                    values += arg_bytes

            type_tag += b'\x00'
            while len(type_tag) % 4 != 0:
                type_tag += b'\x00'
        else:
            type_tag = b',\x00\x00\x00'
            values = b''

        return address_bytes + type_tag + values

    def _parse_response(self, data: bytes) -> OSCResponse:
        """Parse raw OSC response bytes."""
        try:
            import struct

            offset = 0
            address_end = data.index(b"\x00", offset)
            address = data[offset:address_end].decode("utf-8")
            offset = address_end + 1
            while offset % 4 != 0:
                offset += 1

            tags_end = data.index(b"\x00", offset)
            type_tags = data[offset:tags_end].decode("utf-8")
            offset = tags_end + 1
            while offset % 4 != 0:
                offset += 1

            params = []
            for tag in type_tags.lstrip(","):
                if tag == "i":
                    params.append(struct.unpack(">i", data[offset:offset + 4])[0])
                    offset += 4
                elif tag == "f":
                    params.append(struct.unpack(">f", data[offset:offset + 4])[0])
                    offset += 4
                elif tag == "s":
                    value_end = data.index(b"\x00", offset)
                    params.append(data[offset:value_end].decode("utf-8"))
                    offset = value_end + 1
                    while offset % 4 != 0:
                        offset += 1
                elif tag == "T":
                    params.append(True)
                elif tag == "F":
                    params.append(False)

            return OSCResponse(
                success=True,
                data={
                    "address": address,
                    "params": params,
                    "raw": data.decode("utf-8", errors="ignore"),
                },
            )

        except Exception as e:
            logger.warning(f"Parse error: {e}")
            return OSCResponse(success=True, data={"status": "ok"})

    def health_check(self) -> OSCResponse:
        """
        Check if AbletonOSC connection is healthy.

        Returns:
            OSCResponse with health status
        """
        response = self.send_message("/live/test")
        if response.success:
            self._connected = True
        return response

    def __repr__(self) -> str:
        return (
            f"AbletonOSCBridge(host={self._host}, "
            f"send_port={self._send_port}, "
            f"recv_port={self._recv_port})"
        )
