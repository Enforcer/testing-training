from testing_training.myserial import Serial, ACK, NACK


class EnginesControllerException(Exception):
    pass


class UnexpectedResponse(EnginesControllerException):
    pass


class EnginesController:
    def __init__(self) -> None:
        self._serial = Serial("/dev/ttyUSB0", timeout=1)

    def open(self) -> None:
        self._serial.open()

    def close(self) -> None:
        self._serial.closed()

    def move_engine(self, engine_row: int, engine_column: int) -> bool:
        engine_controller_address = 0x02
        drive_command = 0x13
        engine_no = engine_row * 10 + engine_column
        steps = 0x1
        frame = [engine_controller_address, drive_command, engine_no, steps]
        frame_with_checksum = frame + [sum(frame) & 0xFF]
        payload = bytes(frame_with_checksum)
        self._serial.write(payload)
        value = self._serial.read(length=2)
        if value == ACK:
            return True
        elif value == NACK:
            return False
        else:
            raise UnexpectedResponse()
