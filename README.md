# OPA
## Goal
The goal of this project is to build a mobile version of the [Ocular Photosensitivity Analyzer (OPA)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6238927/) that we can use to record light sensitivity outside the lab setting, like at peoples homes or in a hospital bed.

## Approach

## Parts
<details>
  <summary>Click here to see a description of all the parts.</summary>

#### 1. The light source
We choose to use 9 white light LEDs and use a Transistor for pulse with modulation dimming.
- [Diffused White 3mm LED](https://www.adafruit.com/product/778)
- [NPN Bipolar Transistors (PN2222)](https://www.adafruit.com/product/756)

#### 2. The Camera
We used an NoIR camera (i.e. no IR *filter*, therefore it can see IR) with a long wavelength LED to record pupil responses
- [Raspberry Pi NoIR Camera Board v2 - 8 Megapixels](https://www.adafruit.com/product/3100)
- [Super-bright 5mm IR LED - 940nm](https://www.adafruit.com/product/388)

#### 3. Button
- [Push button](https://www.amazon.com/dp/B07RW2YZ4W/?coliid=I2LNKEV2ZDSZ70&colid=2SN8Q5C0S8ZID&psc=1&ref_=lv_ov_lig_dp_it)

#### 4. The raspberry pi
A raspberry pi controls the light source, the camera, button presses and stores all the data. Because the LEDs run on 12V, we used a buck converter so the Pi and the LEDs could run off the same power adapter.
- [Raspberry Pi Zero W](https://www.adafruit.com/product/3708)
- [Micro SD card](https://www.adafruit.com/product/2693)
- [Zero2Go Omini – Multi-Channel Power Supply for Raspberry Pi](https://www.adafruit.com/product/4114)
- [12V DC 1000mA (1A) regulated switching power adapter - UL listed](https://www.adafruit.com/product/798)

#### 5. Housing
We used some PCB board to connect all LEDs. pAll parts were assembled inside a phone case to be able to use it with VR goggles

</details>

## Assembling the parts


## Setting up the RPiW
I am using a Rpi ZeroW. Getting it up and running

If you're not familiar with Raspberry pi, there are many tutorials online on how to get started. Here is a short summary of the steps.
1) Download latest version of Raspberry Pi OS (formarly raspbian) lite (I used 2020-05-27-raspios-buster-lite) and flash on SD card (I use balenaEtcher)
2) Add empty ssh files and wpa_supplicant.conf with network credential if you want to go wifi.
3) insert SD in RPi and boot.
4) Adjust hostname and password if desired with `sudo raspi-config` (recommended)
5) Always start by running `sudo apt-get update` and `sudo apt-get upgrade` (this may take some time)

## Set up GPIO for PWM
sudo apt install python3-pigpio

sudo pigpiod # need to run before running python #https://gpiozero.readthedocs.io/en/stable/remote_gpio.html#preparing-the-raspberry-pi

To automate running the daemon at boot time, run:
$ sudo systemctl enable pigpiod
To run the daemon once using systemctl, run:
$ sudo systemctl start pigpiod

http://abyz.me.uk/rpi/pigpio/python.html#hardware_PWM



#set upt the Pi for camera
sudo apt-get install -y python3-picamera

#### enable the camera
sudo raspi-config
5 interfacing options --> P1 Camera -->  <Yes>
7 advanced options --> A3 Memory split --> 256

sudo apt-get install ffmpeg




``` python3
import pigpio
import time

pi = pigpio.pi()
time.sleep(1)

def pwm(x):
 pi.hardware_PWM(12, 60, x * 10000)

try:
  while True:
    for p in range (0, 100, 5):
      pwm(p)
      time.sleep(0.1)

    for p in range (100, 0, -5):
      pwm(p)
      time.sleep(0.1)

except KeyboardInterrupt:
  pwm(0)
  pi.stop()
```

import pigpio
import time

pi = pigpio.pi()
time.sleep(1)

def pwm(x):
 pi.hardware_PWM(12, 60, x * 10000)

p = 1
while p < 100:
  pwm(p)
  time.sleep(2)
  pwm(0)
  time.sleep(1)
  p = p * 2
pwm(100)
time.sleep(2)
pwm(0)
pi.stop()










##install git
https://linuxize.com/post/how-to-install-git-on-raspberry-pi/

## install h264
http://jollejolles.com/installing-ffmpeg-with-h264-support-on-raspberry-pi/

##Save outputs
https://picamera.readthedocs.io/en/release-1.13/recipes2.html#custom-outputs
https://www.raspberrypi.org/forums/viewtopic.php?t=267096

https://wiki.debian.org/ffmpeg#Installation





# Set up GPIO for PWM
#https://www.radishlogic.com/raspberry-pi/raspberry-pi-pwm-gpio/

run `sudo apt-get install python3-rpi.gpio` on command line
set up a python script with:
`nano pwm_test.py`

``` python
import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
pwm32 = GPIO.PWM(32, 60)
pwm32.start(0)

try:
  while True:
    for dutyCycle in range (0, 100, 5):
      pwm32.ChangeDutyCycle(dutyCycle)
      time.sleep(0.1)

    for dutyCycle in range (100, 0, -5):
      pwm32.ChangeDutyCycle(dutyCycle)
      time.sleep(0.1)

except KeyboardInterrupt:
  pwm32.stop()

# Cleans the GPIO
GPIO.cleanup()
```

Save and close

`python3 pwm_test.py`

Need to switch to RPIO.GPIO to avoid software flicker
https://www.raspberrypi.org/forums/viewtopic.php?t=80223


https://pythonhosted.org/RPIO/pwm_py.html#examples

#install
`sudo apt-get install python-setuptools`
`sudo easy_install -U RPIO`

sudo apt-get install pip3

sudo apt-get install python3-pip
sudo pip3 install RPIO

``` python
from RPIO import PWM

# Setup PWM and DMA channel 0
PWM.setup()
PWM.init_channel(0)
PWM.add_channel_pulse(0, 17, 0, 100) #Granulaity is 10us #Subcycle is 20ms #100 is 100 * 10 = 1000us = 1ms
PWM.add_channel_pulse(0, 17, 0, 200)
PWM.clear_channel_gpio(0, 17)
PWM.cleanup()

```


https://www.raspberrypi.org/forums/viewtopic.php?p=1046060#p1046060



$ sudo apt install git
$ git clone https://github.com/metachris/RPIO.git #https://github.com/metachris/RPIO/tree/v2.zip #
$ cd RPIO
$ sudo python3 setup.py install

git clone https://github.com/JamesGKent/RPIO RPIO2

https://github.com/JamesGKent/RPIO/tree/v2

https://github.com/JamesGKent/RPIO/archive/v2.zip


wget https://github.com/metachris/RPIO/archive/v2.zip
sudo apt-get install python3-dev
unzip v2.zip
cd RPIO-2/
sudo python3 setup.py install
