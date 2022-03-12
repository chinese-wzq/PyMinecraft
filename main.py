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

#本程序使用字体：JetBrains Mono，字体不同可能会出现程序内的注释排版紊乱！

#本程序部分行较长。为什么？因为觉得这样很爽（莫名）
#本程序经常出现直接对函数参数赋值的情况。为什么？因为这样写的行更少，而且不用再想新的变量名啦~

#二次开发提示：
#函数基本没有对参数进行检查，也就是说，如果你的参数用错了，那么程序是会直接崩溃的（甚至可能找不到原因）
#所以，在使用函数前，请务必查看程序中对函数的使用方法，并将函数的实现看一遍

#对了，一些变量和函数参数因为英语能力有限不得不用机翻（其实要是我懒可以直接写中文变量名，不过懒得切输入法）

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

#################感谢与你相遇！###################

#导入OpenGL相关库
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
#导入三角函数相关库
import math
#导入窗口相关库
import win32con,win32gui
#导入区块读取相关库
import os,json
#导入方块贴图生成库
from PIL import Image
from PIL import ImageDraw
#导入字体点阵获取相关库
from freetype import *
#导入numba性能提升
from numba import njit
from numba.types import UniTuple,DictType,int64,float64
from numba.typed import Dict
#导入pythonn程序员必备numpy
import numpy as np
#导入性能测试函数（仅供开发使用）
#import timeit

#允许用户自定义的变量,已将大部分变量做好注释

mouse_move_speed=1 #鼠标移动距离
player_move_speed=0.1
look_length=15  #渲染距离,只支持不小于1的奇数
highest_y=100  #世界最高Y坐标
lowest_y=0   #世界最低Y坐标，目前如果更改将会报错！
player_x=0    #这几个不必细说，都懂都懂
player_y=-1
player_z=-1
font="C:/WINDOWS/Fonts/msyh.ttc"    #显示文字时使用的字体,需完整路径
window_height=400    #窗口的长和宽
window_width=400
set_chat_list_show_time=100      #聊天框显示多久，2/3时间不变，1/3时间淡化消失
main_folder_dir=os.path.join(".",".PyMinecraft")        #指定主目录位置(默认为.//PyMincraft)
save_name="example"         #指定存档名称(位于.//PyMinecraft//saves//下)
load_all_save=True   #在启动时就加载所有的区块，并且不会执行卸载和加载的程序，可以减少程序卡顿，但在存档过大时需谨慎开启

#用户不应该动的变量（当然放这里就代表有能耐你也能动）
save_folder_files_list=os.listdir(os.path.join(main_folder_dir,"saves",save_name))
player_see_x=0
player_see_y=0
player_see_x_temp=0
player_see_y_temp=0
lock_muose=False
debug=False
blocks=Dict.empty(key_type=UniTuple(int64,2),value_type=DictType(UniTuple(int64,3),int64))
#新手入门numba备注：   ↑             ↑               ↑         ↑
#                键的类型    意为有两个int64项的元组 值的类型  意为：键是由3个int64项组成的元组，值是int64的字典
block_temp=Dict.empty(key_type=UniTuple(int64, 3), value_type=int64)
block_texture=[]
debug_text=[['XYZ:',0.0,',',0.0,',',0.0],
            ['EYE:',0,',',0],]
block_size=11   #必须为单数
buffer_block_size=15   #也必须为单数
keyboard={}
for i in [b'\x1b',b'`',b'w',b's',b'a',b'd',b" ",b"x"]:keyboard[i]=False
mouse={0:1,2:1}
input_text=False
input_buffer=""
chat_list=[]
chat_list_show_time=0
guide_buttons=[]

class FileBuffer:
    def __init__(self,buffer_max_size=419430400):self.file,self.max={},buffer_max_size
    def check(self):
        if sys.getsizeof(self.file)>self.max:
            while sys.getsizeof(self.file)>self.max:
                i=self.file.popitem()
                with open(i[0],"w") as f: f.write(i[1])
    def read(self,path:str,really:bool=False):
        if path not in self.file or really:
            with open(path,"r") as f:self.file[path]=f.read()
        return self.file[path]
    def write(self,path:str,content:str,really:bool=False):
        if really:
            with open(path,"w") as f:f.write(content)
        self.file[path]=content
    def save(self):
        for i,ii in self.file.items():
            with open(i,"w") as f:f.write(ii)
