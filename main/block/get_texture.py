# -*- coding: utf-8 -*-

# Always believe,always hope.

#导入方块贴图生成库
from PIL import Image
from PIL import ImageDraw

def create_block_texture(block_type:int):#没错，方块材质直接现画！
    block=Image.new("RGB",(100,100),"white")
    draw=ImageDraw.Draw(block)
    if block_type==1:draw.line([5,5,5,95,95,95,95,5,5,5],(0,255,0),10)
    pixels=block.load()
    all_pixels=[]
    for x in range(100):
        for y in range(100):all_pixels+=list(pixels[x,y])
    return bytes(all_pixels)