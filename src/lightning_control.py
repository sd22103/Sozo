import os
import time

class LED():
    """LED control class
    """
    def __init__(self, hub_num=1, port_num=2):
        """Constructor

        Parameters
        ----------
        hub_num : int, optional
            hub number, by default 1
        port_num : int, optional
            port number, by default 2
        """
        self.hub_num = hub_num
        self.port_num = port_num
        pass

    def on(self):
        """Turn on the LED
        """
        os.system(f"sudo hub-ctrl -h {self.hub_num} -P {self.port_num} -p 1")
        return

    def off(self):
        """Turn off the LED
        """
        os.system(f"sudo hub-ctrl -h {self.hub_num} -P {self.port_num} -p 0")
        return

    def blink(self):
        """Blink the LED
        """
        self.on()
        time.sleep(0.5)
        self.off()
        time.sleep(0.5)
        return