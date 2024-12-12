import tensorflow as tf
import tensorflow_hub as hub
from tensorflow_docs.vis import embed
import numpy as np
import cv2
import time
import traceback

# Import matplotlib libraries
from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.patches as patches

# Some modules to display an animation using imageio.
import imageio
from IPython.display import HTML, display

from utils.common_functions import Camera


# Dictionary that maps from joint names to keypoint indices.
KEYPOINT_DICT = {
    'nose': 0,
    'left_eye': 1,
    'right_eye': 2,
    'left_ear': 3,
    'right_ear': 4,
    'left_shoulder': 5,
    'right_shoulder': 6,
    'left_elbow': 7,
    'right_elbow': 8,
    'left_wrist': 9,
    'right_wrist': 10,
    'left_hip': 11,
    'right_hip': 12,
    'left_knee': 13,
    'right_knee': 14,
    'left_ankle': 15,
    'right_ankle': 16
}

# Maps bones to a matplotlib color name.
KEYPOINT_EDGE_INDS_TO_COLOR = {
    (0, 1): 'm',
    (0, 2): 'c',
    (1, 3): 'm',
    (2, 4): 'c',
    (0, 5): 'm',
    (0, 6): 'c',
    (5, 7): 'm',
    (7, 9): 'm',
    (6, 8): 'c',
    (8, 10): 'c',
    (5, 6): 'y',
    (5, 11): 'm',
    (6, 12): 'c',
    (11, 12): 'y',
    (11, 13): 'm',
    (13, 15): 'm',
    (12, 14): 'c',
    (14, 16): 'c'
}

def _keypoints_and_edges_for_display(keypoints_with_scores,
                                     height,
                                     width,
                                     keypoint_threshold=0.11):
  """Returns high confidence keypoints and edges for visualization.

  Args:
    keypoints_with_scores: A numpy array with shape [1, 1, 17, 3] representing
      the keypoint coordinates and scores returned from the MoveNet model.
    height: height of the image in pixels.
    width: width of the image in pixels.
    keypoint_threshold: minimum confidence score for a keypoint to be
      visualized.

  Returns:
    A (keypoints_xy, edges_xy, edge_colors) containing:
      * the coordinates of all keypoints of all detected entities;
      * the coordinates of all skeleton edges of all detected entities;
      * the colors in which the edges should be plotted.
  """
  keypoints_all = []
  keypoint_edges_all = []
  edge_colors = []
  num_instances, _, _, _ = keypoints_with_scores.shape
  for idx in range(num_instances):
    kpts_x = keypoints_with_scores[0, idx, :, 1]
    kpts_y = keypoints_with_scores[0, idx, :, 0]
    kpts_scores = keypoints_with_scores[0, idx, :, 2]
    kpts_absolute_xy = np.stack(
        [width * np.array(kpts_x), height * np.array(kpts_y)], axis=-1)
    kpts_above_thresh_absolute = kpts_absolute_xy[
        kpts_scores > keypoint_threshold, :]
    keypoints_all.append(kpts_above_thresh_absolute)

    for edge_pair, color in KEYPOINT_EDGE_INDS_TO_COLOR.items():
      if (kpts_scores[edge_pair[0]] > keypoint_threshold and
          kpts_scores[edge_pair[1]] > keypoint_threshold):
        x_start = kpts_absolute_xy[edge_pair[0], 0]
        y_start = kpts_absolute_xy[edge_pair[0], 1]
        x_end = kpts_absolute_xy[edge_pair[1], 0]
        y_end = kpts_absolute_xy[edge_pair[1], 1]
        line_seg = np.array([[x_start, y_start], [x_end, y_end]])
        keypoint_edges_all.append(line_seg)
        edge_colors.append(color)
  if keypoints_all:
    keypoints_xy = np.concatenate(keypoints_all, axis=0)
  else:
    keypoints_xy = np.zeros((0, 17, 2))

  if keypoint_edges_all:
    edges_xy = np.stack(keypoint_edges_all, axis=0)
  else:
    edges_xy = np.zeros((0, 2, 2))
  return keypoints_xy, edges_xy, edge_colors