file_buffer_reader=FileBuffer()
class SmartPlan:
    def __init__(self):self.plan=[]
    def add(self,frequency,callback,priority):
        """
        :param frequency: 频率，每执行一次计时函数算作一个单位时间，如为1则是每次都执行，2为第2次执行一次
        :param callback: 时机到时执行的函数
        :param priority: 优先级。函数从高优先级一直执行到低优先级直到完毕。显示函数应放在最低优先级
        :return: 无
        """
        for i in range(len(self.plan)):
            if self.plan[i][0]==priority:
                self.plan[i]+=[callback,frequency,0]
                return 0
        self.plan.append([priority,[callback,frequency,0]])
        def aa(item):return item[0]
        self.plan.sort(key=aa,reverse=True)
    def clock(self):
        for i in range(len(self.plan)):
            for ii in range(1,len(self.plan[i])):
                if self.plan[i][ii][2]+1==self.plan[i][ii][1]:
                    self.plan[i][ii][2]=0
                    self.plan[i][ii][0]()
                else:self.plan[i][ii][2]+=1
smart_planer=SmartPlan()
def create_block_texture(block_type:int):#没错，方块材质直接现画！
    block=Image.new("RGB",(100,100),"white")
    draw=ImageDraw.Draw(block)
    if block_type==1:draw.line([5,5,5,95,95,95,95,5,5,5],(0,255,0),10)
    pixels=block.load()
    all_pixels=[]
    for x in range(100):
        for y in range(100):all_pixels+=list(pixels[x,y])
    return bytes(all_pixels)
block_texture.append(create_block_texture(1))
@njit
def float2int(i):
    if i>=0:return math.floor(i)
    if i<0:return math.ceil(i)
    return 0
@njit
def flatten(blocks):
    temp={}#这里会根据blocks的类型自动推断，试过了手动指定，不过报错了
    for i,ii in blocks.items():
        for i1,ii1 in ii.items():temp[i1]=ii1
    return temp
#如果设置为加载全部区块，则进行一些操作
if load_all_save:
    for i in save_folder_files_list:
        temp=Dict.empty(key_type=UniTuple(int64,3),value_type=int64)
        for ii,iii in eval(file_buffer_reader.read(os.path.join(main_folder_dir,"saves",save_name,i))).items():temp[ii]=iii#有没有更好的办法直接转换为可以写入blocks的格式？求大佬赐教
        blocks[eval(i)]=temp
    del temp
    block_temp=flatten(blocks)
def unload_block(player_x:int,player_z:int):
    if load_all_save:return 0
    global blocks
    temp=find_block(player_x,player_z)
    temp1=float2int(buffer_block_size/2)
    for i,ii in blocks.items():
        if temp[0]-temp1<=i[0]<=temp[0]+temp1 or temp[1]-temp1<=i[1]<=temp[1]+temp1:
            file_buffer_reader.write(os.path.join(main_folder_dir,"saves",save_name,"("+str(i[0])+","+str(i[1])+")"),str(ii))
            del blocks[i]
    block_temp=flatten(blocks)
def load_block(player_x:int,player_z:int):
    if load_all_save:return 0
    global blocks,draw
    temp=find_block(player_x,player_z)
    temp1=float2int(buffer_block_size/2)
    for i in range(temp[0]-temp1,temp[0]+temp1+1):
        for ii in range(temp[1]-temp1,temp[1]+temp1+1):
            if (i,ii) not in blocks:
                temp2=Dict.empty(key_type=UniTuple(int64,3),value_type=int64)
                for iii,iiii in eval(file_buffer_reader.read(os.path.join(main_folder_dir,"saves",save_name,str((i,ii))))).items():temp2[iii]=iiii  #有没有更好的办法直接转换为可以写入blocks的格式？求大佬赐教
                blocks[eval(i)]=temp2
                draw=True
    block_temp=flatten(blocks)
