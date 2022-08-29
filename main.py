#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
#                本作品为兴趣使然                #
#         本作品与MOJANG工作室没有任何关系         #
#      本作品仅供学习、娱乐，商用请注明项目地址      #
#        欢迎提交拉取请求，这是对我最大的支持        #
#     我也只是一个小小的初三生，很多代码略为粗糙     #
#            因此希望您帮助改进我的代码            #
################################################

#################感谢与你相遇！###################

#导入OpenGL相关库（吐槽一下，隔壁glfw涉及到一些图像的直接就能用pillow的对象，opengl还得自己转换）
import PIL.Image
from OpenGL.GL import *
from OpenGL.GLU import *
#导入glfw库
import glfw
#导入获取列表大小的sys以供opengl使用
import sys
#导入三角函数相关库
import math
#导入numba性能提升相关库（直接将python代码编译为机器码，虽然实测好像没用但是应该会有用吧？）
from numba import njit
from numba.types import UniTuple,float64#这里PyCharm报错，不过实测可以导入，别动就行了
#导入os库以进行文件读取与写入
import os
#导入实用模块
from main.useful_modules import SmartPlanManager,FileBufferManager,TotalVarManager,float2int,PrintText,list_merge,read_resources_from_disk,read_opengl_resources_from_disk
#初始化实用模块
resources=read_resources_from_disk()
file_buffer_manager=FileBufferManager()
smart_plan_manager=SmartPlanManager()
text_printer=PrintText(resources["fonts"]["文鼎PL中楷体.ttf"])
total_var_manager=TotalVarManager({
    "draw":True,
    "file_buffer_manager":file_buffer_manager
})
#导入方块管理器
from main.block import block_manager
block_manager.init(total_var_manager)
#导入世界管理器（施工中awa）

#-------------------------------------------------------------------------------------------------------------------------
#可供自定义的变量有些还放到了main文件夹下面的模块里面，因为这样子就没有必要再考虑如何将本文件里面定义的变量应用到模块里面了，望周知。
#-------------------------------------------------------------------------------------------------------------------------

#允许用户自定义的变量,已将大部分变量做好注释
mouse_move_speed=1 #鼠标移动距离
player_move_speed=0.1
look_length=15  #渲染距离,只支持不小于1的奇数
highest_y=100  #世界最高Y坐标
lowest_y=0   #世界最低Y坐标，目前如果更改将会报错！
player_x=0    #这几个不必细说，都懂都懂
player_y=-1
player_z=-1
window_height=800    #窗口的长和宽
window_width=800
set_chat_list_show_time=100      #聊天框显示多久，2/3时间不变，1/3时间淡化消失

#用户不应该动的变量（当然放这里就代表有能耐你也能动）
player_see_x=0
player_see_y=0
player_see_x_temp=0
player_see_y_temp=window_height/2
lock_mouse=True
debug=False
debug_text=[['XYZ:',0.0,',',0.0,',',0.0],
            ['EYE:',0,',',0],]
