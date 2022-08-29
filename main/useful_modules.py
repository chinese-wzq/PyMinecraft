# -*- coding: utf-8 -*-

# Always believe,always hope.
import sys,math,freetype,os,PIL.Image,numpy

from numba import njit
from OpenGL.GL import *
from io import BytesIO
from PIL import Image

@njit
def float2int(i):
    if i>=0:return math.floor(i)
    if i<0:return math.ceil(i)
    return 0
class FileBufferManager:
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
class SmartPlanManager:#之后可能会全部使用这个东东来对世界事件进行合理的调控
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
                self.plan[i].append([callback,frequency,0])
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
class TotalVarManager:
    def __init__(self, init_var_dict=None):
        if init_var_dict is None:
            init_var_dict = {}
        self.total_var_dict=init_var_dict
    def get_var(self,name):return self.total_var_dict[name] #不检查变量名,是为了防止访问一个不存在的变量还能正常运行，这样可以直接让python抛出异常
    def set_var(self,name,vaule):self.total_var_dict[name]=vaule

class Character:
    def __init__(self,font,buffer=False):
        self.face=freetype.Face(font)
        self.buffer=buffer
        self.characters_buffer={}
    def get_character(self,character,size,color):
        if self.buffer and character+str(size) in self.characters_buffer:return self.characters_buffer[character+str(size)]
        #self.face.set_char_size(size*64)
        self.face.set_pixel_sizes(size,0)
        self.face.load_char(character)
        #进行颜色的填充
        bitmap=list()
        for i in self.face.glyph.bitmap.buffer:bitmap+=list(color)+[i]
        self.characters_buffer[character+str(size)]=bytes(bitmap),self.face.glyph.get_glyph().get_cbox(freetype.FT_GLYPH_BBOX_TRUNCATE),self.face.glyph.advance.x/64
        return self.characters_buffer[character+str(size)]
    def clean_up(self):del self.face
