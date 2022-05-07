# -*- coding: utf-8 -*-

# Always believe,always hope.

import os
from numba import njit
from numba.types import UniTuple,int64,DictType
from numba.typed import Dict
from main.useful_modules import float2int

#允许用户自定义的变量,已将大部分变量做好注释
load_all_save=True   #在启动时就加载所有的区块，并且不会执行卸载和加载的程序，可以减少程序卡顿，但在存档过大时需谨慎开启
main_folder_dir=os.path.join(".",".PyMinecraft")        #指定主目录位置(默认为.//PyMincraft)
save_name="example"         #指定存档名称(位于.//PyMinecraft//saves//下)

#用户不应该动的变量（当然放这里就代表有能耐你也能动）
save_folder_files_list=os.listdir(os.path.join(main_folder_dir,"saves",save_name))
blocks=Dict.empty(key_type=UniTuple(int64,2),value_type=DictType(UniTuple(int64,3),int64))
#新手入门numba备注：   ↑             ↑               ↑         ↑
#                键的类型    意为有两个int64项的元组 值的类型  意为：键是由3个int64项组成的元组，值是int64的字典
block_temp=Dict.empty(key_type=UniTuple(int64, 3), value_type=int64)
block_size=11   #必须为单数
buffer_block_size=15   #也必须为单数

total_var_manager=None

def init(total_var):
    global total_var_manager,block_temp
    total_var_manager=total_var
    # 如果设置为加载全部区块，则进行一些操作
    if load_all_save:
        for i in save_folder_files_list:
            temp = Dict.empty(key_type=UniTuple(int64, 3), value_type=int64)
            for ii, iii in eval(total_var_manager.get_var("file_buffer_manager").read(os.path.join(main_folder_dir,"saves",save_name,i))).items():temp[ii] = iii  # 有没有更好的办法直接转换为可以写入blocks的格式？求大佬赐教
            blocks[eval(i)] = temp
        del temp
        block_temp = flatten(blocks)
@njit
def flatten(blocks_list):
    temp={}#这里numba会根据blocks的类型自动推断，试过了手动指定，不过报错了
    for i,ii in blocks_list.items():
        for i1,ii1 in ii.items():temp[i1]=ii1
    return temp
def unload_block(player_x:int,player_z:int):
    if load_all_save:return
    global blocks,block_temp
    temp=find_block(player_x,player_z)
    temp1=float2int(buffer_block_size/2)
    for i,ii in blocks.items():
        if temp[0]-temp1<=i[0]<=temp[0]+temp1 or temp[1]-temp1<=i[1]<=temp[1]+temp1:
            total_var_manager.get_var("file_buffer_manager").write(os.path.join(main_folder_dir,"saves",save_name,"("+str(i[0])+","+str(i[1])+")"),str(ii))
            del blocks[i]
    block_temp=flatten(blocks)
def load_block(player_x:int,player_z:int):
    if load_all_save:return
    global blocks,block_temp
    temp=find_block(player_x,player_z)
    temp1=float2int(buffer_block_size/2)
    for i in range(temp[0]-temp1,temp[0]+temp1+1):
        for ii in range(temp[1]-temp1,temp[1]+temp1+1):
            if (i,ii) not in blocks:
                temp2=Dict.empty(key_type=UniTuple(int64,3),value_type=int64)
                for iii,iiii in eval(total_var_manager.get_var("file_buffer_manager").read(os.path.join(main_folder_dir,"saves",save_name,str((i,ii))))).items():temp2[iii]=iiii  #有没有更好的办法直接转换为可以写入blocks的格式？求大佬赐教                                               你居然这么闲......好吧，那就让你忙活一下！代码里埋了一些彩蛋，找找看？
                blocks[eval(i)]=temp2
                total_var_manager.set_var("draw",True)
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
def write_block(x:int,y:int,z:int,block_id:int):#为什么不用numba？因为还没有必要😀而且不好搞
    global block_temp,blocks
    if block_id==0:
        try:
            del blocks[find_block(x,z)][(x,y,z)]
            if len(blocks[find_block(x,z)])==0:del blocks[find_block(x,z)]
            block_temp=flatten(blocks)
        except Exception:return 0
    else:
        try:blocks[find_block(x,z)][(x,y,z)]=block_id
        except Exception:
            temp=Dict.empty(key_type=UniTuple(int64,3),value_type=int64)
            temp[(x,y,z)]=block_id
            blocks[find_block(x,z)]=temp
        block_temp=flatten(blocks)
    total_var_manager.set_var("draw",True)
