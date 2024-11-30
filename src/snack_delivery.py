from utils.common_functions import ServoMotor
import time
import traceback

class Delivery():
    """Delivery class to deliver snacks to the user.
    """
    def __init__(self, servo_motor_pin=18):
        """Initialize the Delivery object.

        Parameters
        ----------
        servo_motor_pin : int, optional
            The pin number of the servo motor, by default 18
        """
        self.servo_motor = ServoMotor(servo_motor_pin)
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

def periodic_delivery(shared_state, speaker, delivery, const):
    """Periodically deliver snacks to the user.

    Parameters
    ----------
    shared_state : dict
        Shared state between threads.
    speaker : object of class Speaker
        Speaker object.
    delivery : object of class Delivery
        Delivery object.
    const : object of class Constants
        Constants object.
    """
    start_time = time.time()
    while True:
        try:
            if not shared_state["human_detected"]:
                time.sleep(0.1)
                continue

            if time.time() - start_time >= const.delivery_interval:
                speaker.play_audio(const.treat_audio_file)
                delivery.give()
                speaker.play_audio(const.item_get_audio_file)
                start_time = time.time()

        except Exception as e:
            print("Error in periodic_delivery (from periodic_delivery):", e)
            traceback.print_exc()

        time.sleep(0.1)