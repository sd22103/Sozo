from lightning_control import LED, OrganicEL
from posture_detection import detect
from snack_delivery import Delivery
from utils.common_functions import MotionSensor, Speaker, UltrasonicSensor, input_json
from buildhat import Motor
import time
import random
import traceback

SETTING = input_json("../config/setting.json")
CONST, PINS = SETTING.constants, SETTING.pins


def main():
    try:
        # 初期化
        print("初期化開始")
        led = LED()
        organic_el = OrganicEL(PINS.organic_el)
        motion_sensor = MotionSensor(PINS.motion_sensor)
        mode = "hiroyuki" if random.randint(0, 1) == 1 else "oka-san"
        speaker = Speaker(CONST.audio_path + mode)
        delivery = Delivery()
        caterpillar_motor = Motor(PINS.caterpillar_port)
        right_arm_motor = Motor(PINS.right_arm_port)
        ultrasonic_sensor = UltrasonicSensor(PINS.ultrasonic_sensor.trigger, PINS.ultrasonic_sensor.echo)
        start_time = time.time()
        bad_posture_flag = 0
        continual_bad_posture_flag = 0
        print("初期化終了")
        while True:
            try:
                if motion_sensor.detect_human():
                    led.on()
                    organic_el.on()
                    key_points = detect()

                    if key_points["left_shoulder"][1] > CONST.left_shoulder_x_limit or key_points["right_shoulder"][1] < CONST.right_shoulder_x_limit:
                        speaker.play_audio(CONST.move_audio_file)
                        time.sleep(10)
                        continue

                    if key_points["left_eye"][0] < CONST.left_ete_y_limit or key_points["right_eye"][0] > CONST.right_ete_y_limit or \
                            key_points["left_shoulder"][0] > CONST.left_shoulder_y_limit or key_points["right_shoulder"][0] > CONST.right_shoulder_y_limit:
                        speaker.play_audio(CONST.back_audio_file)
                        caterpillar_motor.run_for_rotations(CONST.caterpillar_back_rotation, CONST.caterpillar_speed)
                        continue

                    nose2eye_y = abs(key_points["nose"][0] - key_points["left_eye"][0])
                    if abs(key_points["left_shoulder"][0] - key_points["right_shoulder"][0]) > (2 * nose2eye_y) or \
                            abs(key_points["left_shoulder"][0] - key_points["nose"][0]) < 2 * nose2eye_y or \
                            abs(key_points["left_hip"][0] - key_points["left_shoulder"][0]) < 4 * nose2eye_y:
                        bad_posture_flag += 1
                        if bad_posture_flag > CONST.bad_posture_limit:
                            speaker.play_audio(CONST.posture_alert_audio_file)
                            bad_posture_flag = 0
                            continual_bad_posture_flag += 1
                            if continual_bad_posture_flag > CONST.bad_posture_limit:
                                run_time_start = time.time()
                                while ultrasonic_sensor.read_distance() > CONST.punch_distance:
                                    caterpillar_motor.start(CONST.caterpillar_speed)
                                caterpillar_motor.stop()
                                run_time_end = time.time()
                                for _ in range(CONST.punch_time):
                                    right_arm_motor.run_for_rotations(3, -100)
                                    right_arm_motor.run_for_rotations(2.5, 100)
                                continual_bad_posture_flag = 0
                                caterpillar_motor.run_for_seconds(run_time_start - run_time_end, CONST.caterpillar_speed)
                                continue
                            continue
                        continue

                    if time.time() - start_time >= CONST.delivery_interval:
                        speaker.play_audio(CONST.treat_audio_file)
                        delivery.give()
                        speaker.play_audio(CONST.item_get_audio_file)
                        start_time = time.time()
                else:
                    led.off()
                    organic_el.off()
                    caterpillar_motor.stop()
                    right_arm_motor.stop()
                    bad_posture_flag = 0
                    continual_bad_posture_flag = 0

            except Exception as e:
                print("Error in main loop:", e)
                traceback.print_exc()
                time.sleep(1)  # 安全のため少し待機して再試行

    except KeyboardInterrupt:
        print("プログラムを終了します。")
    except Exception as e:
        print("Fatal Error:", e)
        traceback.print_exc()
    finally:
        # 終了時の安全対策
        led.off()
        organic_el.off()
        caterpillar_motor.stop()
        right_arm_motor.stop()
        print("リソースを解放しました。")


if __name__ == "__main__":
    main()
