# 一个听写日语的好工具
只需要导入一段音频，就可以自动分句，并且语音识别
使用 `python` 语言, `tkinter` UI框架, `vosk` 语音识别

## 使用教程

1. 安装所需要的库
`pip install -r requirements.txt`

2. 去 `https://alphacephei.com/vosk/models` 下载 `vosk-model-ja-0.22` 模型 (`https://alphacephei.com/vosk/models/vosk-model-ja-0.22.zip`), 解压到项目根目录下, 例如:
```
study_japanese
|
|-------------vosk-model-ja-0.22
|             |
|             |-----------------am
|             |                 |...
|             |
|             |-----------------conf
|             |                 |...
|             |
|             |-----------------graph
|             |                 |...
|             |
|             |-----------------ivector
|             |                 |...
|             |
|             |-----------------README
|             |
|             |-----------------main.py
|             |
|             |-----------------practice.py
|             |
|             |-----------------requirements.txt
|             |
|             |...
```

3. 运行
`python main.py`

5. 自行探索

本项目提供了一个测试文件 `n2.mp3`
