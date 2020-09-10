
import datetime as dt
import time
import os.path
import io
import csv

import subprocess

import picamera
import pigpio

### File name and path ###
path = '/home/pi/Recording'
date = dt.datetime.now().strftime("%d-%m-%Y_%H_%M_%S")
name = 'TEST'
filename     = name+'_'+date+'.h264'
filename_csv = name+'_'+date+'.csv'
complete_path     = os.path.join(path, filename)
complete_path_csv = os.path.join(path, filename_csv)

# Set up gpio
pi = pigpio.pi()
time.sleep(1)

pi.set_mode(23, pigpio.INPUT)
pi.set_pull_up_down(23, pigpio.PUD_UP)

def pwm(x):
 pi.hardware_PWM(12, 60, x * 10000)

# Set up recording fuctions
class MyOutput(object):
    def __init__(self, file, csvFile):
        self.frameNumber = 0
        self.output_file = io.open(file, 'wb')
        self.csvFile = open(csvFile, 'w', newline='')
        self.csvWriter = csv.writer(self.csvFile, delimiter=',',
        quotechar=',', quoting=csv.QUOTE_MINIMAL) #check all arguments
        self.csvWriter.writerow(['FrameNumber', 'CPUTemperature',
        'Time', 'ExposureSpeed', 'FrameRate','FrameRate_delta'])
        self.t0 = time.time()
    def write(self, buf):
        self.frameNumber += 1
        #UpdateLight(self.frameNumber)
        self.output_file.write(buf)
        t = time.time()-self.t0
        self.csvWriter.writerow([self.frameNumber, q,
        ('%.4f' % t), camera.exposure_speed, camera.framerate,
        camera.framerate_delta])

    def flush(self):
        print('%d frames captured' % self.frameNumber)
        self.output_file.flush()

    def close(self):
            self.output_file.close()


pi.write(16,1)
pwm(0)
p = 1
q = 0

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.framerate = 10
    time.sleep(1)
    print('Start recording')
    camera.start_recording(MyOutput(complete_path, complete_path_csv), format='h264')
    camera.wait_recording(5) #5
    while p < 50:
        pwm(p)
        q = p
        camera.wait_recording(2) #2
        pwm(0)
        q = 0
        camera.wait_recording(3) #3
        p = p * 2
        if pi.read(23) == 0:
            print("button pressed")
            p = 51
        print(p)
    pwm(0)
    camera.wait_recording(3) #3
    camera.stop_recording()

    from subprocess import CalledProcessError

    command = "ffmpeg -r {} -i {} -vcodec copy {}.mp4".format(camera.framerate ,complete_path, os.path.splitext(complete_path)[0])
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        os.remove(complete_path)
        print('Recording saved:',os.path.splitext(filename)[0],'.mp4')
    except CalledProcessError as e:
        print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))

pi.write(16,0)
pi.stop()
