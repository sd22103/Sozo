import time
import traceback

def monitor_user(ultrasonic_sensor, led, shared_state, verbose=False):
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
    print("ユーザー検知開始")
    print(f"verbose:{verbose}")
    while True:
        try:
            if verbose:
                print("計測")
            distance = abs(ultrasonic_sensor.read_distance())
            if verbose:
                print(f"distance={distance}cm")
            if distance < 150:
                shared_state["human_detected"] = True
                led.on()
                left_count = 0
            else:
                left_count += 1
                if left_count > 5:
                    shared_state["human_detected"] = False
                    led.off()

        except Exception as e:
            print("Error in monitor_motion (from monitor_user):", e)
            traceback.print_exc()
            
        time.sleep(0.1)