class PrintText:
    def __init__(self,font,buffer=True):#font必须是一个文件流
        self.texture_buffer={}
        self.character=Character(font)
        self.buffer=buffer
    @staticmethod
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
        else:raise ValueError("PrintText：未知的direction参数内容！")
        if parameter[:3]==(1,1,0):
            glVertex3f(x+dx*parameter[4],y+(dy+size[1])*parameter[3],z)
            glTexCoord2f(texcoord[0],texcoord[1])
            glVertex3f(x+(dx+size[0])*parameter[4],y+(dy+size[1])*parameter[3],z)
            glTexCoord2f(texcoord[2],texcoord[3])
            glVertex3f(x+(dx+size[0])*parameter[4],y+dy*parameter[3],z)
            glTexCoord2f(texcoord[4],texcoord[5])
            glVertex3f(x+dx*parameter[4],y+dy*parameter[3],z)
            glTexCoord2f(texcoord[6],texcoord[7])
        elif parameter[:3]==(0,1,1):
            glVertex3f(x,y+dx*parameter[4],z+(dy+size[1])*parameter[3])
            glTexCoord2f(texcoord[0],texcoord[1])
            glVertex3f(x,y+(dx+size[0])*parameter[4],z+(dy+size[1])*parameter[3])
            glTexCoord2f(texcoord[2],texcoord[3])
            glVertex3f(x,y+(dx+size[0])*parameter[4],z+dy*parameter[3])
            glTexCoord2f(texcoord[4],texcoord[5])
            glVertex3f(x,y+dx*parameter[4],z+dy*parameter[3])
            glTexCoord2f(texcoord[6],texcoord[7])
        elif parameter[:3]==(1,0,1):
            glVertex3f(x+(dy+size[1])*parameter[3],y,z+dx*parameter[4])
            glTexCoord2f(texcoord[0],texcoord[1])
            glVertex3f(x+(dy+size[1])*parameter[3],y,z+(dx+size[0])*parameter[4])
            glTexCoord2f(texcoord[2],texcoord[3])
            glVertex3f(x+dy*parameter[3],y,z+(dx+size[0])*parameter[4])
            glTexCoord2f(texcoord[4],texcoord[5])
            glVertex3f(x+dy*parameter[3],y,z+dx*parameter[4])
            glTexCoord2f(texcoord[6],texcoord[7])
        else:raise ValueError("PrintText：未知的parameter参数内容！")
    def _print_text_center(self,text:str,left_x,left_y,left_z,right_x,right_y,right_z,color=(0,0,0),size=24,spacing=0,direction="up",parameter:tuple=(1,1,0,1,1),enter_width=0,m=1):#left均指左下，right均指右上
        #这是居中显示文字的基础实现，需要更高级的API方便显示，要不然每一次都要计算
        #------------------目前还不公开使用，可能会有未知的结果------------------------
        pen_dx,pen_baseline_y=self.print_text_list(text=list(text), x=left_x, y=left_y, z=left_z, color=color, size=size, spacing=spacing, parameter=parameter,display=False)#获取pen_dx
        if parameter[:-2]==(1,1,0) and left_z==right_z:x,y,z=(right_x-left_x-pen_dx)/2+left_x,pen_baseline_y,left_z
        self.print_text_list(text=list(text), x=x, y=y, z=z, color=color, size=size, spacing=spacing, direction=direction, parameter=parameter, enter_width=enter_width, m=m,display=True)
    def print_text_list(self, text:list, x=0, y=0, z=0, color=(0,0,0), size=24,small_height=None,spacing=0,direction="up",parameter:tuple=(1,1,0,1,1),enter_width=0,m=1,display=True):
        #采用freetype+texture方案，更高可塑性，字体更好看！
        #这里是重写版，因为原来那个已经不能适应新的需求了（其实就是时间长了自己忘了思路了，改不动）

        #进行一些对OpenGL的准备
        if display:
            glEnable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        #设置假想的一个画笔位置
        pen_dx=0
        #设置假想的基线位置，因为有字符的底线会小于基线
        pen_baseline_y=0
        #设置变量用来存储每次打印字符最低的底线，用来设置基线，防止重合
        yMin=0
        #开始打印～
        for text_for in range(len(text)):
            for character in text[text_for]:
                if self.buffer and character+str(size)+str(color) in self.texture_buffer:#尝试命中缓存
                    if display:glBindTexture(GL_TEXTURE_2D, self.texture_buffer[character + str(size) + str(color)])
                    character_cbox=self.texture_buffer[character+str(size)+str(color)+"info"][0]
                    character_advance_x=self.texture_buffer[character+str(size)+str(color)+"info"][1]
                    character_size=character_cbox.xMax-character_cbox.xMin,character_cbox.yMax-character_cbox.yMin
                else:#命不中，读取字体文件
                    texture=glGenTextures(1)
                    glBindTexture(GL_TEXTURE_2D,texture)
                    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
                    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
                    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
                    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
                    temp=self.character.get_character(character,size,color)
                    character_types=temp[0]
                    character_cbox=temp[1]
                    character_advance_x=temp[2]
                    character_size=character_cbox.xMax-character_cbox.xMin,character_cbox.yMax-character_cbox.yMin
                    glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,character_size[0],character_size[1],0,GL_RGBA,GL_UNSIGNED_BYTE,character_types)
                    glGenerateMipmap(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D,0)
                    if display:glBindTexture(GL_TEXTURE_2D, texture)
                    if self.buffer:
                        self.texture_buffer[character+str(size)+str(color)]=texture
                        self.texture_buffer[character+str(size)+str(color)+"info"]=character_cbox,character_advance_x
                if display:
                    glBegin(GL_QUADS)
                    PrintText.default_2d(character_size,x,y,z,pen_dx,pen_baseline_y+character_cbox.yMin,direction,parameter)#为什么用函数引出来？因为工程量实在太大，够单独开一个函数讲解了
                    glEnd()
                    glBindTexture(GL_TEXTURE_2D,0)
                pen_dx+=character_advance_x+spacing
                if character_cbox.yMin<yMin:yMin=character_cbox.yMin
            if enter_width==0 and text_for!=len(text)-1:pen_baseline_y-=(self.get_text_yMax(text[text_for+1],size,color)-yMin)*m
            else:pen_baseline_y-=enter_width*m
            if not display:
                return pen_dx,pen_baseline_y
            pen_dx=0
        if display:
            glDisable(GL_BLEND)
            glDisable(GL_TEXTURE_2D)
    def get_text_yMax(self,text,size,color):#获取的同时顺便缓存字符
        yMax=0
        for character in text:
            if self.buffer and character+str(size)+str(color) in self.texture_buffer:
                if self.texture_buffer[character+str(size)+str(color)+"info"][0].yMax>yMax:yMax=self.texture_buffer[character+str(size)+str(color)+"info"][0].yMax
                continue
            if self.buffer:
                texture=glGenTextures(1)
                glBindTexture(GL_TEXTURE_2D,texture)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_REPEAT)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
            temp=self.character.get_character(character,size,color)
            character_cbox=temp[1]
            if self.buffer:
                character_types=temp[0]
                character_advance_x=temp[2]
                character_size=character_cbox.xMax-character_cbox.xMin,character_cbox.yMax-character_cbox.yMin
                glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,character_size[0],character_size[1],0,GL_RGBA,GL_UNSIGNED_BYTE,character_types)
                glGenerateMipmap(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D,0)
                self.texture_buffer[character+str(size)+str(color)]=texture
                self.texture_buffer[character+str(size)+str(color)+"info"]=character_cbox,character_advance_x
            if self.texture_buffer[character+str(size)+str(color)+"info"][0].yMax>yMax:yMax=self.texture_buffer[character+str(size)+str(color)+"info"][0].yMax
        return yMax
