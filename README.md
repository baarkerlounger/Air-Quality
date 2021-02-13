# Raspberry Pi Zero based Air Quality Monitoring Project

## Hardware:

- 1 Raspberry Pi Zero WH (with pre-soldered header) - £ 13.50

- 1 Gravity: Analog Infrared CO2 Sensor For Arduino (0~5000 ppm) - £ 61.00

- 1 MCP3008 - 8-Channel 10-Bit ADC With SPI Interface - £ 3.00

- 1 Raspberry Pi Breadboard (Half Size) - £ 3.00

- 1 The Pi Hut Jumper Bumper Pack (120pcs Dupont Wire) - £ 6.00

- 1 'NOOBS' Preinstalled Micro SD Card (Latest v3.4.0) 16GB - £ 7.00

We use a Raspberry Pi Zero WH as our microcontroller. Since it doesn't have an inbuilt Analog to Digital converter like Arduinos do we need to add an external ADC to our circuit for which we use the MCP3008.

## Setup

## Installation

#### Prepare the Raspberry Pi Zero

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

#### Install InfluxDB

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