def draw_prediction_on_image(
    image, keypoints_with_scores, crop_region=None, close_figure=False,
    output_image_height=None):
  """Draws the keypoint predictions on image.

  Args:
    image: A numpy array with shape [height, width, channel] representing the
      pixel values of the input image.
    keypoints_with_scores: A numpy array with shape [1, 1, 17, 3] representing
      the keypoint coordinates and scores returned from the MoveNet model.
    crop_region: A dictionary that defines the coordinates of the bounding box
      of the crop region in normalized coordinates (see the init_crop_region
      function below for more detail). If provided, this function will also
      draw the bounding box on the image.
    output_image_height: An integer indicating the height of the output image.
      Note that the image aspect ratio will be the same as the input image.

  Returns:
    A numpy array with shape [out_height, out_width, channel] representing the
    image overlaid with keypoint predictions.
  """
  height, width, channel = image.shape
  aspect_ratio = float(width) / height
  fig, ax = plt.subplots(figsize=(12 * aspect_ratio, 12))
  # To remove the huge white borders
  fig.tight_layout(pad=0)
  ax.margins(0)
  ax.set_yticklabels([])
  ax.set_xticklabels([])
  plt.axis('off')

  im = ax.imshow(image)
  line_segments = LineCollection([], linewidths=(4), linestyle='solid')
  ax.add_collection(line_segments)
  # Turn off tick labels
  scat = ax.scatter([], [], s=60, color='#FF1493', zorder=3)

  (keypoint_locs, keypoint_edges,
   edge_colors) = _keypoints_and_edges_for_display(
       keypoints_with_scores, height, width)

  line_segments.set_segments(keypoint_edges)
  line_segments.set_color(edge_colors)
  if keypoint_edges.shape[0]:
    line_segments.set_segments(keypoint_edges)
    line_segments.set_color(edge_colors)
  if keypoint_locs.shape[0]:
    scat.set_offsets(keypoint_locs)

  if crop_region is not None:
    xmin = max(crop_region['x_min'] * width, 0.0)
    ymin = max(crop_region['y_min'] * height, 0.0)
    rec_width = min(crop_region['x_max'], 0.99) * width - xmin
    rec_height = min(crop_region['y_max'], 0.99) * height - ymin
    rect = patches.Rectangle(
        (xmin,ymin),rec_width,rec_height,
        linewidth=1,edgecolor='b',facecolor='none')
    ax.add_patch(rect)

  fig.canvas.draw()
  image_from_plot = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
  image_from_plot = image_from_plot.reshape(
      fig.canvas.get_width_height()[::-1] + (3,))
  plt.close(fig)
  if output_image_height is not None:
    output_image_width = int(output_image_height / height * width)
    image_from_plot = cv2.resize(
        image_from_plot, dsize=(output_image_width, output_image_height),
         interpolation=cv2.INTER_CUBIC)
  return image_from_plot

def to_gif(images, duration):
  """Converts image sequence (4D numpy array) to gif."""
  imageio.mimsave('./animation.gif', images, duration=duration)
  return embed.embed_file('./animation.gif')

def progress(value, max=100):
  return HTML("""
      <progress
          value='{value}'
          max='{max}',
          style='width: 100%'
      >
          {value}
      </progress>
  """.format(value=value, max=max))


model_name = "movenet_lightning_int8"
module = hub.load("https://tfhub.dev/google/movenet/singlepose/lightning/4")
input_size = 192

def movenet(input_image):
	"""Runs detection on an input image.

	Args:
		input_image: A [1, height, width, 3] tensor represents the input image
			pixels. Note that the height/width should already be resized and match the
			expected input resolution of the model before passing into this function.

	Returns:
		A [1, 1, 17, 3] float numpy array representing the predicted keypoint
		coordinates and scores.
	"""
	model = module.signatures['serving_default']

	# SavedModel format expects tensor type of int32.
	input_image = tf.cast(input_image, dtype=tf.int32)
	# Run model inference.
	outputs = model(input_image)
	# Output is a [1, 1, 17, 3] tensor.
	keypoints_with_scores = outputs['output_0'].numpy()
	return keypoints_with_scores

def detect(image_path=None, output_path=None):
	"""Detects keypoints on an image.

  Args:
      image_path: Path to the image.
      output_path: Path to save the output image.

  Returns:
      A dictionary containing the detected keypoints.
	"""
	start = time.time()
	if image_path:
			image = tf.io.read_file(image_path)
			image = tf.image.decode_jpeg(image)
	else:
			camera = Camera()
			image = camera.capt_picture(192, 192)
			image = tf.convert_to_tensor(image)
			
	# Resize and pad the image to keep the aspect ratio and fit the expected size.
	input_image = tf.expand_dims(image, axis=0)
	input_image = tf.image.resize_with_pad(input_image, input_size, input_size)

	# Run model inference.
	keypoints_with_scores = movenet(input_image)
	keypoints = {list(KEYPOINT_DICT)[i]: keypoints_with_scores[0][0][i] for i in range(len(KEYPOINT_DICT))}

	if output_path:
			# Visualize the predictions with image.
			display_image = tf.expand_dims(image, axis=0)
			display_image = tf.cast(tf.image.resize_with_pad(
					display_image, 1280, 1280), dtype=tf.int32)
			output_overlay = draw_prediction_on_image(
					np.squeeze(display_image.numpy(), axis=0), keypoints_with_scores)
			plt.figure(figsize=(5, 5))
			plt.imshow(output_overlay)
			_ = plt.axis('off')
			plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
			plt.close()

	end = time.time()
	print(f"time={round(end-start, 4)}s")

	return keypoints

