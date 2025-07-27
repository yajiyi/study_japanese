import pyaudio
import json
from vosk import Model, KaldiRecognizer

# 加载模型
model = Model("vosk-model-ja-0.22")

# 创建麦克风对象
micro = pyaudio.PyAudio()

# 配置麦克风参数
receiver = micro.open(
    format=pyaudio.paInt16,  # 16位深度音频数据
    channels=1,  # 单声道
    rate=16000,  # 采样率16000Hz
    input=True,  # 从麦克风获取数据
    frames_per_buffer=4000,
)  # 每次读取数据块大小为4000帧

# 创建识别器
recognize = KaldiRecognizer(model, 16000)

print("开始识别！")

while True:
    # 每次读取4000帧数据
    frame = receiver.read(4000)
    # 若识别到数据
    if recognize.AcceptWaveform(frame):
        trans = recognize.Result()
        result = json.loads(trans)["text"].replace(" ", "")
        print(result)
