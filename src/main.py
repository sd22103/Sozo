from utils.common_functions import Speaker, UltrasonicSensor, input_json
from lightning_control import LED, OrganicEL
from monitor_user import monitor_user
from posture_check import posture_check
from snack_delivery import Delivery, periodic_delivery
from buildhat import Motor
import threading
import traceback

SETTING = input_json("../config/setting.json")
CONST, PINS = SETTING.constants, SETTING.pins

def main():
    try:
        print("初期化開始")
        led = LED()
        organic_el = OrganicEL(PINS.organic_el)
        speaker = Speaker(CONST.audio_path)
        delivery = Delivery(PINS.servo_motor)
        caterpillar_motor = Motor(PINS.caterpillar_port)
        right_arm_motor = Motor(PINS.right_arm_port)
        ultrasonic_sensor = UltrasonicSensor(PINS.ultrasonic_sensor.trigger, PINS.ultrasonic_sensor.echo)
        print("初期化終了")

        # スレッド間で共有する状態
        shared_state = {"human_detected": False}

        # スレッドの作成
        threads = [
            threading.Thread(target=monitor_user, args=(ultrasonic_sensor, led, organic_el, shared_state)),
            threading.Thread(target=posture_check, args=(shared_state, speaker, caterpillar_motor, right_arm_motor, ultrasonic_sensor, CONST)),
            threading.Thread(target=periodic_delivery, args=(shared_state, speaker, delivery, CONST)),
        ]

        # スレッドを開始
        for thread in threads:
            thread.start()

        # スレッドを待機
        for thread in threads:
            thread.join()

    except KeyboardInterrupt:
        print("プログラムを終了します。")
    except Exception as e:
        print("Fatal Error:", e)
        traceback.print_exc()
    
    finally:
        if 'led' in locals(): led.off()
        if 'organic_el' in locals(): organic_el.off()
        if 'caterpillar_motor' in locals(): caterpillar_motor.stop()
        if 'right_arm_motor' in locals(): right_arm_motor.stop()

if __name__ == "__main__":
    main()