def posture_check(shared_state, speaker, caterpillar_motor, right_arm_motor, ultrasonic_sensor, const, verbose=False):
  """Check the posture of the detected human and take action accordingly.

  Parameters
  ----------
  shared_state : dict
      Shared state between threads.
  speaker : object of class Speaker
      Speaker object.
  caterpillar_motor : object of class Motor
      Caterpillar motor object.
  right_arm_motor : object of class Motor
      Right arm motor object.
  ultrasonic_sensor : object of class UltrasonicSensor
      Ultrasonic sensor object.
  const : AttrDict
      Constants object.
  verbose : bool, optional
      Whether to print debug messages. The default is False.
  """
  bad_posture_flag = 0
  continual_bad_posture_flag = 0
  while True:
      try:
          if not shared_state["human_detected"]:
              time.sleep(0.1)
              continue
          
          shared_state["bad_posture"] = False
          key_points = detect(output_path=f"/home/sozo/program/Sozo/src/output_img.png") if verbose else detect()
          # if verbose:
          #     print(key_points)

          if key_points["left_shoulder"][1] > const.left_shoulder_x_limit or key_points["right_shoulder"][1] < const.right_shoulder_x_limit:
            speaker.play_audio(const.move_audio_file)
            if verbose:
              if key_points["left_shoulder"][1] > const.left_shoulder_x_limit:
                print("left shoulder is out of frame")
              else:
                print("right shoulder is out of frame")
            time.sleep(5)
            continue

          if key_points["left_eye"][0] < const.left_eye_y_limit or key_points["right_eye"][0] > const.right_eye_y_limit or \
            key_points["left_shoulder"][0] < const.left_shoulder_y_limit or key_points["right_shoulder"][0] > const.right_shoulder_y_limit:
            if verbose:
              if key_points["left_eye"][0] < const.left_eye_y_limit:
                print("left eye is out of frame")
              if key_points["right_eye"][0] > const.right_eye_y_limit:
                print("right eye is out of frame")
              if key_points["left_shoulder"][0] < const.left_shoulder_y_limit:
                print("left shoulder is out of frame")
              if key_points["right_shoulder"][0] > const.right_shoulder_y_limit:
                print("right shoulder is out of frame")
            speaker.play_audio(const.back_audio_file)
            caterpillar_motor.run_for_rotations(const.caterpillar_back_rotation, const.caterpillar_speed)
            continue

          nose2eye_y = abs(key_points["nose"][0] - key_points["left_eye"][0])
          if abs(key_points["left_shoulder"][0] - key_points["right_shoulder"][0]) > (2 * nose2eye_y) or \
              abs(key_points["left_shoulder"][0] - key_points["nose"][0]) < 2 * nose2eye_y or \
              abs(key_points["left_hip"][0] - key_points["left_shoulder"][0]) < 4 * nose2eye_y:
            bad_posture_flag += 1
            shared_state["bad_posture"] = True
            if verbose:
              print(f"bad posture, flag={bad_posture_flag}")
              if abs(key_points["left_shoulder"][0] - key_points["right_shoulder"][0]) > (2 * nose2eye_y):
                print("shoulders are tilted")
              if abs(key_points["left_shoulder"][0] - key_points["nose"][0]) < 2 * nose2eye_y:
                print("shoulder is too close to face")
              if abs(key_points["left_hip"][0] - key_points["left_shoulder"][0]) < 4 * nose2eye_y:
                print("hip is too close to shoulder")
            if bad_posture_flag > const.bad_posture_limit:
              speaker.play_audio(const.posture_alert_audio_file)
              bad_posture_flag = 0
              continual_bad_posture_flag += 1
              if verbose:
                print(f"continual bad posture, flag={continual_bad_posture_flag}")
              if continual_bad_posture_flag > const.bad_posture_limit:
                caterpillar_motor.run_for_seconds(3, -const.caterpillar_speed)
                for i in range(const.punch_time):
                  if verbose:
                     print(f"punch: {i}")
                  right_arm_motor.run_for_rotations(3, -100)
                  right_arm_motor.run_for_rotations(2.5, 100)
                continual_bad_posture_flag = 0
                caterpillar_motor.run_for_seconds(3, const.caterpillar_speed)

      except KeyboardInterrupt:
         print("姿勢検知を終了します")
         break
      
      except Exception as e:
          print("Error in posture_check (from posture_check):", e)
          traceback.print_exc()

      time.sleep(0.05)