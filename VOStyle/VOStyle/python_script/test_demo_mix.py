import random
from enum import Flag
import os
import time
from urllib.parse import unquote
from shutil import copyfile
import scipy.misc as sm
from collections import OrderedDict
import glob
import imageio

# Custom includes
from python_script.dataloaders.combine_dbs import CombineDBs as combine_dbs
import python_script.dataloaders.pascal as pascal
from python_script.dataloaders import custom_transforms as tr
from python_script.dataloaders.helpers import *
import python_script.dataloaders.helpers as helpers
from PIL import Image
# PyTorch includes
import torch.optim as optim
from torchvision import transforms
from torch.utils.data import DataLoader
from torch.nn.functional import upsample
from python_script.networks.mainnetwork import *

import torch
import numpy as np


def GetDistanceMap_click(mask, cp, pad_pixel):
    def find_point(id_x, id_y, ids):
        sel_id = ids[0][random.randint(0, len(ids[0]) - 1)]
        return [id_x[sel_id], id_y[sel_id]]
    # generate bg point
    inds_y, inds_x = np.where(mask > 0.5)
    [h, w] = mask.shape
    left = find_point(inds_x, inds_y, np.where(
        inds_x <= np.min(inds_x)))  # left
    right = find_point(inds_x, inds_y, np.where(
        inds_x >= np.max(inds_x)))  # right
    top = find_point(inds_x, inds_y, np.where(inds_y <= np.min(inds_y)))  # top
    bottom = find_point(inds_x, inds_y, np.where(
        inds_y >= np.max(inds_y)))  # bottom
    x_min = left[0]
    x_max = right[0]
    y_min = top[1]
    y_max = bottom[1]
    left_top = [max(x_min - pad_pixel, 0), max(y_min - pad_pixel, 0)]
    left_bottom = [max(x_min - pad_pixel, 0), min(y_max + pad_pixel, h)]
    right_top = [min(x_max + pad_pixel, w), max(y_min - pad_pixel, 0)]
    righr_bottom = [min(x_max + pad_pixel, w), min(y_max + pad_pixel, h)]

    # generate center point
    cpinds_y, cpinds_x = np.where(cp > 0.5)
    try:
        cpbottom = find_point(cpinds_x, cpinds_y, np.where(
            cpinds_y >= np.max(cpinds_y)))  # bottom
        cpright = find_point(cpinds_x, cpinds_y, np.where(
            cpinds_x >= np.max(cpinds_x)))  # right
        cpx_max = cpright[0]
        cpy_max = cpbottom[1]
        center_point = [cpx_max, cpy_max]
    except:
        cpx_max = int((x_min + x_max) / 2)
        cpy_max = int((y_min + y_max) / 2)
        center_point = [cpx_max, cpy_max]

    a = [center_point, left_top, left_bottom, right_top, righr_bottom]
    return np.array(a)


def get_distancemap(sigma, elem, elem_inside, use_scribble, pad_pixel):
    _target = elem
    targetshape = _target.shape
    _cp = elem_inside
    if np.max(_target) == 0:
        # TODO: handle one_mask_per_point case
        distancemap = np.zeros(
            [targetshape[0], targetshape[1], 2], dtype=_target.dtype)
    else:
        _points = GetDistanceMap_click(_target, _cp, pad_pixel)
        distancemap = make_gt(_target, _points, sigma=sigma,
                              one_mask_per_point=False)
    custom_max = 255.
    tmp = distancemap
    tmp = custom_max * (tmp - tmp.min()) / (tmp.max() - tmp.min() + 1e-10)
    return tmp


def totensor(tmp):
    if tmp.ndim == 2:
        tmp = tmp[:, :, np.newaxis]
    tmp = tmp.transpose((2, 0, 1))
    tmp = tmp[np.newaxis, :, :]
    tmp = torch.from_numpy(tmp)
    return tmp


def getbg(bgx, bgy, bgyw, bgyh, w, h):
    _bg = np.zeros((w, h))
    _bg[bgx:bgx + bgyw, bgy:bgy + bgyh] = 1
    _bg = _bg.astype(np.float32)
    return _bg


def getcp(cx, cy, w, h):
    _cp = np.zeros((w, h))
    _cp[:cy, :cx] = 1
    _cp = _cp.astype(np.float32)
    return _cp


