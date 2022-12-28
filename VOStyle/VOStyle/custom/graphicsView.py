import cv2

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import numpy as np
import settting

class GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super(GraphicsView, self).__init__(parent=parent)
        self.mainwindow = parent
        self._zoom = 0
        self._empty = True
        self._photo = QGraphicsPixmapItem()
        self._scene = QGraphicsScene(self)
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setAlignment(Qt.AlignCenter)  # 居中显示
        self.setDragMode(QGraphicsView.ScrollHandDrag)  # 设置拖动
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumSize(640, 480)
        self.x0 = 0
        self.y0 = 0
        self.x1 = 0
        self.y1 = 0
        self.xc0 = 0
        self.yc0 = 0
        self.xc1 = 0
        self.yc1 = 0
        self.flag = False  # 鼠标是否按下了
        self.move = False  # 鼠标是否在移动
        self.paint_rec = False  # 当前是否需要画矩形
        self.paint_dot = False  # 当前是否需要画点
        self.rec = None
        self.dot = None
        self.drawing = False    #是否在添加像素
        self.drawitems = []
        

        self.pen = QPen(Qt.SolidLine)
        self.pen.setColor(QColor(settting.PEN_COLOR[0],settting.PEN_COLOR[1],settting.PEN_COLOR[2]))
        self.pen.setWidth(settting.PENCIL_WIDTH)

        self.currx = 0
        self.curry = 0
        self.lastx = 0
        self.lasty = 0
        
        self._scene2 = QGraphicsScene(None)
        
        


    def contextMenuEvent(self, event):
        if not self.has_photo():
            return
        menu = QMenu()
        save_action = QAction('图片另存为', self)
        save_action.triggered.connect(self.save_current)  # 传递额外值
        menu.addAction(save_action)
        menu.exec(QCursor.pos())

    def save_current(self):
        file_name = QFileDialog.getSaveFileName(
            self, '图片另存为', './', 'Image files(*.jpg *.gif *.png)')[0]
        print(file_name)
        if file_name:
            self._photo.pixmap().save(file_name)

    def get_image(self):
        if self.has_photo():
            return self._photo.pixmap().toImage()

    def has_photo(self):
        return not self._empty

    def change_image(self, img):
        self.update_image(img)
        self.fitInView()

    def img_to_pixmap(self, img):
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # bgr -> rgb
        h, w, c = img.shape  # 获取图片形状
        image = QImage(img, w, h, 3 * w, QImage.Format_RGB888)
        return QPixmap.fromImage(image)

    def update_image(self, img):
        self.mainwindow.start_play()  # 视频开始播放
        self._empty = False
        self._photo.setPixmap(self.img_to_pixmap(img))

    def fitInView(self, scale=True):
        # 转化图片大小
        rect = QRectF(self._photo.pixmap().rect())
        
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.has_photo():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def wheelEvent(self, event):
        if self.has_photo():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def mousePressEvent(self, event):
        super(GraphicsView, self).mousePressEvent(event)
        viewpoint = QPoint(event.pos())
        scenePoint = self.mapToScene(viewpoint)
        if self.drawing:
            self.currx,self.curry,self.lastx,self.lasty = (0,0,0,0)
            self.lastx = scenePoint.x()
            self.lasty = scenePoint.y()
            self.flag = True

        else:
            if self.paint_rec == True:
                self.x0, self.y0, self.x1, self.y1 = (0, 0, 0, 0)
                self.x0 = scenePoint.x()
                self.y0 = scenePoint.y()
                self.flag = True
            if self.paint_dot == True:
                self.xc0, self.yc0, self.xc1, self.yc1 = (0, 0, 0, 0)
                self.xc0 = scenePoint.x()
                self.yc0 = scenePoint.y()
                self.flag = True

    def painting_dot(self):
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.red)
        self.dot = QGraphicsLineItem()
        self.dot.setPen(pen)
        if self.xc1 == 0 and self.yc1 == 0:
            self.xc1 = self.xc0
            self.yc1 = self.yc0
        self.dot.setLine(self.xc0, self.yc0, self.xc1, self.yc1)
        self._scene.addItem(self.dot)

    def paint_rectangle(self):
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(Qt.red)
        self.rec = QGraphicsRectItem()
        self.rec.setPen(pen)
        if self.x0 > self.x1:
            self.x0, self.x1 = self.x1, self.x0
        if self.y0 > self.y1:
            self.y0, self.y1 = self.y1, self.y0
        self.rec.setRect(QRectF(self.x0, self.y0, np.abs(
            self.x0 - self.x1), np.abs(self.y0 - self.y1)))
        self._scene.addItem(self.rec)

    def paint_path(self):
        item = QGraphicsLineItem()
        item.setPen(self.pen)
        
        item.setLine(self.lastx,self.lasty,self.currx,self.curry)
        self._scene.addItem(item)
        self.drawitems.append(item)


    def mouseReleaseEvent(self, event):
        super(GraphicsView, self).mouseReleaseEvent(event)
        if self.paint_rec == True and self.move == True:
            if self.rec != None:
                self._scene.removeItem(self.rec)
            self.paint_rectangle()
        if self.paint_dot == True:
            if self.dot != None:
                self._scene.removeItem(self.dot)
            self.painting_dot()
        self.flag = False
        self.move = False

    def mouseMoveEvent(self, event):
        super(GraphicsView, self).mouseMoveEvent(event)
        self.move = True
        viewpoint = QPoint(event.pos())
        scenePoint = self.mapToScene(viewpoint)
        if self.flag and self.drawing:
            
                self.currx = scenePoint.x()
                self.curry = scenePoint.y()
                self.paint_path()
                
                self.update() #更新显示

                self.lastx = self.currx
                self.lasty = self.curry

        else:
            if self.flag and self.paint_rec:
                self.x1 = scenePoint.x()
                self.y1 = scenePoint.y()
                if self.rec != None:
                    self._scene.removeItem(self.rec)
                self.update()
                self.paint_rectangle()
            if self.flag and self.paint_dot:
                self.xc1 = scenePoint.x()
                self.yc1 = scenePoint.y()
                if self.dot != None:
                    self._scene.removeItem(self.dot)
                self.update()
                self.painting_dot()

    def startdrawingrec(self):
        self.paint_rec = True

    def stopdrawingrec(self):
        if self.rec is not None:
            self._scene.removeItem(self.rec)
        self.paint_rec = False

    def startdrawingdot(self):
        self.paint_dot = True

    def stopdrawingdot(self):
        if self.dot is not None:
            self._scene.removeItem(self.dot)
        self.paint_dot = False

    def get_tpoint(self):
        return int(self.x0), int(self.y0), int(self.x1), int(self.y1)

    def get_cpoint(self):
        # 返回画线的中点
        return int((self.xc0 + self.xc1) / 2), int((self.yc0 + self.yc1) / 2)

    def start_drawing(self,img):
        #self.mask.setPixmap(self.img_to_pixmap(img))
        #self._scene2.addItem(self.mask)
        img2 = self.img_to_pixmap(img)
        self._scene2.addPixmap(img2)
        self.pen.setColor(QColor(settting.PEN_COLOR[2],settting.PEN_COLOR[1],settting.PEN_COLOR[0]))
        self.pen.setWidth(settting.PENCIL_WIDTH)
        self.drawing = True

    def end_drawing(self):
        photo = self._photo.pixmap()
        
        image = QImage(photo.size(),QImage.Format_RGB32)
        painter = QPainter()
        painter.begin(image)
        painter.setRenderHint(QPainter.Antialiasing)
        for item in self.drawitems:
            self._scene2.addItem(item)
        self._scene2.render(painter)
        painter.end()
        image.save('./work_folder/segmentation_temp/seg_photo.jpg')
        final_pic = cv2.imread('./work_folder/segmentation_temp/seg_photo.jpg')
        
        for item in self.drawitems:
            self._scene.removeItem(item)
            self._scene2.removeItem(item)
        self.update()
        self.drawing = False
        return final_pic

    def start_erase(self,img):
        img2 = self.img_to_pixmap(img)
        self._scene2.addPixmap(img2)
        self.pen.setColor(QColor(settting.ERASE_COLOR[2],settting.ERASE_COLOR[1],settting.ERASE_COLOR[0]))
        self.pen.setWidth(settting.ERASER_WIDTH)
        self.drawing = True

    def end_erase(self):
        photo = self._photo.pixmap()
        
        image = QImage(photo.size(),QImage.Format_ARGB32)
        painter = QPainter()
        painter.begin(image)
        for item in self.drawitems:
            self._scene2.addItem(item)
        self._scene2.render(painter)
        painter.end()
        image.save('./work_folder/segmentation_temp/seg_photo.jpg')
        final_pic = cv2.imread('./work_folder/segmentation_temp/seg_photo.jpg')
        for item in self.drawitems:
            self._scene.removeItem(item)
            self._scene2.removeItem(item)
        self.update()
        self.drawing = False
        return final_pic
    