def list_merge(list_):#可以把如[['XYZ:', 0.0, ',', 0.0, ',', 0.0], ['EYE:', 0, ',', 0]]这样的列表合并成['XYZ:0.0,0.0,0.0', 'EYE:0,0']
    real_list=[]
    for i in range(len(list_)):
        real_list.append('')
        for ii in list_[i]:real_list[i]=real_list[i]+str(ii)
    return real_list
def read_resources_from_disk():
    #将需要的资源读入内存并使用BytesIO模拟文件流
    #而且，还会顺带把方块材质提前准备成纹理VBO
    wating_icon=["main/resources/icon","PyMinecraft_48x48.ico","PyMinecraft_32x32.ico","PyMinecraft_16x16.ico"]
    wating_fonts=["main/resources/fonts","文鼎PL中楷体.ttf"]

    resources={"icon":[],"blocks_texture":[],"fonts":{},"cross_pointer":None}
    for i in range(1,len(wating_icon)):#读取图标
        with open(os.path.join(wating_icon[0],wating_icon[i]),"rb") as f:resources["icon"].append(Image.open(BytesIO(f.read())))

    for i in range(1,len(wating_fonts)):
        with open(os.path.join(wating_fonts[0],wating_fonts[i]),"rb") as f:resources["fonts"][wating_fonts[i]]=BytesIO(f.read())
    return resources
def read_opengl_resources_from_disk():#需要在opengl全部初始化完后才能生成
    wating_blocks_texture=["main/resources/blocks_texture",#索引依次对应方块的上下左右前后
        [["1_grass_around.png","1_grass_down.png","1_grass_up.png"],[2,1,0,0,0,0]]
    ]
    resources=[]

    texture_EBO=glGenBuffers(1)#提前把基本完全相同的texture_coord准备成VBO
    glBindBuffer(GL_ARRAY_BUFFER,texture_EBO)
    a=numpy.array([1.0,1.0,
                   0.0,1.0,
                   0.0,0.0,
                   1.0,0.0],dtype='float32')
    glBufferData(GL_ARRAY_BUFFER,sys.getsizeof(a),a,GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER,0)
    resources.append(texture_EBO)

    for i in range(1,len(wating_blocks_texture)):#读取方块材质
        resources.append([])
        texture_VBO=glGenTextures(len(wating_blocks_texture[i][0]))
        for ii in range(len(wating_blocks_texture[i][0])):
            with open(os.path.join(wating_blocks_texture[0],wating_blocks_texture[i][0][ii]),"rb") as f:
                image=PIL.Image.open(f)#对图片进行转换成opengl支持的格式
                pixels=image.load()
                all_pixels=[]
                for x in range(image.size[0]):
                    for y in range(image.size[1]):
                        all_pixels+=list(pixels[x,y])
                #创建纹理VBO
                glBindTexture(GL_TEXTURE_2D,texture_VBO[ii])
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,GL_CLAMP_TO_EDGE)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,GL_CLAMP_TO_EDGE)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
                glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
                glTexImage2D(GL_TEXTURE_2D,0,GL_RGB,64,64,0,GL_RGBA,GL_UNSIGNED_BYTE,bytes(all_pixels))
                glGenerateMipmap(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D,0)
        resources[i]=[texture_VBO,wating_blocks_texture[i][1]]

    cross_pointer=glGenLists(1)#生成鼠标指针显示列表
    glNewList(cross_pointer,GL_COMPILE)
    glLineWidth(2)
    glBegin(GL_LINES)
    glColor3ub(232, 232, 232)
    glVertex2f(400, 425)
    glVertex2f(400, 375)
    glVertex2f(425, 400)
    glVertex2f(375, 400)
    glEnd()
    glEndList()

    return [resources,cross_pointer]