def loadnetwork(model_name='IOG_PASCAL.pth'):
    # Set gpu_id to -1 to run in CPU mode, otherwise set the id of the corresponding gpu
    gpu_id = 0
    device = torch.device("cuda:" + str(gpu_id)
                          if torch.cuda.is_available() else "cpu")
    # Number of input channels (RGB + heatmap of extreme points)
    nInputChannels = 5
    net = Network(nInputChannels=nInputChannels, num_classes=1,
                  backbone='resnet101',
                  output_stride=16,
                  sync_bn=None,
                  freeze_bn=False)
    pretrain_dict = torch.load(model_name)
    net_dict = net.state_dict()
    for k, v in pretrain_dict.items():
        if k in net_dict:
            net_dict[k] = v
        else:
            print('skil parameters:', k)
    net.load_state_dict(net_dict)
    net.to(device)
    net.eval()
    return net


def IOG_getmask(bgpoint, inside, image, net, use_scribble=False):
    with torch.no_grad():
        gpu_id = 0
        device = torch.device("cuda:"+str(gpu_id)
                              if torch.cuda.is_available() else "cpu")
        w, h, channel = image.shape
        bgx = min(bgpoint[0], bgpoint[2])
        bgy = min(bgpoint[1], bgpoint[3])
        bgyw = abs(bgpoint[0] - bgpoint[2])
        bgyh = abs(bgpoint[1] - bgpoint[3])

        bg = getbg(bgy, bgx, bgyh, bgyw, w, h)
        crop_image = crop_from_mask(image, bg, relax=30, zero_pad=True)
        crop_bg = crop_from_mask(bg, bg, relax=30, zero_pad=True)
        crop_image = fixed_resize(crop_image, (512, 512))
        crop_bg = fixed_resize(crop_bg, (512, 512))

        cx = inside[0]
        cy = inside[1]
        cp = getcp(cx, cy, w, h)
        crop_cp = crop_from_mask(cp, bg, relax=30, zero_pad=True)
        crop_cp = fixed_resize(crop_cp, (512, 512))
        distancemap = get_distancemap(
            sigma=10, elem=crop_bg, elem_inside=crop_cp, use_scribble=use_scribble, pad_pixel=10)

        distancemap = totensor(distancemap)
        crop_image = totensor(crop_image)
        distancemap = distancemap.float()
        crop_image = crop_image.float()

        inputs = torch.cat([crop_image, distancemap], 1)
        inputs = inputs.to(device)
        glo1, glo2, glo3, glo4, refine = net.forward(inputs)
        output_refine = upsample(refine, size=(
            512, 512), mode='bilinear', align_corners=True)

        # generate result
        jj = 0
        outputs = output_refine.to(torch.device('cpu'))
        pred = np.transpose(outputs.data.numpy()[jj, :, :, :], (1, 2, 0))
        pred = 1 / (1 + np.exp(-pred))
        pred = np.squeeze(pred)
        gt = bg
        bbox = get_bbox(gt, pad=30, zero_pad=True)
        result = crop2fullmask(
            pred, bbox, gt, zero_pad=True, relax=0, mask_relax=False)
        # 0~1
        resultmax, resultmin = result.max(), result.min()
        result = (result-resultmin)/(resultmax-resultmin)
        result = (result > 0.3)*255
    return result

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
    # result = add_mask(image, mask, mode)
    # # time.sleep(5)
    # return result


def combine_mask(current, mask):
    # 合并mask，把当前mask和新来的mask合并
    if current is None:
        return mask

    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            flag = False
            for k in range(mask.shape[2]):
                if mask[i][j][k] != 0:
                    flag = True
                    break
            if flag == False:
                continue
            for k in range(mask.shape[2]):
                current[i][j][k] = mask[i][j][k]
    return current


def show_image_process(image, current, mode):
    # 展示图像，把image和mask融合
    if mode == 1 or mode == 3:
        alpha = 0.4

        covery = current
        sum_covery = covery.sum(axis=2)
        # print(sum_covery.shape)
        for c in range(3):
            image[:, :, c] = np.where(
                sum_covery != 0, image[:, :, c] * (1 - alpha) + alpha*covery[:, :, c], image[:, :, c])

    elif mode == 2:
        sum_covery = covery.sum(axis=2)
        for c in range(3):
            image[:, :, c] = np.where(sum_covery == 0, 0, image[:, :, c])
    # mode == 4 直接返回image本身
    return image
