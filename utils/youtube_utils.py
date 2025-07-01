from enum import Enum
from pathlib import Path
from typing import Any, Dict

class AudioCodec(str, Enum):
    mp3 = "mp3"
    acc = "acc"
    m4a = "m4a"
    flac = "flac"
    wav = "wav"
    opus = "opus"
    
class AudioQuality(str, Enum):
    q64 = "64"
    q128 = "128"
    q192 = "192"
    q256 = "256"
    q320 = "320"
    lossless = "0"

class VideoContainer(str, Enum):
    mp4  = "mp4"
    mkv  = "mkv"
    webm = "webm"
    mov  = "mov"

class VideoCodec(str, Enum):
    h264 = "h264"
    hevc = "hevc"
    vp9  = "vp9"
    av1  = "av1"


class YtOptsBuilder:
    """yt-dlp 옵션 설정 유틸리티 클래스"""
    def __init__(self):
        self._opts: Dict[str, Any] = {
            "noplaylist": True,
            "quiet": True
        }
        
    def with_extractor(self, extractor_name: str) -> 'YtOptsBuilder':
        self._opts.setdefault('extractor_args', {})[extractor_name] = []
        return self
    
    def outtmpl(self, template: str) -> "YtOptsBuilder":
        self._opts["outtmpl"] = str(template)
        return self
    
    def format(self, fmt: str) -> "YtOptsBuilder":
        self._opts["format"] = fmt
        return self
    
    def best_video_audio(self) -> "YtOptsBuilder":
        return self.format("bestvideo+bestaudio/best")
    
    def best_audio(self) -> "YtOptsBuilder":
        return self.format("bestaudio/best")
    
    def playlist(self, enable: bool = True) -> "YtOptsBuilder":
        self._opts["noplaylist"] = not enable
        return self
    
    def add_postprocessor(self, pp: dict) -> "YtOptsBuilder":
        self._opts.setdefault("postprocessor", []).append(pp)
    
    def merge_output(self, fmt: VideoContainer) -> "YtOptsBuilder":
        self._opts["merge_output_format"] = fmt.value
        return self
    
    def extract_audio(
        self, *, 
        codec: AudioCodec = AudioCodec.mp3, 
        quilty: AudioQuality = AudioQuality.q192
    ) -> "YtOptsBuilder":
        
        return self.add_postprocessor(
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": codec,
                "preferredquality": quilty
            }
        )
    
    def covert_video(
        self, *,
        container: VideoContainer = VideoContainer.mp4,
        vcodec: VideoCodec = VideoCodec.h264,
    ) -> "YtOptsBuilder":
        pp: Dict[str, Any] = {
            "key": "FFmpegVideoConvertor",
            "preferedformat": container,
            "vcodec": vcodec,
        }
        
        return self.add_postprocessor(pp)
        
    def build(self) -> Dict[str, Any]:
        return self._opts.copy()