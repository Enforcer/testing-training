"""Pretending to be a serial port library."""
import random
import socket
import time

PARITY_ODD = 1
PARITY_EVEN = 2

ACK = b"\x00\x06"
NACK = b"\x00\x15"


class SerialException(Exception):
    pass


class SerialTimeoutException(TimeoutError):
    pass


class Serial:
    def __init__(
        self,
        address: str,
        baudrate: int = 19200,
        bytesize: int = 8,
        parity: int = PARITY_ODD,
        timeout: int = 1,
    ) -> None:
        self._timeout = timeout
        self._opened = False
        self._last_payload: None | bytes = None

    def write(self, payload: bytes) -> None:
        if not self._opened:
            raise SerialException("Port is not open!")
        self._last_payload = payload

    def read(self, length: int) -> bytes:
        if length != 2:
            raise Exception("Sorry dude, I can only read 2 bytes in this training :)")

        if not self._opened:
            raise SerialException("Port is not open!")

        if Serial._TIMEOUT:
            time.sleep(self._timeout)
            raise SerialTimeoutException("Timeout!")

        time.sleep(Serial.TIME_IT_TAKES_TO_RESPOND)
        if Serial._SIMULATE_ERROR:
            return NACK
        else:
            return ACK

    def open(self) -> None:
        if self._opened:
            raise SerialException("Port is already open!")
        self._opened = True

    def close(self) -> None:
        if not self._opened:
            raise SerialException("Port is not open!")
        self._opened = False

    _TIMEOUT = False
    _SIMULATE_ERROR = False

    TIME_IT_TAKES_TO_RESPOND = 0.25
