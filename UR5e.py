import numpy as np
import socket
import time
import struct
import util

HOST = "169.254.193.95"
PORT = 30003


def get_current_tcp():
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((HOST, PORT))
    data = tcp_socket.recv(1108)
    position = struct.unpack('!6d', data[444:492])
    tcp_socket.close()
    return np.asarray(position)


def get_current_pos():  # x, y, theta
    tcp = get_current_tcp()
    print(tcp)
    rpy = util.rv2rpy(tcp[3], tcp[4], tcp[5])
    return np.asarray([tcp[0], tcp[1], rpy[-1]])


def move_to_tcp(target_tcp):
    tool_acc = 0.5  # Safe: 0.5
    tool_vel = 0.1  # Safe: 0.2
    tool_pos_tolerance = [0.001, 0.001, 0.001, 0.05, 0.05, 0.05]
    tcp_command = "movel(p[%f,%f,%f,%f,%f,%f],a=%f,v=%f,t=0,r=0)\n" % (
        target_tcp[0], target_tcp[1], target_tcp[2], target_tcp[3], target_tcp[4],
        target_tcp[5],
        tool_acc, tool_vel)
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect((HOST, PORT))
    tcp_socket.send(str.encode(tcp_command))  # 利用字符串的encode方法编码成bytes，默认为utf-8类型
    tcp_socket.close()
    # 确保已达到目标点，就可以紧接着发送下一条指令
    actual_pos = get_current_tcp()
    target_rpy = util.rv2rpy(target_tcp[3], target_tcp[4], target_tcp[5])
    rpy = util.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
    while not (all([np.abs(actual_pos[j] - target_tcp[j]) < tool_pos_tolerance[j] for j in range(3)])
               and all([np.abs(rpy[j] - target_rpy[j]) < tool_pos_tolerance[j+3] for j in range(3)])):
        actual_pos = get_current_tcp()
        rpy = util.rv2rpy(actual_pos[3], actual_pos[4], actual_pos[5])
        time.sleep(0.01)


def increase_move(delta_x, delta_y, delta_z, delta_theta):
    tcp = get_current_tcp()
    rpy = util.rv2rpy(tcp[3], tcp[4], tcp[5])
    rpy[2] = rpy[2] + delta_theta
    target_rv = util.rpy2rv(rpy)
    target_tcp = np.asarray([tcp[0] + delta_x, tcp[1] + delta_y, tcp[2] + delta_z,
                             target_rv[0], target_rv[1], target_rv[2]])
    move_to_tcp(target_tcp)


def move_down():
    tcp = get_current_tcp()
    tcp[2] = 0.15
    move_to_tcp(tcp)


def move_up():
    tcp = get_current_tcp()
    tcp[2] = 0.25
    move_to_tcp(tcp)
    

def init_ur5():
    go_home()
    move_down()


def go_home():
    move_to_tcp([0, 0, 1, 0, 0., 0.])


def move_to_xyplane(x, y, z, alpha, beta, gamma):
    # move_to_tcp([0.36, -0.39, 0.1, -3.14165/2, 0, 0.])
    move_to_tcp([x, y, z, alpha, beta, gamma])


if __name__ == '__main__':
    # go_home()

    move_to_xyplane(0.30, -0.50, 0.2, -3.14165/2, 0, 0.)
    # move_to_xyplane(0.0, -0.50, 0.2, -3.14165/2, 0, 0.)