@njit
def find_block(x:int,z:int):return float2int((x+block_size/2*int(x<0)*-2+1)/block_size),float2int((z+block_size/2*int(z<0)*-2+1)/block_size)
@njit
def read_block(x:int,y:int,z:int,block_temp:dict):
    """
    以下为基本原理：
    1.先计算输入坐标位于的区块位置
    2.读取区块文件，并将区块放入blocks(使用字典，格式:(0,0):{(0,0,0):1等})
    3.将blocks通过flatten()降维打击（雾）到block_temp,同样使用字典，全部为(0,0,0):1等，方便检索
    4.卸载区块时，直接从blocks中删除对应区块的索引，然后重新生成block_temp
    """
    #后记：为了改成numba我2022/3/5下午甚至反复翻了numba文档十几遍，关键是机翻很难看懂，感受到没文化的累了
    #这里说一下新手入门numba建议用jupyter反复调试，国内没有完整的教程，只能多看文档了，多看多调就能懂一点了
    try:return block_temp[(x,y,z)]
    except Exception:return 0
def write_block(x:int,y:int,z:int,block_ID:int):#为什么不用numba？因为还没有必要😀
    global block_temp,blocks,draw
    if block_ID==0:
        try:
            del blocks[find_block(x,z)][(x,y,z)]
            if len(blocks[find_block(x,z)])==0:del blocks[find_block(x,z)]
            block_temp=flatten(blocks)
        except Exception:return 0
    else:
        try:blocks[find_block(x,z)][(x,y,z)]=block_ID
        except Exception:
            temp=Dict.empty(key_type=UniTuple(int64,3),value_type=int64)
            temp[(x,y,z)]=block_ID
            blocks[find_block(x,z)]=temp
        block_temp=flatten(blocks)
    draw=True
draw=False
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
    global draw,block_VAO,block_VBO_buffer_len,texture_VBO,map
    if not draw:
        block_point_buffer=[]
        block_color_buffer=[]
        texture_coord=[]
        for y in range(lowest_y,highest_y+1):
            for x in range(sx-int((look_length-1)/2),sx+int((look_length-1)/2)+1):
                for z in range(sz-int((look_length-1)/2),sz+int((look_length-1)/2)+1):
                    by_wzq=read_block(x,y,z,block_temp)
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
        draw=True
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D,texture_VBO)
    glBindVertexArray(block_VAO)
    glColor3ub(255,255,255)
    glDrawArrays(GL_QUADS,0,block_VBO_buffer_len)
    glBindVertexArray(0)
class GetCharacterImage:
    def __init__(self,buffer=False):
        self.__bitmap=None
        self.bitmap=None
        self.size_buffer=None
        self.rows=None
        self.face=Face(font)
        self.load=False
        self.buffer=buffer
        if self.buffer:self.characters_buffer={}
    def get_size(self):
        if self.load:
            if self.buffer:return self.size_buffer
            return self.rows,self.__bitmap.width
        else:raise Exception("在创建字符前获取大小")
    def character2types(self,character,size,color,all_row,except_character=(",","，","。",".")):
        """
        :param character: 仅支持单个字符
        :param size: 大小
        :param color: 颜色
        :param all_row: 自动补齐高度，使文字在图像中间
        :param except_character: 不补行的字符元组
        :return: 可以被opengl读取的格式
        """

        if self.buffer and character+str(size) in self.characters_buffer:
            self.size_buffer=self.characters_buffer[character+"_size"]
            return self.characters_buffer[character+str(size)]
        self.face.set_char_size(size*64)
        self.face.load_char(character)
        self.__bitmap=self.face.glyph.bitmap
        bitmap_buffer=self.__bitmap.buffer
        self.load=True
        bitmap__temp=[]
        self.bitmap=[]
        temp=(self.__bitmap.rows,self.__bitmap.width)
        #补行
        if len(bitmap_buffer)<all_row*temp[1] and character not in except_character:
            self.rows=all_row
            #按照指定长度切割列表
            for i in range(temp[0]):bitmap__temp.append(list(bitmap_buffer[i*temp[1]:(i+1)*temp[1]]))
            up_rows=float2int((all_row-len(bitmap__temp))/2)
            down_rows=all_row-len(bitmap__temp)-up_rows
            for _ in range(up_rows):bitmap__temp.insert(0,list([0]*temp[1]))
            for _ in range(down_rows): bitmap__temp.append(list([0]*temp[1]))
            #合并列表
            debug=len(bitmap__temp)
            for _ in range(len(bitmap__temp)-1):
                bitmap__temp[0]+=bitmap__temp[1]
                bitmap__temp.pop(1)
            bitmap__temp=bitmap__temp[0]
        else:
            bitmap__temp=bitmap_buffer
            self.rows=self.__bitmap.rows
        for i in bitmap__temp:self.bitmap+=list(color)+[i]
        if self.buffer:
            self.characters_buffer[character+str(size)]=bytes(self.bitmap)
            self.characters_buffer[character+"_size"]=[self.rows,self.__bitmap.width]
            self.size_buffer=self.characters_buffer[character+"_size"]
            return self.characters_buffer[character+str(size)]
        return bytes(self.bitmap)
