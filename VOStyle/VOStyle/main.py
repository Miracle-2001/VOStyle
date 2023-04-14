import sys
import cv2
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import matplotlib.pyplot as plt
import os
from custom.stackedWidget import StackedWidget
from custom.treeView import FileSystemTreeView
from custom.listWidgets import FuncListWidget, UsedListWidget
from custom.graphicsView import GraphicsView
from custom.listWidgetItems import SegmentationItem
from custom.videoSegmentation import videoSegmentationProducer
from python_script import test_demo_mix

class MyApp(QMainWindow):
    def __init__(self):
        # os.system("python .\\aot\\tools\\demo.py --video_name cxk")
        # super函数调用自己的父类，这里即调用QMainWindow这个父类的init函数
        super(MyApp, self).__init__()
        self.playing = True
        self.tool_bar = self.addToolBar('工具栏')
        #当前地址
        self.main_save_dir_root = os.path.dirname(os.path.abspath(__file__))


        #创建分割视频的images帧目录  
        # self.frames_save_dir = os.path.join(self.main_save_dir_root,
        #                                                 'work_folder','video_annotation')#,'frames','video_name')
        # if not os.path.exists(self.frames_save_dir):
        #     os.mkdir(self.frames_save_dir)

        #创建分割视频的mask目录   
        #保证二者‘video_name’一致#
        self.video_annotations_save_dir = os.path.join(self.main_save_dir_root,
                                                        'work_folder','video_annotation')#,'masks','video_name')#, 'video_annotations')
        if not os.path.exists(self.video_annotations_save_dir):
            os.mkdir(self.video_annotations_save_dir)

        # #生成的视频帧集标注结果保存地址
        # self.segmentationResults_save_dir = os.path.join(self.main_save_dir_root,
        #                                                         'work_folder', 'video_annotation')
        # if not os.path.exists(self.segmentationResults_save_dir):
        #     os.mkdir(self.segmentationResults_save_dir)

        #######没动######
        # self.segmentationResults_temp_dir = os.path.join(self.main_save_dir_root,
        #                                             'work_folder', 'segmentation_temp')#zdj保留mask的图片                                                 
        # if not os.path.exists(self.segmentationResults_temp_dir):
        #     os.makedirs(self.segmentationResults_temp_dir)
        #######没动######

        self.cur_frame_name = None

        self.action_right_rotate = QAction(
            QIcon("icons/右旋转.png"), "向右旋转90", self)
        self.action_left_rotate = QAction(
            QIcon("icons/左旋转.png"), "向左旋转90°", self)
        self.action_histogram = QAction(QIcon("icons/直方图.png"), "直方图", self)
        self.action_start_play = QAction(
            QIcon("icons/startplay.png"), "开始播放", self)
        self.action_pause_play = QAction(
            QIcon("icons/stopplaying.png"), "暂停播放", self)

        self.action_chosen = QAction(
            QIcon("icons/choseToSplit.png"), "选定视频", self)
        self.action_start_video_seg = QAction(
            QIcon("icons/startSeg.png"), "开始标注", self)
        self.action_end_video_seg = QAction(
            QIcon("icons/endSeg.png"), "结束选择", self)
        self.action_video_generate = QAction(
            QIcon("icons/geVideo.png"), "生成视频", self)

        self.action_last_frame = QAction(
            QIcon("icons/lastFrame.png"), "上一帧", self)
        self.action_next_frame = QAction(
            QIcon("icons/nextFrame.png"), "下一帧", self)
        # 以上这段是关于图标的路径，我认为我们可以换一套好看点的图标，这套灰不拉几的太丑了
        self.action_right_rotate.triggered.connect(self.right_rotate)
        self.action_left_rotate.triggered.connect(self.left_rotate)
        self.action_histogram.triggered.connect(self.histogram)
        self.action_start_play.triggered.connect(self.start_play)
        self.action_pause_play.triggered.connect(self.pause_play)
        self.action_chosen.triggered.connect(self.chosen_video)
        self.action_start_video_seg.triggered.connect(self.start_video_seg)
        self.action_video_generate.triggered.connect(self.video_generate)
        self.action_end_video_seg.triggered.connect(self.end_video_seg)
        self.action_last_frame.triggered.connect(self.last_frame)
        self.action_next_frame.triggered.connect(self.next_frame)
        # trigger即qt中的动作，即若用户点击，则某事发生
        self.tool_bar.addActions((self.action_left_rotate, self.action_right_rotate,
                                 self.action_histogram, self.action_start_play, self.action_pause_play,
                                 self.action_chosen, self.action_start_video_seg, self.action_video_generate, self.action_end_video_seg,
                                 self.action_last_frame, self.action_next_frame
                                  ))

        self.useListWidget = UsedListWidget(self) #已添加的功能显示 右侧
        self.funcListWidget = FuncListWidget(self) #图像对应的具体操作 上侧
        self.stackedWidget = StackedWidget(self) #每个操作的属性功能 右侧
        self.fileSystemTreeView = FileSystemTreeView(self) #文件选择 左侧
        self.graphicsView = GraphicsView(self) #图像操作 中央
        # self.videoProducer = videoSegmentationProducer(self,gap=5) #视频操作 中央

        self.dock_file = QDockWidget(self)
        self.dock_file.setWidget(self.fileSystemTreeView)
        self.dock_file.setTitleBarWidget(QLabel('目录'))
        self.dock_file.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.dock_func = QDockWidget(self)
        self.dock_func.setWidget(self.funcListWidget)
        self.dock_func.setTitleBarWidget(QLabel('图像操作'))
        self.dock_func.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.dock_used = QDockWidget(self)
        self.dock_used.setWidget(self.useListWidget)
        self.dock_used.setTitleBarWidget(QLabel('已选操作'))
        self.dock_used.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dock_used.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.dock_attr = QDockWidget(self)
        self.dock_attr.setWidget(self.stackedWidget)
        self.dock_attr.setTitleBarWidget(QLabel('属性'))
        self.dock_attr.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.dock_attr.close()

        self.setCentralWidget(self.graphicsView)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_file)
        self.addDockWidget(Qt.TopDockWidgetArea, self.dock_func)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_used)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_attr)

        self.setWindowTitle('VOStyle 面向视频的像素智能标注系统')
        self.setWindowIcon(QIcon('icons/main.png'))
        self.src_img = None
        self.cur_img = None
        self.seg_img = None
        self.seging = False  # 记录是否在图片分割状态
        self.cur_video = None  # 记录当前选定的视频（如果有的话）
        self.video_seging_refining = False

        self.seg_mode = 0
        self.video_seging = False  # 记录是否在视频分割状态
        self.filetype_is_video = False  # 记录当前界面的是否是视频

    def set_seg_mode(self, mode):
        self.seg_mode = mode

    def get_seg_mode(self):
        return self.seg_mode

    def start_seg(self):
        self.seging = True

    def stop_seg(self):
        self.seging = False

    def get_play_status(self):
        return self.playing

    def update_image(self,color):#施工custom_color
        if self.src_img is None:
            return
        print("count ", self.useListWidget.count())
        img = self.process_image(color)
        self.cur_img = img
        self.graphicsView.update_image(img)

    def change_image(self, img,color = (0,0,0,0)):#施工custom_color
        self.src_img = img
        img = self.process_image(color)
        self.cur_img = img
        self.graphicsView.change_image(img)

    def process_image(self,custom_color):#施工custom_color
        custom_color1 = list(custom_color)[:3]
        custom_color1 = custom_color1[::-1]
        print(custom_color1)
        if self.seging == False:
            img = self.src_img.copy()
        # 如果正在进行seg操作的话
        elif self.seging is True:
            img = self.cur_img.copy()
        for i in range(self.useListWidget.count()):
            # if isinstance(self.useListWidget.item(i), SegmentationItem):#函数来判断一个对象是否是一个已知的类型，类似 type()。施工custom_color
            #     img = self.useListWidget.item(i)(img, self.seg_mode,custom_color1)
            if isinstance(self.useListWidget.item(i), SegmentationItem):
                if self.seg_mode == 1 or self.seg_mode ==3:
                    img = self.useListWidget.item(i)(img, self.seg_mode,custom_color1)
                    self.seg_img = self.get_current_mask()
                else:
                    img = self.useListWidget.item(i)(img, self.seg_mode,custom_color1)
                    
            else:
                img = self.useListWidget.item(i)(img)
        return img

    def get_current_mask(self):
        combined_mask = None
        for i in range(self.useListWidget.count()):
            if isinstance(self.useListWidget.item(i), SegmentationItem):
                combined_mask = self.useListWidget.item(i).get_mask_only()
                break
        return combined_mask

    def change_mask(self,img):
        for i in range(self.useListWidget.count()):
            if isinstance(self.useListWidget.item(i), SegmentationItem):
                self.useListWidget.item(i).change_mask(img)
                break 

    def start_play(self):
        if self.playing is False:
            self.playing = True

    def pause_play(self):
        if self.playing is True:
            self.playing = False
    # 载入当前视频

    def load_video(self, src_video):
        self.cur_video = src_video
    # 选定当前视频

    def chosen_video(self):
        if self.filetype_is_video == False:
            return
        self.videoProducer = videoSegmentationProducer(self,gap=5)
        self.video_seging = True
        self.videoProducer.change_cur_video(self.cur_video)
        self.videoProducer.split_cur_video()

    def clear_list(self):
        tmp_list = []
        for i in range(self.useListWidget.count()):
            tmp_list.append(self.useListWidget.item(i))
        for i in range(len(tmp_list)):
            self.useListWidget.delete_item(tmp_list[i])

    # 开始分割

    def start_video_seg(self):
        if self.filetype_is_video == False or self.video_seging == False:
            return
        self.videoProducer.start_video_segmentation()
        self.video_seging_refining = True

    # 新增object
    def add_new_object(self):
        self.videoProducer.add_object(self.cur_frame_name)

    def clear_mask(self):
        for i in range(self.useListWidget.count()):
            if isinstance(self.useListWidget.item(i), SegmentationItem):
                self.useListWidget.item(i).clear_mask()

    def change_image_with_mask(self, img, mask):
        for i in range(self.useListWidget.count()):
            if isinstance(self.useListWidget.item(i), SegmentationItem):
                self.useListWidget.item(i).change_mask(mask)
        self.change_image(img)

    # 结束分割
    def end_video_seg(self):
        if self.filetype_is_video == False or self.video_seging == False:
            return
        self.video_seging = False
        self.video_seging_refining = False
        self.videoProducer.end_video_segmentation()

    def video_generate(self):
        self.videoProducer.video_generate()

    # 下一帧
    def next_frame(self):
        if self.filetype_is_video == False or self.video_seging == False:
            return
        self.videoProducer.next_frame()

    # 上一帧
    def last_frame(self):
        if self.filetype_is_video == False or self.video_seging == False:
            return
        self.videoProducer.last_frame()

    def right_rotate(self):
        self.graphicsView.rotate(90)

    def left_rotate(self):
        self.graphicsView.rotate(-90)

    def histogram(self):
        color = ('b', 'g', 'r')
        for i, col in enumerate(color):
            histr = cv2.calcHist([self.cur_img], [i], None, [256], [0, 256])
            histr = histr.flatten()
            plt.plot(range(256), histr, color=col)
            plt.xlim([0, 256])
        plt.show()

    def startdrawingrec(self):
        self.graphicsView.startdrawingrec()

    def stopdrawingrec(self):
        self.graphicsView.stopdrawingrec()

    def startdrawingdot(self):
        self.graphicsView.startdrawingdot()

    def stopdrawingdot(self):
        self.graphicsView.stopdrawingdot()

    def get_tpoint(self):
        return self.graphicsView.get_tpoint()

    def get_cpoint(self):
        return self.graphicsView.get_cpoint()
    
    def use_pencil(self,custom_color):#将画笔颜色与调色盘颜色统一
        self.graphicsView.start_drawing(self.seg_img,custom_color)

    def no_use_pencil(self):
        self.seg_img = self.graphicsView.end_drawing()
        print(self.seg_img.shape)
        self.change_mask(self.seg_img)
        img = test_demo_mix.show_image_process(self.src_img.copy(), self.seg_img, self.seg_mode)
        self.cur_img = img
        self.graphicsView.update_image(img)

    def use_eraser(self):
        self.graphicsView.start_erase(self.seg_img)

    def no_use_eraser(self):
        self.seg_img = self.graphicsView.end_erase()
        self.change_mask(self.seg_img)
        img = test_demo_mix.show_image_process(self.src_img.copy(), self.seg_img, self.seg_mode)
        self.cur_img = img
        self.graphicsView.update_image(img)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(open('./custom/styleSheet.qss', encoding='utf-8').read())
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
