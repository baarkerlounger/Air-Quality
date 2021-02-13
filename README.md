# Raspberry Pi Zero based Air Quality Monitoring Project

## Hardware [[1]](#ref_1):

- 1 Raspberry Pi Zero WH (with pre-soldered header) - £ 13.50

- 1 Gravity: Analog Infrared CO2 Sensor For Arduino (0~5000 ppm) - £ 61.00

- 1 MCP3008 - 8-Channel 10-Bit ADC With SPI Interface - £ 3.00

- 1 Raspberry Pi Breadboard (Half Size) - £ 3.00

- 1 The Pi Hut Jumper Bumper Pack (120pcs Dupont Wire) - £ 6.00

- 1 Micro SD Card 16GB - £ 7.00

We use a Raspberry Pi Zero WH as our microcontroller. Since it doesn't have an inbuilt Analog to Digital converter like Arduinos do we need to add an external ADC to our circuit for which we use the MCP3008.

## Setup

## Installation

#### Connect the Hardware [[2]](#ref_2), [[3]](#ref_3)

![MCP3008 pin diagram](images/setup/mcp3008-pins.gif) ![Raspberry Pi Zero pin diagram](images/setup/raspberry-pi-pins.png)

<br></br>

#### Prepare the Raspberry Pi OS [[4]](#ref_4)

Download the Raspberry Pi Imager from https://www.raspberrypi.org/software/ (Raspberry PI imager) and use it to write `Raspberry Pi OS with desktop and recommended software (32 bit)` (the default option) to the MicroSD card.

To enable SSH access place an empty file named <i> ssh </i> into the <i> boot </i>  folder of the <i> boot </i> partition.

```
touch /media/$USER/boot/ssh
```

Pre-configure WIFI access by adding a file named <i> wpa_supplicant.conf </i> there as well:

```
touch wpa_supplicant.conf
echo 'country=GB   
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
   ssid="NETWORK-NAME"
   psk="NETWORK-PASSWORD"
}' > wpa_supplicant.conf

# Flush the write cache
sync
```

Where NETWORK-NAME is the SSID and NETWORK-PASSWORD the password of the WIFI network you want the Raspberry Pi Zero to connect to.

Now insert the MicroSD card into the Raspberry Pi Zero and connect power.

You should be able to connect to it from another device on the same network now using:

```
# Check the Pi is accessible (default name is raspberrypi or use its IP)
ping raspberrypi

# Access the Pi via SSH. The default password is 'raspberry'
ssh pi@raspberrypi
```

Change the default password using:

```
passwd

# Type your old and new password
```

and then run any available updates:

```
sudo apt-get update
sudo apt-get dist-upgrade
sudo apt-get clean
```

<br></br>

#### Install InfluxDB [[5]](#ref_5)

We're going to use InfluxDB as the timeseries database to store our sensor values. It'll be added as a data source in Grafana.

```
# Add the repo key
wget -qO- https://repos.influxdata.com/influxdb.key | sudo apt-key add -
```

```
# Add the repo to your sources
echo "deb https://repos.influxdata.com/debian buster stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
```

```
sudo apt-get update && sudo apt-get install -y influxdb
```

Start the service using systemd and set the config file

```
sudo service influxdb start
```

```
influxd -config /etc/influxdb/influxdb.conf
```

```
echo $INFLUXDB_CONFIG_PATH /etc/influxdb/influxdb.conf
```

```
influxd
```

```
sudo service influxdb restart
```

Next we can use the InfluxDB CLI to check everything is working correctly and create our database ready to write to:

```
# Launch CLI
influx
```

```
create database co2
```

Your InfluxDB instance should now be available on `http://localhost:8086`

<br></br>

#### Install Grafana [[6]](#ref_6)

We're going to use Grafana to visualise our CO2 sensor data over time. The Raspberry PI is armv6 based, packages are available at https://grafana.com/grafana/download?platform=arm.

```
# Install dependencies
sudo apt-get install -y adduser libfontconfig1
```

```
# Download the .deb package
wget https://dl.grafana.com/oss/release/grafana-rpi_7.4.1_armhf.deb
```

```
# Install the downloaded package
sudo dpkg -i grafana-rpi_7.4.1_armhf.deb
```

