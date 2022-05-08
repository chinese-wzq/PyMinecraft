#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Always believe,always hope.

#感谢您的遇见！
#本项目（PyMinecraft）GitHub地址：
#https://github.com/chinese-wzq/PyMinecraft
#本项目（PyMinecraft）Gitee地址：
#https://gitee.com/chinese-wzq/PyMinecraft
#如果你发现有无良程序员大量盗用本程序代码并且未加声明的
#欢迎你与他对线，并且将他的作品地址发给我（让我康康啊♂）
#以下为程序声明以及一些介绍，如果有不符合规范的欢迎提出拉取请求，我不懂开源协议，太多了QAQ

#本程序部分行较长。为什么？因为觉得这样很爽（莫名）
#本程序经常出现直接对函数参数赋值的情况。为什么？因为这样写的行更少，而且不用再想新的变量名啦~

#二次开发提示：
#函数基本没有对参数进行检查，也就是说，如果你的参数用错了，那么程序是会直接崩溃的（甚至可能找不到原因）
#所以，在使用函数前，请务必查看程序中对函数的使用方法，并将函数的实现看一遍
#请将程序中频繁调用但主要为数学计算的函数（如世界的方块读取，寻路AI，碰撞箱检测）加入numba支持（对性能有很大影响）

#对了，一些变量和函数参数因为英语能力有限不得不用机翻（其实要是我懒可以直接写中文变量名，不过懒得切输入法）

################################################
#                本作品为兴趣使然               #
#             我并没有收过任何人的钱财           #
#             也没有与任何人有契约关系           #
#     本作品与MOJANG工作室（BUGJUMP）没有任何关系 #
#    我从来没有查看过Minecraft的源码（反正看不懂) #
#      本作品仅供学习、娱乐，商用请注明项目地址   #
#        欢迎提交拉取请求，这是对我最大的支持     #
#    我也只是一个小小的初二生，很多数学计算略为粗糙#
#            因此希望您帮助改进我的算法          #
################################################

#################感谢与你相遇！###################

import sys
#导入OpenGL相关库
import time

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
#导入GLFW OpenGL窗口跨平台API（同时提供鼠标键盘等的API，也许还可以允许跨模块同一上下文？暂未测试）
from glfw.GLFW import *
#导入三角函数相关库
import math
#导入numba性能提升相关库（直接将python代码编译为机器码）
from numba import njit
from numba.types import UniTuple,float64#这里PyCharm报错，不过实测可以导入，别动代码屎山！
#导入python程序员必备numpy
import numpy as np

#导入实用模块
from main.useful_modules import SmartPlanManager,FileBufferManager,TotalVarManager,GetCharacterImage,float2int
#初始化实用模块
file_buffer_manager=FileBufferManager()
smart_plan_manager=SmartPlanManager()
character_getter=GetCharacterImage()
total_var_manager=TotalVarManager({
    "draw":True,
    "file_buffer_manager":file_buffer_manager
})
#导入方块相关模块
import main.block.get_texture as get_texture
block_texture=[get_texture.create_block_texture(1)]
#导入方块管理器
import main.block.block_manager as block_manager
block_manager.init(total_var_manager)
#导入世界管理器

#可供自定义的变量有些还放到了main文件夹下面的模块里面，因为这样子就没有必要再考虑如何将本文件里面定义的变量应用到模块里面了，望周知。

#允许用户自定义的变量,已将大部分变量做好注释
mouse_move_speed=1 #鼠标移动距离
player_move_speed=0.1
look_length=15  #渲染距离,只支持不小于1的奇数
highest_y=100  #世界最高Y坐标
lowest_y=0   #世界最低Y坐标，目前如果更改将会报错！
player_x=0    #这几个不必细说，都懂都懂
player_y=-1
player_z=-1
window_height=400    #窗口的长和宽
window_width=400
set_chat_list_show_time=100      #聊天框显示多久，2/3时间不变，1/3时间淡化消失

#用户不应该动的变量（当然放这里就代表有能耐你也能动）
player_see_x=0
player_see_y=0
player_see_x_temp=0
player_see_y_temp=0
lock_muose=False
debug=False

debug_text=[['XYZ:',0.0,',',0.0,',',0.0],
            ['EYE:',0,',',0],]
