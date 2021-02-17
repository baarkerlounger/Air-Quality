# -*- coding: utf-8 -*-

import time
from influxdb import InfluxDBClient
import Adafruit_MCP3008

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('co2')

# Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)


# Take a sensor reading every 5 seconds and write it to  InfluxDB
while True:
    SENSOR_CHANNEL = 1
    sensor_value = mcp.read_adc(SENSOR_CHANNEL)
    # https://e2e.ti.com/blogs_/archives/b/precisionhub/archive/2016/04/01/it-s-in-the-math-how-to-convert-adc-code-to-a-voltage-part-1
    # FSR (Full Scale Range) = 3300mV (3.3V reference voltage)
    # MCP3008 is a 10bit ADC so 2^10 codes/values available to represent the full scale range (0-1023)
    # LSB size = FSR/2^N = 3300 / 1024
    FULL_SCALE_RANGE = 3300
    ADC_CODES = 1024.0
    lsb_size = FULL_SCALE_RANGE / ADC_CODES
    voltage = sensor_value * lsb_size
    if (voltage == 0):
        concentration =  None
        error = 50.0
    elif (voltage < 400):
        concentration = None
        error = 50.0
    else:
        # Convert the voltage into concentration in parts per million.
        # The Gravity  Infrared  CO2 Sensor  V1.1 can measure 0-5000ppm and does so by outputting a signal of 0.4-2V
        # so we scale that voltage range over our values. e.g.
        # (400mV - 400) * 50 / 16 = 0 ppm
        # (800mV - 400) * 50 / 16 = 1250 ppm
        # (1200mV - 400) * 50 / 16 = 2500 ppm
        # (2000mV - 400) * 50 / 16 = 5000 ppm
        voltage_difference = voltage - 400
        concentration = voltage_difference * 50.0 / 16.0
        # Accuracy of the Gravity Infrared CO2 Sensor V1.1 is ± 50ppm + 3%
        error = 50 + ((concentration / 100) * 3)
    json_body = [
        {
            "measurement": "co2_reading",
            "tags": {},
            "fields": {
                "voltage": voltage,
                "concentration": concentration,
                "error": error
            }
        }
    ]
    client.write_points(json_body)
    time.sleep(5)
