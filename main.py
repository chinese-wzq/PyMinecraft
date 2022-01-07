# coding=utf-8
# Always believe,always hope.

#感谢您的遇见！
#本项目（PyMinecraft）GitHub地址：
#https://github.com/chinese-wzq/PyMinecraft
#本项目（PyMinecraft）Gitee地址：
#https://gitee.com/this_is_the_best_name/PyMinecraft
#如果你发现有无良程序员大量盗用本程序代码并且未加声明的
#欢迎你与他对线，并且将他的作品地址发给我（让我康康啊♂）
#以下为程序声明以及一些介绍，如果有不符合规范的欢迎提出拉取请求，我不懂开源协议，太多了QAQ

#本程序使用字体：JetBrains Mono，字体不同可能会出现程序内的注释排版紊乱！

#本程序部分行较长。为什么？因为觉得这样很爽（莫名）

################################################
#                本作品为兴趣使然                 #
#             我并没有收过任何人的钱财              #
#             也没有与任何人有契约关系              #
#     本作品与MOJANG工作室（BUGJUMP）没有任何关系    #
#     我从来没有查看过Minecraft的源码（反正看不懂）   #
#      本作品仅供学习、娱乐，商用请注明项目地址        #
#        欢迎提交拉取请求，这是对我最大的支持         #
#    我也只是一个小小的初二生，很多数学计算略为粗糙     #
#            因此希望您帮助改进我的算法             #
################################################
#            本游戏是开源的，所有人可编辑           #
#           因此，我才能尽量保证代码的安全性         #
#          本游戏从设计之初就采用了超多函数设置       #
#          这使得游戏的大部分函数具有参考价值        #
#             如果本游戏的某些函数帮到了您          #
#        欢迎您在项目地址上点一个免费的Star（星）     #
#             你的星会成为我Coding的动力           #
################################################

#################感谢与你相遇！###################

#导入OpenGL相关库
import numpy
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
#导入字体显示相关库
from OpenGL.WGL import *
import win32ui
#导入三角函数相关库
import math
#导入窗口相关库
import win32con,win32gui
#导入区块读取相关库
import json,os,copy

#允许用户自定义的变量,已将大部分变量做好注释
mouse_move_speed=0.01 #鼠标移动距离
player_move_speed=0.1
look_length=15  #渲染距离,只支持不小于1的奇数
highest_y=100  #世界最高Y坐标
lowest_y=0   #世界最低Y坐标，目前如果更改将会报错！
player_x=0    #这几个不必细说，都懂都懂
player_y=-1
player_z=-1
font="Microsoft YaHei UI"    #显示文字时使用的字体
window_long=400    #窗口的长与宽
window_width=400
set_chat_list_show_time=50      #聊天框显示多久，2/3时间不变，1/3时间淡化消失
saves_folder_dir="D:\\桌面\\PyMinecraft\\saves\\"   #指定了存储所有存档的文件夹的位置
save_folder_dir="D:\\桌面\\PyMinecraft\\saves\\example\\"   #指定了存储单个存档的文件夹的位置
load_all_save=False   #在启动时就加载所有的区块，并且不会执行卸载和加载的程序，可以减少程序卡顿，但在存档过大时需谨慎开启

#用户不应该动的变量
save_folder_files_list=os.listdir(save_folder_dir)
player_see_x=0
player_see_y=0
lock_muose=False
debug=False
map=[]
block_color=[(255,255,0)]
debug_text=[['XYZ:',0.0,',',0.0,',',0.0],
            ['EYE:',0,',',0],]
block_size=11   #必须为单数
buffer_block_size=15   #也必须为单数
temp1=block_size/2#区块加载的缓存变量
temp2=(buffer_block_size-1)/2
temp7=(block_size-1)/-2
keyboard={}
for i in [b'\x1b',b'`',b'w',b's',b'a',b'd']:keyboard[i]=False
input_text=False
input_buffer=""
chat_list=[]
chat_list_show_time=0
guide_buttons=[]
def float2int(i):return int(str(i).split(".")[0])
def write_list(wait_write_list:list,write:str,point:list,fill=0,fill_callback=None):#代码再不重写就TM要爆炸了
    really_point=wait_write_list
    for i in range(len(point)):
        while point[i]>len(really_point)-1:
            if fill_callback is None:really_point.append(copy.copy(fill))
            else:really_point.append(fill_callback(i,point))
        if i==len(point)-1:
            really_point[point[i]]=write
            return wait_write_list
        really_point=really_point[point[i]]
