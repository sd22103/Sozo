import time
import traceback

def monitor_user(ultrasonic_sensor, led, organic_el, shared_state):
    """Monitor user and update shared state accordingly.

    Parameters
    ----------
    ultrasonic_sensor : object of class UltrasonicSensor
        Ultrasonic sensor object.
    led : object of class LED
        LED object.
    organic_el : object of class OrganicEL
        OrganicEL object.
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
                organic_el.on()
                left_count = 0
            else:
                left_count += 1
                if left_count > 100:
                    shared_state["human_detected"] = False
                    led.off()
                    organic_el.off()

        except Exception as e:
            print("Error in monitor_motion (from monitor_user):", e)
            traceback.print_exc()
            
        time.sleep(0.1)