Your Grafana instance should now be available on:
`http://raspberrypi:3000` or `http://<IP>:3000` from any device on the same network.

<br> </br>

##### Read Sensor Values and Write them to InfluxDB [[7]](#ref_7), [[8]](#ref_8)

```
# Install dependencies
sudo apt-get install git build-essential python-dev
```

Install the MCP3008 library (https://github.com/adafruit/Adafruit_Python_MCP3008)

```
git clone https://github.com/adafruit/Adafruit_Python_MCP3008.git
cd Adafruit_Python_MCP3008
sudo python setup.py install
```

```
# Install InfluxDB Python library
pip install influxdb
```

Copy the provided `co2.py` script.

The script reads in the sensor value from Channel 1 on the ADC - if you've connected the Gravity Sensor Signal output to a different channel then adjust the code accordingly (line 27).

We then calculate the LSB (Least Significant Bit) size of the ADC using the formula:
```
LSB size = FSB * no_ADC_CODES
```

where:
 -  FSB is the Full Scale Range of the values we are representing. In this case the Gravity Infrared Sensor V1.1 measures CO2 concentrations from 0 to 5000 ppm (parts per million) so our FSB is 5000.

 - no_ADC_CODES is the number of digital output codes/values the ADC has available to represent the FSB. In this case the MCP3008 we are using is a 10Bit ADC so we have 2^10 = 1024 codes available.

We calculate the output voltage of the sensor by
 ```
 voltage = sensor_value * lsb_size
 ```

 i.e.

 ```
 voltage = sensor_value * (5000 / 1024.0)
 ```

 The Gravity Infrared CO2 Sensor V1.1 output signal has a range from 0.4V - 2V. If our calculated voltage is below 0.4V (400mV) we know the sensor is still pre-heating (~3 mins).

 If it's between 0.4V and 2V we need to convert it back to concentration in ppm.

 We do that by scaling our available output voltage values (1600mV) over the range of measurement values (5000ppm):

 ```
 (voltage - 400) * 50.0 / 16.0
 ```

 Giving for example:

 ```
 (400mV - 400) * 50 / 16 = 0 ppm
 (800mV - 400) * 50 / 16 = 1250 ppm
 (1200mV - 400) * 50 / 16 = 2500 ppm
 (2000mV - 400) * 50 / 16 = 5000 ppm
 ```

 We calculate the associated error using the stated accuracy of the CO2 sensor (± 50ppm + 3%):

 ```
 error = 50 + ((calculated_concentration / 100) * 3)
 ```

This does not account for any additional error introduced by the ADC.

<br> </br>

##### Use SystemD to start and run our Python script automatically

Copy the provided `co2_monitor.service` file to `/etc/systemd/system/co2_monitor.service` and then enable and start the service:

The service file assumes that your python script is located at `/home/$USER/Adafruit_Python_MCP3008/co2.py`. If it is located elsewhere adjust the `ExecStart` command accordingly.

```
sudo systemctl daemon-reload
sudo systemctl enable co2_monitor.service
sudo systemctl start co2_monitor.service
```


#### References with thanks
<a id="ref_1"></a>[1] https://thepihut.com/ <br />
[<a id="ref_2"></a>2] https://raspberrypi.stackexchange.com/questions/83610/gpio-pinout-orientation-raspberypi-zero-w <br />
<a id="ref_3"></a>[3] https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008 <br />
<a id="ref_4"></a>[4] https://qrys.ch/setting-up-a-raspberry-pi-zero-w-wh-the-headless-way-with-wifi-and-vnc/ <br />
<a id="ref_5"></a>[5] https://www.circuits.dk/install-grafana-influxdb-raspberry/ <br />
<a id="ref_6"></a>[6] https://computingforgeeks.com/install-influxdb-on-debian-10-buster-linux/ <br />
<a id="ref_7"></a>[7] https://circuitdigest.com/microcontroller-projects/interfacing-gravity-inrared-co2-sensor-to-measure-carbon-dioxide-in-ppm <br />
<a id="ref_8"></a>[8] https://e2e.ti.com/blogs_/archives/b/precisionhub/archive/2016/04/01/it-s-in-the-math-how-to-convert-adc-code-to-a-voltage-part-1
