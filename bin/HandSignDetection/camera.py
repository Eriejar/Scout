import torch
from torch import nn
import sys
from os import path
import cv2

class Reshape(nn.Module):
    def __init__(self, *target_shape):
        super().__init__()
        self.target_shape = target_shape

    def forward(self, x):
        return x.view(*self.target_shape)

class HandGestureClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.pipeline = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=4, kernel_size = 5), #1*96*128 -> 4*92*124
            nn.LeakyReLU(),
            nn.Conv2d(in_channels=4, out_channels=16, kernel_size = 5), #4*92*124 -> 16*88*120
            nn.LeakyReLU(),
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size = 7), #16*88*120 -> 32*82*114
            nn.LeakyReLU(),
            nn.Conv2d(in_channels=32, out_channels=32, kernel_size=7), #32*82*114 -> 32*76*108
            nn.LeakyReLU(),
            nn.Conv2d(in_channels=32, out_channels=4, kernel_size=7), #32*76*108 -> 4*70*102
            Reshape(-1, 4*70*102),
            nn.Linear(in_features=4*70*102, out_features=128),
            nn.Dropout(p=.5),
            nn.ReLU(),
            nn.Linear(in_features=128, out_features=64),
            nn.Dropout(p=.5),
            nn.ReLU(),
            nn.Linear(in_features=64, out_features=6),
            nn.LogSoftmax()
        )

    def forward(self, X):
        return self.pipeline(X)

net = HandGestureClassifier()

# getting path of file relative to current directory
basepath = path.dirname(__file__)
filepath = path.abspath(path.join(basepath, "models", "classifier_5.pt"))
net.load_state_dict(torch.load(filepath, map_location=torch.device('cpu') ) )

from numpy.linalg import norm
from scipy.signal import correlate2d

def canny_norm_filter(image):
    im = norm(image, axis = -1)/((3*(255**2))**.5)
    return cv2.Canny( (im*255).astype(np.uint8), 100, 150)

def canny_color_filter(image):
    return cv2.Canny(image, 100, 150)

def downsample_filter(image, by = 5):
    return image[::by,::by,:]

def difference_kernel(image, size = 3):
    im = np.moveaxis(image, -1, 0)

    size = 3
    gradient_kernel = -np.ones([size, size])
    gradient_kernel /= size**2
    gradient_kernel[ int(size/2) ][ int(size/2) ] *= -1

    im = np.stack(correlate2d(im[a], gradient_kernel, boundary = 'symm') for a in range(3) )

    return np.moveaxis(im, 0, -1).astype(np.uint8)

def mean_denoiser(image, mark = False):
    '''
        Finds mean x, y as well as avg distance from mean along x and y axes.
        zeros out everything beyond a certain distance from mean as determined by
        x and y marginal distance
    '''
    py = np.arange(image.shape[0] )
    vy = image.sum(axis = 1)
    px = np.arange(image.shape[1] )
    vx = image.sum(axis = 0)

    ymean = int( (py @ vy)/vy.sum() if vy.sum() != 0 else 0 )
    xmean = int( (px @ vx)/vx.sum() if vx.sum() != 0 else 0 )

    marginal_x = image.sum(axis = 0)/max(image.sum(), 1)
    marginal_y = image.sum(axis = 1)/max(image.sum(), 1)

    dy = abs(np.arange(image.shape[0]) - ymean )
    dx = abs(np.arange(image.shape[1]) - xmean )

    sy = np.mean( dy * marginal_y )
    sx = np.mean( dx * marginal_x )

    py = image.shape[0] * sy * 5
    px = image.shape[1] * sx * 5

    image = np.moveaxis(np.stack([image]*3), 0, -1)

    if mark:
        image[ymean, xmean] = [255, 0, 0]
        cv2.rectangle(
            image[:,:,0],
            ( int(xmean - px/2), int(ymean - py/2) ),
            ( int(xmean + px/2), int(ymean + py/2) ),
            (255,0,0),
            2)

    mask = np.ones(image.shape[:2])
    mask[
        max(0, int(ymean - py/2) ) : min(int(ymean + py/2), image.shape[0] ),
        max(0, int(xmean - px/2) ) : min(int(xmean + px/2), image.shape[1] )
    ] = 0

    image[mask.astype(bool) ] = 0

    return image

def mean_center(image):
    image = image[:,:,0]

    py = np.arange(image.shape[0] )
    vy = image.sum(axis = 1)
    px = np.arange(image.shape[1] )
    vx = image.sum(axis = 0)

    ymean = int( (py @ vy)/vy.sum() if vy.sum() != 0 else 0 )
    xmean = int( (px @ vx)/vx.sum() if vx.sum() != 0 else 0 )

    y, x = np.where(image)
    y_centered = y - ymean + int(image.shape[0]/2)
    x_centered = x - xmean + int(image.shape[1]/2)

    y_centered = np.clip(y_centered, 0, image.shape[0]-1)
    x_centered = np.clip(x_centered, 0, image.shape[1]-1)

    image = np.zeros(image.shape[:2])
    image[y_centered, x_centered] = 1

    image = np.moveaxis(np.stack([image]*3), 0, -1).astype(np.uint8)
    return image

def contour_image(image):
    image = image.max(axis = -1)
    # Run findContours - Note the RETR_EXTERNAL flag
    # Also, we want to find the best contour possible with CHAIN_APPROX_NONE
    contours, hierarchy = cv2.findContours(image.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Create an output of all zeroes that has the same shape as the input
    # image
    out = np.zeros_like(image)

    # On this output, draw all of the contours that we have detected
    # in white, and set the thickness to be 3 pixels
    cv2.drawContours(out, contours, -1, 255, 1)

    # Spawn new windows that shows us the donut
    # (in grayscale) and the detected contour
    return out

def torchmodel_coefs(image):
    with torch.no_grad():
        if len(image.shape) == 3:
            net_image = image[:,:,0]

        net.eval()
        net_image = image.reshape([1,1,96,128])
        net_image = torch.tensor(net_image).float()
        res = net(net_image)
    predicted = np.argmax(res[0])
    conf = res[0][predicted]

    return predicted, conf

gesture_this_frame = 0
def real_annotate():
    global gesture_this_frame

    filters = [downsample_filter, canny_norm_filter, mean_denoiser, mean_center, contour_image]
    cap = cv2.VideoCapture(1)

    cv2.namedWindow('Main', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Main', (640, 480) )

    while cap.isOpened():
        ret, frame = cap.read()

        process_frame = frame.copy()
        for filter in filters:
            process_frame = filter(process_frame)

        gesture, coef = torchmodel_coefs(process_frame)
        gesture_this_frame = gesture

        cv2.putText(
            frame, "Gesture: {}, Confidence {}".format(gesture, coef.exp() ), (0,25),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1,
            color = (255,0,0), thickness=2
        )

        if ret:
            cv2.imshow('Main', frame)
        else:
            print('No Frame Found')

        keypress = cv2.waitKey(1)
        if keypress == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    from threading import Thread
    inference_thread = Thread(target = real_annotate)
    inference_thread.start()
    while 1:
        print(gesture_this_frame)