# MusicPlugin

**MusicPlugin** 是一个多平台点歌插件，支持通过关键词搜索 QQ 音乐、网易云音乐和酷狗音乐的歌曲信息，并返回歌曲名称、歌手、播放链接和封面。

---

## 功能特性

- 支持以下音乐平台：
  - **QQ 音乐**
  - **网易云音乐**
  - **酷狗音乐**
- 格式化返回结果，包括：
  - 歌曲名称
  - 歌手
  - 播放链接
  - 封面图片
- 通过简单的配置文件，灵活设置各平台的 API 地址。

---

## 文件结构
music_plugin/
├── __init__.py
# 插件初始化文件
├── music_plugin.py  
# 主插件文件
├── config.json.template  
# 配置模板
└── README.md              
# 插件使用说明文档

---

## 配置文件

1. **复制模板文件**：  
   将 `config.json.template` 复制为 `config.json`，并根据需求修改。

2. **配置内容**：
   ```json
   {
       "qq_music": {
           "api_url": "https://c.y.qq.com/soso/fcgi-bin/client_search_cp"
       },
       "netease_music": {
           "api_url": "https://music.163.com/api/search/get"
       },
       "kugou_music": {
           "api_url": "https://songsearch.kugou.com/song_search_v2"
       }
   }

## 测试

点歌 QQ 稻香  
点歌 网易云音乐 南山南  
点歌 酷狗 浪子回头

