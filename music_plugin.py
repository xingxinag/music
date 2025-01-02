import requests
import os
import json
import logging
from plugins import Plugin, register
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from bridge.bridge import EventAction, EventContext

logger = logging.getLogger(__name__)


@register(
    name="MusicPlugin",
    desire_priority=10,
    desc="支持QQ音乐、网易云音乐和酷狗音乐的点歌插件",
    version="1.0",
    author="Your Name",
)
class MusicPlugin(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[EventContext.ON_HANDLE_CONTEXT] = self.handle_request
        self.config = self.load_config()
        logger.info("[MusicPlugin] 插件已初始化")

    def load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if not os.path.exists(config_path):
            logger.error("[MusicPlugin] 配置文件 config.json 不存在，请检查")
            return {}
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def handle_request(self, e_context: EventContext):
        """处理点歌指令"""
        context = e_context["context"]
        if context.type != ContextType.TEXT:
            return

        content = context.content.strip()
        if not content.startswith("点歌 "):
            return

        # 解析指令
        parts = content.split(" ", 2)
        if len(parts) < 3:
            reply = Reply(ReplyType.ERROR, "❌ 格式错误，请使用：点歌 [平台] [关键词]")
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return

        platform_name, keyword = parts[1], parts[2]
        platform_map = {
            "QQ": "qq",
            "网易云音乐": "netease",
            "酷狗": "kugou",
        }
        platform = platform_map.get(platform_name)
        if not platform:
            reply = Reply(ReplyType.ERROR, f"❌ 不支持的平台：{platform_name}，支持的平台有：QQ、网易云音乐、酷狗")
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return

        # 调用搜索功能
        result = self.search_music(platform, keyword)
        if result["error"]:
            reply = Reply(ReplyType.ERROR, f"❌ 错误：{result['message']}")
        else:
            song = result["data"]
            reply = Reply(ReplyType.INFO, f"🎵 歌曲：{song['name']} - {song['artist']}\n📎 链接：{song['url']}\n🖼️ 封面：{song['cover']}")
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS

    def search_music(self, platform, keyword):
        """根据平台搜索音乐"""
        if platform == "qq":
            return self.search_qq_music(keyword)
        elif platform == "netease":
            return self.search_netease_music(keyword)
        elif platform == "kugou":
            return self.search_kugou_music(keyword)
        else:
            return {"error": True, "message": "不支持的平台"}

    def search_qq_music(self, keyword):
        """搜索 QQ 音乐"""
        try:
            api_url = self.config.get("qq_music", {}).get("api_url", "")
            params = {"w": keyword, "format": "json", "p": 1, "n": 1}
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()
            song = data["data"]["song"]["list"][0]
            return {
                "error": False,
                "data": {
                    "name": song["songname"],
                    "artist": song["singer"][0]["name"],
                    "url": f"https://y.qq.com/n/ryqq/songDetail/{song['songmid']}",
                    "cover": f"https://y.qq.com/music/photo_new/T002R300x300M000{song['albummid']}.jpg",
                },
            }
        except Exception as e:
            logger.error(f"[MusicPlugin] QQ音乐搜索出错：{e}")
            return {"error": True, "message": "QQ音乐搜索失败"}

    def search_netease_music(self, keyword):
        """搜索 网易云音乐"""
        # 此处补充网易云音乐搜索逻辑
        return {"error": True, "message": "未实现"}

    def search_kugou_music(self, keyword):
        """搜索 酷狗音乐"""
        # 此处补充酷狗音乐搜索逻辑
        return {"error": True, "message": "未实现"}