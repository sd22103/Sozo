import time
import traceback

def monitor_user(ultrasonic_sensor, led, speaker, shared_state, const, verbose=False):
    """Monitor user and update shared state accordingly.

    Parameters
    ----------
    ultrasonic_sensor : object of class UltrasonicSensor
        Ultrasonic sensor object.
    led : object of class LED
        LED object.
    speaker : object of class Speaker
        Speaker object.
    shared_state : dict
        Shared state between threads.
    const : AttrDict
        Constants object.
    verbose : bool, optional
        Whether to print debug messages. The default is False.
    """
    left_count = 0
    print("ユーザー検知開始")
    print(f"verbose:{verbose}")
    led_flag = 0
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
                if led_flag == 0:
                    speaker.play_audio(const.start_audio_file)
                left_count = 0
                led_flag = 1
            else:
                left_count += 1
                if left_count > 5:
                    if led_flag == 1:
                        speaker.play_audio(const.finish_audio_file)
                    led_flag = 0
                    shared_state["human_detected"] = False
                    led.off()

        except Exception as e:
            print("Error in monitor_motion (from monitor_user):", e)
            traceback.print_exc()
            
        time.sleep(0.1)