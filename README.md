# VOStyle

# 说明文档

**运行命令：**python main.py

**requirement:**

- opencv系列库
- pytorch 系列库
- numpy
- PyQt5
- scipy
- imageio
- PIL

另外，由于IOG和AOT网络过大，无法随代码一同上传，所以请自行下载并移动到指定位置。

请进入https://github.com/shiyinzhang/Inside-Outside-Guidance下载IOG_PASCAL.pth（https://drive.google.com/file/d/1GLZIQlQ-3KUWaGTQ1g_InVcqesGfGcpW/view）

并移动到python_script文件夹下

请进入https://github.com/yoxu515/aot-benchmark下载R50_AOTL_PRE_YTB_DAV.pth（https://drive.google.com/file/d/1qJDYn3Ibpquu4ffYoQmVjg1YCbr2JQep/view）

并移动到aot/pretrain_models文件夹下

**主要文件：**

- main.py ：运行前端的文件，定义了MyAPP类，里面创建了窗口中各个对象的实例
- icons：保存着窗口中各个按钮/栏目的图标
- image：保存着测试用的图像
- python_script：里面保存着用于图片语义分割的代码
    - test_demo_mix.py：定义了pred_click()函数
- dots.txt：保存着语义分割的模式（分为在原图画彩色mask和只保留原图mask部分两种）和六个点的坐标
- custom：设定了主窗口各个部分的组件和功能函数
    - graphicsView.py：重载了GraphicsView类，主要功能是对图片和视频等进行展示，其展示的功能是通过设置一个GraphicsScene来实现的，每次更换图片，就是重新更换Scene中的Item（具体的逻辑关系可以去了解下GraphicsView类，View-Scene-Item的关系类似于容器-场景-实例的关系）
    - ListWidgetitems.py：里面定义了列表Items，即主窗口上侧的列表功能的具体实现。每个类里面的`__init__()`会初始化操作的参数，`__call__()`会根据参数返回进行操作后的图片
    - ListWidgets.py：里面设定了表格的样式和重载了一些添加功能的操作，一般不需要修改
    - stackedWidget.py：同上，一般不需要修改
    - styleSheet.qss：设计了主窗口的不同部分的风格，可以通过这里修改各个部件的颜色，字体等
    - tableWidget.py：设计了右侧功能的属性窗口，定义的参数通过这个类传给MyAPP类，并根据参数修改图片，更新图片
    - videoSegmentation.py：一切关于视频分割的操作
    - treeView.py：主要设计了左侧文件选择的功能
        - select_image：根据file_name来选择文件，并读取图片，将其传给MyAPP类

**选择图片的函数调用及思路：**

首先在treeView.py中设计了选择图片的功能，用户选择图片后，调用select_image函数，将用户选择的文件的路径读入并加载为opencv格式的图片，然后调用MyAPP的change_image函数。

在change_image函数中，首先将MyAPP中的变量self.src_img设置为当前选择的img，并对当前img调用self.process_image()函数，这个函数可以将图片经过右侧功能栏已选的一系列操作；然后将self.cur_img设置为转化后的图片，并通过调用self.graphicsView中的update_image将图片展示窗口中的图片转化为当前转化后的图片。



**视频级语义分割**

步骤：

1.双击视频

2.点工具栏的OK

3.上一帧下一帧按钮调整，每一帧都可以按语义分割来分割**（注意！①语义分割之后要点保存标注）**

4.点击ST，开始分割

5.点击ED，结束分割





**更新2022.8.20：**

**1.视频支持拖拽（进度条）**

用上一帧下一帧代替了

**2.视频支持播放，暂停**

已实现

**3.语义分割增加保存mask按钮**

点击保存标注即可保存。

路径在：work_folder\mask_saved

**4.增加选择框：显示mask/不显示mask**

点击即可改变现实情况

**5.视频和mask放在一起播放**

未实现

**6.增加开始视频物体分割按钮**

点击ST，开始分割

**更新2022.12.28：**

**7.增加橡皮擦和画笔功能**

20221228已实现，详细请查看Doc中的铅笔橡皮文档

**8.增加mask颜色，铅笔颜色调色盘选择功能**

20221228已实现，详细请查看Doc中颜色选择器文档

**9.增加基础图像处理功能**

20221228已实现，详细请查看Doc中基础图像处理文档

**10.增加视频标注再修改，和标注视频生成功能**

20221228已实现，详细请查看Doc中视频修正文档