keyboard={}
for i in [b'\x1b',b'`',b'w',b's',b'a',b'd',b" ",b"x"]:keyboard[i]=False
mouse={0:1,2:1}
input_text=False
input_buffer=""
chat_list=[]
chat_list_show_time=0
guide_buttons=[]
block_VAO=0
block_VBO_buffer_len=0
texture_VBO=0

def print_blocks(sx:int,sy:int,sz:int):#这里将来会选择性显示方块，不会全部显示一遍，多伤显卡QAQ
    #特别鸣谢：Stack Overflow用户Rabbid76
    #没有他回答了我两个问题，我这一辈子都做不出来
    #问题链接：
    #https://stackoverflow.com/questions/70476151/opengl-vbo-can-run-without-error-but-no-graphics
    #https://stackoverflow.com/questions/70610206/opengl-vbo-vao-ebo-can-run-without-error-but-no-graphics
    #https://stackoverflow.com/questions/70844191/pyopengl-run-with-no-texture
    #虽然他没有叫我贴上这个注释，不过我想，做人要学会感恩😀
    global block_VAO,block_VBO_buffer_len,texture_VBO
    if total_var_manager.get_var("draw"):
        total_var_manager.set_var("draw",False)
        block_point_buffer=[]
        block_color_buffer=[]
        texture_coord=[]
        for y in range(lowest_y,highest_y+1):
            for x in range(sx-int((look_length-1)/2),sx+int((look_length-1)/2)+1):
                for z in range(sz-int((look_length-1)/2),sz+int((look_length-1)/2)+1):
                    by_wzq=block_manager.read_block(x,y,z,block_manager.block_temp)
                    if not by_wzq==0:
                        #图盗的
                        #    v4----- v5
                        #   /|      /|
                        #  v0------v1|
                        #  | |     | |
                        #  | v7----|-v6
                        #  |/      |/
                        #  v3------v2
                        block_point_buffer+=[x-0.5,y+0.5,z-0.5,  #V0
                                             x+0.5,y+0.5,z-0.5,  #V1
                                             x+0.5,y+0.5,z+0.5,  #V5
                                             x-0.5,y+0.5,z+0.5,  #V4

                                             x-0.5,y-0.5,z-0.5,  #V3
                                             x+0.5,y-0.5,z-0.5,  #V2
                                             x+0.5,y-0.5,z+0.5,  #V6
                                             x-0.5,y-0.5,z+0.5,  #V7

                                             x+0.5,y-0.5,z-0.5,  #V2
                                             x+0.5,y-0.5,z+0.5,  #V6
                                             x+0.5,y+0.5,z+0.5,  #V5
                                             x+0.5,y+0.5,z-0.5,  #V1

                                             x-0.5,y-0.5,z-0.5,  #V3
                                             x-0.5,y-0.5,z+0.5,  #V7
                                             x-0.5,y+0.5,z+0.5,  #V4
                                             x-0.5,y+0.5,z-0.5,  #V0

                                             x-0.5,y-0.5,z-0.5,  #V3
                                             x+0.5,y-0.5,z-0.5,  #V2
                                             x+0.5,y+0.5,z-0.5,  #V1
                                             x-0.5,y+0.5,z-0.5,  #V0

                                             x-0.5,y-0.5,z+0.5,  #V7
                                             x+0.5,y-0.5,z+0.5,  #V6
                                             x+0.5,y+0.5,z+0.5,  #V5
                                             x-0.5,y+0.5,z+0.5,] #V4
                        block_color_buffer+=(0.0,0.0,0.0)*6
                        texture_coord+=[1.0,1.0,
                                        0.0,1.0,
                                        0.0,0.0,
                                        1.0,0.0]*6
        #创建顶点VBO
        block_VBO=glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,block_VBO)
        a=np.array(block_point_buffer,dtype='float32')
        glBufferData(GL_ARRAY_BUFFER,sys.getsizeof(a),a,GL_STATIC_DRAW)
        block_VBO_buffer_len=int(len(a)/3)
        #创建纹理VBO
        texture_VBO=glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D,texture_VBO)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,100,100,0,GL_RGB,GL_UNSIGNED_BYTE,block_texture[0])
        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D,0)
        #创建纹理指针
        texture_EBO=glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,texture_EBO)
        a=np.array(texture_coord,dtype='float32')
        glBufferData(GL_ARRAY_BUFFER,sys.getsizeof(a),a,GL_STATIC_DRAW)
        #绑定VAO
        block_VAO=glGenVertexArrays(1)
        glBindVertexArray(block_VAO)
        #绑定顶点VBO
        glBindBuffer(GL_ARRAY_BUFFER,block_VBO)
        glVertexPointer(3,GL_FLOAT,0,None)
        glEnableClientState(GL_VERTEX_ARRAY)
        #绑定纹理VBO
        glBindBuffer(GL_ARRAY_BUFFER,texture_EBO)
        glTexCoordPointer(2,GL_FLOAT,0,None)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        #解绑
        glBindVertexArray(0)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D,texture_VBO)
    glBindVertexArray(block_VAO)
    glColor3ub(255,255,255)
    glDrawArrays(GL_QUADS,0,block_VBO_buffer_len)
    glBindVertexArray(0)
