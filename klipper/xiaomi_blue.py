# HTU21D(F)/Si7013/Si7020/Si7021/SHT21 i2c based temperature sensors support
#
# Copyright (C) 2020  Lucio Tarantino <lucio.tarantino@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
from bluepy import btle
import struct
from threading import Thread
from multiprocessing import Process


class XIAOMI_BLUE:
    _blue_connect = None

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.reactor = self.printer.get_reactor()
        self.report_time = config.getint('report_time', 20, minval=10)
        self.mac = config.get('mac_address')
        self.temp = self.min_temp = self.max_temp = self.humidity = self.voltage = self.battery = 0.
        self.sample_timer = self.reactor.register_timer(self._sample_read)
        self.printer.add_object("xiaomi_blue " + self.name, self)
        self.printer.register_event_handler("klippy:connect",
                                            self.handle_connect)
        self.printer.register_event_handler("klippy:disconnect",
                                            self.handle_disconnect)
        self._thread = None

    def connect(self):
        if self._blue_connect is None:
            self._blue_connect = btle.Peripheral(self.mac)
        return self._blue_connect

    def close(self):
        if self._blue_connect is not None:
            self._blue_connect.disconnect()
        self._blue_connect = self._thread = None

    def handle_connect(self):
        self.reactor.update_timer(self.sample_timer, self.reactor.NOW)

    def handle_disconnect(self):
        self.close()

    def setup_minmax(self, min_temp, max_temp):
        self.min_temp = min_temp
        self.max_temp = max_temp

    def setup_callback(self, cb):
        self._callback = cb

    def get_report_time_delta(self):
        return self.report_time

    def _sample_read(self, eventtime):
        # try:
        #     if self._thread is None or not self._thread.isAlive():
        #         self._thread = XiaoMiTempBt(self)
        #         self._thread.start()
        #     else:
        #         logging.info('xiaomi: thread is alive!')
        # except Exception as e:
        #     logging.info("xiaomi error: %s" % e.message)
        #     self.close()
        try:
            if self._thread is None or not self._thread.is_alive():
                self._thread = Process(target=self.read())
                self._thread.start()
            else:
                logging.info('xiaomi: thread is alive!')
        except Exception as e:
            logging.info("xiaomi error: %s" % e.message)

        mcu = self.printer.lookup_object('mcu')
        measured_time = self.reactor.monotonic()
        self._callback(mcu.estimated_print_time(measured_time), self.temp)
        return measured_time + self.report_time

    def read(self):
        try:
            p = self.connect()
            p.writeCharacteristic(0x0038, b'\x01\x00', True)
            p.writeCharacteristic(0x0046, b'\xf4\x01\x00', True)
            measure = Measure(self)
            p.withDelegate(measure)

            if not p.waitForNotifications(1000):
                logging.info('xiaomi: read timeout!')
            self.close()

        except Exception as e:
            logging.info("xiaomi error: %s" % e.message)
            self.close()

    def get_temp(self, eventtime):
        return self.temp, 0.

    def get_status(self, eventtime):
        return {
            'temperature': round(self.temp, 2),
            'humidity': self.humidity,
            'voltage': self.voltage,
            'battery': self.battery
        }


class XiaoMiTempBt(Thread):
    def __init__(self, obj):
        super(XiaoMiTempBt, self).__init__()
        self.obj = obj

    def run(self):
        try:
            p = self.obj.connect()
            p.writeCharacteristic(0x0038, b'\x01\x00', True)
            p.writeCharacteristic(0x0046, b'\xf4\x01\x00', True)
            measure = Measure(self.obj)
            p.withDelegate(measure)

            if not p.waitForNotifications(1000):
                logging.info('xiaomi: read timeout!')
            self.obj.close()

        except Exception as e:
            logging.info("xiaomi error: %s" % e.message)
            self.obj.close()


class Measure(btle.DefaultDelegate):
    battery = None  # type: float
    voltage = None  # type: int
    humidity = None  # type: int
    temp = None  # type: int

    def __init__(self, obj):
        self.obj = obj
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        try:
            t = data[0:2].encode('hex').decode('hex')
            temp = float(struct.unpack('<h', t)[0]) / 100
            if temp > 0:
                self.obj.temp = temp
            humidity = int(data[2:3].encode('hex'), 16)
            if humidity > 0:
                self.obj.humidity = humidity
            v = data[3:5].encode('hex').decode('hex')
            voltage = float(struct.unpack('<h', v)[0]) / 1000
            if voltage > 0:
                self.obj.voltage = voltage
            battery = round((voltage - 2) / (3.261 - 2) * 100, 2)
            if battery > 0:
                self.obj.battery = battery
            logging.info("xiaomi: temp=%f, humidity=%f, voltage=%f, battery=%f" % (temp, humidity, voltage, battery))

        except Exception as e:
            logging.info("xiaomi error: %s" % e.message)


def load_config(config):
    # Register sensor
    pheater = config.get_printer().lookup_object("heaters")
    pheater.add_sensor_factory('XIAOMI_BLUE', XIAOMI_BLUE)