mouse={0:0,1:0}#0为未按下，1为按下
input_text=False
input_buffer=""
chat_list=[]
chat_list_show_time=0
guide_buttons=[]
where_player_block=block_manager.find_block(player_x,player_z)
window=None#glfw的窗口
blocks_display_list=None#print_blocks会把方块保存成显示列表，算是最简单的提高性能的方法了
keyboard={}
for i in [256,ord("`"),ord("W"),ord("S"),ord("A"),ord("D"),ord(" "),ord("X")]:keyboard[i]=False#为什么wasd是大写？实测的...
def print_blocks(sx:int,sy:int,sz:int):#这里将来会选择性显示方块，不会全部显示一遍，多伤显卡QAQ
    def draw_a_face_of_the_square(direction:str,x:int,y:int,z:int,by_wzq:int):
        #图来自网络
        #    v4----- v5
        #   /|      /|
        #  v0------v1|
        #  | |     | |
        #  | v7----|-v6
        #  |/      |/
        #  v3------v2
        if direction=="up":
            glBindTexture(GL_TEXTURE_2D,resources["blocks_texture"][by_wzq][0][resources["blocks_texture"][by_wzq][1][0]])
            vertex_points=[x-0.5,y+0.5,z+0.5,  #V4
                           x+0.5,y+0.5,z+0.5,  #V5
                           x+0.5,y+0.5,z-0.5,  #V1
                           x-0.5,y+0.5,z-0.5]  #V0
        elif direction=="down":
            glBindTexture(GL_TEXTURE_2D,resources["blocks_texture"][by_wzq][0][resources["blocks_texture"][by_wzq][1][1]])
            vertex_points=[x-0.5,y-0.5,z-0.5,  #V3
                           x+0.5,y-0.5,z-0.5,  #V2
                           x+0.5,y-0.5,z+0.5,  #V6
                           x-0.5,y-0.5,z+0.5]  #V7
        elif direction=="left":
            glBindTexture(GL_TEXTURE_2D,resources["blocks_texture"][by_wzq][0][resources["blocks_texture"][by_wzq][1][2]])
            vertex_points=[x-0.5,y+0.5,z+0.5,  #V4
                           x-0.5,y+0.5,z-0.5,  #V0
                           x-0.5,y-0.5,z-0.5,  #V3
                           x-0.5,y-0.5,z+0.5]  #V7
        elif direction=="right":
            glBindTexture(GL_TEXTURE_2D,resources["blocks_texture"][by_wzq][0][resources["blocks_texture"][by_wzq][1][3]])
            vertex_points=[x+0.5,y+0.5,z-0.5,  #V1
                           x+0.5,y+0.5,z+0.5,  #V5
                           x+0.5,y-0.5,z+0.5,  #V6
                           x+0.5,y-0.5,z-0.5]  #V2
        elif direction=="front":
            glBindTexture(GL_TEXTURE_2D,resources["blocks_texture"][by_wzq][0][resources["blocks_texture"][by_wzq][1][4]])
            vertex_points=[x-0.5,y+0.5,z-0.5,  #V0
                           x+0.5,y+0.5,z-0.5,  #V1
                           x+0.5,y-0.5,z-0.5,  #V2
                           x-0.5,y-0.5,z-0.5]  #V3
        elif direction=="behind":
            glBindTexture(GL_TEXTURE_2D,resources["blocks_texture"][by_wzq][0][resources["blocks_texture"][by_wzq][1][5]])
            vertex_points=[x+0.5,y+0.5,z+0.5,  #V5
                           x-0.5,y+0.5,z+0.5,  #V4
                           x-0.5,y-0.5,z+0.5,  #V7
                           x+0.5,y-0.5,z+0.5]  #V6
        else:raise ValueError("print_blocks:draw_a_face_of_the_square：未知的direction参数内容！")
        tex_coord=(0,1,1,1,1,0,0,0)#顺序：左上、右上、右下、左下
        glBegin(GL_QUADS)
        for i in range(4):
            glVertex3f(vertex_points[i*3],vertex_points[i*3+1],vertex_points[i*3+2])
            glTexCoord(tex_coord[i*2],tex_coord[i*2+1])
        glEnd()
        glBindTexture(GL_TEXTURE_2D,0)
    #特别鸣谢：Stack Overflow用户Rabbid76
    #没有他回答了我三个问题，我这一辈子都做不出来
    #问题链接：
    #https://stackoverflow.com/questions/70476151/opengl-vbo-can-run-without-error-but-no-graphics
    #https://stackoverflow.com/questions/70610206/opengl-vbo-vao-ebo-can-run-without-error-but-no-graphics
    #https://stackoverflow.com/questions/70844191/pyopengl-run-with-no-texture
    #虽然他根本不知道：）
    global where_player_block,blocks_display_list
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor3ub(255,255,255)#防止聊天框淡化的时候一起给淡化了
    if total_var_manager.get_var("draw") or block_manager.find_block(player_x,player_z)!=where_player_block:
        where_player_block=block_manager.find_block(player_x,player_z)
        total_var_manager.set_var("draw",False)
        glDeleteLists(blocks_display_list,1)#这里第一次执行会报错，所以在底下的go_to_world提前生成了一个
        blocks_display_list=glGenLists(1)
        glNewList(blocks_display_list,GL_COMPILE)
        for y in range(lowest_y,highest_y+1):
            for x in range(sx-int((look_length-1)/2),sx+int((look_length-1)/2)+1):
                for z in range(sz-int((look_length-1)/2),sz+int((look_length-1)/2)+1):
                    by_wzq=block_manager.read_block(x,y,z,block_manager.block_temp)
                    if not by_wzq==0:
                        draw_a_face_of_the_square("up",x,y,z,by_wzq)
                        draw_a_face_of_the_square("down",x,y,z,by_wzq)
                        draw_a_face_of_the_square("left",x,y,z,by_wzq)
                        draw_a_face_of_the_square("right",x,y,z,by_wzq)
                        draw_a_face_of_the_square("front",x,y,z,by_wzq)
                        draw_a_face_of_the_square("behind",x,y,z,by_wzq)
        glEndList()
    glCallList(blocks_display_list)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
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
        #显示坐标系文字（方便与MC原版进行校对）
        text_printer.print_text_list(["x"], 1, 0, 0, size=1)
        text_printer.print_text_list(["y"], 0, 1, 0, size=1)
        text_printer.print_text_list(["z"], 0, 0, 1, size=1)
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
        text_printer.print_text_list(list_merge(debug_text),y=776)