class PrintText:
    def __init__(self):self.texture_buffer={}
    def default_2d(size,x,y,z,dx,dy,direction="up",parameter:tuple=(1,1,0,1,1)):
        #parameter参数说明:
        #第一个参数:是否往x坐标扩展[0不扩展,1正方向扩展]
        #第二个参数:是否往y坐标扩展[0不扩展,1正方向扩展]
        #第三个参数:是否往z坐标扩展[0不扩展,1正方向扩展]
        #第四个参数:位于基线下或上[1朝上，-1朝下]
        #第五个参数:位于基线左或右[1朝右，-1朝左]
        #本函数只有3种可能的情况：
        #
        #         Y
        #        /|-----⌉
        #       v0|   ↑ |    1,1,0
        #       | |     |
        # 0,1,1↙| v7------v6 X
        #       |/   →   /
        #        v3------v2
        #       Z   1,0,1
        #以V7为中心点
        #(0,1)-→---------(1,1)
        #  |               |
        #  |   TexCoord    ↓
        #  ↑  by 13905069  |
        #  |               |
        #(0,0)---------←-(1,0)
        #计算起始点，以及朝向
        if direction=="up":texcoord=(1,0,1,1,0,1,0,0)
        elif direction=="down":texcoord=(1,1,1,0,0,0,0,1)
        else:raise ValueError("未知的direction参数内容！")
        if parameter[:3]==(1,1,0):
            glVertex3f(x+dx*parameter[4],y+(dy+size[0])*parameter[3],z)
            glTexCoord2f(texcoord[0],texcoord[1])
            glVertex3f(x+(dx+size[1])*parameter[4],y+(dy+size[0])*parameter[3],z)
            glTexCoord2f(texcoord[2],texcoord[3])
            glVertex3f(x+(dx+size[1])*parameter[4],y+dy*parameter[3],z)
            glTexCoord2f(texcoord[4],texcoord[5])
            glVertex3f(x+dx*parameter[4],y+dy*parameter[3],z)
            glTexCoord2f(texcoord[6],texcoord[7])
        if parameter[:3]==(0,1,1):
            glVertex3f(x,y+dx*parameter[4],z+(dy+size[0])*parameter[3])
            glTexCoord2f(texcoord[0],texcoord[1])
            glVertex3f(x,y+(dx+size[1])*parameter[4],z+(dy+size[0])*parameter[3])
            glTexCoord2f(texcoord[2],texcoord[3])
            glVertex3f(x,y+(dx+size[1])*parameter[4],z+dy*parameter[3])
            glTexCoord2f(texcoord[4],texcoord[5])
            glVertex3f(x,y+dx*parameter[4],z+dy*parameter[3])
            glTexCoord2f(texcoord[6],texcoord[7])
        if parameter[:3]==(1,0,1):
            glVertex3f(x+(dy+size[0])*parameter[3],y,z+dx*parameter[4])
            glTexCoord2f(texcoord[0],texcoord[1])
            glVertex3f(x+(dy+size[0])*parameter[3],y,z+(dx+size[1])*parameter[4])
            glTexCoord2f(texcoord[2],texcoord[3])
            glVertex3f(x+dy*parameter[3],y,z+(dx+size[1])*parameter[4])
            glTexCoord2f(texcoord[4],texcoord[5])
            glVertex3f(x+dy*parameter[3],y,z+dx*parameter[4])
            glTexCoord2f(texcoord[6],texcoord[7])
    def print_text_list(self,text:list,x=0,y=0,z=0,m=1,color=(0,0,0),size=24,spacing=2,all_row=20,buffer=True,direction="up",parameter:tuple=(1,1,0,1,1),row_small=None):#采用freetype+texture，更方便自定义，字体更好看！
        #vertex_function函数为了实现各个方向的文字显示
        #这个函数各种方向显示的实现真的想了很久
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glDisable(GL_DEPTH_TEST)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        dy=0
        for i in text:
            qaq=0
            dx=x
            if i=="": i=" "
            for ii in "".join([str(x) for x in i]):#需要进行特殊处理
                if ii==" ":
                    a=(all_row,float2int(9/24*size))#这里根据一个比较接近空格的数据进行了计算
                    if row_small is not None: a=(row_small,a[1]*(a[0]/row_small))
                    if a[0]>qaq: qaq=a[0]
                    dx+=a[1]+spacing
                    continue
                if buffer and ii+str(size)+str(color)+str(all_row) in self.texture_buffer:
                    a=self.texture_buffer[ii+str(size)+str(color)+str(all_row)+"_size"]
                    glBindTexture(GL_TEXTURE_2D,self.texture_buffer[ii+str(size)+str(color)+str(all_row)])
                else:
                    texture=glGenTextures(1)
                    glBindTexture(GL_TEXTURE_2D,texture)
                    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
                    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
                    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
                    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
                    aa=character_getter.character2types(ii,size=size,color=color,all_row=all_row)
                    a=character_getter.get_size()
                    glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,a[1],a[0],0,GL_RGBA,GL_UNSIGNED_BYTE,aa)
                    glGenerateMipmap(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D,0)
                    if buffer:
                        self.texture_buffer[ii+str(size)+str(color)+str(all_row)]=texture
                        self.texture_buffer[ii+str(size)+str(color)+str(all_row)+"_size"]=a
                    glBindTexture(GL_TEXTURE_2D,texture)
                if row_small is not None: a=(row_small,a[1]*(row_small/a[0]))
                if a[0]>qaq: qaq=a[0]
                glBegin(GL_QUADS)
                PrintText.default_2d(a,x,y,z,dx,dy,direction,parameter)#为什么用函数引出来？因为工程量实在太大，够单独开一个函数讲解了
                glEnd()
                dx+=a[1]+spacing
            dy+=qaq*m
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
text_printer=PrintText()
def debug_3d():
    if debug:
        #显示一个世界原点的坐标系
        glLineWidth(1)
        glBegin(GL_LINES)
        glColor3ub(0,0,255)
        glVertex3f(0,0,0)
        glVertex3f(1,0,0)
        glColor3ub(0,255,0)
        glVertex3f(0,0,0)
        glVertex3f(0,1,0)
        glColor3ub(255,0,0)
        glVertex3f(0,0,0)
        glVertex3f(0,0,1)
        glEnd()
        #显示坐标系文字（方便与MC原版进行矫正）
        text_printer.print_text_list(["x"],1,0,0,row_small=1)
        text_printer.print_text_list(["y"],0,1,0,row_small=1)
        text_printer.print_text_list(["z"],0,0,1,row_small=1)
