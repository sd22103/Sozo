import cv2
import RPi.GPIO as GPIO
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
        GPIO.cleanup()
        return


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

       