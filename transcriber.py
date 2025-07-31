import os
import whisper
from typing import Optional


class Transcriber:
    def __init__(self, model_name: str = "turbo", model_dir: str = "model"):
        """
        初始化语音转文字器
        参数:
            model_name: 要使用的 Whisper 模型名称，例如 "base", "small", "medium", "large"
            model_dir: 模型文件存储的目录
        """
        self.model_name = model_name
        self.model_dir = model_dir
        # 设置 ffmpeg 路径为项目下的 program 文件夹
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(current_dir, "program/ffmpeg/bin")
        os.environ['path']+=os.pathsep+ffmpeg_path
        # 确保模型目录存在
        os.makedirs(model_dir, exist_ok=True)
        # 限制 PyTorch 多线程
        os.environ["OMP_NUM_THREADS"] = "1"
        os.environ["MKL_NUM_THREADS"] = "1"
        # 加载模型
        self.model = whisper.load_model(model_name, download_root=model_dir)



    def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """
        将音频文件转换为文本
        参数:
            audio_path: 音频文件路径
            language: 音频语言代码（可选），如果不指定，模型会自动识别
        返回:
            转换后的文本
        """
        # 检查文件是否存在
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件 {audio_path} 不存在")

        # 使用 Whisper 模型进行转录
        result = self.model.transcribe(audio_path, language=language,fp16=False)

        # 返回转录的文本
        return result["text"]