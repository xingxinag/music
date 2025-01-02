"""
MusicPlugin - 多平台点歌插件
支持 QQ 音乐、网易云音乐、酷狗音乐的歌曲搜索功能。
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "支持 QQ 音乐、网易云音乐、酷狗音乐的多平台点歌插件"

from .music_plugin import MusicPlugin

# 可选：插件初始化方法
def load_plugin():
    return MusicPlugin()