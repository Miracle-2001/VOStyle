from ctypes import resize
import cv2
import os
import numpy as np
import json
import shutil
from PIL import Image
from config import _palette, color_palette
# from CFBImaster.eval_net import start_prediction
from skimage.morphology.binary import binary_dilation


class videoSegmentationProducer():
    def __init__(self, parent, gap=5):
        self.mainwindow = parent
        self.cur_video = None
        self.frame_gap = gap

        # main_save_dir_root="../"
        # 创建分割视频的images帧目录
        # self.video_annotations_save_dir=self.mainwindow.video_annotations_save_dir

        # self.frames_save_dir = self.mainwindow.frames_save_dir
        # #创建分割视频的mask目录
        # self.annotations_save_dir = self.mainwindow.annotations_save_dir
        # #生成的视频帧集标注结果保存地址
        # self.segmentationResults_save_dir = self.mainwindow.segmentationResults_save_dir
        # #合成视频保存地址   ##
        # self.video_save_dir = os.path.join(
        #     self.mainwindow.main_save_dir_root, 'work_folder', 'video_generated')

        # 一些list，来存帧和标注的情况
        self.frames_list = []  # 保存原视频每一帧的名字
        # 保存每一个标注对应原视频的名字。也即，如果在第00000.jpg进行标注，这个list就会插入一个内容为00000.jpg的string
        self.annotations_list = []
        # 当前显示的是第几帧
        self.cur_pointer = 0
        self.before_seg = True

        # if not os.path.exists(self.frames_save_dir):
        #     os.makedirs(self.frames_save_dir)
        # if not os.path.exists(self.annotations_save_dir):
        #     os.makedirs(self.annotations_save_dir)
        # if not os.path.exists(self.segmentationResults_save_dir):
        #     os.makedirs(self.segmentationResults_save_dir)

    # 删除文件夹中全部内容并创建新文件夹
    def delete_files(self, path):
        shutil.rmtree(path)

    def change_cur_video(self, src_video):
        print("changing Video")
        self.cur_video = src_video
        self.frames_list.clear
        self.annotations_list.clear
        self.cur_pointer = 0
        self.before_seg = True
        self.video_name = src_video.split(".")[0].split("/")[1]
        # self.delete_files(self.frames_save_dir)
        # self.delete_files(self.annotations_save_dir)
        # self.delete_files(self.segmentationResults_save_dir)
        self.video_current_work_folder = os.path.join(
            self.mainwindow.video_annotations_save_dir, self.video_name)
        print("video_curr ", self.video_current_work_folder)

        if os.path.exists(self.video_current_work_folder):
            self.delete_files(self.video_current_work_folder)

        os.mkdir(self.video_current_work_folder)
        self.frames_save_dir = os.path.join(
            self.video_current_work_folder, 'video_frames')
        os.mkdir(self.frames_save_dir)
        # 创建分割视频的mask目录
        self.annotations_save_dir = os.path.join(
            self.video_current_work_folder, 'video_labels_pre')
        self.mainwindow.current_video_annotations_pre_save_dir = self.annotations_save_dir
        os.mkdir(self.annotations_save_dir)

        # 生成的视频帧集标注结果保存地址
        self.segmentationResults_save_dir = os.path.join(
            self.video_current_work_folder, 'video_labels_gen')
        os.mkdir(self.segmentationResults_save_dir)
        self.mainwindow.current_video_annotations_refine_save_dir = self.segmentationResults_save_dir
        #合成视频保存地址   ##
        self.video_save_dir = self.segmentationResults_save_dir

        self.mainwindow.clear_list()

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

                    resized_image = image # .resize((1280, 720), Image.ANTIALIAS)

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
        print("add object ", frame_name)
        if frame_name not in self.annotations_list:
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
        # os.system("cd CFBImaster")

        ##os.system("python eval_net.py")
        os.system(
            f"python .\\aot\\tools\\demo.py --video_name {self.video_name}")
        # os.system("cd..")
        self.cur_pointer = 0
        self.before_seg = False
        self.show_frame()
        return

    def jpg2png(self, name: str):
        tmp = name.split('.')
        assert (tmp[1] == 'jpg')
        return tmp[0]+'.png'

    def show_frame(self):
        print("show_frame ")
        print(self.annotations_list)
        print(self.frames_list)
        print('cur ', self.cur_pointer)
        cur_frame_name = os.path.join(
            os.path.join(self.frames_save_dir, self.frames_list[self.cur_pointer]))
        img = cv2.imdecode(np.fromfile(
            cur_frame_name, dtype=np.uint8), -1)
        self.mainwindow.cur_frame_name = self.frames_list[self.cur_pointer]
        self.mainwindow.clear_mask()

        mask = None
        cur_mask_name = None
        if self.before_seg == True:  # 还没有开始视频分割 从video_annotation文件里面找mask
            cur_name = self.frames_list[self.cur_pointer]
            if cur_name in self.annotations_list:
                cur_name = self.jpg2png(cur_name)
                cur_mask_name = os.path.join(
                    os.path.join(self.annotations_save_dir, cur_name))
                mask = cv2.imdecode(np.fromfile(
                    cur_mask_name, dtype=np.uint8), -1)

        else:
            cur_mask_name = os.path.join(
                os.path.join(self.segmentationResults_save_dir, self.jpg2png(self.frames_list[self.cur_pointer])))
            mask = cv2.imdecode(np.fromfile(
                cur_mask_name, dtype=np.uint8), -1)

        print(cur_frame_name)
        print(cur_mask_name)
        if mask is None:
            print("mask is None")
        else:
            print("mask isn't None")
        self.mainwindow.change_image_with_mask(img, mask)

    # 下一帧

    def next_frame(self):
        print("...................", self.frames_list)
        if self.cur_pointer != len(self.frames_list)-1:
            self.cur_pointer += 1
            self.show_frame()
        return

    # 上一帧
    def last_frame(self):
        if self.cur_pointer != 0:
            self.cur_pointer -= 1
            self.show_frame()
        return

    # 结束视频分割 （还没有完善）
    def end_video_segmentation(self):
        self.cur_video = None
        self.cur_pointer = 0
        self.frames_list.clear
        self.annotations_list.clear
        self.before_seg = True
        self.mainwindow.clear_list()
        return

    def video_generate(self):
        def get_file_names(search_path):
            for (dirpath, _, filenames) in os.walk(search_path):
                for filename in filenames:
                    yield filename  # os.path.join(dirpath, filename)

        def save_to_video(mask_save_dir, img_save_dir, output_video_file, frame_rate):

            if not os.path.exists(output_video_file):
                os.makedirs(output_video_file)
            output_video_file += '\\video.mp4'

            list_files = [i for i in get_file_names(mask_save_dir)]
            # 拿一张图片确认宽高
            img0 = cv2.imread(os.path.join(
                mask_save_dir, list_files[0]))
            # print(img0)
            height, width, layers = img0.shape
            # 视频保存初始化 VideoWriter
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 或*'mp4v'
            videowriter = cv2.VideoWriter(
                output_video_file, fourcc, frame_rate, (width, height))
            # 核心，保存的东西
            for f in list_files:
                if f.split('.')[1]!='jpg' and f.split('.')[1]!='png':
                    continue
                # f = '%s.png' % f
                # print("saving..." + f)
                input_img_path = os.path.join(
                    img_save_dir, f.split('.')[0] + '.jpg')
                input_mask_path = os.path.join(
                    mask_save_dir,
                    f.split('.')[0] + '.png')
                input_image = Image.open(input_img_path)
                input_label = Image.open(input_mask_path)

                overlayed_image = overlay(
                    np.array(input_image, dtype=np.uint8),
                    np.array(input_label, dtype=np.uint8), color_palette)
                videowriter.write(overlayed_image[..., [2, 1, 0]])

            videowriter.release()
            cv2.destroyAllWindows()
            print('Success save %s!' % output_video_file)

        def overlay(image, mask, colors=[0, 0, 0], cscale=1, alpha=0.4):
            colors = np.atleast_2d(colors) * cscale

            im_overlay = image.copy()
            object_ids = np.unique(mask)

            for object_id in object_ids[1:]:
                # Overlay color on  binary mask

                foreground = image * alpha + np.ones(
                    image.shape) * (1 - alpha) * np.array(colors[object_id])
                binary_mask = mask == object_id

                # Compose image
                im_overlay[binary_mask] = foreground[binary_mask]

                countours = binary_dilation(binary_mask) ^ binary_mask
                im_overlay[countours, :] = 0

            return im_overlay.astype(image.dtype)

        save_to_video(self.segmentationResults_save_dir, self.frames_save_dir,
                      self.video_save_dir, int(20/self.frame_gap))


# # 图片变视频
# output_dir = 'img/flower/'
# mask_save_dir = os.path.join(output_dir, '')  # 输入图片存放位置
# output_video_file = 'video/flower_20.mp4'  # 输入视频保存位置以及视频名称
# save_to_video(mask_save_dir, output_video_file, 20/)
