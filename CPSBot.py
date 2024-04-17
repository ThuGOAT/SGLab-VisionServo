import cv2
from time import sleep
from vision import *
from Controller import *

stage = {'lOGGING',
         'HOME',
         'SCORES',
         'CUSTOM',
         'ANALYZE',
         'PLAY',
         'LEARN',
         'SHOP'}

command = {'PLAY',
           ''}

class CPSBot:
    def __init__(self):

        # # initialization of the stage detection, at which page the game is
        # self.stage = None
        # self.stage_img_refs = []
        # self.hist_refs = []
        # for i in range(len(stage)):
        #     str_stage = stage[i]
        #     dir = "D://YanDengfeng//SRT//ROS//UR5e_kinematics//stage//ANALYZE.png"
        #     self.stage_img_refs[i] = cv2.imread(dir) #此处未完成路径拼接
        #     self.hist_refs[i] = cv2.calcHist([self.stage_img_refs[i]], [0], None, [256], [0.0, 255.0])
        
        # # command like clicking a settled button 
        # self.command = None
        # self.tp = TextProcess()

        # initialization of a target, in CPS Check
        self.target = IconProcess(4)


    # def prepost(self, frame):
    #     frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

    def detect_stage(self, frame):
        degree = []
        hist = cv2.calcHist([frame], [0], None, [256], [0.0, 255.0])
        for i in range(len(stage)):

            # calculate the similarity of hist and hist_ref
            degree[i] = 0
            for j in range(len(hist)):
                if hist[j] != self.hist_refs[i][j]:
                    degree[i] = degree[i] + (1 + abs(hist[j] - self.hist_refs[i][j]) / max(hist[j], self.hist_refs[i][j]))
                else:
                    degree[i] = degree[i] + 1
            degree[i] = degree[i] / len(hist)
        
        # the smaller the degree is, the more similar the images are
        min_degree = min(degree)
        min_index = np.argmin(degree)

        self.stage = stage[min_index]

    # def command(self, frame):
    #     ROI = frame[0:960, 0:80]
    #     tp.detect_text(ROI)
        
    def get_target_position(self, frame):
        target_position = self.target.get_icon_position(frame)
        return target_position
    
        
if __name__ == "__main__":
    # index = 1
    # video = cv2.VideoCapture('CPS.mp4')
    # while True:
    #     _, frame = video.read()
    #     if index == 1:
    #         cv2.imwrite("frame.png", frame)
    #         gray_blur = cv2.medianBlur(frame, 9)
    #         cv2.imwrite("gray_blur.png", gray_blur)
    #     if frame is None:
    #         break
    #     frame = cv2.resize(frame, dsize=None,fx=0.5,fy=0.5)
    #     # gray_blur = cv2.medianBlur(frame, 9)
    #     cps = CPSBot()
    #     target_position = cps.get_target_position(frame)
    #     if index == 1:
    #         cv2.imwrite("frame_process.png", frame)
    #     cv2.imshow('frame', frame)
    #     index = 2
    #     # sleep(0.02)
    #     cv2.waitKey(0)
    # cv2.destroyAllWindows()
    img = cv2.imread("D://YanDengfeng//SRT//ROS//UR5e_kinematics//Snipaste_2024-04-14_19-43-26.png")
    img = cv2.resize(img, dsize=None,fx=0.5,fy=0.5)
    cv2.imwrite("origin_img.png", img)
    gray_blur = cv2.medianBlur(img, 9)
    cv2.imwrite("gray_blur_img.png", gray_blur) 
    at = ArrowTrack()
    arrow_position = at.get_arrow_position(img)
    cv2.imwrite("process_img.png", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()