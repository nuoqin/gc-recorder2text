## GC录音工具


### 👉🏻 GC录音工具 👈🏻
GC录音工具是一个运行在笔记本电脑上的应用程序，最初的设计初衷是为了在开会时进行录音记录。
它能够帮助用户完整保存会议过程中的交流内容，从而在会后回顾时避免遗漏重要的信息或遗忘关键内容。

### 🖥️ 项目工程介绍
项目是基于pyaudio+openai-whisper+tkinter

pyaudio（recording.py）实现录音开始、暂停、回复、结束功能。
openai-whisper(transcriber.py)实现录音结束后生成的output.wav文件转文本内容。
tkinter（recorderApp.py） 实现一个桌面可视化的程序。

#### 项目工程目录
```
-- gc-recorder2text
---- model              #存放openai-whisper模型的路径 系统首次启动会自动下载，默认是turbo
---- output             #存放录音文件、录音文本
---- program            #存放ffmpeg程序
---- app.py             #项目启动器
---- recorderApp.py
---- recording.py
---- transcriber.py
```

### 📣 项目启动

```java
conda create -n gc-s2t python=3.10
conda activate gc-s2t

pip install -r requirements.txt

python app.py

```

