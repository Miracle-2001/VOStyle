
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import scipy.misc as sm
from PIL import Image
import cv2
import settting

'''
颜色控件，参考
https://blog.csdn.net/weixin_30325071/article/details/97344026
https://blog.csdn.net/qq_15332903/article/details/54879615

test:

    app = QApplication(sys.argv) 
    qb = ColorDialog() 
    #res = qb.show()
    res = qb.showDialog()
    print(res)
    sys.exit(app.exec_())

'''
from PyQt5.QtWidgets import QApplication, QPushButton, QColorDialog, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import sys


class ColorDialog (QWidget):
    def __init__(self):
        super().__init__()
        # 颜色值
        color = QColor(0, 0, 0)
        # 位置
        self.setGeometry(300, 300, 350, 280)
        # 标题
        self.setWindowTitle('颜色选择')
        # 按钮名称
        self.button = QPushButton('Dialog', self)
        self.button.setFocusPolicy(Qt.NoFocus)
        # 按钮位置
        self.button.move(40, 20)
        # 按钮绑定方法
        self.button.clicked.connect(self.showDialog)
        self.setFocus()
        self.widget = QWidget(self)
        self.widget.setStyleSheet(
            'QWidget{background-color:%s} ' % color.name())
        self.widget.setGeometry(130, 22, 200, 100)
        # print(color)

    def showDialog(self):
        col = QColorDialog.getColor()
        print(col.name(), "\n")
        if col.isValid():
            self.widget.setStyleSheet(
                'QWidget {background-color:%s}' % col.name())
        print(col.getRgb())
        return col.getRgb()


