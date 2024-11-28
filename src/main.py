from lightning_control import LED, OrganicEL
from posture_detection import detect
from snack_delivery import Delivery
from utils.common_functions import MotionSensor, Speaker, UltrasonicSensor
from buildhat import Motor
import time
import random
import traceback

AUDIO_PATH = "../audio/"
MOVE_AUDIO_FILE = "move.wav"
BACK_AUDIO_FILE = "back.wav"
POSTURE_ALERT_AUDIO_FILE = "posture_alert.wav"
TREAT_AUDIO_FILE = "treat.wav"
ITEM_GET_AUDIO_FILE = "item_get.mp3"
RIGHT_ARM_PORT = "A"
CATERPILLAR_PORT = "B"
LEFT_SHOULDER_X_LIMIT = 0.95
LEFT_SHOULDER_Y_LIMIT = 0.05
RIGHT_SHOULDER_X_LIMIT = 0.05
RIGHT_SHOULDER_Y_LIMIT = 0.95
LEFT_ETE_Y_LIMIT = 0.15
RIGHT_ETE_Y_LIMIT = 0.4
CATERPILLAR_BACK_ROTATION = 1
CATERPILLAR_SPEED = 100
BAD_POSTURE_LIMIT = 3
PUNCH_DISTANCE = 30
PUNCH_TIME = 3
DELIVERY_INTERVAL = 40 * 60


def main():
    try:
        # 初期化
        print("初期化開始")
        led = LED()
        organic_el = OrganicEL()
        motion_sensor = MotionSensor()
        mode = "hiroyuki" if random.randint(0, 1) == 1 else "oka-san"
        speaker = Speaker(AUDIO_PATH + mode)
        delivery = Delivery()
        caterpillar_motor = Motor(CATERPILLAR_PORT)
        right_arm_motor = Motor(RIGHT_ARM_PORT)
        ultrasonic_sensor = UltrasonicSensor()
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

                    if key_points["left_shoulder"][1] > LEFT_SHOULDER_X_LIMIT or key_points["right_shoulder"][1] < RIGHT_SHOULDER_X_LIMIT:
                        speaker.play_audio(MOVE_AUDIO_FILE)
                        time.sleep(10)
                        continue

                    if key_points["left_eye"][0] < LEFT_ETE_Y_LIMIT or key_points["right_eye"][0] > RIGHT_ETE_Y_LIMIT or \
                            key_points["left_shoulder"][0] > LEFT_SHOULDER_Y_LIMIT or key_points["right_shoulder"][0] > RIGHT_SHOULDER_Y_LIMIT:
                        speaker.play_audio(BACK_AUDIO_FILE)
                        caterpillar_motor.run_for_rotations(CATERPILLAR_BACK_ROTATION, CATERPILLAR_SPEED)
                        continue

                    nose2eye_y = abs(key_points["nose"][0] - key_points["left_eye"][0])
                    if abs(key_points["left_shoulder"][0] - key_points["right_shoulder"][0]) > (2 * nose2eye_y) or \
                            abs(key_points["left_shoulder"][0] - key_points["nose"][0]) < 2 * nose2eye_y or \
                            abs(key_points["left_hip"][0] - key_points["left_shoulder"][0]) < 4 * nose2eye_y:
                        bad_posture_flag += 1
                        if bad_posture_flag > BAD_POSTURE_LIMIT:
                            speaker.play_audio(POSTURE_ALERT_AUDIO_FILE)
                            bad_posture_flag = 0
                            continual_bad_posture_flag += 1
                            if continual_bad_posture_flag > BAD_POSTURE_LIMIT:
                                run_time_start = time.time()
                                while ultrasonic_sensor.read_distance() > PUNCH_DISTANCE:
                                    caterpillar_motor.start(CATERPILLAR_SPEED)
                                caterpillar_motor.stop()
                                run_time_end = time.time()
                                for _ in range(PUNCH_TIME):
                                    right_arm_motor.run_for_rotations(3, -100)
                                    right_arm_motor.run_for_rotations(2.5, 100)
                                continual_bad_posture_flag = 0
                                caterpillar_motor.run_for_seconds(run_time_start - run_time_end, CATERPILLAR_SPEED)
                                continue
                            continue
                        continue

                    if time.time() - start_time >= DELIVERY_INTERVAL:
                        speaker.play_audio(TREAT_AUDIO_FILE)
                        delivery.give()
                        speaker.play_audio(ITEM_GET_AUDIO_FILE)
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