#如果设置为加载全部区块，则进行一些操作
if load_all_save:
    for i in save_folder_files_list:
        a,b=i.split(",")
        a=int(a)
        b=int(b)
        with open(save_folder_dir+str(a)+','+str(b)) as f: map=write_list(map,json.load(f),[a>=0,a+int(a<0),b>=0,b+int(b<0)],fill=[])
def read_block(x:int,y:int,z:int):#此模块包装了读取方块的代码,未来可能也会把世界生成的代码放里边！
    #以下为基本原理：
    #1.先计算输入坐标位于的区块位置
    #2.读取区块文件，并将区块放入map进行缓存
    #                               ↑
    #将区块放入缓存中，并卸载超出缓存区域的区块，关于map的区块索引结构结构：（存在负数，每层需要两层，一层正一层负）
    #                                                         第一层：区块的X
    #                                                         第二层：区块的Z
    #                                                         此索引方法虽然会出现许多空的项，但是比全部载入对内存的消耗少得多了
    #3.从区块里读取指定位置方块,索引方法：（不存在负数情况），随后返回指定位置方块
    #                              第一层：Y
    #                              第二层：X
    #                              第二层：Z
    global map
    #第一步
    i=1
    ii=1
    if x<0:i=-1
    if z<0:ii=-1
    block_X=float2int((x+temp1*i)/block_size)
    block_Z=float2int((z+temp1*ii)/block_size)
    #第二步，这里决定先卸载再载入
    temp3=block_X>=0
    temp4=block_X+int(block_X<0)
    temp5=block_Z>=0
    temp6=block_Z+int(block_Z<0)
    if not load_all_save:
        for i in range(len(map)):
            for ii in range(len(map[i])):
                for iii in range(len(map[i][ii])):
                    for iiii in range(len(map[i][ii][iii])):
                        if i>0:a=ii
                        else:a=ii*-1-1
                        if iii>0:aa=iiii
                        else:aa=iiii*-1-1
                        if not block_X-temp2<=a<=block_X+temp2 or not block_Z-temp2<=aa<=block_Z+temp2:
                            with open(save_folder_dir+str(a)+","+str(aa),"w") as f:json.dump(map[i][ii][iii][iiii],f)
                            map[i][ii][iii][iiii]=0
        try:
            if not map[temp3][temp4][temp5][temp6]:raise IndexError
        except IndexError:
            if str(block_X)+','+str(block_Z) in save_folder_files_list:
                with open(save_folder_dir+str(block_X)+','+str(block_Z)) as a:map=write_list(map,json.load(a),[temp3,temp4,temp5,temp6],[])
            else:
                return 0
    #第三步
    #    v4----- v5
    #   /|      /|
    #  v0------v1|
    #  | |↗    | |
    #  | v7----|-v6
    #  |/      |/
    #  v3------v2→
    #目标就是先求出区块中心，随后求出V3这个点的位置，最后换算坐标进入区块坐标系
    center_block_x=(block_X-0.5)*block_size
    center_block_z=(block_Z-0.5)*block_size
    try:return map[temp3][temp4][temp5][temp6][y][float2int(x-center_block_x)][float2int(z-center_block_z)]
    except IndexError:return 0
def write_block_fill_callback(a,b):
    if a==len(b)-1:return 0
    else:return []
def write_block(x:int,y:int,z:int,write:int):
    global map
    #第一步
    i=1
    ii=1
    if x<0:i=-1
    if z<0:ii=-1
    block_X=float2int((x+temp1*i)/block_size)
    block_Z=float2int((z+temp1*ii)/block_size)
    temp3=block_X>=0
    temp4=block_X+int(block_X<0)
    temp5=block_Z>=0
    temp6=block_Z+int(block_Z<0)
    center_block_x=(block_X-0.5)*block_size
    center_block_z=(block_Z-0.5)*block_size
    map=write_list(map,write,[temp3,temp4,temp5,temp6,y,float2int(x-center_block_x),float2int(z-center_block_z)],fill_callback=write_block_fill_callback)