class TableWidget(QTableWidget):
    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent=parent)
        self.mainwindow = parent
        self.setShowGrid(True)  # 显示网格
        self.setAlternatingRowColors(True)  # 隔行显示颜色
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().sectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().sectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setStretchLastSection(True)
        self.setFocusPolicy(Qt.NoFocus)
        self.seg = False
        self.mode = 0
        self.color = (0, 0, 0, 0)

    def signal_connect(self):
        for spinbox in self.findChildren(QSpinBox):
            self.seg = False
            spinbox.valueChanged.connect(self.update_item)
        for doublespinbox in self.findChildren(QDoubleSpinBox):
            self.seg = False
            doublespinbox.valueChanged.connect(self.update_item)
        for combox in self.findChildren(QComboBox):
            self.seg = False
            combox.currentIndexChanged.connect(self.update_item)
        for checkbox in self.findChildren(QCheckBox):
            self.seg = False
            checkbox.stateChanged.connect(self.update_item)
        for button in self.findChildren(QPushButton):  # 语义分割的运行按键
            if button.objectName() == "start button":
                button.clicked.connect(self.start_get_seg)
            elif button.objectName() == "save mask":
                button.clicked.connect(self.save_current_mask)
            elif button.objectName() == "show mask":
                button.clicked.connect(self.change_show_mask_state)
            elif button.objectName() == "custom mask color":  # 选择mask颜色，施工中
                button.clicked.connect(self.chose_color)

    def chose_color(self):
        #app = QApplication(sys.argv)
        qb = ColorDialog()
        res = qb.showDialog()
        print('color ', res)
        self.color = res
        # sys.exit(app.exec_())

    def update_seg_data(self):
        with open('./dots.txt', 'r', encoding="UTF-8") as f:
            data = f.read()
            mode, x0, y0, x1, y1, xc, yc = map(
                int, data.split(" ", 6))  # 分割字符串
        items = [self.mode, x0, y0, x1, y1, xc, yc]
        with open('./dots.txt', 'w', encoding="UTF-8") as f:
            for item in items:
                f.write(str(item) + " ")

    def start_get_seg(self):
        self.mode = 1
        self.seg = True
        self.update_seg_data()
        self.update_item(self.color)
        self.mode = 3
        self.seg = False
        self.update_item(self.color)

    # mask显示与否状态改变
    def change_show_mask_state(self):
        if self.mode <= 3:
            self.mode = 4  # not show
        else:
            self.mode = 3  # show

        # self.seg = False
        # self.update_seg_data()
        self.update_item(self.color)

    # 保存当前标注
    def save_current_mask(self):
        # 根据当前是图片分割还是视频分割保存在不同位置
        if self.mainwindow.filetype_is_video == False and self.mainwindow.video_seging == False:
            filename = 'lastest_mask.png'
            save_dir = os.path.join(
                self.mainwindow.main_save_dir_root, 'work_folder')
            save_dir = os.path.join(save_dir, 'masks_saved')
            mask = self.mainwindow.get_current_mask()
            print(save_dir)
            print(mask)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            cv2.imwrite(os.path.join(save_dir, filename), mask)  # 这里把sm变成了cv2

        elif self.mainwindow.video_seging_refining == False:
            filename = self.mainwindow.cur_frame_name
            save_dir = self.mainwindow.current_video_annotations_pre_save_dir
            self.mainwindow.add_new_object()
            mask = self.mainwindow.get_current_mask()
            mask = Image.fromarray(mask)
            resized_image = mask #.resize((1280, 720), Image.ANTIALIAS)

            print(save_dir)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            filename = filename.split('.')[0]+'.png'
            resized_image.save(os.path.join(save_dir, filename))

        else:  # 已经视频分割 正在处于修正阶段
            filename = self.mainwindow.cur_frame_name
            save_dir = self.mainwindow.current_video_annotations_refine_save_dir
            mask = self.mainwindow.get_current_mask()
            mask = Image.fromarray(mask)
            resized_image = mask #.resize((1280, 720), Image.ANTIALIAS)
            print(save_dir)
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            filename = filename.split('.')[0]+'.png'
            resized_image.save(os.path.join(save_dir, filename))

    def update_item(self, color):
        if self.seg == False:
            self.mainwindow.stop_seg()
            self.mainwindow.set_seg_mode(self.mode)
            param = self.get_params()
            self.mainwindow.useListWidget.currentItem().update_params(param)
            self.mainwindow.update_image(self.color)
        elif self.seg == True:
            self.mainwindow.start_seg()
            self.mainwindow.set_seg_mode(self.mode)
            param = self.get_params()
            self.mainwindow.useListWidget.currentItem().update_params(param)
            self.mainwindow.update_image(self.color)

    def update_params(self, param=None):
        for key in param.keys():
            box = self.findChild(QWidget, name=key)
            if isinstance(box, QSpinBox) or isinstance(box, QDoubleSpinBox):
                box.setValue(param[key])
            elif isinstance(box, QComboBox):
                box.setCurrentIndex(param[key])
            elif isinstance(box, QCheckBox):
                box.setChecked(param[key])

    def get_params(self):
        param = {}
        for spinbox in self.findChildren(QSpinBox):
            param[spinbox.objectName()] = spinbox.value()
        for doublespinbox in self.findChildren(QDoubleSpinBox):
            param[doublespinbox.objectName()] = doublespinbox.value()
        for combox in self.findChildren(QComboBox):
            param[combox.objectName()] = combox.currentIndex()
        for combox in self.findChildren(QCheckBox):
            param[combox.objectName()] = combox.isChecked()
        return param


class GrayingTableWidget(TableWidget):
    def __init__(self, parent=None):
        super(GrayingTableWidget, self).__init__(parent=parent)


class FilterTabledWidget(TableWidget):
    def __init__(self, parent=None):
        super(FilterTabledWidget, self).__init__(parent=parent)

        self.kind_comBox = QComboBox()
        self.kind_comBox.addItems(['均值滤波', '高斯滤波', '中值滤波'])
        self.kind_comBox.setObjectName('kind')

        self.ksize_spinBox = QSpinBox()
        self.ksize_spinBox.setObjectName('ksize')
        self.ksize_spinBox.setMinimum(1)
        self.ksize_spinBox.setSingleStep(2)

        self.setColumnCount(2)
        self.setRowCount(2)
        self.setItem(0, 0, QTableWidgetItem('类型'))
        self.setCellWidget(0, 1, self.kind_comBox)
        self.setItem(1, 0, QTableWidgetItem('核大小'))
        self.setCellWidget(1, 1, self.ksize_spinBox)

        self.signal_connect()


