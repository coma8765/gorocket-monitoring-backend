import logging
import os
from typing import Optional, List, Callable

import serial
from pydantic import BaseModel, ValidationError


class InputData(BaseModel):
    """Input data from radio module"""
    # TODO: Add dynamic
    TEAM_ID: str
    START_TIME: int
    VOLTAGE: float
    VECTOR_ABS: float
    ALTITUDE: float
    IS_STARTED: bool
    IS_APOGEE: bool
    IS_RESCUE: bool
    IS_SPUTNIK_CATCH: bool
    IS_LANDING: bool
    IS_TESTING: bool = False


class Transfer:
    """Logic for transfer from UART module"""

    is_on: bool = True
    logger: logging.Logger
    serial: serial.Serial
    raw_data: List[str] = []
    data: List[InputData] = []
    callbacks: [Callable] = []

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        self.logger.info("Init")
        # noinspection PyBroadException
        try:
            self.serial = serial.Serial(
                port=os.getenv("SERIAL_PORT"),
                baudrate=os.getenv("SERIAL_BOUND", 9600),
                bytesize=8,
                # timeout=0.01,
                stopbits=serial.STOPBITS_ONE
            )
        except Exception:
            self.logger.exception("Port not found")
            return

        self.logger.info("Connection opened")

    def load(self):
        if getattr(self, "serial", None):
            try:
                # noinspection PyTypeChecker
                try:
                    self.raw_data.append(self.serial.readline()[:-2].decode("utf-8"))
                except (PermissionError, IOError, UnicodeDecodeError):
                    self.logger.warning("Error decode data")
                    return
                data = self._parse_raw_data(self.raw_data[-1])
                if data:
                    self.data.append(data)
                    self.logger.debug(self.data[-1])
                    [callback(data.dict()) for callback in self.callbacks]
                else:
                    self.logger.debug(self.raw_data[-1])
            except serial.serialutil.SerialException:
                self.logger.exception("Read error")

        else:
            self.logger.error("Serial don't init")

    def _parse_raw_data(self, data: str) -> Optional[InputData]:
        params = data.split(";")

        if len(params) < 10:
            self.logger.error(f"Don't parse data len is {len(params)}")
            return

        # self.logger.warning(params)
        try:
            return InputData(
                TEAM_ID=params[0],
                START_TIME=params[1],
                VOLTAGE=params[2],
                VECTOR_ABS=params[3],
                ALTITUDE=params[4],
                IS_STARTED=params[5],
                IS_APOGEE=params[6],
                IS_RESCUE=params[7],
                IS_SPUTNIK_CATCH=params[8],
                IS_LANDING=params[9],
                IS_TESTING=len(params) == 11 and True or False,
            )
        except ValidationError:
            self.logger.error(f"Validation error {len(params)}")
            return

    def thread(self):
        """Thread for run always data getter"""
        while self.is_on:
            self.load()

        self.logger.info("Transport off")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    transport = Transfer()
    try:
        transport.thread()
    except KeyboardInterrupt:
        transport.is_on = False
