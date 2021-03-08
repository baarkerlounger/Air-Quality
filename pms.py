
#!/usr/bin/env python

from pms5003 import PMS5003
from influxdb import InfluxDBClient
import time

client = InfluxDBClient(host='localhost', port=8086)
client.switch_database('air_quality')

# Configure the PMS5003
pms5003 = PMS5003(
    device='/dev/ttyAMA0',
    baudrate=9600,
)

try:
    while True:
        data = pms5003.read()
        json_body = [
            {
                "measurement": "particulates",
                "tags": {},
                "fields": {
                    "pm1.0": data.pm_ug_per_m3(1.0),
                    "pm2.5": data.pm_ug_per_m3(2.5),
                    "pm10": data.pm_ug_per_m3(10)
                }
            }
        ]
        client.write_points(json_body)
        time.sleep(5)