draw=False
block_VAO=0
block_EBO_buffer_len=0
def print_blocks(sx:int,sy:int,sz:int):#这里将来会选择性显示方块，不会全部显示一遍，多伤显卡QAQ
    #特别鸣谢：Stack Overflow用户Rabbid76
    #没有他回答了我两个问题，我这一辈子都做不出来
    #问题链接：
    #https://stackoverflow.com/questions/70476151/opengl-vbo-can-run-without-error-but-no-graphics
    #https://stackoverflow.com/questions/70610206/opengl-vbo-vao-ebo-can-run-without-error-but-no-graphics
    #虽然他别没有叫我贴上这个注释，不过我想，做人要学会感恩😀
    global draw,block_VAO,block_EBO_buffer_len
    if not draw:
        block_point_buffer=[]
        block_color_buffer=[]
        block_EBO_buffer=[]
        color_EBO_buffer=[]
        for x in range(sx-int((look_length-1)/2),sx+int((look_length-1)/2)+1):
            for y in range(lowest_y,highest_y+1):
                for z in range(sz-int((look_length-1)/2),sz+int((look_length-1)/2)+1):
                    by_wzq=read_block(x,y,z)
                    if not by_wzq==0:
                        #图盗的
                        #    v4----- v5
                        #   /|      /|
                        #  v0------v1|
                        #  | |     | |
                        #  | v7----|-v6
                        #  |/      |/
                        #  v3------v2
                        a=len(block_point_buffer)/3
                        block_point_buffer+=[x-0.5,y+0.5,z-0.5,#V0
                                            x+0.5,y+0.5,z-0.5,#V1
                                            x+0.5,y-0.5,z-0.5,#V2
                                            x-0.5,y-0.5,z-0.5,#V3
                                            x-0.5,y+0.5,z+0.5,#V4
                                            x+0.5,y+0.5,z+0.5,#V5
                                            x+0.5,y-0.5,z+0.5,#V6
                                            x-0.5,y-0.5,z+0.5]#V7
                        block_EBO_buffer+=[a+0,a+1,a+5,a+4,
                                           a+3,a+2,a+6,a+7,
                                           a+0,a+3,a+7,a+4,
                                           a+1,a+2,a+6,a+5,
                                           a+0,a+1,a+2,a+3,
                                           a+4,a+5,a+6,a+7]
                        block_color_buffer+=block_color[by_wzq-1]*8
        #创建顶点VBO
        block_VBO=glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,block_VBO)
        a=numpy.array(block_point_buffer,dtype='float32')
        glBufferData(GL_ARRAY_BUFFER,sys.getsizeof(a),a,GL_STATIC_DRAW)
        #创建颜色VBO
        color_VBO=glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,color_VBO)
        a=numpy.array(block_color_buffer,dtype='float32')
        glBufferData(GL_ARRAY_BUFFER,sys.getsizeof(a),a,GL_STATIC_DRAW)
        #绑定VAO
        block_VAO=glGenVertexArrays(1)
        glBindVertexArray(block_VAO)
        #绑定EBO
        #必须先绑定再创建EBO
        block_EBO=glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER,block_EBO)
        a=numpy.array(block_EBO_buffer,dtype='uint32')
        glBufferData(GL_ELEMENT_ARRAY_BUFFER,sys.getsizeof(a),a,GL_STATIC_DRAW)
        block_EBO_buffer_len=len(a)
        #绑定顶点VBO
        glBindBuffer(GL_ARRAY_BUFFER,block_VBO)
        glVertexPointer(3,GL_FLOAT,0,None)
        glEnableClientState(GL_VERTEX_ARRAY)
        #绑定颜色VBO
        glBindBuffer(GL_ARRAY_BUFFER,color_VBO)
        glColorPointer(3,GL_FLOAT,0,None)
        glEnableClientState(GL_COLOR_ARRAY)
        #解绑
        glBindVertexArray(0)
        draw=True
    glBindVertexArray(block_VAO)
    glDrawElements(GL_QUADS,block_EBO_buffer_len,GL_UNSIGNED_INT,None)
    glBindVertexArray(0)
def print_text_list(text:list,callback=None,x=0,y=0,m=1,color=(250,255,255)):#TODO:以后别忘了把这个颜色改掉，换个更好看的
    global font,window_width
    debug_hDC=wglGetCurrentDC()
    font_hieght=30
    #设定文字的字体、颜色和背景
    win32gui.SelectObject(debug_hDC,win32ui.CreateFont({"height":font_hieght,"name":font}).GetSafeHandle())
    win32gui.SetBkMode(debug_hDC,win32con.TRANSPARENT)
    glColor3ub(color[0],color[1],color[2])
    if callback is not None:callback(debug_hDC)
    #开始显示（把连接和显示整到一起去了）
    glLoadIdentity()
    glTranslatef(-0.3,0.29,-0.1)#-0.1是为了防止文字被后面的物体遮挡！
    qaq=y
    draw_text_list=glGenLists(1)
    for i in text:
        glRasterPos2f(x,-qaq)
        for ii in i:
            for iii in str(ii):
                wglUseFontBitmapsW(debug_hDC,ord(iii),1,draw_text_list)
                glCallList(draw_text_list)
        qaq+=font_hieght/3000*m
    win32gui.DeleteObject(debug_hDC)
