# coding=utf-8
# 不会吧不会吧还有人不知道UTF-8??????

#感谢您查看我的作品！
#本项目唯一地址（没有码云地址哦）：
#https://github.com/yi-ge-shuai-qi-de-kai-fa-zhe/PyMinecraft
#如果你发现有无良程序员大量盗用本程序代码并且未加声明的
#欢迎你与他对线，并且将他的作品地址发给我（让我康康♂）
#以下为生命以及一些介绍，如果有不符合规范的欢迎提出拉取请求，我不懂开源协议，太多了QAQ

#################################################
#                本作品为兴趣使然                  #
#             我并没有收过任何人的钱财              #
#             也没有与任何人有契约关系              #
#     本作品与MOJANG工作室（BUGJUMP）没有任何关系    #
#     我从来没有查看过Minecraft的源码（反正看不懂）   #
#      本作品仅供学习、娱乐，商用请注明项目地址       #
#        欢迎提交拉取请求，这是对我最大的支持         #
#    我也只是一个小小的初二生，很多数学计算略为粗糙     #
#            因此希望您帮助改进我的算法             #
################################################
#            本游戏是开源的，所有人可编辑           #
#           因此，我才能尽量保证代码的安全性         #
#          本游戏从设计之初就采用了超多函数设置       #
#          这时的游戏的大部分函数具有参考价值        #
#             如果本游戏的某些函数帮到了您          #
#        欢迎您在项目地址上点一个免费的Star（星）    #
#             你的星会成为我Coding的动力          #
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
#允许用户自定义的变量
mouse_move_speed=0.01 #鼠标移动距离
player_move_speed=0.5
look_length=9  #渲染距离,只支持不小于1的奇数
highest_y=100  #世界最高Y坐标
lowest_y=0   #世界最低Y坐标
player_x=0
player_y=0
player_z=-1
font="msyh.ttc"    #显示文字时使用的字体

#用户不应该动的变量
player_see_x=0#为了以后的更新做好准备
player_see_y=0
lock_muose=False
mouse_should_move_pos=(0,0)
mouse_fix_No1=5
debug=True
map=[[],[[[],[[[],[1]]]]]]
block_color=[(50,205,50)]
def Formulas_of_trigonometri_functions_move(look_x:float,look_y:float):
    global player_move_speed
    return 0
def get_two_float(num:float):
    a,b,c=str(num).partition('.')
    c=c.zfill(2)[:2]
    return float(a+b+c)
def generate_text_image(text:str,color:str,size:int):
    global font
    Wzq_NB=ImageFont.truetype(font,size)
    size=Wzq_NB.getsize(text)
    wzq=Image.new("RGBA",size)
    picture=ImageDraw.Draw(wzq)
    picture.text((0,0),text,font=Wzq_NB,fill=color)
    return bytes(list(np.concatenate(np.split(np.ravel(wzq.transpose(Image.FLIP_TOP_BOTTOM)),[size[0]*4])))),Wzq_NB.getsize(text)
def debug_main():
    global debug
    if debug:
        global player_see_x,player_see_y
        mua=generate_text_image("E:"+str(get_two_float(player_see_x))+";"+str(get_two_float(player_see_y)),"blue",50)
        glDrawPixels(mua[1][0],mua[1][1],GL_RGBA,GL_UNSIGNED_BYTE,mua[0])
def find_block(x:int,y:int,z:int):
    global map
    try:
        return map[x>=0][abs(x)][y>=0][abs(y)][z>=0][abs(z)]
    except:
        return 0
def print_blocks(sx:int,sy:int,sz:int):
    global look_length,highest_y,lowest_y,block_color
    by_13905069=(sx-int((look_length-1)/2),sx+int((look_length-1)/2)+1)
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
                    glVertex3f(x+0.5,y-0.5,z+0.5)#V6
                    glVertex3f(x-0.5,y-0.5,z+0.5)#V7
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
    #渲染结束
    #调试模式
    debug_main()
    glutSwapBuffers()
def keyboardchange(button,x,y):#实现暂停、视角的前进与后退等功能
    if button==b'\x1b':#是否开启鼠标控制
        global lock_muose,mouse_fix_No1,mouse_should_move_pos
        if lock_muose:
            lock_muose=False
            glutSetCursor(GLUT_CURSOR_LEFT_ARROW)
        else:
            glutWarpPointer(mouse_should_move_pos[0],mouse_should_move_pos[1])
            lock_muose=True
            mouse_fix_No1=1
            glutSetCursor(GLUT_CURSOR_NONE)
            glutPostRedisplay()
    elif button==b'`':#调试模式
        global debug
        if debug:debug=False
        else:debug=True
    else:
        print(button)
def change(x,y):
    global mouse_should_move_pos
    mouse_should_move_pos=(400,400)
    glutPostRedisplay()#没了它，拉动窗口图形就会变形
def mousemove(x,y):
    global lock_muose,mouse_fix_No1
    if lock_muose and mouse_fix_No1==5:
        global mouse_move_speed,mouse_should_move_pos,player_see_x,player_see_y
        #这里重写了一下，为了以后的更新做准备
        player_see_x=(x-mouse_should_move_pos[0])*mouse_move_speed+player_see_x
        player_see_y=(y-mouse_should_move_pos[1])*mouse_move_speed+player_see_y
        glutWarpPointer(mouse_should_move_pos[0],mouse_should_move_pos[1])
        mouse_fix_No1=1
        glutPostRedisplay()
        return 0
    mouse_fix_No1+=1
def draw_main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
    glutCreateWindow("Minecraft 重置版 ByWzq".encode('GBK',errors="replace"))
    glutSetCursor(GLUT_CURSOR_NONE)
    glutReshapeWindow(800,800)
    glViewport(0,0,800,800)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    glutDisplayFunc(draw)
    glutReshapeFunc(change)#在每次拉动窗口的时候重新渲染
    glutKeyboardFunc(keyboardchange)
    glutPassiveMotionFunc(mousemove)
    glutMainLoop()
draw_main()
#generate_text_image(".","blue",100)