class MorphTabledWidget(TableWidget):
    def __init__(self, parent=None):
        super(MorphTabledWidget, self).__init__(parent=parent)

        self.op_comBox = QComboBox()
        self.op_comBox.addItems(
            ['腐蚀操作', '膨胀操作', '开操作', '闭操作', '梯度操作', '顶帽操作', '黑帽操作'])
        self.op_comBox.setObjectName('op')  # 什么OP

        self.ksize_spinBox = QSpinBox()
        self.ksize_spinBox.setMinimum(1)
        self.ksize_spinBox.setSingleStep(2)
        self.ksize_spinBox.setObjectName('ksize')

        self.kshape_comBox = QComboBox()
        self.kshape_comBox.addItems(['方形', '十字形', '椭圆形'])
        self.kshape_comBox.setObjectName('kshape')

        self.setColumnCount(2)
        self.setRowCount(3)
        self.setItem(0, 0, QTableWidgetItem('类型'))
        self.setCellWidget(0, 1, self.op_comBox)
        self.setItem(1, 0, QTableWidgetItem('核大小'))
        self.setCellWidget(1, 1, self.ksize_spinBox)
        self.setItem(2, 0, QTableWidgetItem('核形状'))
        self.setCellWidget(2, 1, self.kshape_comBox)
        self.signal_connect()


class GradTabledWidget(TableWidget):
    def __init__(self, parent=None):
        super(GradTabledWidget, self).__init__(parent=parent)

        self.kind_comBox = QComboBox()
        self.kind_comBox.addItems(['Sobel算子', 'Scharr算子', 'Laplacian算子'])
        self.kind_comBox.setObjectName('kind')

        self.ksize_spinBox = QSpinBox()
        self.ksize_spinBox.setMinimum(1)
        self.ksize_spinBox.setSingleStep(2)
        self.ksize_spinBox.setObjectName('ksize')

        self.dx_spinBox = QSpinBox()
        self.dx_spinBox.setMaximum(1)
        self.dx_spinBox.setMinimum(0)
        self.dx_spinBox.setSingleStep(1)
        self.dx_spinBox.setObjectName('dx')

        self.dy_spinBox = QSpinBox()
        self.dy_spinBox.setMaximum(1)
        self.dy_spinBox.setMinimum(0)
        self.dy_spinBox.setSingleStep(1)
        self.dy_spinBox.setObjectName('dy')

        self.setColumnCount(2)
        self.setRowCount(4)

        self.setItem(0, 0, QTableWidgetItem('类型'))
        self.setCellWidget(0, 1, self.kind_comBox)
        self.setItem(1, 0, QTableWidgetItem('核大小'))
        self.setCellWidget(1, 1, self.ksize_spinBox)
        self.setItem(2, 0, QTableWidgetItem('x方向'))
        self.setCellWidget(2, 1, self.dx_spinBox)
        self.setItem(3, 0, QTableWidgetItem('y方向'))
        self.setCellWidget(3, 1, self.dy_spinBox)

        self.signal_connect()


class ThresholdTableWidget(TableWidget):
    def __init__(self, parent=None):
        super(ThresholdTableWidget, self).__init__(parent=parent)

        self.thresh_spinBox = QSpinBox()
        self.thresh_spinBox.setObjectName('thresh')
        self.thresh_spinBox.setMaximum(255)
        self.thresh_spinBox.setMinimum(0)
        self.thresh_spinBox.setSingleStep(1)

        self.maxval_spinBox = QSpinBox()
        self.maxval_spinBox.setObjectName('maxval')
        self.maxval_spinBox.setMaximum(255)
        self.maxval_spinBox.setMinimum(0)
        self.maxval_spinBox.setSingleStep(1)

        self.method_comBox = QComboBox()
        self.method_comBox.addItems(
            ['二进制阈值化', '反二进制阈值化', '截断阈值化', '阈值化为0', '反阈值化为0', '大津算法'])
        self.method_comBox.setObjectName('method')

        self.setColumnCount(2)
        self.setRowCount(3)

        self.setItem(0, 0, QTableWidgetItem('类型'))
        self.setCellWidget(0, 1, self.method_comBox)
        self.setItem(1, 0, QTableWidgetItem('阈值'))
        self.setCellWidget(1, 1, self.thresh_spinBox)
        self.setItem(2, 0, QTableWidgetItem('最大值'))
        self.setCellWidget(2, 1, self.maxval_spinBox)

        self.signal_connect()


