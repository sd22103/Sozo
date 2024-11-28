import os

class LED():
    """LED control class
    """
    def __init__(self, hub_num=2, port_num=2):
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
        os.system(f"sudo uhubctl -l {self.hub_num} -p {self.port_num} -a on")
        return

    def off(self):
        """Turn off the LED
        """
        os.system(f"sudo uhubctl -l {self.hub_num} -p {self.port_num} -a off")
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