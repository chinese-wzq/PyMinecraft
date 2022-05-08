# -*- coding: utf-8 -*-

# Always believe,always hope.
import sys,math
from numba import njit
#导入字体点阵获取相关库
from freetype import Face

font="/usr/share/fonts/wenquanyi/wqy-zenhei/wqy-zenhei.ttc"    #显示文字时使用的字体,需完整路径

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
    def get_var(self,name):return self.total_var_dict[name] #不检查变量名,是为了防止访问一个不存在的变量还能正常运行
    def set_var(self,name,vaule):self.total_var_dict[name]=vaule

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
