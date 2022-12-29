import cv2
import numpy as np
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *


class FileSystemTreeView(QTreeView, QDockWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.mainwindow = parent
        self.fileSystemModel = QFileSystemModel()
        self.fileSystemModel.setRootPath('.')
        self.setModel(self.fileSystemModel)
        # 隐藏size,date等列
        self.setColumnWidth(0, 200)
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)
        # 不显示标题栏
        self.header().hide()
        # 设置动画
        self.setAnimated(True)
        # 选中不显示虚线
        self.setFocusPolicy(Qt.NoFocus)
        self.doubleClicked.connect(self.select_image)
        self.setMinimumWidth(200)
        self.chose_new = False
        self.is_playing = False

    def select_image(self, file_index):  # 在双击选择了图片或视频后会调用这个函数

        # 如果当前软件正在进行分割 则选择无效
        if self.mainwindow.seging == True or self.mainwindow.video_seging == True:
            return

        file_name = self.fileSystemModel.filePath(file_index)
        self.new_select()
        if file_name.endswith(('.jpg', '.png', '.bmp')):  # 选中的是图片
            self.mainwindow.filetype_is_video = False
            src_img = cv2.imdecode(np.fromfile(file_name, dtype=np.uint8), -1)
            self.mainwindow.change_image(src_img)

        elif file_name.endswith(('.mp4')):
            self.mainwindow.filetype_is_video = True

            src_video = cv2.VideoCapture(file_name)
            self.mainwindow.load_video(file_name)
            while self.is_playing == True:
                None
            self.chose_new = False
            while (src_video.isOpened()):
                if self.chose_new:
                    self.chose_new = False
                    self.is_playing = False
                    break
                if self.mainwindow.video_seging:
                    self.is_playing = False
                    break
                ret, frame = src_video.read()
                self.playing = self.mainwindow.get_play_status()
                while self.playing is False:
                    self.playing = self.mainwindow.get_play_status()  # 更新播放状态
                    cv2.waitKey(int(1000 / 20))
                if ret:
                    self.mainwindow.change_image(frame)
                else:
                    break
                cv2.waitKey(50)  # 延时播放

    def new_select(self):
        self.chose_new = True
        self.mainwindow.stop_seg()
        items = [0, 0, 0, 0, 0, 0, 0]
        with open('./dots.txt', 'w', encoding="UTF-8") as f:
            for item in items:
                f.write(str(item) + " ")
