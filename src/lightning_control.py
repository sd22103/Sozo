import os
import RPi.GPIO as GPIO
class LED():
    """LED control class
    """
    def __init__(self, hub_num="1-1"):
        """Constructor

        Parameters
        ----------
        hub_num : str, optional
            hub number, by default 1-1
        """
        self.hub_num = hub_num
        return

    def on(self):
        """Turn on the LED
        """
        os.system(f"sudo uhubctl -l {self.hub_num} -a on")
        return

    def off(self):
        """Turn off the LED
        """
        os.system(f"sudo uhubctl -l {self.hub_num} -a off")
        return

    def blink(self, t=5):
        """Blink the LED

        Parameters
        ----------
        t : int, optional
            number of times to blink, by default 5
        """
        for i in range(t):
            self.on()
            self.off()
        return
    

class OrganicEL():
    """Organic EL control class
    """
    def __init__(self, pin=2):
        """Constructor

        Parameters
        ----------
        pin : int, optional
            GPIO pin number, by default 2
        """
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        return
    
    def on(self):
        """Turn on the Organic EL
        """
        GPIO.output(self.pin, GPIO.HIGH)
        return
    
    def off(self):
        """Turn off the Organic EL
        """
        GPIO.output(self.pin, GPIO.LOW)
        return
    
    def __del__(self):
        """Destructor
        """
        GPIO.cleanup()
        return