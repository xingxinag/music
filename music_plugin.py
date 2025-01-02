import requests
import json
import os


class MusicPlugin:
    def __init__(self):
        try:
            self.config = self.load_config()
        except Exception as e:
            print(f"[MusicPlugin] Failed to load configuration: {e}")
            self.config = {}

    def load_config(self):
        """加载配置文件"""
        config_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError("Configuration file config.json not found")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def search_music(self, platform, keyword):
        """根据平台和关键词搜索音乐"""
        if platform == "qq":
            return self.search_qq_music(keyword)
        elif platform == "netease":
            return self.search_netease_music(keyword)
        elif platform == "kugou":
            return self.search_kugou_music(keyword)
        else:
            return {"error": True, "message": f"不支持的平台：{platform}"}

    def search_qq_music(self, keyword):
        """搜索 QQ 音乐"""
        try:
            api_url = self.config["qq_music"]["api_url"]
            params = {
                "ct": 24,
                "qqmusic_ver": 1298,
                "remoteplace": "txt.yqq.song",
                "searchid": "64404621762404874",
                "aggr": 1,
                "catZhida": 1,
                "lossless": 0,
                "sem": 1,
                "t": 0,
                "p": 1,
                "n": 1,
                "w": keyword,
                "platform": "yqq",
                "format": "json",
            }
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            if "data" not in data or "song" not in data["data"] or "list" not in data["data"]["song"]:
                return {"error": True, "message": "未找到相关歌曲，请尝试其他关键词。"}

            song = data["data"]["song"]["list"][0]
            return self.format_music_result(
                name=song["songname"],
                artist=song["singer"][0]["name"] if song.get("singer") else "未知歌手",
                url=f"https://i.y.qq.com/v8/playsong.html?songmid={song['songmid']}",
                cover=f"https://y.qq.com/music/photo_new/T002R300x300M000{song['albummid']}.jpg"
            )
        except Exception as e:
            return {"error": True, "message": f"QQ音乐搜索出错：{e}"}

    def search_netease_music(self, keyword):
        """搜索 网易云音乐"""
        try:
            api_url = self.config["netease_music"]["api_url"]
            params = {"s": keyword, "type": 1, "limit": 1}
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data.get("result") or not data["result"].get("songs"):
                return {"error": True, "message": "未找到相关歌曲，请尝试其他关键词。"}

            song = data["result"]["songs"][0]
            return self.format_music_result(
                name=song["name"],
                artist=", ".join([artist["name"] for artist in song.get("artists", [])]),
                url=f"https://music.163.com/#/song?id={song['id']}",
                cover=song["album"]["picUrl"]
            )
        except Exception as e:
            return {"error": True, "message": f"网易云音乐搜索出错：{e}"}

    def search_kugou_music(self, keyword):
        """搜索 酷狗音乐"""
        try:
            api_url = self.config["kugou_music"]["api_url"]
            params = {"keyword": keyword, "format": "json", "pagesize": 1}
            response = requests.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data.get("data") or not data["data"].get("info"):
                return {"error": True, "message": "未找到相关歌曲，请尝试其他关键词。"}

            song = data["data"]["info"][0]
            return self.format_music_result(
                name=song["songname_original"],
                artist=song["singername"],
                url=f"https://www.kugou.com/song/#hash={song['hash']}",
                cover=song["img"]
            )
        except Exception as e:
            return {"error": True, "message": f"酷狗音乐搜索出错：{e}"}

    def format_music_result(self, name, artist, url, cover):
        """格式化歌曲结果"""
        return {
            "error": False,
            "data": {
                "name": name,
                "artist": artist,
                "url": url,
                "cover": cover,
            }
        }

    def handle_request(self, platform, keyword):
        """处理点歌请求"""
        result = self.search_music(platform, keyword)
        if result["error"]:
            return f"❌ 错误：{result['message']}"
        song = result["data"]
        return f"🎵 歌曲：{song['name']} - {song['artist']}\n📎 链接：{song['url']}\n🖼️ 封面：{song['cover']}"


# 测试代码
if __name__ == "__main__":
    plugin = MusicPlugin()
    print(plugin.h