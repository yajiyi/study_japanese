import tkinter as tk
from tkinter import filedialog, ttk  # 添加 ttk
import practice
import pyaudio
import threading
import time
import math

def choose_file(event):
    file_path = filedialog.askopenfilename(
        filetypes=[("Audio Files", "*.mp3 *.wav *.flac *.m4a")]
    )  # 打开文件对话框，选择音频文件
    if file_path:
        path_input.delete(0, tk.END)
        path_input.insert(0, file_path)

def make_chunks(audio_segment, chunk_length):
    """
    Breaks an AudioSegment into chunks that are <chunk_length> milliseconds
    long.
    if chunk_length is 50 then you'll get a list of 50 millisecond long audio
    segments back (except the last one, which can be shorter)
    """
    number_of_chunks = math.ceil(len(audio_segment) / float(chunk_length))
    return [audio_segment[i * chunk_length:(i + 1) * chunk_length]
            for i in range(int(number_of_chunks))]

playing = False  # 播放音频状态
player_threads = []  # 用于存储播放线程
def _play_with_pyaudio(seg, play_button):

    # Just in case there were any exceptions/interrupts, we release the resource
    # So as not to raise OSError: Device Unavailable should play() be used again
    def worker(seg, play_button):
        global playing, repeat_var, current_sentence_index
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(seg.sample_width),
                        channels=seg.channels,
                        rate=seg.frame_rate,
                        output=True)
        playing = True  # 设置播放状态为 True
        while playing:  # 如果播放状态为 True，则继续播放
            try:
                # break audio into half-second chunks (to allows keyboard interrupts)
                for chunk in make_chunks(seg, 500):
                    stream.write(chunk._data)
                    if not playing:  # 如果播放状态为 False，则停止播放
                        break  # 跳出循环

            finally:
                if not playing: # 如果播放状态为 False，则停止播放
                    break  # 跳出循环
                if repeat_var.get() == 0:  # 如果未选择重复播放
                    break  # 跳出循环
                else:
                    time.sleep(2)  # 等待2秒后继续播放
        stream.stop_stream()
        stream.close()
        p.terminate()
        playing = False  # 设置播放状态为 False
    player_threads.append(threading.Thread(target=worker, args=(seg, play_button)))
    player_threads[-1].start()  # 启动播放线程

def play_audio(segment, play_button):
    global playing

    playing = True  # 设置播放状态为 True
    _play_with_pyaudio(segment, play_button)  # 使用 pyaudio 播放音频

current_sentence_index = 0  # 当前句子索引
def start_practice(event):
    path = path_input.get()  # 获取输入框中的音频文件路径

    def show_sentence(i, start_offset):
        global repeat_var, current_sentence_index
        current_sentence_index = i  # 更新当前句子索引
        
        def submit_text(event):
            # 获取输入框中的文本
            answer_label.config(text=sentence_text)  # 显示用户输入的文本

        def next_sentence(event):
            global playing
            text_input.destroy()  # 销毁输入框
            submit_button.destroy()  # 销毁提交按钮
            answer_label.destroy()  # 销毁答案标签
            repeat_checkbox.destroy()  # 销毁重复播放选择框
            play_button.destroy()  # 销毁播放按钮
            next_button.destroy()  # 销毁下一个按钮
            playing = False
            for thread in player_threads:
                thread.join()
            player_threads.clear()
            show_sentence(i + 1, break_point)  # 显示下一个分割的音频段

        def play(event=None):
            global playing
            if play_button.config("text")[-1] == "开始播放":
                play_button.config(text="停止播放")
                play_audio(sentence_segment, play_button)
            else:
                playing = False
                play_button.config(text="开始播放")


        sentence_segment, break_point = practice.split_audio_next(path, start_offset)  # 获取当前分割的音频段
        # 对每个分割后的音频段进行识别
        sentence_text = practice.recognize_audio_segments(sentence_segment)

        # 创建输入框
        text_input = ttk.Entry(root, width=50)
        text_input.place(x=10, y=100, width=400, height=25)

        # 创建提交按钮
        submit_button = ttk.Button(root, text="提交")
        submit_button.place(x=420, y=100, width=60, height=25)
        submit_button.bind("<ButtonRelease>", submit_text)

        # 创建播放按钮
        play_button = ttk.Button(root, text="开始播放")
        play_button.place(x=10, y=160, width=100, height=25)
        play_button.bind("<ButtonRelease>", play)

        # 创建重复播放选择框
        repeat_checkbox = ttk.Checkbutton(root, text="重复播放", variable=repeat_var)
        repeat_checkbox.place(x=80, y=160, width=100, height=25)

        # 创建标签显示正确答案
        answer_label = ttk.Label(root)
        answer_label.place(x=10, y=130, width=400, height=25)

        # 创建下一个按钮
        next_button = ttk.Button(root, text="下一个")
        next_button.place(x=420, y=130, width=60, height=25)
        next_button.bind("<ButtonRelease>", next_sentence)  # 清除输入框和标签

        play()

    show_sentence(0, 0)  # 显示第一个分割的音频段


# 创建主窗口
root = tk.Tk()
root.geometry("500x400")

repeat_var = tk.IntVar(value=0)

# 创建输入框，改用 ttk.Entry 并指定父容器
path_input = ttk.Entry(root, width=50)  # 创建音频文件路径输入框
path_input.place(x=10, y=10, width=400, height=25)

# 创建选择音频文件按钮，改用 ttk.Button 并指定父容器
path_choose_button = ttk.Button(root, text="...")  # 创建选择音频文件按钮
path_choose_button.place(x=420, y=10, width=25, height=25)
path_choose_button.bind("<ButtonRelease>", choose_file)  # 绑定按钮左键松开事件

# 创建开始练习按钮，改用 ttk.Button 并指定父容器
start_practice_button = ttk.Button(root, text="开始练习")  # 创建开始练习按钮
start_practice_button.place(x=10, y=50, width=100, height=25)
start_practice_button.bind("<ButtonRelease>", start_practice)  # 绑定按钮左键松开事件


root.mainloop()