def debug_2d():
    global debug_text
    if debug:
        #更新调试信息
        a=debug_text[0]
        a[1]=round(player_x,2)
        a[3]=round(player_y,2)
        a[5]=round(player_z,2)
        debug_text[0]=a
        a=debug_text[1]
        a[1]=round(player_see_x,2)
        a[3]=round(player_see_y,2)
        debug_text[1]=a
        #调用文字显示函数显示debug内容，并顺便打印文字出来
        text_printer.print_text_list(debug_text,y=780,m=-1)
@njit(UniTuple(float64,3)(float64,float64))
def view_orientations(px,py):
    #我觉得math模块的pi好像精度不高，于是这坨数字就出现了
    pi=3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196442881097566593344612847564823378678316527120190914564856692346034861045432664821339360726024914127372458700660631558817488152092096282925409171536436789259036001133053054882046652138414695194151160943305727036575959195309218611738193261179310511854807446237996274956735188575272489122793818301194912
    return math.cos(px*pi/180-90),math.sin(py*pi/180),math.sin(px*pi/180-90)*-1
#尊敬的代码阅读者，当你看到这里的时候可能会有点疑惑这是什么,为什么一行代码就搞定了？
#好吧，老实说，因为偶然的巧合（说是三角函数负数可以输出正数，然而现在我发现不能），我删掉了一些代码
#然后又因为降智的想法，又删了一些（像现在这样），结果没想到程序跑得很好（对，就很离谱）
#所以说if全都没了，只剩下这堆实际有用的代码。
#里面有个我打死都理解不了的px*math.pi/180-90，单位都不一样直接就减了，但是就是可以正常运行，你说奇不奇怪？？？
#不过程序界有个原则就是能跑就不改，我一改就不行。我放弃了。今天算是受到了程序的教育了，以前一直觉得要完全理解，现在发现我太幼稚了。
def world_main_loop():
    global input_text,chat_list_show_time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(-0.3,0.3,-0.3,0.3,0.1,8)
    #笔记：
    #glFrustum(left,right,bottom,top,zNear,zFar)
    #这个函数的参数只定义近裁剪平面的左下角点和右上角点的三维空间坐标，即(left，bottom，-near)和(right，top，-near)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    #计算视角望向的位置
    x,y,z=view_orientations(player_see_x,player_see_y)
    gluLookAt(
        player_x,player_y+1,player_z,
        player_x+x,player_y+y+1,player_z+z,
        0,1,0
    )
    block_manager.load_block(float2int(player_x),float2int(player_z))
    #渲染方块
    print_blocks(float2int(player_x),float2int(player_y),float2int(player_z))
    #显示选中的方块
    #    v4----- v5
    #   /|      /|
    #  v0------v1|
    #  | |     | |
    #  | v7----|-v6
    #  |/      |/
    #  v3------v2
    i=mouse_hit_test(block_manager.block_temp,player_see_x,player_see_y,player_x,player_y,player_z)
    if i is not None:
        x,y,z=i[0]
        a=[x-0.5,y+0.5,z-0.5,  #V0
           x+0.5,y+0.5,z-0.5,  #V1
           x+0.5,y-0.5,z-0.5,  #V2
           x-0.5,y-0.5,z-0.5,  #V3
           x-0.5,y+0.5,z+0.5,  #V4
           x+0.5,y+0.5,z+0.5,  #V5
           x+0.5,y-0.5,z+0.5,  #V6
           x-0.5,y-0.5,z+0.5,] #V7
        b=[0,3,1,2,5,6,4,7,0,1,4,5,7,6,3,2,0,4,1,5,2,6,3,7]
        glLineWidth(5)
        glBegin(GL_LINES)
        glColor3ub(232,232,232)
        for i in range(int(len(b)/2)):
            glVertex3f(a[b[i*2]*3],a[b[i*2]*3+1],a[b[i*2]*3+2])
            glVertex3f(a[b[i*2+1]*3],a[b[i*2+1]*3+1],a[b[i*2+1]*3+2])
        glEnd()
    debug_3d()
    #进入2D状态
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,window_height*2,0,window_width*2)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    #显示指针
    glLineWidth(2)
    glBegin(GL_LINES)
    glColor3ub(232,232,232)
    glVertex2f(400,425)
    glVertex2f(400,375)
    glVertex2f(425,400)
    glVertex2f(375,400)
    glEnd()
    #调试模式
    debug_2d()
    #显示指令栏
    if chat_list_show_time!=0 and not input_text:
        chat_list_show_time-=1
        if set_chat_list_show_time/3*1<chat_list_show_time:text_printer.print_text_list([input_buffer]+chat_list)
        else:
            glColor4ub(255,255,255,float2int(765/set_chat_list_show_time*chat_list_show_time))
            text_printer.print_text_list([input_buffer]+chat_list)
    if input_text:text_printer.print_text_list([input_buffer]+chat_list)
    block_manager.unload_block(float2int(player_x),float2int(player_z))
    #保持窗口
    window_reshape()
    #交换缓存，显示画面
    glutSwapBuffers()