def debug_print_coordinates_text(hDC):
    #显示坐标系文字（方便与MC原版进行矫正）
    a=glGenLists(1)
    glRasterPos3f(1,0,0)
    wglUseFontBitmapsW(hDC,ord('x'),1,a)
    glCallList(a)
    glRasterPos3f(0,1,0)
    wglUseFontBitmapsW(hDC,ord('y'),1,a)
    glCallList(a)
    glRasterPos3f(0,0,1)
    wglUseFontBitmapsW(hDC,ord('z'),1,a)
    glCallList(a)
def debug_main():
    global debug,player_see_x,player_see_y,player_x,player_y,player_z,debug_text
    if debug:
        #显示一个世界原点的坐标系
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
        print_text_list(debug_text,debug_print_coordinates_text)
def view_orientations(px,py,callback=None):
    #我还没有学过三角函数，因此如果输入负数也能正常使用，以下代码可以更加简洁。请帮忙改一改哈😀
    if callback is not None:
        px,py=callback(px,py)
    if px>=0:
        if px>90:
            x=math.cos(px-90)
            z=math.sin(px-90)*-1
        else:
            x=math.sin(px)
            z=math.cos(px)
    else:
        if px<-90:
            x=math.cos((px+90)*-1)*-1
            z=math.sin((px+90)*-1)*-1
        else:
            x=math.sin(px*-1)*-1
            z=math.cos(px*-1)
    if py>=0:
        y=math.sin(py)
    else:
        y=math.sin(py*-1)*-1
    return x,y,z
def world_main_loop():
    global input_text,chat_list_show_time
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(-0.3,0.3,-0.3,0.3,0.1,8)
    #笔记：
    #glFrustum(left,right,bottom,top,zNear,zFar)
    #这个函数的参数只定义近裁剪平面的左下角点和右上角点的三维空间坐标，即（left，bottom，-near）和（right，top，-near)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    #计算视角望向的位置
    x,y,z=view_orientations(player_see_x,player_see_y)
    gluLookAt(
        player_x,player_y+1,player_z,
        player_x+x,player_y+y+1,player_z+z,
        0,1,0
    )
    #渲染方块
    print_blocks(int(player_x),int(player_y),int(player_z))
    #调试模式
    debug_main()
    if chat_list_show_time!=0 and not input_text:
        chat_list_show_time-=1
        if set_chat_list_show_time/3*1<chat_list_show_time:print_text_list([input_buffer]+chat_list,y=0.585,m=-1)
        else:
            a=int(255/(set_chat_list_show_time/3*1)*(set_chat_list_show_time/3*1-(set_chat_list_show_time/3*1)+chat_list_show_time))
            print_text_list([input_buffer]+chat_list,y=0.585,m=-1,color=(a,a,a))
    #显示指令栏
    if input_text:print_text_list([input_buffer]+chat_list,y=0.585,m=-1)
    glutSwapBuffers()
def walk_left(a,b):return a+1.57,b#1.57是实测出来的数据~
def spectator_mode(button):
    global player_x,player_y,player_z
    if button in [b'w',b's']:
        x,y,z=view_orientations(player_see_x,player_see_y)
        if button==b's':
            x*=-1
            y*=-1
            z*=-1
    else:
        x,y,z=view_orientations(player_see_x,player_see_y,walk_left)
        if button==b'd':
            x*=-1
            z*=-1
        y=0
    player_x+=x*player_move_speed
    player_y+=y*player_move_speed
    player_z+=z*player_move_speed
    glutPostRedisplay()
def run_command(command):#名义上叫做运行指令，实际上负责了聊天框输入事件处理的全部
    global chat_list,chat_list_show_time,draw
    if command[0]=="/":
        #对输入进行拆分
        command_split=command[1:].split(' ')
        if command_split[0]=="fill":
            for i in range(10):
                write_block(int(command_split[1])+i,int(command_split[2]),int(command_split[3]),int(command_split[4]))
            draw=False
        if command_split[0]=="tp":
            global player_x,player_y,player_z
            player_x=float(command_split[1])
            player_y=float(command_split[2])
            player_z=float(command_split[3])
    chat_list=[input_buffer]+chat_list
    chat_list_show_time=set_chat_list_show_time
