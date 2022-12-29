# 铅笔橡皮文档使用文档

作者：张登甲

时间：2022.12.28

## 原理

### 初始条件

1. 设置文件

    设置文件`settting.py`主要保存了一些重要参数，后续可能会进行更新（英文确实打错了，不要在意这些细节)
    内容如下

    ```python
    PEN_COLOR = (255,0,0)
    ERASE_COLOR = [0,0,0]
    PENCIL_WIDTH = 20
    ERASER_WIDTH = 20
    ```
    `PEN_COLOR`代表笔的颜色，`ERASE_COLOR`代表橡皮的颜色，`PENCIL_WIDTH`代表笔的粗细，`ERASER_WIDTH`代表橡皮的粗细.

2. 设置笔的粗细和颜色

    ```python
    def start_drawing(self,img,custom_color = settting.PEN_COLOR):
        custom_color1 = list(custom_color)
        img2 = self.img_to_pixmap(img)
        img2.scaled(img2.width(),img2.height(),aspectRatioMode=Qt.IgnoreAspectRatio,transformMode=Qt.SmoothTransformation)
        self._scene2.addPixmap(img2)
        
        #self.pen.setColor(QColor(settting.PEN_COLOR[2],settting.PEN_COLOR[1],settting.PEN_COLOR[0]))
        self.pen.setColor(QColor(custom_color1[0],custom_color1[1],custom_color1[2]))
        self.pen.setWidth(settting.PENCIL_WIDTH)
        self.drawing = True
    ```

    在函数开始，设置笔的粗细和颜色，笔的颜色调用的是调色板设置的颜色，具体内容请查看调色板相关文档，笔的粗细调用了设置文件里的笔的粗细。

3. 设置橡皮的粗细和颜色

    ```python
    def start_erase(self,img):
        img2 = self.img_to_pixmap(img)
        self._scene2.addPixmap(img2)
        self.pen.setColor(QColor(settting.ERASE_COLOR[2],settting.ERASE_COLOR[1],settting.ERASE_COLOR[0]))
        self.pen.setWidth(settting.ERASER_WIDTH)
        self.drawing = True
    ```

    对于橡皮的粗细，则直接调用了设置文件里的橡皮颜色和橡皮粗细，因为橡皮的颜色基本无需改动。


### 画笔动作

1. 主要动作在`grahpicsView.py`文件中

    ```python
    def paint_path(self):
        item = QGraphicsLineItem()
        item.setPen(self.pen)
        
        item.setLine(self.lastx,self.lasty,self.currx,self.curry)
        self._scene.addItem(item)
        self.drawitems.append(item)
    ```

    该函数的核心功能是添加线条，从而达到填充像素的目的,`drawitems`是一个列表，主要储存添加了什么东西。

2. 在鼠标按下动作

    ```python
    def mousePressEvent(self, event):
        super(GraphicsView, self).mousePressEvent(event)
        viewpoint = QPoint(event.pos())
        scenePoint = self.mapToScene(viewpoint)
        self.now_x,self.now_y = scenePoint.x(),scenePoint.y()
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
    ```

    `drawing`表示正在绘画，首先取得当前的`x`,`y`坐标，然后令`flag`为真，表示鼠标当前已经按下

3. 鼠标移动动作

    ```python
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
    ```

    `flag`表示鼠标按下，`drawing`表示正在绘画，如果正在绘画，就更新当前的坐标参数，然后通过`paint_path()`函数更新路径，最后更新坐标参数即可。

4. 结束动作（更新mask和图片）

    ```python
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
        tmp = image
        cv_image = np.zeros((tmp.height(), tmp.width(), 3), dtype=np.uint8)
        print('begin cv_image type:',type(cv_image))
        for row in range(0, tmp.height()):
            for col in range(0, tmp.width()):
                r = qRed(tmp.pixel(col, row))
                g = qGreen(tmp.pixel(col, row))
                b = qBlue(tmp.pixel(col, row))
                # cv_image[row, col, 0] = r
                # cv_image[row, col, 1] = g
                # cv_image[row, col, 2] = b
                cv_image[row, col, 0] = b
                cv_image[row, col, 1] = g
                cv_image[row, col, 2] = r

        final_pic = cv2.imread('./work_folder/segmentation_temp/seg_photo.jpg')
        sum_covery = final_pic.sum(axis=2)
        for c in range(3):
            a = settting.PEN_COLOR[c]
            final_pic[:, :, c] = np.where(
                sum_covery <=10, 0,a)


        for item in self.drawitems:
            self._scene.removeItem(item)
            self._scene2.removeItem(item)
        self.update()
        self.drawing = False
        return cv_image
    ``` 

    结束画笔的使用之后，画笔会将当前的图片转化成`numpy`类型的数据然后保存起来，同时也会在本地以`jpg`格式保存留作备份。

    由于转化成为`numpy`是遍历整个图片的操作，所以会导致用时过长的问题，也可以直接通过`cv2`读取保存的图片文件，但是这样会导致图片失真，所以最终选用转化为`numpy`的方法加强准确性。

    橡皮的结束功能同理，故这里不予以展示。

    ```python
        def no_use_pencil(self):

            self.seg_img = self.graphicsView.end_drawing()
            self.change_mask(self.seg_img)
            img = test_demo_mix.show_image_process(self.src_img.copy(), self.
            seg_img, self.seg_mode)
            self.cur_img = img
            self.graphicsView.update_image(img)
    ```

    该函数的功能主要是将`mask`更新，然后更新整张图片

    