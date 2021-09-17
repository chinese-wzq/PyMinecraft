# coding=utf-8
# 不会吧不会吧还有人不知道UTF-8??????

#感谢您查看我的作品！
#本项目唯一地址（没有码云地址哦）：
#https://github.com/yi-ge-shuai-qi-de-kai-fa-zhe/PyMinecraft
#如果你发现有无良程序员大量盗用本程序代码并且未加声明的
#欢迎你与他对线，并且将他的作品地址发给我（让我康康♂）
#以下为生命以及一些介绍，如果有不符合规范的欢迎提出拉取请求，我不懂开源协议，太多了QAQ

#################################################
#                本作品为兴趣使然                #
#             我并没有收过任何人的钱财            #
#             也没有与任何人有契约关系            #
#     本作品与MOJANG工作室（BUGJUMP）没有任何关系 #
#     我从来没有查看过Minecraft的源码（反正看不懂）#
#      本作品仅供学习、娱乐，商用请注明项目地址    #
#        欢迎提交拉取请求，这是对我最大的支持      #
#    我也只是一个小小的初二生，很多数学计算略为粗糙 #
#            因此希望您帮助改进我的算法           #
################################################
#            本游戏是开源的，所有人可编辑         #
#           因此，我才能尽量保证代码的安全性      #
#          本游戏从设计之初就采用了超多函数设置   #
#          这时的游戏的大部分函数具有参考价值     #
#             如果本游戏的某些函数帮到了您       #
#        欢迎您在项目地址上点一个免费的Star（星） #
#             你的星会成为我Coding的动力        #
###############################################

#################感谢与你相遇！###################

#导入OpenGL相关库
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
#导入字体显示相关库
from PIL import Image,ImageDraw,ImageFont
import numpy as np
#导入三角函数相关库
import math
#导入窗口相关库
import win32con,win32gui

#允许用户自定义的变量
#已将大部分变量做好注释
mouse_move_speed=0.01 #鼠标移动距离
player_move_speed=0.1
look_length=9  #渲染距离,只支持不小于1的奇数
highest_y=100  #世界最高Y坐标
lowest_y=0   #世界最低Y坐标
player_x=0
player_y=0
player_z=-1
font="msyh.ttc"    #显示文字时使用的字体
window_long=400    #窗口的长与宽
window_width=400

#用户不应该动的变量
player_see_x=0
player_see_y=0
lock_muose=False
mouse_fix_No1=5
debug=True
map=[[],[[[],[[[],[1]]]]]]
block_color=[(50,205,50)]
hwnd=0
debug_text=[]

def get_two_float(num:float):
    a,b,c=str(num).partition('.')
    c=c.zfill(2)[:2]
    return float(a+b+c)
def generate_text_image(text:list,color:str,size:int):
    global font,window_width
    w=[]
    for i in range(len(text)):
        mi=""
        for ii in text[i]:
            mi+=str(ii)
        w.append(mi)
    Wzq_NB=ImageFont.truetype(font,size)
    size_x=0
    for i in w:
        qaq=Wzq_NB.getsize(i)
        if qaq[0]>size_x:size_x=qaq[0]
    wzq=Image.new("RGBA",(size_x,window_width*2))
    picture=ImageDraw.Draw(wzq)
    hi=0
    for i in w:
        picture.text((0,hi),i,font=Wzq_NB,fill=color)
        hi+=Wzq_NB.getsize(i)[1]
    return bytes(list(np.ravel(wzq.transpose(Image.FLIP_TOP_BOTTOM)))),(size_x,window_width*2)
def debug_main():
    global debug
    if debug:
        global player_see_x,player_see_y,player_x,player_y,player_z,debug_text
        #以下为没法的代码设计，嘤嘤嘤
        a=debug_text[0]
        a[1]=get_two_float(player_x)
        a[3]=get_two_float(player_y)
        a[5]=get_two_float(player_z)
        debug_text[0]=a
        a=debug_text[1]
        a[1]=get_two_float(player_see_x)
        a[3]=get_two_float(player_see_y)
        debug_text[1]=a
        wzq=generate_text_image(debug_text,"blue",20)
        glDrawPixels(wzq[1][0],wzq[1][1],GL_RGBA,GL_UNSIGNED_BYTE,wzq[0])
def find_block(x:int,y:int,z:int):
    global map
    try:
        return map[x>=0][abs(x)][y>=0][abs(y)][z>=0][abs(z)]
    except:
        return 0
