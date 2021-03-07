# Setup Guide Part II - Particulate Sensor

## Hardware [[1]](#ref_1) [[2]](#ref_2):

 - PMS5003 Particulate Matter Sensor - £24.90
 - Pimoroni Breakout board for PMS5003 Sensor - £2.99

 ## Setup

 ## Installation

 #### Connect the Hardware [[3]](#ref_3)

 Use Female / Female Jumper wires to make the following connections between the PMS5003 and the Raspberry Pi:


     PMS5003 VCC to Raspberry Pi 5V  (5V power +)
     PMS5003 GND to Raspberry Pi GND (Ground -)
     PMS5003 TX  to Raspberry Pi GPIO14 (UART0_TXD Serial Transmit)
     PMS5003 RX  to Raspberry Pi GPIO15 (UART0_RXD Serial Receive)


 #### References with thanks
 <a id="ref_1"></a>[1] https://thepihut.com/ <br />
 <a id="ref_2 "></a>[2] https://coolcomponents.co.uk/ <br />
 <a id="ref_3 "></a>[3] https://www.rigacci.org/wiki/doku.php/doc/appunti/hardware/raspberrypi_air <br />