#感谢csdn文章https://blog.csdn.net/weixin_43757333/article/details/110736766！现在它已经是准确的了！
@njit(UniTuple(float64,3)(float64,float64))
def view_orientations(px,py):return math.cos(math.pi/180*py)*math.sin(math.pi/180*px),math.sin(math.pi/180*py),-math.cos(math.pi/180*py)*math.cos(math.pi/180*px)
def world_main_loop():
    global input_text,chat_list_show_time,player_y
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(-0.3,0.3,-0.3,0.3,0.1,8)
    #笔记：
    #glFrustum(left,right,bottom,top,zNear,zFar)
    #这个函数的参数只定义近裁剪平面的左下角点和右上角点的三维空间坐标，即(left，bottom，-near)和(right，top，-near)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    #计算视角望向的位置
    for i in [ord("W"),ord("S"),ord("A"),ord("D")]:
        if keyboard[i]:spectator_mode(i)
    if keyboard[ord(" ")]:player_y+=0.1
    if keyboard[ord("X")]: player_y-=0.1
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
    temp=mouse_hit_test(block_manager.block_temp, player_see_x, player_see_y, player_x, player_y, player_z)
    if temp is not None:
        x,y,z=temp[0]
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
        for temp in range(int(len(b) / 2)):
            glVertex3f(a[b[temp*2]*3],a[b[temp*2]*3+1],a[b[temp*2]*3+2])
            glVertex3f(a[b[temp*2+1]*3],a[b[temp*2+ 1]*3+1],a[b[temp*2+1]*3+2])
        glEnd()
    debug_3d()
    #进入2D状态
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,window_height,0,window_width)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    #显示指针
    glCallList(resources["cross_pointer"])
    #调试模式
    debug_2d()
    #显示指令栏
    if chat_list_show_time!=0 and not input_text:
        chat_list_show_time-=1
        if set_chat_list_show_time/3*1<chat_list_show_time:text_printer.print_text_list([input_buffer] + chat_list, m=-1)
        else:
            glColor4ub(255,255,255,float2int(765/set_chat_list_show_time*chat_list_show_time))
            text_printer.print_text_list([input_buffer] + chat_list, m=-1)
    if input_text:text_printer.print_text_list([input_buffer] + chat_list, m=-1)
    block_manager.unload_block(float2int(player_x),float2int(player_z))
    #聊天框淡化事件，必须要激活
    smart_plan_manager.clock()
def spectator_mode(button):
    global player_x,player_y,player_z
    if button in [ord("W"),ord("S")]:
        x,y,z=view_orientations(player_see_x,player_see_y)
        if button==ord("S"):x,y,z=x*-1,y*-1,z*-1
    else:
        x,y,z=view_orientations(player_see_x+90,player_see_y)
        if button==ord("A"):x,z=x*-1,z*-1
        y=0
    player_x,player_y,player_z=player_x+x*player_move_speed,player_y+y*player_move_speed,player_z+z*player_move_speed
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
            for temp1,temp2 in block_manager.blocks.items():file_buffer_manager.write(os.path.join(block_manager.main_folder_dir, "saves", block_manager.save_name, "(" + str(temp1[0]) + "," + str(temp1[1]) + ")"), str(temp2))
        elif command_split[0]=="main_run":
            eval(" ".join(command_split[1:]))#属于python这种解释型语言独有的快乐，就是随便运行任何代码
        else:chat_list=["未知的指令！"]+chat_list
    chat_list_show_time=set_chat_list_show_time