def spectator_mode(button):
    global player_x,player_y,player_z
    if button in [b'w',b's']:
        x,y,z=view_orientations(player_see_x,player_see_y)
        if button==b's':x,y,z=x*-1,y*-1,z*-1
    else:
        x,y,z=view_orientations(player_see_x+90,player_see_y)
        if button==b'd':x,z=x*-1,z*-1
        y=0
    player_x,player_y,player_z=player_x+x*player_move_speed,player_y+y*player_move_speed,player_z+z*player_move_speed
    glutPostRedisplay()
def run_command(command):#名义上叫做运行指令，实际上负责了聊天框输入事件处理的全部
    global chat_list,chat_list_show_time
    chat_list=[input_buffer]+chat_list
    if command[0]=="/":
        #对输入进行拆分
        command_split=command[1:].split(' ')
        if command_split[0]=="fill":block_manager.write_block(int(command_split[1]),int(command_split[2]),int(command_split[3]),int(command_split[4]))
        elif command_split[0]=="tp":
            global player_x,player_y,player_z
            player_x=float(command_split[1])
            player_y=float(command_split[2])
            player_z=float(command_split[3])
        elif command_split[0]=="saves":
            for i,ii in block_manager.blocks.items():file_buffer_manager.write(os.path.join(block_manager.main_folder_dir, "saves", block_manager.save_name, "(" + str(i[0]) + "," + str(i[1]) + ")"), str(ii))
        elif command_split[0]=="set_var":
            eval("total_var_manager.set_var(\""+command_split[1]+"\","+command_split[2]+")")
        else:chat_list=["未知的指令！"]+chat_list
    chat_list_show_time=set_chat_list_show_time
