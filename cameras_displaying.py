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
    while True:
        for num in range(len(cameras)):
            if cameras[num].isOpened():
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
    while True: #not len(cameras) == len(caps):
        choose_cam = int(raw_input('Введите номер камеры: '))
        cameras.append(caps[choose_cam - 1])
        if len(cameras) == len(caps):
            print('Выведены все камеры')
            thread3 = threading.Thread(target=_user_deletion)
            thread3.start()
            thread3.join()
            break


def _user_deletion():
    global cameras, choose_del
    choose_del = int(raw_input('Введите номер камеры, чтобы удалить её с дисплея: '))
    cameras.remove(cameras[choose_del-1])


def _threading_initialization():
    thread1 = threading.Thread(target=_video_stream)
    thread2 = threading.Thread(target=_user_input)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    return thread1, thread2


if __name__ == '__main__':
    # warnings.simplefilter('ignore')
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
    _threading_initialization()
    
    
