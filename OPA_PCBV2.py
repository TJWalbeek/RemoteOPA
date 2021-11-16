
import datetime as dt
import time
import os.path
import os
import io
import csv
import subprocess
from subprocess import CalledProcessError
import picamera
import pigpio
pi = pigpio.pi()

button_pin = 27
data_retrieve_pin = 17
IR_pin1 = 22
IR_pin2 = 11
indicatorLed_pin = 19
indicatorLed_pin2 = 26
PWM_pin = 13

p = 0
q = 0
button_presses = 0
button_pressed = False
IndicatiorLED = False

pi.set_mode(IR_pin1, pigpio.OUTPUT)
pi.set_mode(IR_pin2, pigpio.OUTPUT)

def set_filenames():
    ### File name and path ###
    path = '/home/pi/Recording'
    #date = dt.datetime.now().strftime("%d-%m-%Y_%H_%M_%S")
    date = dt.datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
    name = 'Data'
    filename     = name+'_'+date+'.h264'
    filename_csv = name+'_'+date+'.csv'
    complete_path     = os.path.join(path, filename)
    complete_path_csv = os.path.join(path, filename_csv)
    return(path, date, name, filename, filename_csv, complete_path, complete_path_csv)

def set_up_pins():
    global pi

    # Set up gpio
    time.sleep(1)
    #Set button pin
    pi.set_mode(button_pin, pigpio.INPUT)
    pi.set_pull_up_down(button_pin, pigpio.PUD_UP)
    #Set data pin
    pi.set_mode(data_retrieve_pin, pigpio.INPUT)
    pi.set_pull_up_down(data_retrieve_pin, pigpio.PUD_UP)
    #Set up LED print
    pi.set_mode(indicatorLed_pin, pigpio.OUTPUT) # GPIO 17 as output
    pi.set_mode(IR_pin1, pigpio.OUTPUT) # For IR
    pi.set_mode(IR_pin2, pigpio.OUTPUT) # For IR

    pi.write(indicatorLed_pin, True)
    time.sleep(0.5)
    pi.write(indicatorLed_pin, False)

def pwm(x):
    global pi, q
    '''
    x is the light intensity as % duty cycle.
    '''
    pi.hardware_PWM(PWM_pin, 10000, int(x * 10000))
    q = x #set parameter for saving curring light intensity

def set_up_starting_paramters():
    global p, pi, button_presses, button_pressed, IndicatiorLED

    p = 1/64#4 #0.125 #Set first light intencity
    button_presses = 0
    button_pressed = False
    #pi.hardware_PWM(13, 120, 100000) #turn on IR LEDs
    pi.write(IR_pin1, True)
    pi.write(IR_pin2, True)
    pwm(0) #initiate the pwm for main lights
    IndicatiorLED = True
    pi.write(indicatorLed_pin, IndicatiorLED)

def wait_for_start_press():
    global pi, IndicatiorLED
    start = False
    while not start:
        #blink LED
        IndicatiorLED = not IndicatiorLED
        pi.write(indicatorLed_pin, IndicatiorLED)

        #Check for button press
        if pi.read(button_pin) == 0:
            start = True
            IndicatiorLED = False
            pi.write(indicatorLed_pin, IndicatiorLED)
        time.sleep(0.5)

def set_camera_settings():
    global camera
    camera.resolution = (640, 480)
    #camera.zoom = (0.15,0,0.7,0.7) #(x, y, w, h)
    camera.color_effects = (128,128) #Grayscale
    camera.framerate = 10
    time.sleep(0.1)

def start_the_recording(x):
    '''
    x: integer to set duration for baseline recording
    '''
    set_camera_settings()
    camera.start_recording(MyOutput(complete_path, complete_path_csv), format='h264')
    camera.wait_recording(x) #5

def pulse_lights(x):
    pwm(p) #Turns on light
    camera.wait_recording(x) #Record for x secs
    pwm(0) #Turn off lights

def record_button_press_between_lights(x):
    global button_presses, button_pressed
    t1= time.time()
    wait = True
    button_pressed = False
    while wait:
        camera.wait_recording(0.1) #3
        if pi.read(button_pin) == 0 and button_pressed == False:
            print("button pressed")
            button_presses += 1
            button_pressed = True
        t2= time.time()
        if t2 - t1 > x:
            wait = False

def update_light_intensity():
    global p, button_presses
    if button_pressed:
        p = p / 4
    else:
        p = p * 2
    if p > 100:
        p = 99
        button_presses += 1


def record_button_duration():
    while pi.read(button_pin) == 1:
    	time.sleep(0.1)

    t1 = time.time()
    while pi.read(button_pin) == 0:
    	time.sleep(0.1)
    t2 = time.time()
    IndicatiorLED = False
    pi.write(indicatorLed_pin, IndicatiorLED)
    return t2 - t1

# Set up recording fuctions
class MyOutput(object):
    def __init__(self, file, csvFile):
        self.frameNumber = 0
        self.output_file = io.open(file, 'wb')
        self.csvFile = open(csvFile, 'w', newline='')
        self.csvWriter = csv.writer(self.csvFile, delimiter=',',
        quotechar=',', quoting=csv.QUOTE_MINIMAL) #check all arguments
        self.csvWriter.writerow(['FrameNumber', 'Light',
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

path, date, name, filename, filename_csv, complete_path, complete_path_csv = set_filenames()
set_up_pins()

if pi.read(data_retrieve_pin) == 0:
    print("ResearchMode")
    pi.write(indicatorLed_pin2, True)
    time.sleep(1.5)
    pi.write(indicatorLed_pin2, False)
    pi.stop()
    exit()

set_up_starting_paramters()
print("Ready to start. Press button when ready.")
wait_for_start_press()
print("Starting...")

with picamera.PiCamera() as camera:
    #Start recording and record 5 seconds of baseline
    print('Start recording')
    start_the_recording(5)

    while button_presses < 3:
        #print(p)
        pulse_lights(2.5) #Turns on light for x seconds
        record_button_press_between_lights(7.5)
        update_light_intensity()

    pwm(0)
    camera.wait_recording(3) #3
    #Turn of camera and IR led
    camera.stop_recording()
    pi.write(IR_pin1, False)
    pi.write(IR_pin2, False)
    #pi.hardware_PWM(13, 120, 0)

    # Convert video file to .mp4
    command = "ffmpeg -r {} -i {} -vcodec copy {}.mp4".format(camera.framerate ,complete_path, os.path.splitext(complete_path)[0])
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        os.remove(complete_path)
        print('Recording saved:',os.path.splitext(filename)[0],'.mp4')
    except CalledProcessError as e:
        print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))

#turn on indicatior light to indicate saving file is done
IndicatiorLED = True
pi.write(indicatorLed_pin, IndicatiorLED)

#print("Done, restart (1sec) or turn off (5 sec)")
#t_delta = record_button_duration()
#print(f"Button was pressed for {t_delta} seconds")
print("Done. Press button to shut down.")
wait_for_start_press()

pi.stop()

os.system("sudo shutdown now")
