from utils.common_functions import ServoMotor
import time
class Delivery():
    """Delivery class to deliver snacks to the user.
    """
    def __init__(self):
        """Initialize the Delivery class.
        """
        self.servo_motor = ServoMotor()
        self.servo_motor.set_angle(0)

    def give(self, open_time=2):
        """Give the snack to the user.

        Parameters
        ----------
        open_time : int, optional
            The time to open the servo motor, by default 2
        """
        self.servo_motor.set_angle(90)
        time.sleep(open_time)
        self.servo_motor.set_angle(0)
        return
