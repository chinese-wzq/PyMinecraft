<a href="https://996.icu"><img src="https://img.shields.io/badge/link-996.icu-red.svg" alt="996.icu" /></a>
<img src="https://img.shields.io/badge/高性能-基于PyOpenGL，而不是PyGame等游戏库-blue.svg" />

中文 | [Gitee English](https://gitee.com/chinese-wzq/PyMinecraft/blob/master/README_EN.md) | [Github English](https://github.com/chinese-wzq/PyMinecraft/blob/master/README_EN.md)
# python&Minecraft,所以叫做"PyMinecraft"
![](https://www.wumouren.xyz/wp-content/uploads/2022/01/pyminecraft.png)
******************************************************************************
<a href="https://info.flagcounter.com/zBbk"><img src="https://s05.flagcounter.com/map/zBbk/size_l/txt_000000/border_CCCCCC/pageviews_1/viewers_0/flags_0/" alt="Flag Counter" border="0"></a>
******************************************************************************
# 本项目仅支持Windows（其实只需要进行小小的移植，但是我懒）
******************************************************************************
# 如果您想鼓励我，给我点个免费的Star吧，实在不行提交几个Pull requests也行啊QAQ
##### 你不点Star,我不点Star,程序员明天就自杀
******************************************************************************
### 感谢OpenGL入门教程[写给 python 程序员的 OpenGL 教程](https://blog.csdn.net/xufive/article/details/86565130)
******************************************************************************
### 为什么会有这个项目？
##### 本来是想学习PyOpenGL,当时想到Minecraft也是用OpenGL渲染的，那么为什么我不能呢？于是，这样一个Python写的Mincraft就横空出世了。
******************************************************************************

# 使用教程：
>一、安装依赖库
>>本项目所需依赖库:
>>* PyOpenGL
>>>64位电脑不能使用`pip install PyOpenGL`直接安装，因为默认安装的是32位的，否则会出现错误：OpenGL.error.NullFunctionError: Attempt to call an undefined function”
>>>
>>>64位应该下载.whl文件安装，32位可直接使用 `pip install pyopengl` 安装
>>>
>>>对于64位电脑，你可以在https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl 下载对应的whl如“”PyOpenGL‑3.1.5‑cp310‑cp310‑win_amd64.whl“”后使用`pip install 你下载的whl文件`安装
>>* pywin32,freetype-py,numba,numpy,pillow
>>>你可以在命令行里运行"pip install pywin32 freetype-py numba numpy pillow"安装
>
>二、 运行主程序
>>运行"main.py"即可。
******************************************************************************
# 按键说明：
* ~键打开debug模式（包含坐标和坐标轴等）
******************************************************************************
# Github已更新"看板"，你可以在那里看到我将来和现在的计划。[空降地址🪂](https://github.com/chinese-wzq/PyMinecraft/projects/)
# 看完了想要贡献？看看这儿：[空降地址🪂](https://github.com/chinese-wzq/PyMinecraft/projects/6)
# 欢迎参与讨论[空降地址🪂](https://github.com/chinese-wzq/PyMinecraft/discussions)
# Github上不了？试试[dev-sidecar(开发者边车)](https://gitee.com/docmirror/dev-sidecar)
******************************************************************************
# 我在做什么?(实时更新):
## 添加GLFW
******************************************************************************
# 我们的愿景：（中文独占）
## 1. 给予服务器更多的权限，可以向客户端直接发送类python代码/图像/文本（直接发送python代码并执行有安全隐患，因此我将在客户端提供函数，发送的类python代码只能使用函数提供的功能，也可以给发送的python代码提供一个虚拟环境，防止越权），并直接由客户端执行，可以实现原版类似mod的功能
## 2. 客户端原生支持mod，但具体的mod框架需要他人开发，客户端只提供覆盖函数的功能。
## 3. 由于游戏开源，欢迎各位同仁一起给游戏添加新的内容与玩法！（注释注释！）
******************************************************************************
# 永远不要忘记Minecraft,那是只属于我们的世界。