class EdgeTableWidget(TableWidget):
    def __init__(self, parent=None):
        super(EdgeTableWidget, self).__init__(parent=parent)

        self.thresh1_spinBox = QSpinBox()
        self.thresh1_spinBox.setMinimum(0)
        self.thresh1_spinBox.setMaximum(255)
        self.thresh1_spinBox.setSingleStep(1)
        self.thresh1_spinBox.setObjectName('thresh1')

        self.thresh2_spinBox = QSpinBox()
        self.thresh2_spinBox.setMinimum(0)
        self.thresh2_spinBox.setMaximum(255)
        self.thresh2_spinBox.setSingleStep(1)
        self.thresh2_spinBox.setObjectName('thresh2')

        self.setColumnCount(2)
        self.setRowCount(2)

        self.setItem(0, 0, QTableWidgetItem('阈值1'))
        self.setCellWidget(0, 1, self.thresh1_spinBox)
        self.setItem(1, 0, QTableWidgetItem('阈值2'))
        self.setCellWidget(1, 1, self.thresh2_spinBox)
        self.signal_connect()


class ContourTableWidget(TableWidget):
    def __init__(self, parent=None):
        super(ContourTableWidget, self).__init__(parent=parent)

        self.bbox_comBox = QComboBox()
        self.bbox_comBox.addItems(['正常轮廓', '外接矩形', '最小外接矩形', '最小外接圆'])
        self.bbox_comBox.setObjectName('bbox')

        self.mode_comBox = QComboBox()
        self.mode_comBox.addItems(['外轮廓', '轮廓列表', '外轮廓与内孔', '轮廓等级树'])
        self.mode_comBox.setObjectName('mode')

        self.method_comBox = QComboBox()
        self.method_comBox.addItems(['无近似', '简易近似'])
        self.method_comBox.setObjectName('method')

        self.setColumnCount(2)
        self.setRowCount(3)

        self.setItem(0, 0, QTableWidgetItem('轮廓模式'))
        self.setCellWidget(0, 1, self.mode_comBox)
        self.setItem(1, 0, QTableWidgetItem('轮廓近似'))
        self.setCellWidget(1, 1, self.method_comBox)
        self.setItem(2, 0, QTableWidgetItem('边界模式'))
        self.setCellWidget(2, 1, self.bbox_comBox)
        self.signal_connect()


class EqualizeTableWidget(TableWidget):
    def __init__(self, parent=None):
        super(EqualizeTableWidget, self).__init__(parent=parent)
        self.red_checkBox = QCheckBox()
        self.red_checkBox.setObjectName('red')
        self.red_checkBox.setTristate(False)
        self.blue_checkBox = QCheckBox()
        self.blue_checkBox.setObjectName('blue')
        self.blue_checkBox.setTristate(False)
        self.green_checkBox = QCheckBox()
        self.green_checkBox.setObjectName('green')
        self.green_checkBox.setTristate(False)

        self.setColumnCount(2)
        self.setRowCount(3)

        self.setItem(0, 0, QTableWidgetItem('R通道'))
        self.setCellWidget(0, 1, self.red_checkBox)
        self.setItem(1, 0, QTableWidgetItem('G通道'))
        self.setCellWidget(1, 1, self.green_checkBox)
        self.setItem(2, 0, QTableWidgetItem('B通道'))
        self.setCellWidget(2, 1, self.blue_checkBox)
        self.signal_connect()


