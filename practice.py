import vosk
from pydub import AudioSegment
import json

model = vosk.Model("vosk-model-ja-0.22")  # 加载模型

AUDIO_PATH = ""
AUDIO = None
TOTAL_MS = 0
def split_audio_next(
    audio_path, current_offset=0, min_silence_len=2000, silence_thresh=-40, keep_silence=500, chunk_ms=200
):
    """
    从 current_offset 开始扫描音频，仅扫描到下一个符合条件的静默断点，
    返回当前句子的 AudioSegment 以及下一个句子起始的偏移位置。
    如果未找到断点，则返回剩余全部音频及总时长。
    """
    global AUDIO_PATH, AUDIO, TOTAL_MS
    if audio_path != AUDIO_PATH:
        audio = AudioSegment.from_file(audio_path)
        total_ms = len(audio)
        AUDIO_PATH = audio_path
        AUDIO = audio
        TOTAL_MS = total_ms
    index = current_offset
    run = 0
    break_point = None

    # 逐步扫描，找到第一个连续静默达到要求的点
    while index < TOTAL_MS:
        frame = AUDIO[index : index + chunk_ms]
        if frame.dBFS < silence_thresh:
            run += 1
        else:
            if run * chunk_ms >= min_silence_len:
                break_point = index - run * chunk_ms + (run * chunk_ms) // 2
                break
            run = 0
        index += chunk_ms

    if break_point is None:
        break_point = TOTAL_MS

    # 根据断点计算当前句子的开始和结束位置，并去除两端的静默
    seg_start = max(current_offset - keep_silence, 0)
    seg_end = min(break_point + keep_silence, TOTAL_MS)

    # 去除前端静默
    while seg_start < seg_end and AUDIO[seg_start : seg_start + 1].dBFS < silence_thresh:
        seg_start += 1
    # 去除后端静默
    while seg_start < seg_end and AUDIO[seg_end - 1 : seg_end].dBFS < silence_thresh:
        seg_end -= 1
    if (seg_end - seg_start) <= 1000:
        return split_audio_next(audio_path, break_point)
    segment = AUDIO[seg_start:seg_end]
    return segment, break_point

def recognize_audio_segments(segment):
    """
    对分割后的 AudioSegment 进行语音识别，返回识别后的文本
    """
    # Vosk 要求：单声道、16kHz
    audio = segment
    audio = audio.set_frame_rate(16000).set_channels(1)
    data = audio.raw_data
    recognizer = vosk.KaldiRecognizer(model, 16000)
    results = []
    recognizer.AcceptWaveform(data)
    result = recognizer.Result()
    results.append(result)
    texts = [json.loads(r).get("text", "") for r in results]
    return "".join(texts).replace(" ", "")