def lock_or_unlock_mouse(a):
    global lock_mouse
    if a:
        lock_mouse=False
        glfw.set_input_mode(window,glfw.CURSOR,glfw.CURSOR_NORMAL)
    else:
        lock_mouse=True
        glfw.set_input_mode(window,glfw.CURSOR,glfw.CURSOR_DISABLED)
@njit
def mouse_hit_test(block_temp,see_x,see_y,px,py,pz):
    #感谢开源项目https://github.com/fogleman/Minecraft提供的函数思路！（没错，同样是在做Minecraft）
    m=8#精度
    x,y,z=px,py+1,pz
    x_vector,y_vector,z_vector=view_orientations(see_x,see_y)
    x_vector,y_vector,z_vector=x_vector/m,y_vector/m,z_vector/m
    for _ in range(70*m):
        free_block=round(x),round(y),round(z)
        x,y,z=x+x_vector,y+y_vector,z+z_vector
        if y<lowest_y-0.5:return None
        if block_manager.read_block(round(x),round(y),round(z),block_temp)!=0:
            return (round(x),round(y),round(z)),free_block
    return None
def world_mouseclick(window,button,action,mods):
    if button==glfw.MOUSE_BUTTON_LEFT or button==glfw.MOUSE_BUTTON_RIGHT:mouse[button==glfw.MOUSE_BUTTON_RIGHT]=int(action==glfw.PRESS)#简单来说这一行代码的作用就是给mouse的1或0如果按下就标记为1没按下就标记为0
    if mouse[1]:
        temp=mouse_hit_test(block_manager.block_temp,player_see_x,player_see_y,player_x,player_y,player_z)
        if temp is not None:block_manager.write_block(temp[1][0],temp[1][1],temp[1][2],1)
    if mouse[0]:
        temp=mouse_hit_test(block_manager.block_temp,player_see_x,player_see_y,player_x,player_y,player_z)
        if temp is not None:block_manager.write_block(temp[0][0],temp[0][1],temp[0][2],0)
def glfw_keyboard_callback(_,key,scancode,action,mods):
    global input_text,input_buffer,debug
    if debug:print("glfw-char",key,scancode,action,mods)
    if input_text:
        if key==257:#回车
            input_text=False
            run_command(input_buffer)
            input_buffer=""
            lock_or_unlock_mouse(False)
        elif key==256:#ESC
            input_text=False
            input_buffer=""
            lock_or_unlock_mouse(False)
        elif key==259:input_buffer=input_buffer[:-1]#Backspace
    else:
        if not keyboard[256] and key==256:lock_or_unlock_mouse(lock_mouse)#锁定或非锁定状态
        elif not keyboard[96] and key==96:#调试模式
            if debug:debug=False
            else:debug=True
        if key in keyboard and action==glfw.PRESS:keyboard[key]=True
        if key in keyboard and action==glfw.RELEASE:keyboard[key]=False
def glfw_keyboard_fix_callback(_,codepoint):
    global input_text,input_buffer
    if debug:print("glfw-key",codepoint)
    if input_text:input_buffer+=chr(codepoint)
    else:
        if codepoint==ord("/"):
            input_text=True
            lock_or_unlock_mouse(True)
            input_buffer="/"
            return 0
        elif codepoint==ord("t"):
            input_text=True
            lock_or_unlock_mouse(True)
            glfw.set_input_mode(window,glfw.CURSOR,glfw.CURSOR_NORMAL)
            return 0
def world_mousemove(_,x,y):
    global player_see_x,player_see_y,player_see_y_temp
    if lock_mouse:
        player_see_x=(x-window_width/2)%360
        if player_see_y+player_see_y_temp-y>89.5:player_see_y=89.5
        elif player_see_y+player_see_y_temp-y<-89.5:player_see_y=-89.5#为什么是89.5而不是90？因为程序采用万向节控制视角，所以会出现“万向节死锁”，这样做可以避免达到90触发死锁
        else:player_see_y+=player_see_y_temp-y
        player_see_y_temp=y
