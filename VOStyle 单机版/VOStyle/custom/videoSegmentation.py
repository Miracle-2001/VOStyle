from ctypes import resize
import cv2
import os
import numpy as np
import json
from PIL import Image
#from CFBImaster.eval_net import start_prediction


class videoSegmentationProducer():
    def __init__(self, parent, gap=5):
        self.mainwindow = parent
        self.cur_video = None
        self.frame_gap = gap
        # 一些保存路径
        self.frames_save_dir = os.path.join(self.mainwindow.main_save_dir_root,
                                            'work_folder', 'video_frames')
        self.annotations_save_dir = os.path.join(self.mainwindow.main_save_dir_root,
                                                 'work_folder', 'video_annotations')
        self.segmentationResults_save_dir = os.path.join(self.mainwindow.main_save_dir_root,
                                                         'work_folder', 'segmentation_results')
        # 一些list，来存帧和标注的情况
        self.frames_list = []
        self.annotations_list = []
        # 当前显示的是第几帧
        self.cur_pointer = 0

        if not os.path.exists(self.frames_save_dir):
            os.makedirs(self.frames_save_dir)
        if not os.path.exists(self.annotations_save_dir):
            os.makedirs(self.annotations_save_dir)
        if not os.path.exists(self.segmentationResults_save_dir):
            os.makedirs(self.segmentationResults_save_dir)

    # 修改当前video
    def change_cur_video(self, src_video):
        self.cur_video = src_video

    def get_name(self, str):
        need = 5-len(str)
        res = str
        for i in range(need):
            res = '0'+res
        return res

    # 把视频分成一帧一帧
    def split_cur_video(self):

        now_seg_video = cv2.VideoCapture(self.cur_video)

        number_of_frame = 0
        while (now_seg_video.isOpened()):
            ret, frame = now_seg_video.read()
            if ret:
                if number_of_frame % self.frame_gap == 0:
                    image = Image.fromarray(
                        cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                    resized_image = image.resize((1280, 720), Image.ANTIALIAS)

                    resized_image.save(os.path.join(self.frames_save_dir, self.get_name(str(
                        number_of_frame))+'.jpg'))
                number_of_frame += 1
            else:
                break

        self.frames_list = os.listdir(self.frames_save_dir)
        self.frames_list.sort()

        for f in self.frames_list:
            print('find files: ', f)
        self.cur_pointer = 0

        # 回溯前，把第一帧送到change image里并显示:
        first_frame_name = os.path.join(
            os.path.join(self.frames_save_dir, self.frames_list[0]))
        img = cv2.imdecode(np.fromfile(
            first_frame_name, dtype=np.uint8), -1)

        self.mainwindow.cur_frame_name = self.frames_list[0]
        self.mainwindow.change_image(img)
    # 新标注了一个物体，加入annotations_list里面

    def add_object(self, frame_name):
        self.annotations_list.append(frame_name)
    # 生成json

    def json_file_process(self):
        objectDict = {}
        for i in range(len(self.annotations_list)):
            start_frame = self.annotations_list[i]
            j = self.frames_list.index(start_frame)
            cur_frame_list = self.frames_list[j:len(self.frames_list)]
            cur_frame_list = [sr.split('.')[0] for sr in cur_frame_list]
            cur_dict = {"category": None, "frames": cur_frame_list}
            objectDict[str(i+1)] = cur_dict
        fileDirDict = {"objects": objectDict}
        fileDirDict = {"annotations": fileDirDict}
        fileDirDict = {"videos": fileDirDict}
        json_save_path = os.path.join(
            self.mainwindow.main_save_dir_root, 'work_folder')

        with open(os.path.join(json_save_path, "meta.json"), "w") as f:
            json.dump(fileDirDict, f)

        return
    # 开始分割 （还没有完善）

    def start_video_segmentation(self):
        self.json_file_process()
        # start_prediction()
        #os.system("cd CFBImaster")
        os.system("python eval_net.py")
        # os.system("cd..")
        return
    # 下一帧

    def next_frame(self):
        if self.cur_pointer != len(self.frames_list)-1:
            self.cur_pointer += 1
            cur_frame_name = os.path.join(
                os.path.join(self.frames_save_dir, self.frames_list[self.cur_pointer]))
            img = cv2.imdecode(np.fromfile(
                cur_frame_name, dtype=np.uint8), -1)
            self.mainwindow.cur_frame_name = self.frames_list[self.cur_pointer]
            self.mainwindow.change_image(img)

        return
    # 上一帧

    def last_frame(self):
        if self.cur_pointer != 0:
            self.cur_pointer -= 1
            cur_frame_name = os.path.join(
                os.path.join(self.frames_save_dir, self.frames_list[self.cur_pointer]))
            img = cv2.imdecode(np.fromfile(
                cur_frame_name, dtype=np.uint8), -1)
            self.mainwindow.cur_frame_name = self.frames_list[self.cur_pointer]
            self.mainwindow.change_image(img)

        return
    # 结束视频分割 （还没有完善）

    def end_video_segmentation(self):
        self.cur_video = None
        self.cur_pointer = 0
        self.frames_list.clear
        self.annotations_list.clear
        return
