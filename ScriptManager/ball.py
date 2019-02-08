import sys
import cv2
import numpy
import math
from enum import Enum

class GripPipeline:
    """
    An OpenCV pipeline generated by GRIP.
    """


    def __init__(self):
        """initializes all values to presets or None if need to be set
        """

        self.__blur_type = BlurType.Box_Blur
        self.__blur_radius = 24.324324324324326

        self.blur_output = None

        self.__hsv_threshold_input = self.blur_output
        self.__hsv_threshold_hue = [0.0, 18.03056027164686]
        self.__hsv_threshold_saturation = [156, 255.0]
        self.__hsv_threshold_value = [161, 255.0]

        self.hsv_threshold_output = None


        self.__mask_mask = self.hsv_threshold_output

        self.mask_output = None

        self.__cv_erode_src = self.mask_output
        self.__cv_erode_kernel = None
        self.__cv_erode_anchor = (-1, -1)
        self.__cv_erode_iterations = 1.0
        self.__cv_erode_bordertype = cv2.BORDER_CONSTANT
        self.__cv_erode_bordervalue = (-1)

        self.cv_erode_output = None

        self.__find_lines_input = self.cv_erode_output

        self.find_lines_output = None


    def process(self, source0):
        """
        Runs the pipeline and sets all outputs to new values.
        """
        # Step Blur0:
        self.__blur_input = source0
        (self.blur_output) = self.__blur(self.__blur_input, self.__blur_type, self.__blur_radius)

        # Step HSV_Threshold0:
        self.__hsv_threshold_input = self.blur_output
        (self.hsv_threshold_output) = self.__hsv_threshold(self.__hsv_threshold_input, self.__hsv_threshold_hue, self.__hsv_threshold_saturation, self.__hsv_threshold_value)

        # Step Mask0:
        self.__mask_input = source0
        self.__mask_mask = self.hsv_threshold_output
        (self.mask_output) = self.__mask(self.__mask_input, self.__mask_mask)

        # Step CV_erode0:
        self.__cv_erode_src = self.mask_output
        (self.cv_erode_output) = self.__cv_erode(self.__cv_erode_src, self.__cv_erode_kernel, self.__cv_erode_anchor, self.__cv_erode_iterations, self.__cv_erode_bordertype, self.__cv_erode_bordervalue)

        # Step Find_Lines0:
        self.__find_lines_input = self.cv_erode_output
        (self.find_lines_output) = self.__find_lines(self.__find_lines_input)


    @staticmethod
    def __blur(src, type, radius):
        """Softens an image using one of several filters.
        Args:
            src: The source mat (numpy.ndarray).
            type: The blurType to perform represented as an int.
            radius: The radius for the blur as a float.
        Returns:
            A numpy.ndarray that has been blurred.
        """
        if(type is BlurType.Box_Blur):
            ksize = int(2 * round(radius) + 1)
            return cv2.blur(src, (ksize, ksize))
        elif(type is BlurType.Gaussian_Blur):
            ksize = int(6 * round(radius) + 1)
            return cv2.GaussianBlur(src, (ksize, ksize), round(radius))
        elif(type is BlurType.Median_Filter):
            ksize = int(2 * round(radius) + 1)
            return cv2.medianBlur(src, ksize)
        else:
            return cv2.bilateralFilter(src, -1, round(radius), round(radius))

    @staticmethod
    def __hsv_threshold(input, hue, sat, val):
        """Segment an image based on hue, saturation, and value ranges.
        Args:
            input: A BGR numpy.ndarray.
            hue: A list of two numbers the are the min and max hue.
            sat: A list of two numbers the are the min and max saturation.
            lum: A list of two numbers the are the min and max value.
        Returns:
            A black and white numpy.ndarray.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        return cv2.inRange(out, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))

    @staticmethod
    def __mask(input, mask):
        """Filter out an area of an image using a binary mask.
        Args:
            input: A three channel numpy.ndarray.
            mask: A black and white numpy.ndarray.
        Returns:
            A three channel numpy.ndarray.
        """
        return cv2.bitwise_and(input, input, mask=mask)

    @staticmethod
    def __cv_erode(src, kernel, anchor, iterations, border_type, border_value):
        """Expands area of lower value in an image.
        Args:
           src: A numpy.ndarray.
           kernel: The kernel for erosion. A numpy.ndarray.
           iterations: the number of times to erode.
           border_type: Opencv enum that represents a border type.
           border_value: value to be used for a constant border.
        Returns:
            A numpy.ndarray after erosion.
        """
        return cv2.erode(src, kernel, anchor, iterations = (int) (iterations +0.5),
                            borderType = border_type, borderValue = border_value)

    class Line:

        def __init__(self, x1, y1, x2, y2):
            self.x1 = x1
            self.y1 = y1
            self.x2 = x2
            self.y2 = y2

        def length(self):
            return numpy.sqrt(pow(self.x2 - self.x1, 2) + pow(self.y2 - self.y1, 2))

        def angle(self):
            return math.degrees(math.atan2(self.y2 - self.y1, self.x2 - self.x1))
    @staticmethod
    def __find_lines(input):
        """Finds all line segments in an image.
        Args:
            input: A numpy.ndarray.
        Returns:
            A filtered list of Lines.
        """
        detector = cv2.createLineSegmentDetector()
        if (len(input.shape) == 2 or input.shape[2] == 1):
            lines = detector.detect(input)
        else:
            tmp = cv2.cvtColor(input, cv2.COLOR_BGR2GRAY)
            lines = detector.detect(tmp)
        output = []
        if len(lines) != 0:
            for i in range(1, len(lines[0])):
                tmp = GripPipeline.Line(lines[0][i, 0][0], lines[0][i, 0][1],
                                lines[0][i, 0][2], lines[0][i, 0][3])
                output.append(tmp)
        return output


BlurType = Enum('BlurType', 'Box_Blur Gaussian_Blur Median_Filter Bilateral_Filter')

from picamera import PiCamera
from picamera.array import PiRGBArray
from table import Table
import io

table = Table()

grip = GripPipeline()


def main (stop_message):
    
    def connection(stop_message):
    
        x = stop_message[0]
        
        print("[*]Thread 2 queue:", x)
        
        if x != 2:
            print("[*]Thread 2 exiting")
            cam.close()
            sys.exit()
    
    cam = PiCamera()
    cam.resolution = (640,480)
    cam.framerate = 32
    rawCap = PiRGBArray(cam, size=(640,480))
    
    for frame in cam.capture_continuous(rawCap, format='bgr', use_video_port=True):
        
        frame = frame.array
        try:
            grip.process(frame)
        
            max = 0;
            for i in grip.find_lines_output:
                if i.x1 > max:
                    max = i.x1
            x1 = max
            min = 1000000
            for i in grip.find_lines_output:
                if i.x1 < min:
                    min = i.x1
            x2 = min
            max = 0
            for i in grip.find_lines_output:
                if i.y1 > max:
                    max = i.y1
            y1 = max
            min = 1000000
            for i in grip.find_lines_output:
                if i.y1 < min:
                    min = i.y1
            y2 = min
            max = 0
            print(str(x1)+" --- "+str(x2)+" ---"+str(y1)+" --- "+str(y2))
            cv2.rectangle(grip.mask_output,(x1,y1),(x2,y2),(255,255,255),2)
            sideX = ((x1-x2)/2)+x2
            sideY = ((y1-y2)/2)+y2
            cv2.circle(grip.mask_output,(int(sideX),int(sideY)),50,(255,255,255),2)
            print("Ball found")
        
            table.updateNumber((sideX, sideY))
        
        except Exception as e:
            print(e)
            print("--------------")
            print("Ball not found")
        
            table.updateNumber("B00B13S")
        
        cv2.imshow('frame',grip.mask_output)
        rawCap.truncate(0)
    ##    xraw.seek(0)
    
        connection(stop_message)
    
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