character_getter=GetCharacterImage()
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
    #我还没有学过三角函数，因此如果输入负数也能正常使用，以下代码可以更加简洁。请帮忙改一改哈😀
    px*=math.pi/180
    py*=math.pi/180
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
    load_block(float2int(player_x),float2int(player_z))
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
    i=mouse_hit_test(block_temp,player_see_x,player_see_y,player_x,player_y,player_z)
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
    #交换缓存，显示画面
    unload_block(float2int(player_x),float2int(player_z))
    glutSwapBuffers()
def spectator_mode(button):
    global player_x,player_y,player_z
    if button in [b'w',b's']:
        x,y,z=view_orientations(player_see_x,player_see_y)
        if button==b's':
            x*=-1
            y*=-1
            z*=-1
    else:
        x,y,z=view_orientations(player_see_x+90,player_see_y)
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
            write_block(int(command_split[1]),int(command_split[2]),int(command_split[3]),int(command_split[4]))
            draw=False
        if command_split[0]=="tp":
            global player_x,player_y,player_z
            player_x=float(command_split[1])
            player_y=float(command_split[2])
            player_z=float(command_split[3])
        if command_split[0]=="saves":
            for i,ii in blocks.items():file_buffer_reader.write(os.path.join(main_folder_dir,"saves",save_name,"("+str(i[0])+","+str(i[1])+")"),str(ii))
    chat_list=[input_buffer]+chat_list
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
    """
        简单阐述一下思路吧
        在网上看到一个分离轴算法，类似手电筒打影子的东西，不过如果要用在这里的话没法放置方块，
        不过曲线救国，我可以在检测到射线有交集的那个方块四周检测，检测到了就代表那个位置是能
        放置方块的了！

        至于如何处理这么多的方块，我个人的办法是以玩家头部为中心逐步扩大检测范围。当然还可以根据
        玩家头部的角度来减少范围，不过三角函数我一直没完全搞懂QAQ现在的player_see_x和y都是很
        将就的，可能还需要作者进一步学习吧
    """

def world_mouseclick(button,state,x,y):
    global mouse,draw
    if not mouse[2]:
        i=mouse_hit_test(block_temp,player_see_x,player_see_y,player_x,player_y,player_z)
        if i is not None:
            write_block(i[1][0],i[1][1],i[1][2],1)
            draw=False
    if not mouse[0]:
        i=mouse_hit_test(block_temp,player_see_x,player_see_y,player_x,player_y,player_z)
        if i is not None:
            write_block(i[0][0],i[0][1],i[0][2],0)
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
    smart_planer.clock()
    glutPostRedisplay()
def guide_button_event_init():
    global guide_buttons
    guide_buttons=[]
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
def init():
    #进行glut的最基础初始化
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE|GLUT_DEPTH|GLUT_RGBA)
    glutCreateWindow("PyMinecraft ByWzq".encode('GBK',errors="replace"))
    #使用户无法更改窗口大小
    hwnd=win32gui.GetForegroundWindow()
    A=win32gui.GetWindowLong(hwnd,win32con.GWL_STYLE)
    A^=win32con.WS_THICKFRAME
    win32gui.SetWindowLong(hwnd,win32con.GWL_STYLE,A)
    #完成其余的初始化
    glutReshapeWindow(window_height*2,window_width*2)
    glClearColor(0.0,174.0,238.0,238.0)
    smart_planer.add(1000,file_buffer_reader.save,1)
#可直接覆盖函数实现自己的功能
for i in os.listdir(os.path.join(main_folder_dir,"mods")):
    if i.split(".")[-2:]==["enable","py"]:
        with open(os.path.join(main_folder_dir,"mods",i)) as f: exec(f.read())
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
#代码破800行啦！
#我推送了88次代码！
