import cv2
import queue
import threading
import time
from paddleocr import PaddleOCR
import difflib
import logging
import numpy as np

# 自定义无缓存读视频类
class VideoCapture:
    """
        Customized VideoCapture, always read latest frame.
    """
    
    def __init__(self, camera_id):
        # "camera_id" is a int type id or string name
        self.cap = cv2.VideoCapture(camera_id)
        self.q = queue.Queue(maxsize=3)
        self.stop_threads = False    # to gracefully close sub-thread
        th = threading.Thread(target=self._reader)
        th.daemon = True             # 设置工作线程为后台运行
        th.start()

    # 实时读帧，只保存最后一帧
    def _reader(self):
        while not self.stop_threads:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait() 
                except queue.Empty:
                    pass
            self.q.put(frame)

    def read(self):
        return self.q.get()
    
    def terminate(self):
        self.stop_threads = True
        self.cap.release()


class ScreenProcess:
    """
        ScreenProcess created for detecting the pose of computer screen.
    """
    
    def __init__(self):
        self.is_screen = False
        self.box = []
        self.result_img = []
    
    def detect_screen(self, frame):

        self.is_screen = False  # make sure the flag is initialized.

        gray_blur = cv2.medianBlur(frame, 5)
        edges_img = cv2.Canny(gray_blur, 100, 200)

        cnts = cv2.findContours(edges_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

        if cnts != None:
            cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
            for cnt in cnts:
                cnt_len = cv2.arcLength(cnt, True)
                self.box = cv2.approxPolyDP(cnt, 0.01 * cnt_len, True)
                cnt_area = cv2.contourArea(cnt)
                if len(self.box) == 4 and cnt_area > 10000:
                    self.is_screen = True
                    cv2.drawContours(frame, [self.box], -1, (255, 255, 0), 3)
                    # print(self.box)
                    break

    def perspective_transform(self, frame):
        # resolution of a computer screen normally
        ROTATED_SIZE_W = 960
        ROTATED_SIZE_H = 540
        print(self.box)

        # prepost the box reached by function detect_screen
        # box_after = [0, 0, 0, 0]
        # sum_temp = []
        # index_temp = [0, 1, 2, 3]
        # for i in range(4):
        #     sum_temp.append(self.box[i][0][0] + self.box[i][0][1])
        # print("sum_temp", sum_temp)
        # min_index = np.argmin(sum_temp)
        # print("min_index", min_index)
        # max_index = np.argmax(sum_temp)
        # print("max_index", max_index)
        # index_temp.remove(min_index)
        # index_temp.remove(max_index)
        # print("index_temp", index_temp)
        # box_after[0] = self.box[min_index]
        # # print("box_after[0]", box_after[0])
        # box_after[3] = self.box[max_index]
        # # print("box_after[3]", box_after[3])
        # if self.box[index_temp[0]][0][0] > self.box[index_temp[1]][0][0]:
        #     box_after[1] = self.box[index_temp[0]]
        #     box_after[2] = self.box[index_temp[1]]
        # else:
        #     box_after[1] = self.box[index_temp[1]]
        #     box_after[2] = self.box[index_temp[0]]
        # print("box_after", box_after)

        # pts1 = np.float32([box_after[0], box_after[1], box_after[2], box_after[3]])
        pts1 = np.float32([self.box[1], self.box[0], self.box[3], self.box[2]])
        pts2 = np.float32([[0, 0], [ROTATED_SIZE_W, 0], [ROTATED_SIZE_W, ROTATED_SIZE_H], [0, ROTATED_SIZE_H], ])

        M = cv2.getPerspectiveTransform(pts1, pts2)
        self.result_img = cv2.warpPerspective(frame, M, (ROTATED_SIZE_W, ROTATED_SIZE_H))


class TextProcess:
    """
        TextProcess Created for processing the texts reached by camera.
    """
    def __init__(self):
        self.is_text = False
        self.txts = []
        self.scores = []
        self.start_point = []
        self.end_point = []
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch',use_gpu=False) # need to run only once to download and load model into memory
        logging.disable(logging.DEBUG)  # 关闭DEBUG日志的打印
        logging.disable(logging.WARNING)  # 关闭WARNING日志的打印       

    def detect_text(self, frame):
        # cv2.imshow("Camera", frame)
        result = self.ocr.ocr(frame, cls=True) # 这里的img_path可以直接换成图片
        for line in result:
            if line != None:
                # print(line)
                for element in line:
                    self.start_point = [int(num) for num in element[0][0]]
                    self.end_point = [int(num) for num in element[0][2]]
                    self.txts = element[1][0]
                    self.scores = element[1][1]
                if self.scores > 0.5:
                    self.is_text = True 

    def text_judgement(self, num):

        txts_ref = [ '此电脑', 'Solidworks', '新建文件夹','新建文件夹(2)']

        if num == 1:
            similarity = difflib.SequenceMatcher(None, self.txts, txts_ref[0]).ratio()
        elif num == 2:
            similarity = difflib.SequenceMatcher(None, self.txts, txts_ref[1]).ratio()
        elif num == 3:
            similarity = difflib.SequenceMatcher(None, self.txts, txts_ref[2]).ratio()
        elif num == 4:
            similarity = difflib.SequenceMatcher(None, self.txts, txts_ref[3]).ratio()
        else:
            print("wrong num!\n")
            
        if self.is_text==True and similarity > 0.8:
            cv2.rectangle(frame, self.start_point, self.end_point, 255, 2)
            
            print(self.start_point, self.end_point, self.txts)
                # cv2.rectangle(frame, start_point, end_point, (0,0,255), 2)
                # boxes = [int(num) for num in element[0]]


class ContourProcess:
    """
        ContourProcess created for detecting the contours of software's icon.
    """
    def __init__(self):
        self.cnts = []
        self.cnts_ref = []
        self.u = []
        self.v = []

        self.img_ref = np.array(['D:/YanDengfeng/SRT/ROS/UR5e_kinematics/Computer.png', 
                                 'D:/YanDengfeng/SRT/ROS/UR5e_kinematics/Solidworks.png',
                                 'D:/YanDengfeng/SRT/ROS/UR5e_kinematics/Folder.png'])
        self.hsv_img_ref = []
        for i in range(3):
            self.hsv_img_ref[i] = cv2.cvtColor(self.img_ref[i], cv2.COLOR_RGB2HSV)
        
        # Contour reference of a computer's icon
        lower_gray = np.array([90,50,50])
        upper_gray = np.array([110,255,255])
        gray_zone = cv2.inRange(self.hsv_img_ref[0], lower_gray, upper_gray)
        edges = cv2.Canny(gray_zone, 100, 200)
        self.cnts_ref[0], _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)    #获取轮廓，对轮廓不建立等级，压缩存储元素
        self.cnts_ref[0] = sorted(self.cnts_ref[0], key=cv2.contourArea, reverse=True)
        
        # Contour reference of a solidworks' icon
        lower_red = np.array([90,50,50])
        upper_red = np.array([110,255,255])
        red_zone = cv2.inRange(self.hsv_img_ref[1], lower_red, upper_red)
        edges = cv2.Canny(red_zone, 100, 200)
        self.cnts_ref[1], _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)    #获取轮廓，对轮廓不建立等级，压缩存储元素
        self.cnts_ref[1] = sorted(self.cnts_ref[1], key=cv2.contourArea, reverse=True)

        # Contour reference of a folder's icon
        lower_yellow = np.array([90,50,50])
        upper_yellow = np.array([110,255,255])
        yellow_zone = cv2.inRange(self.hsv_img_ref[2], lower_yellow, upper_yellow)
        edges = cv2.Canny(yellow_zone, 100, 200)
        self.cnts_ref[2], _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)    #获取轮廓，对轮廓不建立等级，压缩存储元素
        self.cnts_ref[2] = sorted(self.cnts_ref[2], key=cv2.contourArea, reverse=True)

    def detect_computer(self, frame):
        """
            function detect_folder created for detecting the position of computer icon.
        """

        hsv_img = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        lower_yellow = np.array([90,50,50])
        upper_yellow = np.array([110,255,255])
        yellow_zone = cv2.inRange(hsv_img, lower_yellow, upper_yellow)
        edges = cv2.Canny(yellow_zone, 100, 200)
        self.cnts, _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        u_temp = []
        v_temp = []
        folder_position_u = []
        folder_position_v = []

        for cnt in self.cnts:
            area = cv2.contourArea(cnt)
            moment1 = cv2.moments(cnt)
            hu1 = cv2.HuMoments(moment1).flatten()
            moment2 = cv2.moments(self.cnts_ref[2][0])
            hu2 = cv2.HuMoments(moment2).flatten()
            similarity = cv2.matchShapes(hu1, hu2, cv2.CONTOURS_MATCH_I3, 0)
            if similarity < 0.1 and area > 2000:
                for i in range(len(cnt)):
                    u_temp.append(cnt[i-1][0][0])
                    v_temp.append(cnt[i-1][0][1])
                folder_position_u.append(int(0.5*(max(u_temp)+min(u_temp))))
                folder_position_v.append(int(0.5*(max(v_temp)+min(v_temp))))
                u_temp = []
                v_temp = []
                cv2.drawContours(frame, cnt, -1, (0,255,0), 2)
                cv2.circle(frame, (folder_position_u[0],folder_position_v[0]), 2, color=(0,0,255), thickness=-1)
                print("folder position: ", [folder_position_u, folder_position_v])

    def detect_folder(self, frame):
        """
            function detect_folder created for detecting the position of folder icon.
        """

        hsv_img = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        lower_yellow = np.array([90,50,50])
        upper_yellow = np.array([110,255,255])
        yellow_zone = cv2.inRange(hsv_img, lower_yellow, upper_yellow)
        edges = cv2.Canny(yellow_zone, 100, 200)
        self.cnts, _ = cv2.findContours(edges.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

        u_temp = []
        v_temp = []
        folder_position_u = []
        folder_position_v = []

        for cnt in self.cnts:
            area = cv2.contourArea(cnt)
            moment1 = cv2.moments(cnt)
            hu1 = cv2.HuMoments(moment1).flatten()
            moment2 = cv2.moments(self.cnts_ref[2][0])
            hu2 = cv2.HuMoments(moment2).flatten()
            similarity = cv2.matchShapes(hu1, hu2, cv2.CONTOURS_MATCH_I3, 0)
            if similarity < 0.1 and area > 2000:
                for i in range(len(cnt)):
                    u_temp.append(cnt[i-1][0][0])
                    v_temp.append(cnt[i-1][0][1])
                folder_position_u.append(int(0.5*(max(u_temp)+min(u_temp))))
                folder_position_v.append(int(0.5*(max(v_temp)+min(v_temp))))
                u_temp = []
                v_temp = []
                cv2.drawContours(frame, cnt, -1, (0,255,0), 2)
                cv2.circle(frame, (folder_position_u[0],folder_position_v[0]), 2, color=(0,0,255), thickness=-1)
                print("folder position: ", [folder_position_u, folder_position_v])
        
    def contour_judgement(self, frame, num):
        
        if num == 1:
            self.detect_computer(self, frame)
        elif num == 2:
            self.detect_solidworks(self, frame)
        elif num == 3:    # 识别的是“新建文件夹”
            self.detect_folder(self, frame)            


# class IconProcess:
#     """
#         IconProcess created for detecting the position of software's icon.
#     """
#     def __init__(self, num):

#         if num == 1:
#             self.img_ref = cv2.imread('Computer.png', 0)
#             # self.lower_color = np.array([90,50,50])     # lower thresholds of yellow in hsv color-space
#             # self.upper_color = np.array([110,255,255])  # upper thresholds of yellow in hsv color-space

#         elif num == 2:
#             self.img_ref = cv2.imread('Solidworks.png', 0)
#             # self.lower_color = np.array([90,50,50])     # lower thresholds of yellow in hsv color-space
#             # self.upper_color = np.array([110,255,255])  # upper thresholds of yellow in hsv color-space

#         elif num == 3:
#             self.img_ref = cv2.imread('Folder.png', 0)
#             # self.lower_color = np.array([90,50,50])     # lower thresholds of yellow in hsv color-space
#             # self.upper_color = np.array([110,255,255])  # upper thresholds of yellow in hsv color-space
        
#         self.icon_loc = []
        
#     def detect_icon(self, frame):
#         """
#             function detect_folder created for detecting the position of icon.
#         """

#         frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         res = cv2.matchTemplate(frame_gray, self.img_ref, cv2.TM_CCOEFF)
#         threshold = 2000000
#         self.icon_loc = np.where( res >= threshold)

#     def get_icon_position(self, frame):
#         self.detect_icon(frame)
#         icon_position = self.icon_loc
#         w, h = self.img_ref.shape[::-1]
#         for pt in zip(*self.icon_loc[::-1]):
#             cv2.rectangle(frame, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
#         return icon_position


class IconProcess:
    """
        ArrowTrack created for tracking the cursor on the screen.
    """
    def __init__(self, num):
        
        if num == 1:
            self.template = cv2.imread('template/Folder.png', 0)
        
        elif num == 2:
            self.template = cv2.imread('template/Solidworks.png', 0)

        elif num == 3:
            self.template = cv2.imread('template/Edge.png', 0)

        elif num == 4:
            self.template = cv2.imread('template/Target.png', 0)
        
        elif num == 5:
            self.template = cv2.imread('template/Target_miss.png', 0)

        # self.max_loc = []
        self.top_left = []
        self.bottom_right = []

    def detect_icon(self, frame):

        w, h = self.template.shape[::-1]

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(frame_gray, self.template, cv2.TM_CCOEFF)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        self.top_left = max_loc
        self.bottom_right = (self.top_left[0] + w, self.top_left[1] + h)
    
    def get_icon_position(self, frame):
        self.detect_icon(frame)
        icon_position = np.array([0.5*(self.top_left[0]+self.bottom_right[0]),
                                   0.5*(self.top_left[1]+self.bottom_right[1])])
        cv2.rectangle(frame, self.top_left, self.bottom_right, 255, 2)
        return icon_position


class CursorTrack:
    """
        CursorTrack created for following cursor's tracks by optical-flow method.
    """
    def __init__(self):

        # Parameters of ShiTomasi corner detection
        self.feature_params = dict(maxCorners=100,
                                   qualityLevel=0.3,
                                   minDistance=7,
                                   blockSize=7)
        
        # Parameters of optical-flow method
        self.lk_params = dict(winSize=(15, 15),
                              maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        
        cap = cv2.VideoCapture(1)
        ret, self.old_frame = cap.read()
    
    # def upgrade(self):
        
class ArrowTrack:
    """
        ArrowTrack created for tracking the cursor on the screen.
    """
    def __init__(self):
        self.template = cv2.imread('template/Cursor.png', 0)
        # self.max_loc = []
        self.top_left = []
        self.bottom_right = []

    def detect_arrow(self, frame):

        w, h = self.template.shape[::-1]

        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(frame_gray, self.template, cv2.TM_CCOEFF)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        self.top_left = max_loc
        self.bottom_right = (self.top_left[0] + w, self.top_left[1] + h)
    
    def get_arrow_position(self, frame):
        self.detect_arrow(frame)
        arrow_position = np.array([0.5*(self.top_left[0]+self.bottom_right[0]),
                                   0.5*(self.top_left[1]+self.bottom_right[1])])
        cv2.rectangle(frame, self.top_left, self.bottom_right, 255, 2)
        return arrow_position


if __name__ == "__main__":        
    # 测试自定义VideoCapture类
    cap = VideoCapture(0)
    tp = TextProcess()
    cp = ContourProcess()
    while True:
        frame = cap.read()
        tp.detect_text(frame)
        tp.text_judgement(3)
        cv2.imshow("frame", frame)
        if chr(cv2.waitKey(1)&255) == 'q':  # 按 q 退出
            cap.terminate()
            break