def lock_or_unlock_mouse(a):
    global lock_muose
    if a:
        lock_muose=False
        glutSetCursor(GLUT_CURSOR_LEFT_ARROW)
    else:
        glutWarpPointer(window_height,window_width)
        lock_muose=True
        glutSetCursor(GLUT_CURSOR_NONE)
        glutPostRedisplay()
@njit
def mouse_hit_test(block_temp,player_see_x,player_see_y,player_x,player_y,player_z):
    #感谢开源项目https://github.com/fogleman/Minecraft提供的函数思路！（没错，同样是在做Minecraft）
    m=8#精度
    x,y,z=player_x,player_y+1,player_z
    x_vector,y_vector,z_vector=view_orientations(player_see_x,player_see_y)
    x_vector,y_vector,z_vector=x_vector/m,y_vector/m,z_vector/m
    free_block=0
    for _ in range(70*m):
        free_block=round(x),round(y),round(z)
        x,y,z=x+x_vector,y+y_vector,z+z_vector
        if y<lowest_y-0.5:return None
        if block_manager.read_block(round(x),round(y),round(z),block_temp)!=0:
            return (round(x),round(y),round(z)),free_block
    return None
def world_mouseclick(button,state,x,y):
    global mouse,draw
    if not mouse[2]:
        i=mouse_hit_test(block_manager.block_temp,player_see_x,player_see_y,player_x,player_y,player_z)
        if i is not None:
            block_manager.write_block(i[1][0],i[1][1],i[1][2],1)
            draw=False
    if not mouse[0]:
        i=mouse_hit_test(block_manager.block_temp,player_see_x,player_see_y,player_x,player_y,player_z)
        if i is not None:
            block_manager.write_block(i[0][0],i[0][1],i[0][2],0)
            draw=False
    mouse[button]=state
def keyboarddown(button,x,y):
    global keyboard,input_text,input_buffer,debug,lock_muose,player_y
    if input_text:
        if button==b'\r':
            input_text=False
            run_command(input_buffer)
            input_buffer=""
            lock_or_unlock_mouse(False)
        elif button==b'\x1b':
            input_text=False
            input_buffer=""
            lock_or_unlock_mouse(False)
        elif button==b'\x08':input_buffer=input_buffer[:-1]
        else:input_buffer+=button.decode()
        glutPostRedisplay()
    else:
        if not keyboard[b'\x1b'] and button==b'\x1b':lock_or_unlock_mouse(lock_muose)#锁定或非锁定状态
        elif not keyboard[b'`'] and button==b'`':#调试模式
            if debug:debug=False
            else:debug=True
            glutPostRedisplay()
        elif button==b'/':
            input_text=True
            lock_or_unlock_mouse(True)
            input_buffer="/"
            glutPostRedisplay()
            return 0
        elif button==b't':
            input_text=True
            lock_or_unlock_mouse(True)
            glutSetCursor(GLUT_CURSOR_LEFT_ARROW)
            glutPostRedisplay()
            return 0
        keyboard[button]=True
def keyboardup(button,x,y):
    global keyboard
    keyboard[button]=False
