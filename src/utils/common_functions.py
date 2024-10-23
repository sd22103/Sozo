import cv2
import RPi.GPIO as GPIO
from gpiozero import OutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory
from datetime import datetime
import time
import os

class Camera:
    """Camera class to capture picture or video.
    """
    def __init__(self, dev_id=0, path=None):
        """Initialize the camera object.

        Parameters
        ----------
        dev_id : int, optional
            Device ID of the camera, by default 0
        path : str, optional
            Path of the directory to save the picture or video, by default None
        """
        self.cap = cv2.VideoCapture(dev_id)
        self.path = path
        if path is None:
            self.path = os.getcwd()
        if not self.cap.isOpened():
            print('Failed to open camera.')
        

    def capt_picture(self, width=640, height=480, file_name=None):
        """Capture a picture from the camera.

        Parameters
        ----------
        width : int, optional
            Width of the picture, by default 640
        height : int, optional
            Height of the picture, by default 480
        file_name : str, optional
            Name of the picture file, by default None
        """
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        ret, frame = self.cap.read()
        if ret:
            if file_name is None:
                file_name = datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'
            path = os.path.join(self.path, file_name)
            cv2.imwrite(path, frame)
        else:
            print('Failed to capture picture.')
            return
        self.cap.release()
        cv2.destroyAllWindows()
        return
    
    def capt_video(self, width=640, height=480, rec_sec=5, fps=30, fourcc=('m', 'p', '4', 'v'), file_name=None):
        """Capture a video from the camera.

        Parameters
        ----------
        width : int, optional
            Width of the video, by default 640
        height : int, optional
            Height of the video, by default 480
        rec_sec : int, optional
            Duration of the video in seconds, by default 5
        fps : int, optional
            Frame per second, by default 30
        fourcc : tuple, optional
            FourCC code, by default ('m', 'p', '4', 'v')
        file_name : str, optional
            Name of the video file, by default None
        """
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        fourcc = cv2.VideoWriter_fourcc(*fourcc)
        if file_name is None:
            file_name = datetime.now().strftime('%Y%m%d%H%M%S') + '.mp4'
        path = os.path.join(self.path, file_name)
        out = cv2.VideoWriter(path, fourcc, fps, (width, height))
        for _ in range(fps * rec_sec):
            ret, frame = self.cap.read()
            if not ret:
                print('Failed to capture video.')
                return
            out.write(frame)
        self.cap.release()
        out.release()
        cv2.destroyAllWindows()
        return
    
    def __del__(self):
        """Release the camera and close the window.
        """
        self.cap.release()
        cv2.destroyAllWindows()
    

class UltrasonicSensor:
    """Ultrasonic distance sensor class to measure distance.
    """
    def __init__(self, trig=27, echo=18):
        """Initialize the ultrasonic distance sensor.

        Parameters
        ----------
        trig : int, optional
            GPIO pin number for the trigger, by default 27
        echo : int, optional
            GPIO pin number for the echo, by default 18
        """
        self.trig = trig
        self.echo = echo
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trig, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
    
    def read_distance(self):
        """Read the distance from the ultrasonic distance sensor.

        Returns
        -------
        float
            Distance in cm
        """
        GPIO.output(self.trig, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(self.trig, GPIO.LOW)
        while GPIO.input(self.echo) == GPIO.LOW:
            sig_off = time.time()
        while GPIO.input(self.echo) == GPIO.HIGH:
            sig_on = time.time()
        duration = sig_off - sig_on
        distance = duration * 17000
        return distance
    
    def __del__(self):
        """Clean up the GPIO pins.
        """
        GPIO.cleanup()


class MotionSensor:
    def __init__(self, pin=14):
        """Initialize the motion sensor.

        Parameters
        ----------
        pin : int, optional
            GPIO pin number for the motion sensor, by default 14
        """
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)

    def detect_human(self):
        return GPIO.input(self.pin) == GPIO.HIGH
    
    def __del__(self):
        """Clean up the GPIO pins.
        """
        GPIO.cleanup()


class Stepper():
    """Stepper motor class to control the stepper motor.
    """
    def __init__(self, number_of_steps, mpins=[21, 17, 27, 22], method_step="half"):
        """Initialize the stepper motor.

        Parameters
        ----------
        number_of_steps : int
            Number of steps per revolution 
        mpins : list, optional
            List of GPIO pin numbers for the motor, by default [21, 17, 27, 22]
        method_step : str, optional
            Method of stepping, by default "half"
        """
        self.step_number = 0
        self.direction = 0
        self.last_step_time = 0
        self.number_of_steps = number_of_steps
        self._method_step = method_step
        if method_step == "full":
            self._vlist = [[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1], [1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]]
        elif method_step == "wave":
            self._vlist = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        else:
            self._vlist = [[1, 0, 0, 0], [1, 1, 0, 0], [0, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 0], [0, 0, 1, 1], [0, 0, 0, 1], [1, 0, 0, 1]]
            self._method_step = "half"
        factory = PiGPIOFactory()
        self.mpins = [OutputDevice(pin, pin_factory=factory) for pin in mpins]
        self.set_speed()

    def set_speed(self, what_speed=10):
        """Set the speed of the stepper motor.

        Parameters
        ----------
        what_speed : int, optional
            Speed of the motor, by default 10
        """
        self.step_delay = 60.0 * 1000 * 1000 * 1000 / self.number_of_steps / what_speed
        return
    
    def step(self, steps_to_move, auto_stop=True):
        """Move the stepper motor.

        Parameters
        ----------
        steps_to_move : int
            Number of steps to move
        auto_stop : bool, optional
            Stop the motor after moving, by default True
        """
        if self._method_step == "half":
            steps_to_move *= 2
        steps_left = abs(steps_to_move)
        self.direction = 1 if steps_to_move > 0 else 0
        while steps_left > 0:
            now = time.time_ns()
            if (now - self.last_step_time) >= self.step_delay:
                self.last_step_time = now
                if self.direction == 1:
                    self.step_number += 1
                    if self.step_number == self.number_of_steps:
                        self.step_number = 0
                else:
                    if self.step_number == 0:
                        self.step_number = self.number_of_steps
                    self.step_number -= 1
                steps_left -= 1
                self._step_motor(self.step_number % 8)
        if auto_stop:
            self.stop()
        return
    
    def _step_motor(self, this_step):
        """Step the motor.

        Parameters
        ----------
        this_step : int
            Step number
        """
        for val, mpin in zip(self._vlist[this_step], self.mpins):
            mpin.on() if val else mpin.off()
        return
    
    def stop(self):
        """Stop the motor.
        """
        for mpin in self.mpins:
            mpin.off()
        return
    
    def __del__(self):
        """Stop the motor and clean up the GPIO pins.
        """
        self.stop()
        for mpin in self.mpins:
            mpin.close()
        return
    
    