class HoughLineTableWidget(TableWidget):
    def __init__(self, parent=None):
        super(HoughLineTableWidget, self).__init__(parent=parent)

        self.thresh_spinBox = QSpinBox()
        self.thresh_spinBox.setMinimum(0)
        self.thresh_spinBox.setSingleStep(1)
        self.thresh_spinBox.setObjectName('thresh')

        self.min_length_spinBox = QSpinBox()
        self.min_length_spinBox.setMinimum(0)
        self.min_length_spinBox.setSingleStep(1)
        self.min_length_spinBox.setObjectName('min_length')

        self.max_gap_spinbox = QSpinBox()
        self.max_gap_spinbox.setMinimum(0)
        self.max_gap_spinbox.setSingleStep(1)
        self.max_gap_spinbox.setObjectName('max_gap')

        self.setColumnCount(2)
        self.setRowCount(3)

        self.setItem(0, 0, QTableWidgetItem('交点阈值'))
        self.setCellWidget(0, 1, self.thresh_spinBox)
        self.setItem(1, 0, QTableWidgetItem('最小长度'))
        self.setCellWidget(1, 1, self.min_length_spinBox)
        self.setItem(2, 0, QTableWidgetItem('最大间距'))
        self.setCellWidget(2, 1, self.max_gap_spinbox)
        self.signal_connect()


class LightTableWidget(TableWidget):
    def __init__(self, parent=None):
        super(LightTableWidget, self).__init__(parent=parent)

        self.alpha_spinBox = QDoubleSpinBox()
        self.alpha_spinBox.setMinimum(0)
        self.alpha_spinBox.setMaximum(3)
        self.alpha_spinBox.setSingleStep(0.1)
        self.alpha_spinBox.setObjectName('alpha')

        self.beta_spinbox = QSpinBox()
        self.beta_spinbox.setMinimum(0)
        self.beta_spinbox.setSingleStep(1)
        self.beta_spinbox.setObjectName('beta')

        self.setColumnCount(2)
        self.setRowCount(2)

        self.setItem(0, 0, QTableWidgetItem('alpha'))
        self.setCellWidget(0, 1, self.alpha_spinBox)
        self.setItem(1, 0, QTableWidgetItem('beta'))
        self.setCellWidget(1, 1, self.beta_spinbox)
        self.signal_connect()


class GammaITabelWidget(TableWidget):
    def __init__(self, parent=None):
        super(GammaITabelWidget, self).__init__(parent=parent)
        self.gamma_spinbox = QDoubleSpinBox()
        self.gamma_spinbox.setMinimum(0)
        self.gamma_spinbox.setSingleStep(0.1)
        self.gamma_spinbox.setObjectName('gamma')

        self.setColumnCount(2)
        self.setRowCount(1)

        self.setItem(0, 0, QTableWidgetItem('gamma'))
        self.setCellWidget(0, 1, self.gamma_spinbox)
        self.signal_connect()


class Drawer():
    pass


