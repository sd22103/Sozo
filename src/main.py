from lightning_control import LED, OrganicEL
from posture_detection import detect
from snack_delivery import Delivery
from utils.common_functions import MotionSensor, Speaker, UltrasonicSensor
from buildhat import Motor
import time

MOVE_AUDIO_FILE = "audio/move.mp3"
BACK_AUDIO_FILE = "audio/back.mp3"
POSTURE_ALERT_AUDIO_FILE = "audio/posture_alert.mp3"
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
DELIVERY_INTERVAL = 40*60


def main():
    led = LED()
    organic_el = OrganicEL()
    motion_sensor = MotionSensor()
    speaker = Speaker()
    delivery = Delivery()
    caterpillar_motor = Motor(CATERPILLAR_PORT)
    right_arm_motor = Motor(RIGHT_ARM_PORT)
    ultrasonic_sensor = UltrasonicSensor()
    start_time = time.time()
    bad_posture_flag = 0
    continual_bad_posture_flag = 0

    while True:
        if motion_sensor.detect_human():
            led.on()
            organic_el.on()
            key_points = detect()
            if key_points["left_shoulder"][1]>LEFT_SHOULDER_X_LIMIT or key_points["right_shoulder"][1]<RIGHT_SHOULDER_X_LIMIT:
                speaker.play_audio(MOVE_AUDIO_FILE)
                time.sleep(10)
                continue
            if key_points["left_eye"][0]<LEFT_ETE_Y_LIMIT or key_points["right_eye"][0]>RIGHT_ETE_Y_LIMIT or\
                key_points["left_shoulder"][0]>LEFT_SHOULDER_Y_LIMIT or key_points["right_shoulder"][0]>RIGHT_SHOULDER_Y_LIMIT:
                speaker.play_audio(BACK_AUDIO_FILE)
                caterpillar_motor.run_for_rotations(CATERPILLAR_BACK_ROTATION, CATERPILLAR_SPEED)
                continue
            nose2eye_y = abs(key_points["nose"][0]-key_points["left_eye"][0])
            if abs(key_points["left_shoulder"][0]-key_points["right_shoulder"][0])>(2*nose2eye_y) or\
                abs(key_points["left_shoulder"][0]-key_points["nose"][0])<2*nose2eye_y or\
                abs(key_points["left_hip"][0]-key_points["left_shoulder"][0])<4*nose2eye_y:
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
                        continue
                    continue
                continue
            if time.time()-start_time >= DELIVERY_INTERVAL:
                delivery.give()
                start_time = time.time()
        else:
            led.off()
            organic_el.off()
            caterpillar_motor.stop()
            right_arm_motor.stop()
            bad_posture_flag = 0
            continual_bad_posture_flag = 0

if __name__ == "__main__":
    main()