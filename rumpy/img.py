from PIL import Image
import base64
import io


class Img:
    def decode(self, content: str) -> bytes:
        """把 rum trx 中的图片内容即 content （经过编码的图片字节流）解码为图片字节流"""
        content = base64.b64decode(bytes(content, encoding="utf-8"))
        return Image.open(io.BytesIO(content))

    def save(self, content: str, filepath: str) -> bytes:
        """把 rum trx 中的图片内容即 content （经过编码的图片字节流）解码后保存为本地文件"""
        return self.decode(content).save(filepath)