class SegmentationWidget(TableWidget):
    def __init__(self, parent=None):
        # 设置控件属性
        # self.mode = 0
        super(SegmentationWidget, self).__init__(parent=parent)
        self.mainwindow = parent  # mainwindow是MyAPP
        self.seg_tpoint = QPushButton()
        self.seg_tpoint.setObjectName('rectangle')
        self.seg_tpoint.setText("框图")
        self.seg_tp_up = QPushButton()
        self.seg_tp_up.setObjectName("rectangle update")
        self.seg_tp_up.setText("上传")
        self.seg_cpoint = QPushButton()
        self.seg_cpoint.setObjectName('cpoint')
        self.seg_cpoint.setText("画点")
        self.seg_cp_up = QPushButton()
        self.seg_cp_up.setObjectName("cpoint update")
        self.seg_cp_up.setText("上传")

        self.pencil_start = QPushButton()
        self.pencil_start.setObjectName("pencil start")
        self.pencil_start.setText("铅笔")

        self.pencil_end = QPushButton()
        self.pencil_end.setObjectName("pencil end")
        self.pencil_end.setText("结束")

        self.eraser_start = QPushButton()
        self.eraser_start.setObjectName("eraser start")
        self.eraser_start.setText("橡皮")

        self.eraser_end = QPushButton()
        self.eraser_end.setObjectName("eraser end")
        self.eraser_end.setText("结束")

        self.setColumnCount(2)
        self.setRowCount(8)

        self.setCellWidget(0, 0, self.seg_tpoint)
        self.setCellWidget(0, 1, self.seg_tp_up)
        self.setCellWidget(1, 0, self.seg_cpoint)
        self.setCellWidget(1, 1, self.seg_cp_up)
        self.setCellWidget(2, 0, self.pencil_start)
        self.setCellWidget(2, 1, self.pencil_end)
        self.setCellWidget(3, 0, self.eraser_start)
        self.setCellWidget(3, 1, self.eraser_end)

        self.seg_tpoint.clicked.connect(self.draw_tpoints)
        self.seg_cpoint.clicked.connect(self.draw_cpoint)
        self.seg_tp_up.clicked.connect(self.update_tp)
        self.seg_cp_up.clicked.connect(self.update_cp)
        self.pencil_start.clicked.connect(self.use_pencil)
        self.pencil_end.clicked.connect(self.no_use_pencil)
        self.eraser_start.clicked.connect(self.use_eraser)
        self.eraser_end.clicked.connect(self.no_use_eraser)

        # 以上是真实发生的动作，以下是给这些动作格子命名
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.xc = 0
        self.yc = 0

        self.go = QPushButton()
        self.go.setText("语义分割")
        self.go.setObjectName("start button")
        self.setItem(2, 0, QTableWidgetItem('start_button'))
        # self.get_mask = QPushButton()
        # self.get_mask.setText("快乐扣图")
        # self.get_mask.setObjectName("get mask")
        # self.setItem(3, 0, QTableWidgetItem("get_mask"))
        self.save_mask = QPushButton()
        self.save_mask.setText("保存标注")
        self.save_mask.setObjectName("save mask")
        self.setItem(4, 0, QTableWidgetItem("save_mask"))

        self.show_mask = QPushButton()
        self.show_mask.setText("显示标注")
        self.show_mask.setObjectName("show mask")
        self.setItem(5, 0, QTableWidgetItem("show_mask"))
        # custom_color
        self.custom_mask_color = QPushButton()
        self.custom_mask_color.setText("选择mask颜色")
        self.custom_mask_color.setObjectName("custom mask color")
        self.setItem(6, 0, QTableWidgetItem("custom_mask_color"))


        self.setCellWidget(4, 0, self.go)
        self.setCellWidget(5, 0, self.custom_mask_color)
        self.setCellWidget(6, 0, self.save_mask)
        self.setCellWidget(7, 0, self.show_mask)
        self.setSpan(4, 0, 1, 2)
        self.setSpan(5, 0, 1, 2)
        self.setSpan(6, 0, 1, 2)
        self.setSpan(7, 0, 1, 2)
        self.signal_connect()

    def draw_tpoints(self):
        self.mainwindow.pause_play()
        self.mainwindow.stopdrawingdot()
        self.mainwindow.startdrawingrec()

    def draw_cpoint(self):
        self.mainwindow.pause_play()
        self.mainwindow.stopdrawingrec()
        self.mainwindow.startdrawingdot()

    def update_tp(self):
        self.x0, self.y0, self.x1, self.y1 = self.mainwindow.get_tpoint()
        self.mainwindow.stopdrawingrec()
        self.update_data()

    def update_cp(self):
        self.xc, self.yc = self.mainwindow.get_cpoint()
        self.mainwindow.stopdrawingdot()
        self.update_data()

    def update_data(self):
        mode = self.mainwindow.get_seg_mode()
        items = [mode, self.x0, self.y0, self.x1, self.y1, self.xc, self.yc]
        with open('./dots.txt', 'w', encoding="UTF-8") as f:
            for item in items:
                f.write(str(item) + " ")

    def use_pencil(self):
        print("i am using pencil")
        self.mainwindow.use_pencil(self.color)

    def use_eraser(self):
        print("i am using eraser")
        self.mainwindow.use_eraser()

    def no_use_pencil(self):
        print(1)
        self.mainwindow.no_use_pencil()

    def no_use_eraser(self):
        print(1)
        self.mainwindow.no_use_eraser()