def print_blocks(sx:int,sy:int,sz:int):
    sx=int(sx)
    sy=int(sy)
    sz=int(sz)
    global look_length,highest_y,lowest_y,block_color
    by_13905069=(sx-int((look_length-1)/2),sz+int((look_length-1)/2)+1)
    for x in range(by_13905069[0],by_13905069[1]):
        for y in range(lowest_y,highest_y+1):
            for z in range(by_13905069[0],by_13905069[1]):
                by_wzq=find_block(x,y,z)
                if not by_wzq==0:
                    #这里先粗略写一下
                    #    v4----- v5
                    #   /|      /|
                    #  v0------v1|
                    #  | |     | |
                    #  | v7----|-v6
                    #  |/      |/
                    #  v3------v2
                    #盗图大师
                    color=block_color[by_wzq-1]
                    glBegin(GL_QUAD_STRIP)
                    glColor3ub(color[0],color[1],color[2])
                    glVertex3f(x-0.5,y+0.5,z-0.5)#V0
                    glVertex3f(x+0.5,y+0.5,z-0.5)#V1
                    glVertex3f(x-0.5,y-0.5,z-0.5)#V3
                    glVertex3f(x+0.5,y-0.5,z-0.5)#V2
                    ###########待施工###########
                    # glVertex3f(x+0.5,y-0.5,z+0.5)#V6
                    # glVertex3f(x-0.5,y-0.5,z+0.5)#V7
                    # glVertex3f(x-0.5,y+0.5,z-0.5)#V0
                    # glVertex3f(x+0.5,y+0.5,z-0.5)#V1
                    # glVertex3f(x+0.5,y+0.5,z+0.5)#V5
                    # glVertex3f(x-0.5,y+0.5,z+0.5)#V4
                    # glVertex3f(x-0.5,y-0.5,z-0.5)#V3
                    # glVertex3f(x+0.5,y-0.5,z-0.5)#V3
                    glEnd()
def draw():
    global player_see_x,player_see_y,player_x,player_y,player_z
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(0.3,-0.3,0.3,-0.3,0.1,1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(
        player_x,player_y+1,player_z,
        player_see_x,player_see_y,0,
        0,1,0
    )
    #渲染方块
    print_blocks(player_x,player_y,player_z)
    #调试模式
    debug_main()
    glutSwapBuffers()
def formulas_of_trigonometri_functions_move(look_x:float,look_y:float):
    global player_move_speed
    x=math.cos(look_x)*player_move_speed
    z=math.sin(look_x)*player_move_speed
    y=math.cos(look_y)*player_move_speed
    return x,y,z
def spectator_mode(button):
    global player_see_x,player_see_y,player_x,player_y,player_z
    x,y,z=formulas_of_trigonometri_functions_move(player_see_x,player_see_y)
    if button==b's':
        pass
    elif button==b'w':
        x=-1*x
        y=-1*y
        z=-1*z
    player_x+=x
    player_y+=y
    player_z+=z
    glutPostRedisplay()
def keyboardchange(button,x,y):
    if button==b'\x1b':#是否开启鼠标控制
        global lock_muose,mouse_fix_No1,window_width,window_long
        if lock_muose:
            lock_muose=False
            glutSetCursor(GLUT_CURSOR_LEFT_ARROW)
        else:
            glutWarpPointer(window_long,window_width)
            lock_muose=True
            mouse_fix_No1=1
            glutSetCursor(GLUT_CURSOR_NONE)
            glutPostRedisplay()
    elif button==b'w' or button==b's':
        spectator_mode(button)
    elif button==b'`':#调试模式
        global debug
        if debug:debug=False
        else:debug=True
    else:
        print(button)
def mousemove(x,y):
    global lock_muose,mouse_fix_No1
    if lock_muose and mouse_fix_No1==5:
        global mouse_move_speed,player_see_x,player_see_y,window_width,window_long
        player_see_x=(x-window_long)*mouse_move_speed+player_see_x
        player_see_y=(y-window_width)*mouse_move_speed+player_see_y
        glutWarpPointer(window_long,window_width)
        mouse_fix_No1=1
        glutPostRedisplay()
        return 0
    mouse_fix_No1+=1
def main():
    global hwnd,window_width,window_long,debug_text
    #进行glut的最基础初始化
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutCreateWindow("Minecraft 重置版 ByWzq".encode('GBK',errors="replace"))
    glutSetCursor(GLUT_CURSOR_NONE)
    #使用户无法更改窗口大小
    hwnd=win32gui.GetForegroundWindow()
    A=win32gui.GetWindowLong(hwnd,win32con.GWL_STYLE)
    A ^=win32con.WS_THICKFRAME
    win32gui.SetWindowLong(hwnd,win32con.GWL_STYLE,A)
    #Debug信息的初始化
    debug_text.append(['XYZ:',0.0,',',0.0,',',0.0])
    debug_text.append(['EYE:',0,',',0])
    #完成其余的初始化
    glutReshapeWindow(window_long*2,window_width*2)
    glViewport(0,0,window_long*2,window_width*2)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glutDisplayFunc(draw)
    glutKeyboardFunc(keyboardchange)
    glutPassiveMotionFunc(mousemove)
    glutMainLoop()
main()