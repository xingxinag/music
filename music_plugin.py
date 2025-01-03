import os
import json
import logging
import requests
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from plugins import Plugin, register

logger = logging.getLogger(__name__)

PLATFORMS = {
    "QQ": "qq",
    "网易云音乐": "netease",
    "酷狗": "kugou",
}

@register(
    name="MusicPlugin",
    desire_priority=10,
    desc="支持QQ音乐、网易云音乐和酷狗音乐的点歌插件",
    version="1.6",
    author="xingxing",
)
class MusicPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        logger.info("[MusicPlugin] 插件已初始化")
        
    def on_plugin_load(self):
        # 注册 #点歌 指令
        self.register_command("#点歌", self.get_help_text())

        # 注册 #help 指令
        self.register_command("#help", "输入 #help <插件名> 查看特定插件的使用说明，例如 #help MusicPlugin")

    def get_help_text(self, **kwargs):
        help_text = "使用格式：#点歌 [平台] [关键词]\n支持的平台：\n"
        for platform in PLATFORMS:
            help_text += f"- {platform}：例如 #点歌 {platform} 关键词\n"
        return help_text

    def load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if not os.path.exists(config_path):
            logger.error("[MusicPlugin] 配置文件 config.json 不存在，请检查")
            return {}
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def on_handle_context(self, e_context):
        """监听并处理上下文事件"""
        if e_context["context"].type != ContextType.TEXT:
            return

        # 检查触发条件
        content = e_context["context"].content.strip()
        matched_prefix = next((prefix for prefix in ["@xxx", "猫猫", "喵喵", "小猫猫",] if content.startswith(prefix)), None)

        if not matched_prefix:
            return

        # 移除前缀并解析命令
        content = content[len(matched_prefix):].strip()
        if not content.startswith("@xxx", "猫猫", "喵喵", "小猫猫"):
            return

        # 解析具体命令
        parts = content[1:].split(" ", 2)
        if len(parts) < 1:
            e_context["reply"] = self.reply_error("请输入具体的命令")
            return

        command = parts[0]
        if command == "#help":
            if len(parts) < 2:
                e_context["reply"] = self.reply_text("请指定要查看帮助的插件名，例如 #help MusicPlugin")
            elif parts[1] == "MusicPlugin":
                e_context["reply"] = self.reply_text(self.get_help_text())
            else:
                e_context["reply"] = self.reply_error(f"未知插件：{parts[1]}，请检查拼写")
            return

        if command != "#点歌":
            return

        if len(parts) < 3:
            e_context["reply"] = self.reply_error("格式错误，请按照 #点歌 [平台] [关键词] 的格式输入")
            return

        platform_name, keyword = parts[1], parts[2]
        platform = PLATFORMS.get(platform_name)
        if not platform:
            e_context["reply"] = self.reply_error(f"不支持的平台：{platform_name}，支持的平台有：{list(PLATFORMS.keys())}")
            return

        # 搜索音乐
        result = self.search_music(platform, keyword)
        e_context["reply"] = self.reply_music(platform_name, result)

    def search_music(self, platform, keyword):
        """根据平台搜索音乐"""
        search_func = getattr(self, f"search_{platform}_music", None)
        if not search_func:
            return {"error": True, "message": "不支持的平台"}
        
        return search_func(keyword)

    def search_qq_music(self, keyword):
        """搜索QQ音乐"""
        try:
            api_url = self.config.get("qq_music", {}).get("api_url", "")
            result = self.http_get(api_url, params={"w": keyword, "format": "json", "p": 1, "n": 1})
            data = result.json()
            
            if "data" not in data or "song" not in data["data"] or "list" not in data["data"]["song"]:
                return {"error": True, "message": "未找到相关歌曲，请尝试其他关键词"} 
            
            song = data["data"]["song"]["list"][0]
            return {
                "error": False,
                "data": {
                    "name": song["songname"],
                    "artist": song["singer"][0]["name"] if song.get("singer") else "未知歌手",
                    "url": f"https://y.qq.com/n/ryqq/songDetail/{song['songmid']}",
                    "image": f"https://y.qq.com/music/photo_new/T002R300x300M000{song['albummid']}.jpg",
                },
            }
        except requests.RequestException as e:
            logger.exception("[MusicPlugin] QQ音乐搜索请求异常")
            return {"error": True, "message": "QQ音乐搜索请求失败，请稍后重试"}
        except (KeyError, IndexError, json.JSONDecodeError) as e:  
            logger.exception("[MusicPlugin] QQ音乐搜索结果解析异常")
            return {"error": True, "message": "QQ音乐搜索结果解析失败，请联系管理员"}
        except Exception as e:
            logger.exception("[MusicPlugin] QQ音乐搜索未知异常")
            return {"error": True, "message": "QQ音乐搜索出错，请联系管理员"}
            
    def search_netease_music(self, keyword):
        """搜索网易云音乐"""
        try:
            api_url = self.config.get("netease_music", {}).get("api_url", "")
            result = self.http_get(api_url, params={"keywords": keyword, "limit": 1})
            data = result.json()

            if data["code"] != 200 or not data["result"]["songs"]:
                return {"error": True, "message": "未找到相关歌曲，请尝试其他关键词"}

            song = data["result"]["songs"][0]
            return {
                "error": False,
                "data": {
                    "name": song["name"],
                    "artist": song["artists"][0]["name"],
                    "url": f"https://music.163.com/#/song?id={song['id']}",
                    "image": song["artists"][0]["img1v1Url"],
                },
            }
        except requests.RequestException as e:
            logger.exception("[MusicPlugin] 网易云音乐搜索请求异常")
            return {"error": True, "message": "网易云音乐搜索请求失败，请稍后重试"}
        except (KeyError, IndexError, json.JSONDecodeError) as e:  
            logger.exception("[MusicPlugin] 网易云音乐搜索结果解析异常")
            return {"error": True, "message": "网易云音乐搜索结果解析失败，请联系管理员"}
        except Exception as e:
            logger.exception("[MusicPlugin] 网易云音乐搜索未知异常")
            return {"error": True, "message": "网易云音乐搜索出错，请联系管理员"}

    def search_kugou_music(self, keyword):
        """搜索酷狗音乐"""
        try:
            api_url = self.config.get("kugou_music", {}).get("api_url", "")
            result = self.http_get(api_url, params={"keyword": keyword, "pagesize": 1})
            data = result.json()

            if data["status"] != 1 or not data["data"]["info"]:
                return {"error": True, "message": "未找到相关歌曲，请尝试其他关键词"}

            song = data["data"]["info"][0]
            return {
                "error": False,
                "data": {
                    "name": song["songname"],
                    "artist": song["singername"],
                    "url": f"https://www.kugou.com/song/#hash={song['hash']}&album_id={song['album_id']}",
                    "image": "",
                },
            }
        except requests.RequestException as e:
            logger.exception("[MusicPlugin] 酷狗音乐搜索请求异常")
            return {"error": True, "message": "酷狗音乐搜索请求失败，请稍后重试"}
        except (KeyError, IndexError, json.JSONDecodeError) as e:  
            logger.exception("[MusicPlugin] 酷狗音乐搜索结果解析异常")
            return {"error": True, "message": "酷狗音乐搜索结果解析失败，请联系管理员"}
        except Exception as e:  
            logger.exception("[MusicPlugin] 酷狗音乐搜索未知异常")
            return {"error": True, "message": "酷狗音乐搜索出错，请联系管理员"}
                
    @staticmethod  
    def http_get(url, params=None, **kwargs):
        """发送GET请求"""
        try:
            response = requests.get(url, params=params, **kwargs)
            response.raise_for_status() 
            return response
        except requests.RequestException as e:
            logger.exception(f"[MusicPlugin] GET请求异常：{url}")
            raise
        
    @staticmethod
    def reply_text(text):
        """纯文本回复"""
        reply = Reply()
        reply.type = ReplyType.TEXT
        reply.content = text
        return reply

    @staticmethod
    def reply_error(message):
        """错误回复"""
        reply = Reply()
        reply.type = ReplyType.ERROR
        reply.content = message
        return reply

    @staticmethod  
    def reply_music(platform_name, music_data):
        """音乐回复"""
        if music_data["error"]:
            return MusicPlugin.reply_error(music_data["message"])

        song = music_data["data"]
        reply = Reply()
        reply.type = ReplyType.MUSIC
        reply.content = {
            "platform": platform_name,
            "name": song["name"],
            "artist": song["artist"],
            "url": song["url"],
            "image": song["image"],
        }
        return reply
