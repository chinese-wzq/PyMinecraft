# coding=utf-8
# Always believe,always hope.

#导入numba.jit编译函数为机器码，需要牺牲python部分特性才可翻译
#记得通过pip安装numba，命令：pip install numba
from numba.extending import overload
#我真的憋不住了。我这里改了这么久就是为了试试numba，结果跑性能测试一看我去更慢。WDNMD我不搞了（不过上面一行的注释删掉可以体验一下）
@overload(open)
def read_block_jit(x:int,y:int,z:int,map:list):#此模块包装了读取方块的代码,未来可能也会把世界生成的代码放里边！
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
                            f=open(os.path.join(main_folder_dir,"saves",save_name,+str(a)+","+str(aa)),"w")
                            json.dump(map[i][ii][iii][iiii],f)
                            f.close()
                            map[i][ii][iii][iiii]=0
        try:
            if not map[temp3][temp4][temp5][temp6]:raise IndexError
        except IndexError:
            if str(block_X)+','+str(block_Z) in save_folder_files_list:
                a=open(os.path.join(main_folder_dir,"saves",save_name,str(block_X)+','+str(block_Z)))
                map=write_list(map,json.load(a),[temp3,temp4,temp5,temp6],[])
                a.close()
            else:
                return 0,map
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
    try:return map[temp3][temp4][temp5][temp6][y][float2int(x-center_block_x)][float2int(z-center_block_z)],map
    except IndexError:return 0,map
def read_block(x:int,y:int,z:int):
    #用于封装使用了jit的方块读取函数。
    #因为使用了jit，导致不能直接修改全局变量，故这里专门封装了一个函数实现保存修改后的map
    global map
    result,map=read_block_jit(x,y,z,map)
    return result
