# HTU21D(F)/Si7013/Si7020/Si7021/SHT21 i2c based temperature sensors support
#
# Copyright (C) 2020  Lucio Tarantino <lucio.tarantino@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
from sensor.HTU21D import HTU21D

HTU21D_I2C_ADDR = 0x40

class HTU21D_HOST:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.reactor = self.printer.get_reactor()
        self.report_time = config.getint('htu21d_report_time', 30, minval=5)
        i2c_addr = config.getint('htu21d_address', HTU21D_I2C_ADDR)
        self.htu = HTU21D(1, i2c_addr)
        self.temp = self.min_temp = self.max_temp = self.humidity = 0.
        self.sample_timer = self.reactor.register_timer(self._sample_htu21d)
        self.printer.add_object("htu21d_host " + self.name, self)
        self.printer.register_event_handler("klippy:connect",
                                            self.handle_connect)

    def handle_connect(self):
        self.reactor.update_timer(self.sample_timer, self.reactor.NOW)

    def setup_minmax(self, min_temp, max_temp):
        self.min_temp = min_temp
        self.max_temp = max_temp

    def setup_callback(self, cb):
        self._callback = cb

    def get_report_time_delta(self):
        return self.report_time

    def _sample_htu21d(self, eventtime):
        try:
            h = self.htu.humidity()
            self.humidity = h.RH
            t = self.htu.temperature()
            self.temp = t.C

        except Exception:
            logging.exception("htu21d: Error reading data")
            self.temp = self.humidity = .0
            return self.reactor.NEVER

        if self.temp < self.min_temp or self.temp > self.max_temp:
            self.printer.invoke_shutdown(
                "HTU21D temperature %0.1f outside range of %0.1f:%.01f"
                % (self.temp, self.min_temp, self.max_temp))

        # measured_time = self.reactor.monotonic()
        # print_time = self.i2c.get_mcu().estimated_print_time(measured_time)
        # self._callback(print_time, self.temp)

        mcu = self.printer.lookup_object('mcu')
        measured_time = self.reactor.monotonic()
        self._callback(mcu.estimated_print_time(measured_time), self.temp)
        return measured_time + self.report_time

    def get_temp(self, eventtime):
        return self.temp, 0.

    def get_status(self, eventtime):
        return {
            'temperature': round(self.temp, 2),
            'humidity': self.humidity
        }

def load_config(config):
    # Register sensor
    pheater = config.get_printer().lookup_object("heaters")
    pheater.add_sensor_factory('HTU21D_HOST', HTU21D_HOST)