def guide_main_loop():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0,window_height,0,window_width)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    text_printer.print_text_list(text=["PyMinecraft"], x=0, y=700, size=100)
    glfw.swap_buffers(window)
def go_to_guide():#处理情况：游戏退出到主界面，其他界面退出到主界面
    glfw.set_input_mode(window,glfw.CURSOR_NORMAL,glfw.CURSOR_DISABLED)
    glMatrixMode(GL_MODELVIEW)
    glLoadMatrixd(init_info[0])
    glMatrixMode(GL_PROJECTION)
    glLoadMatrixd(init_info[1])
    return guide_main_loop
def go_to_world():
    glViewport(0,0,window_height,window_width)
    glfw.set_input_mode(window,glfw.CURSOR,glfw.CURSOR_DISABLED)
    glfw.set_cursor_pos_callback(window,world_mousemove)
    glfw.set_mouse_button_callback(window,world_mouseclick)
    glfw.set_key_callback(window,glfw_keyboard_callback)
    glfw.set_char_callback(window,glfw_keyboard_fix_callback)
    global resources,blocks_display_list#只能在opengl初始化后初始化的资源
    temp=read_opengl_resources_from_disk()
    resources["blocks_texture"],resources["cross_pointer"]=temp
    blocks_display_list=glGenLists(1)
    return world_main_loop
def glfw_error_callback(error_code,error_info):#欢迎大家在这个函数如一下一样添加解决方案
    print("glfw错误！错误代码：",error_code,"\n错误描述：",error_info)
    errors={65544:"你当前正在使用x11，但系统包管理器安装的glfw仍为glfw-wayland，请安装glfw-x11"}
    if error_code in errors:print("\n根据错误代码匹配到可能的解决方案：\n"+errors[error_code]+"\n")
def init():
    global window
    #设置glfw报错回调
    glfw.set_error_callback(glfw_error_callback)
    #进行glfw的最基础初始化
    glfw.init()
    glfw.window_hint(glfw.DOUBLEBUFFER,glfw.TRUE)#启用双缓冲
    glfw.window_hint(glfw.RESIZABLE,glfw.FALSE)#设置窗口大小不可由用户调整
    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER,glfw.TRUE)#启用alpha通道
    glfw.window_hint(glfw.SCALE_TO_MONITOR,glfw.TRUE)#窗口居中
    window=glfw.create_window(window_height,window_width,"PyMinecraft ByWzq",None,None)
    #设置窗口图标（总算能设置啦！）
    glfw.set_window_icon(window,3,resources["icon"])
    glfw.make_context_current(window)
    #glutInitDisplayMode(GLUT_DOUBLE|GLUT_DEPTH|GLUT_RGBA)
    #完成其余的初始化
    glClearColor(0.0,174.0,238.0,238.0)
    smart_plan_manager.add(1000,file_buffer_manager.save, 1)
#可直接覆盖函数实现自己的功能,可以当成mod加载器
for i in os.listdir(os.path.join(block_manager.main_folder_dir,"mods")):
    if i.split(".")[-2:]==["enable","py"]:
        with open(os.path.join(block_manager.main_folder_dir,"mods",i),"rt") as f: exec(f.read())
    elif i.split(".")[-2:]!=["disable","py"] and i!="readme.txt":
        print("未知的mod状态码！请检查.PyMinecraft/mods文件夹下的mod开头是否均为enable或disable！\n正在退出......")
        exit(1)
init()
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LESS)
init_info=(glGetDoublev(GL_MODELVIEW_MATRIX),glGetDoublev(GL_PROJECTION_MATRIX))
#这里if后面的数字填1或0，填0进入世界（成熟），填1进入界面（没做，只有背景和测试文字）
if 0:main_game_loop_function=go_to_guide()
else:main_game_loop_function=go_to_world()
while glfw.window_should_close(window)==0:#正式开始运行
    glfw.poll_events()
    main_game_loop_function()
    glfw.swap_buffers(window)#交换缓存，显示画面
glfw.terminate()#释放glfw资源
text_printer.character.clean_up()#释放freetype资源
#　    ☆ *　. 　☆
#　　  . ∧＿∧ ∩　* ☆
#* ☆ ( ・∀・)/ .
#　. ⊂　　  ノ* ☆
#☆ * (つ ノ .☆
#　　  (ノ
#总代码破800行啦！
#我推送了100次代码！
