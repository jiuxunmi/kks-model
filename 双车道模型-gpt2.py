import numpy as np
import os
import random
import matplotlib.pyplot as plt
from PIL import Image

# 设置道路长度 v; 运行时间 T; 生成概率 prob_create; 
# 换道概率 prob_change; 减速概率 prob_slowdown; 
# 车辆状态 color；最大速度 maxspeed;
# 安全距离 Gi = k * vi; 换道参数 delta 和 gc; 反应系数 k;
# 红绿灯参数 tlight
v = 1000
T = 1000
prob_create = [0.2, 0.2]
prob_change = 0.05
prob_slowdown = 0.2
speed = np.ones((2, v + 1)) * -1
color = np.zeros((2, v))
maxspeed = [4, 3]
delta = 1
gc = 3
k = 5
tlight = 60

# 状态更新过程
def update(color, speed, t):
    if np.mod(int(t / tlight), 2) == 0:
        speed[:, v] = -1
    else:
        speed[:, v] = 0
    newspeed = np.array(speed, copy=True)
    newcolor = np.array(color, copy=True)
    i = 0
    while i < v:
        while i < v and speed[0, i] == -1 and speed[1, i] == -1:
            i = i + 1
        if i < v:
            in0 = i + 1
            while in0 < v and speed[0, in0] == -1:
                in0 = in0 + 1
            in1 = i + 1
            while in1 < v and speed[1, in1] == -1:
                in1 = in1 + 1
            ib0 = i
            while ib0 > 0 and speed[0, ib0] == -1:
                ib0 = ib0 - 1
            ib1 = i
            while ib1 > 0 and speed[1, ib1] == -1:
                ib1 = ib1 - 1
            # 0 车道的情况
            if speed[0, i] != -1:
                q = 0
                if speed[1, in1] >= speed[0, in0] + delta or speed[1, in1] >= speed[0, i] + delta or in1 == v:
                    gnn = in1 - i - 1
                    gnb = i - ib1 - 1
                    if gnn >= min(speed[0, i], gc) and gnb >= min(speed[1, ib1], gc):
                        p = random.random()
                        if p <= prob_change:
                            q = 1
                            newspeed[1, i] = speed[0, i]
                            newspeed[0, i] = -1
                            newcolor[0, i] = 0
                            newcolor[1, i] = 1
                # 加速
                if q == 0:
                    gi = in0 - i - 1
                    inn = in0
                elif q == 1:
                    gi = in1 - i - 1
                    inn = in1
                Gi = k * newspeed[q, i]
                if speed[q, v] == -1 and inn == v:
                    gi = Gi + 1
                if gi <= Gi:
                    newspeed[q, i] = speed[0, i] + np.sign(speed[q, inn] - speed[0, i])
                else:
                    newspeed[q, i] = min(speed[0, i] + 1, maxspeed[q])
                # 减速
                newspeed[q, i] = min(newspeed[q, i], gi)
                # 随机慢化
                p = random.random()
                if p <= prob_slowdown and newspeed[q, i] > 0:
                    newspeed[q, i] = newspeed[q, i] - 1
                # 位置更新
                if newspeed[q, i] > 0:
                    ni = int(i + newspeed[q, i])
                    if ni < v:
                        newcolor[q, ni] = 1
                        newspeed[q, ni] = newspeed[q, i]
                    newcolor[q, i] = 0
                    newspeed[q, i] = -1
            # 1 车道情况
            if speed[1, i] != -1:
                q = 1
                if speed[0, in0] >= speed[1, in1] + delta or in0 == v and speed[1, i] >= speed[1, in1]:
                    gnn = in0 - i - 1
                    gnb = i - ib0 - 1
                    if gnn >= min(speed[1, i], gc) and gnb >= min(speed[0, ib1], gc):
                        p = random.random()
                        if p <= prob_change:
                            q = 0
                            newspeed[0, i] = speed[1, i]
                            newspeed[1, i] = -1
                            newcolor[0, i] = 1
                            newcolor[1, i] = 0
                # 加速
                if q == 0:
                    gi = in0 - i - 1
                    inn = in0
                elif q == 1:
                    gi = in1 - i - 1
                    inn = in1
                Gi = k * newspeed[q, i]
                if speed[q, v] == -1 and inn == v:
                    gi = Gi + 1
                if gi <= Gi:
                    newspeed[q, i] = speed[1, i] + np.sign(speed[q, inn] - speed[1, i])
                else:
                    newspeed[q, i] = min(speed[1, i] + 1, maxspeed[q])
                # 减速
                newspeed[q, i] = min(newspeed[q, i], gi)
                # 随机慢化
                p = random.random()
                if p <= prob_slowdown and newspeed[q, i] > 0:
                    newspeed[q, i] = newspeed[q, i] - 1
                # 位置更新
                if newspeed[q, i] > 0:
                    ni = int(i + newspeed[q, i])
                    if ni < v:
                        newcolor[q, ni] = 1
                        newspeed[q, ni] = newspeed[q, i]
                    newcolor[q, i] = 0
                    newspeed[q, i] = -1    
        i = i + 1
    speed = np.array(newspeed, copy=True)
    color = np.array(newcolor, copy=True)
    # 初始车辆进入
    p = random.random()
    for la in range(2):
        if p <= prob_create[la] and speed[la, 0] == -1:
            speed[la, 0] = random.randint(1, maxspeed[la])
            color[la, 0] = 1
    return color, speed

# 将每步的交通图合并为 GIF 动图
def create_gif(img_dir, image_list, gif_name, duration):
    frames = []
    for image_name in sorted(image_list, key=lambda x: int(x.split('.')[0])):  # 按序号排序
        frames.append(Image.open(os.path.join(img_dir, image_name)))
    frames[0].save(gif_name, save_all=True, append_images=frames[1:], duration=duration * 1000, loop=0)
    return

Tsm = []
img_dir = './images'
if not os.path.exists(img_dir):
    os.makedirs(img_dir)

for t in range(T):
    nc = np.zeros((131, v, 3))
    for j in range(3):
        nc[61, :, j] = color[0, :]
        nc[62, :, j] = color[0, :]
        nc[63, :, j] = color[0, :]
        nc[69, :, j] = color[1, :]
        nc[70, :, j] = color[1, :]
        nc[71, :, j] = color[1, :]
    color, speed = update(color, speed, t)

    # 添加序号标注
    plt.figure(figsize=(10, 5), dpi=300)  # 设置更高的分辨率
    plt.imshow(nc)
    plt.text(v // 2, 10, f'step {t + 1}', fontsize=20, color='white', ha='center', va='top', bbox=dict(facecolor='black', alpha=0.5, edgecolor='none'))
    plt.axis('off')
    plt.savefig(os.path.join(img_dir, f"{t}.png"), bbox_inches='tight', pad_inches=0)  # 去掉多余的白边
    plt.close()

    su = []
    for m in range(2):
        for n in range(v):
            if speed[m, n] > 0:
                su.append(speed[m, n])
    if su:  # 只有在 su 非空时才计算均值
        Tsm.append(np.mean(su))

# 生成 GIF
duration = 0.05
gif_name = os.path.join(img_dir, 'traffic_simulation.gif')
create_gif(img_dir, os.listdir(img_dir), gif_name, duration)