def world_mousemove(x,y):
    global player_see_x_temp,player_see_y_temp
    if lock_muose and window_height!=x and window_width!=y:
        player_see_x_temp=(window_height-x)*mouse_move_speed
        player_see_y_temp=(window_width-y)*mouse_move_speed
        glutWarpPointer(window_height,window_width)
        glutPostRedisplay()
def backgroud():
    global keyboard,player_y,player_see_y,player_see_y_temp,player_see_x,player_see_x_temp
    #键盘
    for i in [b'w',b's',b'a',b'd']:
        if keyboard[i]:spectator_mode(i)
    if keyboard[b' ']:player_y+=0.1
    if keyboard[b'x']: player_y-=0.1
    wzqnb=5
    if player_see_y_temp!=0:
        player_see_y_temp,player_see_y=player_see_y_temp-wzqnb*(-1+(player_see_y_temp>0)*2),player_see_y+wzqnb*(-1+(player_see_y_temp>0)*2)
        if math.fabs(player_see_y_temp)<wzqnb:player_see_y_temp,player_see_y=0,player_see_y_temp+player_see_y
        if player_see_y>90:player_see_y=90
        if player_see_y<-90:player_see_y=-90
    if player_see_x_temp!=0:
        player_see_x_temp,player_see_x=player_see_x_temp-wzqnb*(-1+(player_see_x_temp>0)*2),player_see_x+wzqnb*(-1+(player_see_x_temp>0)*2)
        if math.fabs(player_see_x_temp)<wzqnb:player_see_x_temp,player_see_x=0,player_see_x_temp+player_see_x
        if player_see_x>180:player_see_x=-180
        if player_see_x<-180: player_see_x=180
    #聊天框淡化事件，必须要激活
    smart_plan_manager.clock()
    glutPostRedisplay()
def guide_main_loop():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,window_height*2,0,window_width*2)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    text_printer.print_text_list(text=["P"],x=0,y=400,size=96,row_small=10)
    glutSwapBuffers()
def guide_init():#处理情况：游戏退出到主界面，其他界面退出到主界面
    glutSetCursor(GLUT_CURSOR_LEFT_ARROW)
    glutIdleFunc(nothing)
    glutPassiveMotionFunc(nothing)
    glutMouseFunc(nothing)
    glMatrixMode(GL_MODELVIEW)
    glLoadMatrixd(init_info[0])
    glMatrixMode(GL_PROJECTION)
    glLoadMatrixd(init_info[1])
    glutDisplayFunc(guide_main_loop)
def go_to_world():
    glViewport(0,0,window_height*2,window_width*2)
    glutSetCursor(GLUT_CURSOR_NONE)
    glutDisplayFunc(world_main_loop)
    glutIdleFunc(backgroud)
    glutPassiveMotionFunc(world_mousemove)
    glutMouseFunc(world_mouseclick)
def nothing(*args):pass
def window_reshape():glutReshapeWindow(window_height*2,window_width*2)
def init():
    #进行glut的最基础初始化
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_DEPTH|GLUT_RGBA)
    glutCreateWindow("PyMinecraft ByWzq".encode('GBK',errors="replace"))
    #完成其余的初始化
    glutReshapeWindow(window_height*2,window_width*2)
    glClearColor(0.0,174.0,238.0,238.0)
    smart_plan_manager.add(1000,file_buffer_manager.save, 1)
    #smart_plan_manager.add(100,window_reshape,1)
#可直接覆盖函数实现自己的功能
for i in os.listdir(os.path.join(block_manager.main_folder_dir,"mods")):
    if i.split(".")[-2:]==["enable","py"]:
        with open(os.path.join(block_manager.main_folder_dir,"mods",i)) as f: exec(f.read())
init()
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LESS)
glutKeyboardFunc(keyboarddown)
glutKeyboardUpFunc(keyboardup)
init_info=(glGetDoublev(GL_MODELVIEW_MATRIX),glGetDoublev(GL_PROJECTION_MATRIX))
#这里二选一注释，注释第一个进入世界（成熟），注释第二个进入界面（没做，只有背景和测试文字）
#guide_init()
go_to_world()
glutMainLoop()#正式开始运行
#　    ☆ *　. 　☆
#　　  . ∧＿∧ ∩　* ☆
#* ☆ ( ・∀・)/ .
#　. ⊂　　  ノ* ☆
#☆ * (つ ノ .☆
#　　  (ノ
#总代码破800行啦！
#我推送了100次代码！
