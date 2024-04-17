from vision import *
from UR5e import *
from com import *
from Controller import *
from CPSBot import *
import numpy as np
import cv2
from time import sleep

def task_A():
    """
        Foul assignments included in task_A:
        1. To detect the screen, the icon and the cursor in the screen as well as their positions.
        2. To control the UR5e robot arm to move the keyboard like human.
        3. To double-click to launch Solidworks. 
        4. To grab and release the keyboard.
         
        Created bt Dengfeng Yan, April 2nd, 2004.
    """
    
    move_to_xyplane(0.20, -0.60, 0.2, -3.14165/2, 0, 0.)
    move_to_xyplane(0.20, -0.60, 0.047, -3.14165/2, 0, 0.)
    sleep(0.5)
    # move_to_xyplane(0.20, -0.60, 0.047, -3.14165/2, 0, 0.)
    bellow_close()

    cap = cv2.VideoCapture(1)

    ct = MyController()
    sp = ScreenProcess()
    at = ArrowTrack()
    ip = IconProcess(3)
    # tp = TextProcess()

    # move_to_xyplane(0.334, -0.45, 0.05, -3.14165/2, 0, 0.)
    index = 1

    while True:
        ret, frame = cap.read()

        sp.detect_screen(frame)
        
        if sp.is_screen == True:

            sp.perspective_transform(frame)
            screen_img = sp.result_img

            at.detect_arrow(screen_img)
            cursor_position = at.get_arrow_position(screen_img)
            
            ip.detect_icon(screen_img)
            icon_position = ip.get_icon_position(screen_img)

            # tp.detect_text(screen_img)
            # tp.text_judgement(3)

            # text_position = np.array([0.5*(tp.start_point[0]+tp.end_point[0]),
            #                           0.5*(tp.start_point[1]+tp.end_point[1])])
            
            if ct.is_inplace(icon_position, cursor_position) == False:
                increase_x, increase_y = ct.adjust(cursor_position, icon_position)
                increase_move(increase_x, increase_y, 0, 0)
                print("cursor_position", index, cursor_position)
                print("icon_position", index, icon_position)

            elif ct.is_inplace(icon_position, cursor_position) == True:
                print("Already here!") 
                sleep(2)
                index_2()
                sleep(3)
                break

            index = index + 1

            cv2.imshow("screen", screen_img)
        
        cv2.imshow("frame", frame)
        
        if chr(cv2.waitKey(1)&255) == 'q':  # 按 q 退出
            # cap.terminate()
            break
    
    move_to_xyplane(0.20, -0.60, 0.2, -3.14165/2, 0, 0.)
    move_to_xyplane(0.0, -0.50, 0.2, -3.14165/2, 0, 0.)
    move_to_xyplane(0.0, -0.50, 0.047, -3.14165/2, 0, 0.)
    sleep(2)
    bellow_open()
    sleep(3)
    move_to_xyplane(0.0, -0.50, 0.2, -3.14165/2, 0, 0.)


def task_B():
    """
        Foul assignments included in task_B:
        1. To detect the screen, the target and the cursor in the screen as well as their positions.
        2. To control the UR5e robot arm to move the keyboard like human.
        3. To click when a target is detected. 
        4. To grab and release the keyboard.
         
        Created bt Dengfeng Yan, April 9th, 2004.
    """
    
    # move_to_xyplane(0.20, -0.60, 0.2, -3.14165/2, 0, 0.)
    # move_to_xyplane(0.20, -0.60, 0.047, -3.14165/2, 0, 0.)
    # sleep(0.5)
    # move_to_xyplane(0.20, -0.60, 0.047, -3.14165/2, 0, 0.)
    # bellow_close()

    cap = cv2.VideoCapture(1)

    ct = MyController()
    sp = ScreenProcess()
    at = ArrowTrack()
    cps = CPSBot()
    # tp = TextProcess()

    index = 1

    sleep(5)
    index_1()

    # move_to_xyplane(0.334, -0.45, 0.05, -3.14165/2, 0, 0.)

    while True:
        ret, frame = cap.read()

        sp.detect_screen(frame)
        
        cv2.imshow("frame", frame)

        if sp.is_screen == True:

            sp.perspective_transform(frame)
            screen_img = sp.result_img
            

            at.detect_arrow(screen_img)
            cursor_position = at.get_arrow_position(screen_img)
            
            target_position = cps.get_target_position(screen_img)

            # tp.detect_text(screen_img)
            # tp.text_judgement(3)

            # text_position = np.array([0.5*(tp.start_point[0]+tp.end_point[0]),
            #                           0.5*(tp.start_point[1]+tp.end_point[1])])
            
            cv2.imshow("screen", screen_img)
            save_path = "{}/{:>03d}.jpg".format('fetch', index)
            cv2.imwrite(save_path, screen_img)

            if ct.is_inplace(target_position, cursor_position) == False:
                increase_x, increase_y = ct.adjust(cursor_position, target_position)
                increase_move(increase_x, increase_y, 0, 0)
                print("cursor_position", index, cursor_position)
                print("target_position", index, target_position)

            elif ct.is_inplace(target_position, cursor_position) == True:
                print("Already here!") 
                index_1()
                sleep(1.3)
                # break

            index = index + 1
        
        if chr(cv2.waitKey(1)&255) == 'q':  # 按 q 退出
            # cap.terminate()
            break
    
    # move_to_xyplane(0.20, -0.60, 0.2, -3.14165/2, 0, 0.)
    # move_to_xyplane(0.0, -0.50, 0.2, -3.14165/2, 0, 0.)
    # move_to_xyplane(0.0, -0.50, 0.047, -3.14165/2, 0, 0.)
    # sleep(2)
    # bellow_open()
    # sleep(3)
    # move_to_xyplane(0.0, -0.50, 0.2, -3.14165/2, 0, 0.)


if __name__ == "__main__":
    task_B()
    # ser.close()

