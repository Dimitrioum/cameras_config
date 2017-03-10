# -*- coding: utf-8 -*-
import threading
import time
import sys
import cv2
import re
import subprocess
import os
import warnings

def _check_stat_cam(index):
    return cv2.VideoCapture(index).read()[0]

def _get_cameras(numbers, devices, check_stat):
    global cameras_names
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    cameras_names = []

    for i in devices.split('\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                if int(dinfo['bus']) in numbers and 'root' not in dinfo['tag'].split(' '):
                    cameras_names.append(dinfo['tag'])

    if (check_stat):
        cameras_names.insert(0, 'stationary')
        numbers.append(len(numbers)+1)

    return dict(zip([(i+1) for i in range(len(numbers))], cameras_names))

def _get_all_devices():
    df = subprocess.check_output("lsusb", shell=True)
    return df

def _video_stream():
    global cameras

    def _is_opened(video_obj):
        return video_obj.isOpened()

    while True:
        for num in range(len(cameras)):
            if map(_is_opened, cameras):
                rets, frames = cameras[num].read()
                if(rets):
                    cv2.imshow('camera%d' % (num + 1), frames)
                    cv2.waitKey(1)

def _stream_initialization(list_of_cameras):
    global choose_cam, caps, cameras
    caps = [] # all devices available
    cameras = [] # displayed devices
    for item in range(len(list_of_cameras)):
        caps.append(cv2.VideoCapture(item))
    choose_cam = 0
    cameras.append(caps[0])

def _user_input():
    global choose_cam, cameras, caps
    while True:
        if raw_input() == 'add':
            choose_cam = int(raw_input('Введите номер камеры: '))
            if caps[choose_cam - 1] in cameras:
                print('Камера уже выведена на дисплей!')
            elif len(cameras) == len(caps):
                print('Выведены все камеры')
            else:
                cameras.append(caps[choose_cam - 1])
        elif raw_input() == 'del':
            choose_del = int(raw_input('Введите номер камеры, чтобы удалить её с дисплея: '))
            cameras.remove(cameras[choose_del - 1])
            caps[choose_del - 1].release()
            cv2.destroyWindow('camera%d' % choose_del)
        elif (raw_input() != 'add') and (raw_input() != 'del'):
            print('Введите add для добавления камеры, del - для удаления камеры с дисплея')




# def _user_deletion():
#     global cameras, choose_del
#     choose_del = int(raw_input('Введите номер камеры, чтобы удалить её с дисплея: '))
#     cameras.remove(cameras[choose_del-1])


def _threading_initialization():
    thread1 = threading.Thread(target=_video_stream)
    thread2 = threading.Thread(target=_user_input)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    return thread1, thread2


if __name__ == '__main__':
    #check if there is a stationary camera
    check_stat = _check_stat_cam(0)

    #get the list of all connected devices
    devices = _get_all_devices()
    print(devices)

    #choose necessary devices
    numbers = raw_input('Введите номера USB-портов видеокамер через запятую для дальнейшей работы: ').split(',')
    numbers = [int(i) for i in numbers]

    print(_get_cameras(numbers, devices, check_stat))

    #init the videostream
    _stream_initialization(cameras_names)

    #thread creating
    #thread_lock = threading.Lock()

    _threading_initialization()

    # thread1 = threading.Thread(target=_video_stream)
    # thread2 = threading.Thread(target=_user_input)
    #
    # thread1.start()
    # thread2.start()
    #
    # thread1.join()
    # thread2.join()

    # while True:
    #     if raw_input() == 'next':
    #         _user_input()
    #     elif raw_input() == 'del':
    #         _user_deletion()
    #     else:
    #         print('Для добавления камеры введите next')

