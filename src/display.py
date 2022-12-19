import machine
import framebuf
import utime

# 0~3 gray
EPD_4IN2_4Gray_lut_vcom = [
    0x00, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x60, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x00, 0x14, 0x00, 0x00, 0x00, 0x01,
    0x00, 0x13, 0x0A, 0x01, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00
]
# R21
EPD_4IN2_4Gray_lut_ww = [
    0x40, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x90, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x10, 0x14, 0x0A, 0x00, 0x00, 0x01,
    0xA0, 0x13, 0x01, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]
# R22H r
EPD_4IN2_4Gray_lut_bw = [
    0x40, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x90, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x00, 0x14, 0x0A, 0x00, 0x00, 0x01,
    0x99, 0x0C, 0x01, 0x03, 0x04, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]
# R23H w
EPD_4IN2_4Gray_lut_wb = [
    0x40, 0x0A, 0x00, 0x00, 0x00, 0x01,
    0x90, 0x14, 0x14, 0x00, 0x00, 0x01,
    0x00, 0x14, 0x0A, 0x00, 0x00, 0x01,
    0x99, 0x0B, 0x04, 0x04, 0x01, 0x01,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]
#  R24H b
EPD_4IN2_4Gray_lut_bb = [
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

        self._busy_pin = machine.Pin(self.BUSY_PIN, machine.Pin.IN, machine.Pin.PULL_UP)
        self._cs_pin = machine.Pin(self.CS_PIN, machine.Pin.OUT)

        self._lut_4Gray_vcom = EPD_4IN2_4Gray_lut_vcom
        self._lut_4Gray_ww = EPD_4IN2_4Gray_lut_ww
        self._lut_4Gray_bw = EPD_4IN2_4Gray_lut_bw
        self._lut_4Gray_wb = EPD_4IN2_4Gray_lut_wb
        self._lut_4Gray_bb = EPD_4IN2_4Gray_lut_bb

        self._spi = machine.SPI(1)
        self._spi.init(baudrate=4000_000)
        self._dc_pin = machine.Pin(self.DC_PIN, machine.Pin.OUT)

        self._buffer = bytearray(self.HEIGHT * self.WIDTH // 4)
        self.image = framebuf.FrameBuffer(self._buffer, self.WIDTH, self.HEIGHT, framebuf.GS2_HMSB)

        self.init()
        self.clear()
        utime.sleep_ms(500)

    def _digital_write(self, pin, value):
        pin.value(value)

    def _digital_read(self, pin):
        return pin.value()

    def delay_ms(self, delay):
        utime.sleep(delay / 1000.0)

    def _spi_writebyte(self, data):
        self._spi.write(bytearray(data))

    def module_exit(self):
        self._digital_write(self._reset_pin, 0)

    # Hardware reset
    def reset(self):
        for _ in range(3):
            self._digital_write(self._reset_pin, 1)
            self.delay_ms(20)
            self._digital_write(self._reset_pin, 0)
            self.delay_ms(2)
        self._digital_write(self._reset_pin, 1)
        self.delay_ms(20)

    def send_command(self, command):
        self._digital_write(self._dc_pin, 0)
        self._digital_write(self._cs_pin, 0)
        self._spi_writebyte([command])
        self._digital_write(self._cs_pin, 1)

    def send_data(self, data):
        self._digital_write(self._dc_pin, 1)
        self._digital_write(self._cs_pin, 0)
        self._spi_writebyte([data])
        self._digital_write(self._cs_pin, 1)

    def read_busy(self):
        """
        Waits until the display is busy.
        """
        print("e-Paper busy")
        while self._digital_read(self._busy_pin) == 0:  # LOW: idle, HIGH: busy
            self.send_command(0x71)
            self.delay_ms(100)
        print("e-Paper busy release")

    def turn_on_display(self):
        self.send_command(0x12)
        self.delay_ms(100)
        self.read_busy()

    def lut(self):
        self.send_command(0x20)
        for count in range(0, 42):
            self.send_data(self._lut_4Gray_vcom[count])

        self.send_command(0x21)
        for count in range(0, 42):
            self.send_data(self._lut_4Gray_ww[count])

        self.send_command(0x22)
        for count in range(0, 42):
            self.send_data(self._lut_4Gray_bw[count])

        self.send_command(0x23)
        for count in range(0, 42):
            self.send_data(self._lut_4Gray_wb[count])

        self.send_command(0x24)
        for count in range(0, 42):
            self.send_data(self._lut_4Gray_bb[count])

        self.send_command(0x25)
        for count in range(0, 42):
            self.send_data(self._lut_4Gray_ww[count])

    def init(self):
        self.reset()
        self.send_command(0x01)  # POWER SETTING
        self.send_data(0x03)
        self.send_data(0x00)  # VGH=20V,VGL=-20V
        self.send_data(0x2b)  # VDH=15V
        self.send_data(0x2b)  # VDL=-15V
        self.send_data(0x13)

        self.send_command(0x06)  # booster soft start
        self.send_data(0x17)  # A
        self.send_data(0x17)  # B
        self.send_data(0x17)  # C

        self.send_command(0x04)
        self.read_busy()

        self.send_command(0x00)  # panel setting
        self.send_data(0x3f)  # KW-3f   KWR-2F	BWROTP 0f	BWOTP 1f

        self.send_command(0x30)  # PLL setting
        self.send_data(0x3c)  # 100hz

        self.send_command(0x61)  # resolution setting
        self.send_data(0x01)  # 400
        self.send_data(0x90)
        self.send_data(0x01)  # 300
        self.send_data(0x2c)

        self.send_command(0x82)  # vcom_DC setting
        self.send_data(0x12)

        self.send_command(0x50)  # VCOM AND DATA INTERVAL SETTING
        self.send_data(0x97)

    def clear(self):
        if self.WIDTH % 8 == 0:
            wide = self.WIDTH // 8
        else:
            wide = self.WIDTH // 8 + 1

        self.send_command(0x10)
        for j in range(0, self.HEIGHT):
            for i in range(0, wide):
                self.send_data(0xff)

        self.send_command(0x13)
        for j in range(0, self.HEIGHT):
            for i in range(0, wide):
                self.send_data(0xff)

        self.send_command(0x12)
        self.delay_ms(10)
        self.turn_on_display()

    def draw_image(self, image):
        def for_each_pixel():
            for i in range(self.WIDTH * self.HEIGHT // 8):
                output_byte = 0

                # Iterate over the least significant and most significant bits of the pixel
                for j in range(2):
                    # Extract the pixel value from the image
                    pixel_value = image[i * 2 + j]

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
                            output_byte |= 0x00  # gray1
                        else:  # 0x01
                            output_byte |= 0x01  # gray2

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
                            output_byte |= 0x01  # gray1
                        else:  # 0x01
                            output_byte |= 0x00  # gray2

                        # If j is not equal to 1 or k is not equal to 1, shift output_byte one position to the left
                        if (j != 1) | (k != 1):
                            output_byte <<= 1

                        # Shift pixel_value two positions to the right
                        pixel_value >>= 2

                self.send_data(output_byte)

        self.send_command(0x10)
        for_each_pixel()

        self.send_command(0x13)
        for_each_pixel()

        self.lut()
        self.turn_on_display()

    def sleep(self):
        # self.send_command(0x02)  # power off
        # self.ReadBusy()
        self.send_command(0x07)  # deep sleep
        self.send_data(0xA5)
