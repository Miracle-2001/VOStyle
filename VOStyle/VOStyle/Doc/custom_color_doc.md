# 语义分割mask调色板选择文档

作者：杜海玮

时间：2022.12.28

关于如何改造屎山的一些经验以及函数文档

## 原理

### 颜色输入

在test_demo_mix.py文件中的一段函数指定了当前mask的颜色：

```python
'''
调色板建设工程，杜海玮
用户指定颜色变量 custom_color 
'''
def pred_click(image, bgpoint, cppoint, net, mode,custom_color):
    #model_name = './python_script/IOG_PASCAL.pth'
    img = Image.fromarray(cv2.cvtColor(
        image, cv2.COLOR_BGR2RGB))  # opencv 图像转换为Image图像
    img = np.array(img)  # Image图像转换为numpy数组
    mask = IOG_getmask(bgpoint, cppoint, img, net, False)
    mask = Image.fromarray(mask.astype('uint8')).convert('RGB')
    mask = cv2.cvtColor(np.asarray(mask), cv2.COLOR_RGB2BGR)
    random_color = [random.randint(0, 255), random.randint(
        0, 255), random.randint(0, 255)]
    
    sum_mask = mask.sum(axis=2)
    # for x in range(mask.shape[0]):
    #     for y in range(mask.shape[1]):
    #         if sum_mask[x][y] != 0:
    #             mask[x, y, :] = random_color[:]
    print(custom_color)
    for x in range(mask.shape[0]):
        for y in range(mask.shape[1]):
            if sum_mask[x][y] != 0:
                mask[x, y, :] = custom_color[:]

    return mask
```

注释掉的部分为之前的随机选色代码段，保留了恢复成随机选色模式的能力。

在该函数上添加参数

``````
custom_color
``````

形式为一个长度为3的列表，网络接受bgr形式的颜色参数。

### 颜色选择

在tableWidget.py文件中，增加颜色控件类：

````python
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
from PyQt5.QtWidgets import QApplication, QPushButton, QColorDialog , QWidget
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import QColor 
import sys 

class ColorDialog ( QWidget): 
    def __init__(self ): 
        super().__init__() 
        #颜色值
        color = QColor(0, 0, 0) 
        #位置
        self.setGeometry(300, 300, 350, 280) 
        #标题
        self.setWindowTitle('颜色选择') 
        #按钮名称
        self.button = QPushButton('Dialog', self) 
        self.button.setFocusPolicy(Qt.NoFocus) 
        #按钮位置
        self.button.move(40, 20) 
        #按钮绑定方法
        self.button.clicked.connect(self.showDialog) 
        self.setFocus()
        self.widget = QWidget(self) 
        self.widget.setStyleSheet('QWidget{background-color:%s} '%color.name()) 
        self.widget.setGeometry(130, 22, 200, 100) 
        #print(color)
        
    def showDialog(self): 
        col = QColorDialog.getColor() 
        print(col.name(),"\n")
        if col.isValid(): 
            self.widget.setStyleSheet('QWidget {background-color:%s}'%col.name()) 
        print(col.getRgb())
        return col.getRgb()
````

该类将输出一个rgb的四元组。

在表格按钮中新增对应按钮：

`````python
        #custom_color
        self.show_mask = QPushButton()
        self.show_mask.setText("选择mask颜色")
        self.show_mask.setObjectName("custom mask color")
        self.setItem(4, 0, QTableWidgetItem("custom_mask_color"))
`````

在调用该表格的connect中新增对应互动机制：

````python
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
            elif button.objectName() == "get mask":
                button.clicked.connect(self.start_get_mask)
            elif button.objectName() == "save mask":
                button.clicked.connect(self.save_current_mask)
            elif button.objectName() == "show mask":
                button.clicked.connect(self.change_show_mask_state)
            elif button.objectName() == "custom mask color":#选择mask颜色，施工中
                button.clicked.connect(self.chose_color)
````

这里需要注意，语义分割中的选择图片，标注图片以及对应的两个上传按钮是在该文件中的第一层实现的，而之后的语义分割动作封装了一个新的函数singal_connect来实现，意义不明，可能和别的操作有关，暂时不管，本着屎山不破坏原则先把调色盘加到它的末尾。

## 实现过程

之后便需要将颜色的选择和输入使用变量连接起来，在所有涉及相关传参的地方加上对应的变量名custom_color。涉及部分较多，不一一赘述，若修改建议善用搜索功能，推荐逐步修改，按照报错的时候的问题去改，这样可以最大限度的保证原始屎山结构稳定。

最后在main.py中汇合：

````python
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
            if isinstance(self.useListWidget.item(i), SegmentationItem):#函数来判断一个对象是否是一个已知的类型，类似 type()。施工custom_color
                img = self.useListWidget.item(i)(img, self.seg_mode,custom_color1)
            else:
                img = self.useListWidget.item(i)(img)
        return img
````

这里将传入的颜色元组变成一个列表，然后进行反转，成为bgr形式的长度为3的列表，完成。