# hardware/display_driver.py
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text

class TimingDisplay:
    def __init__(self, cs_pin: int):
        """Initializes the MAX7219 display."""
        serial = spi(port=0, device=cs_pin, gpio=noop())
        self.device = max7219(serial, cascaded=1, block_orientation=0)

    def show_time(self, elapsed_time: float):
        """Displays the time formatted as SS.ss"""
        time_str = f"{elapsed_time:05.2f}"
        with canvas(self.device) as draw:
            text(draw, (0, 0), time_str, fill="white")

    def show_message(self, message: str):
        """Displays a short text message."""
        with canvas(self.device) as draw:
            text(draw, (0, 0), message, fill="white")
            
    def clear(self):
        """Clears the display."""
        self.device.clear()