def lock_or_unlock_mouse(a):
    global lock_muose
    if a:
        lock_muose=False
        glutSetCursor(GLUT_CURSOR_LEFT_ARROW)
    else:
        glutWarpPointer(window_long,window_width)
        lock_muose=True
        glutSetCursor(GLUT_CURSOR_NONE)
        glutPostRedisplay()
def keyboarddown(button,x,y):
    global keyboard,input_text,input_buffer,debug,lock_muose
    if input_text:
        if button==b'\x1b' or button==b'\r':
            input_text=False
            run_command(input_buffer)
            input_buffer=""
            lock_or_unlock_mouse(False)
        elif button==b'\x08':input_buffer=input_buffer[:-1]
        else:input_buffer+=button.decode()
        glutPostRedisplay()
    else:
        if not keyboard[b'\x1b'] and button==b'\x1b':lock_or_unlock_mouse(lock_muose)#锁定或非锁定状态
        elif not keyboard[b'`'] and button==b'`':#调试模式
            if debug:
                glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)
                debug=False
            else:
                glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
                debug=True
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
            return 0
        keyboard[button]=True
def keyboardup(button,x,y):
    global keyboard
    keyboard[button]=False
def world_mousemove(x,y):
    global player_see_x,player_see_y
    if lock_muose and window_long!=x and window_width!=y:
        player_see_x=(window_long-x)*mouse_move_speed+player_see_x
        player_see_y=(window_width-y)*mouse_move_speed+player_see_y
        #这里增加了数值限制，防止过头，因为是实测的数据，可能有不准，见谅~
        if player_see_y>2:player_see_y=2
        if player_see_y<-2:player_see_y=-2
        if player_see_x>3:player_see_x-=6
        if player_see_x<-3: player_see_x+=6
        glutWarpPointer(window_long,window_width)
        glutPostRedisplay()
def backgroud():
    global keyboard
    #键盘
    for i in [b'w',b's',b'a',b'd']:
        if keyboard[i]:spectator_mode(i)
    #聊天框淡化事件，必须要激活
    if chat_list_show_time!=0 and not input_text:glutPostRedisplay()
def guide_button_event_init():
    global guide_buttons
    guide_buttons=[]
def guide_main_loop():
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
    glColor3f(1.0,0.0,0.0)
    glRectf(-0.5,-0.5,0.5,0.5)
    glutSwapBuffers()
def guide_init():#处理情况：游戏退出到主界面，其他界面退出到主界面
    glutSetCursor(GLUT_CURSOR_LEFT_ARROW)
    glutIdleFunc(nothing)
    glutPassiveMotionFunc(nothing)
    glMatrixMode(GL_MODELVIEW)
    glLoadMatrixd(init_info[0])
    glMatrixMode(GL_PROJECTION)
    glLoadMatrixd(init_info[1])
    glutDisplayFunc(guide_main_loop)
def go_to_world():
    glutSetCursor(GLUT_CURSOR_NONE)
    glutDisplayFunc(world_main_loop)
    glutIdleFunc(backgroud)
    glutPassiveMotionFunc(world_mousemove)
def nothing(*args):pass
def init():
    #进行glut的最基础初始化
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_DEPTH)
    glutCreateWindow("PyMinecraft ByWzq".encode('GBK',errors="replace"))
    #使用户无法更改窗口大小
    hwnd=win32gui.GetForegroundWindow()
    A=win32gui.GetWindowLong(hwnd,win32con.GWL_STYLE)
    A^=win32con.WS_THICKFRAME
    win32gui.SetWindowLong(hwnd,win32con.GWL_STYLE,A)
    #完成其余的初始化
    glutReshapeWindow(window_long*2,window_width*2)
    glViewport(0,0,window_long*2,window_width*2)
    glClearColor(0.0,0.0,0.0,0.0)
init()
glEnable(GL_DEPTH_TEST)
glDepthFunc(GL_LESS)
glutKeyboardFunc(keyboarddown)
glutKeyboardUpFunc(keyboardup)
init_info=(glGetDoublev(GL_MODELVIEW_MATRIX),glGetDoublev(GL_PROJECTION_MATRIX))
go_to_world()
glutMainLoop()#正式开始运行
