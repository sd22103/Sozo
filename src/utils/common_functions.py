import cv2
from datetime import datetime
import os

class Camera:
    """Camera class to capture picture or video.
    """
    def __init__(self, dev_id=0, path=None):
        """Initialize the camera object.

        Parameters
        ----------
        dev_id : int, optional
            Device ID of the camera, by default 0
        path : _type_, optional
            Path of the directory to save the picture or video, by default None
        """
        self.cap = cv2.VideoCapture(dev_id)
        self.path = path
        if path is None:
            self.path = os.getcwd()
        if not self.cap.isOpened():
            print('Failed to open camera.')
        

    def capt_picture(self, width=640, height=480, file_name=None):
        """Capture a picture from the camera.

        Parameters
        ----------
        width : int, optional
            Width of the picture, by default 640
        height : int, optional
            Height of the picture, by default 480
        file_name : _type_, optional
            Name of the picture file, by default None
        """
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        ret, frame = self.cap.read()
        if ret:
            if file_name is None:
                file_name = datetime.now().strftime('%Y%m%d%H%M%S') + '.jpg'
            path = os.path.join(self.path, file_name)
            cv2.imwrite(path, frame)
        else:
            print('Failed to capture picture.')
            return
        self.cap.release()
        cv2.destroyAllWindows()
        return
    
    def capt_video(self, width=640, height=480, rec_sec=5, fps=30, fourcc=('m', 'p', '4', 'v'), file_name=None):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        fourcc = cv2.VideoWriter_fourcc(*fourcc)
        if file_name is None:
            file_name = datetime.now().strftime('%Y%m%d%H%M%S') + '.mp4'
        path = os.path.join(self.path, file_name)
        out = cv2.VideoWriter(path, fourcc, fps, (width, height))
        for _ in range(fps * rec_sec):
            ret, frame = self.cap.read()
            if not ret:
                print('Failed to capture video.')
                return
            out.write(frame)
        self.cap.release()
        out.release()
        cv2.destroyAllWindows()
        return