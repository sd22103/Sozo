
import torch
import PIL
from PIL import Image
import torchvision
from torchvision import transforms
import cv2
import matplotlib.pyplot as plt

class PoseEstimation:
    """Posture Detection class for detecting human pose from image using pretrained model.
    """
    def __init__(self, img_path, model, device='cpu'):
        """Initialize the class with image path, model and device.

        Parameters
        ----------
        img_path : str
            Path of the image file.
        model : torch model
            Pretrained model for detecting human pose
        device : str, optional
            Device to use for processing the image and model, by default 'cpu'
        """
        self.frame_raw = cv2.imread(img_path)
        self.frame = cv2.cvtColor(self.frame_raw, cv2.COLOR_BGR2RGB)
        self.image = Image.fromarray(self.frame)
        self.model = model
        self.device = device

    def detect(self, save=False, save_path=None):
        """Detect human pose from the image.

        Parameters
        ----------
        save : bool, optional
            Save the image with detected pose, by default False
        save_path : str, optional
            Path to save the image, by default None
        """
        with torch.no_grad():
            transform = transforms.Compose([transforms.ToTensor()])
            inputs = transform(self.image).unsqueeze(0).to(self.device)
            self.model.eval()
            outputs = self.model(inputs)
            key_point = []
            for i in range(len(outputs[0]['boxes'])):
                if outputs[0]['scores'][i] > 0.9:
                    x0 = int(outputs[0]['boxes'][i][0])
                    y0 = int(outputs[0]['boxes'][i][1])
                    x1 = int(outputs[0]['boxes'][i][2])
                    y1 = int(outputs[0]['boxes'][i][3])
                    bbox = cv2.rectangle(self.frame, (x0, y0), (x1, y1), (0, 0, 300), 3, 4)
                    x, y = [], []
                    for j in range(len(outputs[0]['keypoints'][0])):
                        kp_x = int(outputs[0]['keypoints'][i][j][0])
                        kp_y = int(outputs[0]['keypoints'][i][j][1])
                        x.append(kp_x)
                        y.append(kp_y)
                        bbox = cv2.circle(self.frame_raw, (kp_x, kp_y), 2, (50, 300, 0), 3, 4)
                    key_point.append((x, y))
            for a in key_point:
                x = a[0]
                y = a[1]
                bbox = cv2.line(self.frame_raw, (x[5], y[5]), (x[6], y[6]), (300, 0, 0), 5) # left shoulder to right shoulder
                bbox = cv2.line(self.frame_raw, (x[5], y[5]), (x[7], y[7]), (300, 0, 0), 5) # left shoulder to left elbow
                bbox = cv2.line(self.frame_raw, (x[6], y[6]), (x[8], y[8]), (300, 0, 0), 5) # right shoulder to right elbow
                bbox = cv2.line(self.frame_raw, (x[7], y[7]), (x[9], y[9]), (300, 0, 0), 5) # left elbow to left wrist
                bbox = cv2.line(self.frame_raw, (x[8], y[8]), (x[10], y[10]), (300, 0, 0), 5) # right elbow to right wrist
            
            if save:
                self.show(bbox, save=True, save_path=save_path)
            else:
                self.show(bbox)
    
    def show(self, bbox, save=False, save_path=None):
        """Display the image with detected pose.

        Parameters
        ----------
        bbox : cv2 image
            Image with detected pose
        save : bool, optional
            Save the image, by default False
        save_path : str, optional
            Path to save the image, by default None
        """
        plt.figure(figsize=(12, 9))
        plt.imshow(cv2.cvtColor(bbox, cv2.COLOR_BGR2RGB))
        plt.axis('off')
        if save:
            plt.savefig(save_path)
        plt.show()
        plt.close()
