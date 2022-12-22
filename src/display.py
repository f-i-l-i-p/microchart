import machine
import framebuf
import utime

# 0~3 gray
LUT_VCOM = [
    0x00, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x60, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x00, 0x14, 0x00, 0x00, 0x00, 0x01,
    0x00, 0x13, 0x0A, 0x01, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00
]
# R21
LUT_WW = [
    0x40, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x90, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x10, 0x14, 0x0A, 0x00, 0x00, 0x01,
    0xA0, 0x13, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]
# R22H r
LUT_BW = [
    0x40, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x90, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x00, 0x14, 0x0A, 0x00, 0x00, 0x01,
    0x99, 0x0C, 0x01, 0x03, 0x04, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]
# R23H w
LUT_WB = [
    0x40, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x90, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x00, 0x14, 0x0A, 0x00, 0x00, 0x01,
    0x99, 0x0B, 0x04, 0x04, 0x01, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]
#  R24H b
LUT_BB = [
    0x80, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x90, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x20, 0x14, 0x0A, 0x00, 0x00, 0x01,
    0x50, 0x13, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]


class Display:
    WIDTH = 400
    HEIGHT = 300

    RST_PIN = 13
    DC_PIN = 8
    CS_PIN = 6
    BUSY_PIN = 21

    BLACK = 0x00
    DARK_GRAY = 0xaa
    LIGHT_GRAY = 0x55
    WHITE = 0xff

    def __init__(self):
        self._reset_pin = machine.Pin(self.RST_PIN, machine.Pin.OUT)
        self._dc_pin = machine.Pin(self.DC_PIN, machine.Pin.OUT)
        self._cs_pin = machine.Pin(self.CS_PIN, machine.Pin.OUT)
        self._busy_pin = machine.Pin(self.BUSY_PIN, machine.Pin.IN, machine.Pin.PULL_UP)

        self._spi = machine.SPI(1)
        self._spi.init(baudrate=4000_000)

        self._buffer = bytearray(self.HEIGHT * self.WIDTH // 4)
        self.image = framebuf.FrameBuffer(self._buffer, self.WIDTH, self.HEIGHT, framebuf.GS2_HMSB)

        self._init()
        #self.clear()
        self._delay_ms(500)

    def turn_on_display(self) -> None:
        self._send_command(0x12)
        self._delay_ms(100)
        self._read_busy()

    # Hardware reset
    def reset(self) -> None:
        for _ in range(3):
            self._digital_write(self._reset_pin, 1)
            self._delay_ms(20)
            self._digital_write(self._reset_pin, 0)
            self._delay_ms(2)
        self._digital_write(self._reset_pin, 1)
        self._delay_ms(20)

    def clear(self) -> None:
        if self.WIDTH % 8 == 0:
            wide = self.WIDTH // 8
        else:
            wide = self.WIDTH // 8 + 1

        self._send_command(0x10)
        for j in range(0, self.HEIGHT):
            for i in range(0, wide):
                self._send_data(0xff)

        self._send_command(0x13)
        for j in range(0, self.HEIGHT):
            for i in range(0, wide):
                self._send_data(0xff)

        self._send_command(0x12)
        self._delay_ms(10)
        self.turn_on_display()

    def redraw(self) -> None:
        """
        Sends the image buffer to the display.
        """
        def send_bytes(temp: bool):
            for i in range(self.WIDTH * self.HEIGHT // 8):
                output_byte = 0

                # Iterate over the least significant and most significant bits of the pixel
                for j in range(2):
                    # Extract the pixel value from the image
                    pixel_value = self._buffer[i * 2 + j]

                    # Iterate over the two least significant and two most significant bits of the pixel value
                    for k in range(2):
                        # Extract the two least significant bits of the pixel value
                        pixel_bits = pixel_value & 0x03

                        # Set output_byte based on the value of pixel_bits
                        if pixel_bits == 0x03:
                            output_byte |= 0x01  # white
                        elif pixel_bits == 0x00:
                            output_byte |= 0x00  # black
                        elif pixel_bits == 0x02:
                            output_byte |= 0x00 if temp else 0x01  # gray1
                        else:  # 0x01
                            output_byte |= 0x01 if temp else 0x00  # gray2

                        # Shift output_byte one position to the left
                        output_byte <<= 1
                        # Shift pixel_value two positions to the right
                        pixel_value >>= 2
                        # Extract the two most significant bits of the pixel value
                        pixel_bits = pixel_value & 0x03

                        # Set output_byte based on the value of pixel_bits
                        if pixel_bits == 0x03:  # white
                            output_byte |= 0x01
                        elif pixel_bits == 0x00:  # black
                            output_byte |= 0x00
                        elif pixel_bits == 0x02:
                            output_byte |= 0x00 if temp else 0x01  # gray1
                        else:  # 0x01
                            output_byte |= 0x01 if temp else 0x00  # gray2

                        # If j is not equal to 1 or k is not equal to 1, shift output_byte one position to the left
                        if (j != 1) | (k != 1):
                            output_byte <<= 1

                        # Shift pixel_value two positions to the right
                        pixel_value >>= 2

                self._send_data(output_byte)

        self._send_command(0x10)
        send_bytes(True)

        self._send_command(0x13)
        send_bytes(False)

        self._lut()
        self.turn_on_display()

    def sleep(self) -> None:
        """
        Puts the display in sleep mode.
        """
        # self.send_command(0x02)  # power off
        # self.ReadBusy()
        self._send_command(0x07)  # deep sleep
        self._send_data(0xA5)

    def _digital_write(self, pin, value) -> None:
        pin.value(value)

    def _digital_read(self, pin) -> bool:
        return pin.value()

    def _delay_ms(self, delay) -> None:
        utime.sleep(delay / 1000.0)

    def _spi_writebyte(self, data) -> None:
        self._spi.write(bytearray(data))

    def _module_exit(self) -> None:
        self._digital_write(self._reset_pin, 0)

    def _send_command(self, command) -> None:
        self._digital_write(self._dc_pin, 0)
        self._digital_write(self._cs_pin, 0)
        self._spi_writebyte([command])
        self._digital_write(self._cs_pin, 1)

    def _send_data(self, data) -> None:
        self._digital_write(self._dc_pin, 1)
        self._digital_write(self._cs_pin, 0)
        self._spi_writebyte([data])
        self._digital_write(self._cs_pin, 1)

    def _read_busy(self) -> None:
        """
        Waits until the display is busy.
        """
        print("e-Paper busy")
        while not self._digital_read(self._busy_pin):  # LOW: idle, HIGH: busy
            self._send_command(0x71)
            self._delay_ms(100)
        print("e-Paper busy release")

    def _lut(self) -> None:
        self._send_command(0x20)
        for count in range(0, 42):
            self._send_data(LUT_VCOM[count])

        self._send_command(0x21)
        for count in range(0, 42):
            self._send_data(LUT_WW[count])

        self._send_command(0x22)
        for count in range(0, 42):
            self._send_data(LUT_BW[count])

        self._send_command(0x23)
        for count in range(0, 42):
            self._send_data(LUT_WB[count])

        self._send_command(0x24)
        for count in range(0, 42):
            self._send_data(LUT_BB[count])

        self._send_command(0x25)
        for count in range(0, 42):
            self._send_data(LUT_WW[count])

    def _init(self) -> None:
        self.reset()
        self._send_command(0x01)  # POWER SETTING
        self._send_data(0x03)
        self._send_data(0x00)  # VGH=20V,VGL=-20V
        self._send_data(0x2b)  # VDH=15V
        self._send_data(0x2b)  # VDL=-15V
        self._send_data(0x13)

        self._send_command(0x06)  # booster soft start
        self._send_data(0x17)  # A
        self._send_data(0x17)  # B
        self._send_data(0x17)  # C

        self._send_command(0x04)
        self._read_busy()

        self._send_command(0x00)  # panel setting
        self._send_data(0x3f)  # KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f

        self._send_command(0x30)  # PLL setting
        self._send_data(0x3c)  # 100hz

        self._send_command(0x61)  # resolution setting
        self._send_data(0x01)  # 400
        self._send_data(0x90)
        self._send_data(0x01)  # 300
        self._send_data(0x2c)

        self._send_command(0x82)  # vcom_DC setting
        self._send_data(0x12)

        self._send_command(0x50)  # VCOM AND DATA INTERVAL SETTING
        self._send_data(0x97)

