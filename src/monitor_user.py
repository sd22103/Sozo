import time
import traceback

def monitor_user(ultrasonic_sensor, led, shared_state):
    """Monitor user and update shared state accordingly.

    Parameters
    ----------
    ultrasonic_sensor : object of class UltrasonicSensor
        Ultrasonic sensor object.
    led : object of class LED
        LED object.
    shared_state : dict
        Shared state between threads.
    """
    left_count = 0
    while True:
        try:
            distance = ultrasonic_sensor.read_distance()
            if distance < 200:
                shared_state["human_detected"] = True
                led.on()
                left_count = 0
            else:
                left_count += 1
                if left_count > 100:
                    shared_state["human_detected"] = False
                    led.off()

        except Exception as e:
            print("Error in monitor_motion (from monitor_user):", e)
            traceback.print_exc()
            
        time.sleep(0.1)