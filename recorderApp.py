import gc
import os.path
import threading
import tkinter as tk
from tkinter import ttk, messagebox


from recording import SoundRecording
from transcriber import Transcriber




class RecorderApp:
    def __init__(self, root):
        # 定义一个线程
        self._thread = None
        self.recorder = SoundRecording()
        self.root = root
        #设置标题
        self.root.title("GC录音器")
        #设置样式
        self.style = ttk.Style()
        self.root.configure(bg="#f5f5f5")

        self._configure_style()

        self.status_label = ttk.Label(root, text="未开始", font=("微软雅黑", 12), foreground="#333")
        self.status_label.pack(pady=(20, 10))

        self.start_btn = ttk.Button(root, text="开始录音", command=self.start_recording, style="TButton")
        self.start_btn.pack(pady=5)

        self.pause_btn = ttk.Button(root, text="暂停录音",  command=self.pause_recording, style="TButton")
        self.pause_btn.pack(pady=5)

        self.resume_btn = ttk.Button(root, text="继续录音", command=self.resume_recording, style="TButton")
        self.resume_btn.pack(pady=5)

        self.stop_btn = ttk.Button(root, text="停止录音",  command=self.stop_recording, style="TButton")
        self.stop_btn.pack(pady=5)

        self.stop_btn = ttk.Button(root, text="转文本", command=self.audio2Text, style="TButton")
        self.stop_btn.pack(pady=5)

    def _configure_style(self):
        self.style.theme_use("clam")  # 比默认更现代
        self.style.configure("TButton",
                             font=("微软雅黑", 12),
                             padding=10,
                             borderwidth=0,
                             focusthickness=0,
                             background="#4CAF50",
                             foreground="white")
        self.style.map("TButton",
                       background=[("active", "#45a049")])

        self.style.configure("Danger.TButton",
                             font=("微软雅黑", 11),
                             padding=10,
                             background="#f44336",
                             foreground="white")
        self.style.map("Danger.TButton",
                       background=[("active", "#da190b")])

    def start_recording(self):
        if self.recorder is not None:
            self.recorder=SoundRecording()

        if self.recorder.start():
            self.status_label.config(text="录音中")
        else:
            messagebox.showinfo("提示", "录音已经在进行中")

    def pause_recording(self):
        if self.recorder.pause():
            self.status_label.config(text="已暂停")
        else:
            messagebox.showwarning("警告", "当前未在录音或已暂停")

    def resume_recording(self):
        if self.recorder.resume():
            self.status_label.config(text="录音中")
        else:
            messagebox.showwarning("警告", "当前未暂停")

    def stop_recording(self):
        if self.recorder.stop():
            self.status_label.config(text="已停止")
            messagebox.showinfo("完成", f"录音已保存到：{self.recorder.output_path}")
        else:
            messagebox.showwarning("警告", "当前未在录音中")

    def audio2Text(self):

        if os.path.exists(self.recorder.output_path):
            self.status_label.config(text="正在转文字...")
            def transcribe_chunks():
                try:
                    os.makedirs("output/chunks", exist_ok=True)
                    # 把ffmpeg添加的环境变量中
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    ffmpeg_dir = os.path.join(current_dir, "program/ffmpeg/bin")
                    os.environ["PATH"] += os.pathsep + ffmpeg_dir
                    # 显式设置路径
                    from pydub import AudioSegment
                    AudioSegment.converter = os.path.join(ffmpeg_dir, "ffmpeg.exe")
                    audio = AudioSegment.from_wav(self.recorder.output_path)
                    # --- 切割参数 ---
                    chunk_size_bytes = 1 * 1024 * 1024  # 1MB
                    bytes_per_ms = audio.frame_rate * audio.frame_width * audio.channels / 1000
                    chunk_size_ms = int(chunk_size_bytes / bytes_per_ms)
                    total_chunks = (len(audio) + chunk_size_ms - 1) // chunk_size_ms
                    chunks_paths = []

                    for i in range(total_chunks):
                        start = i * chunk_size_ms
                        end = min((i + 1) * chunk_size_ms, len(audio))
                        chunk = audio[start:end]
                        chunk_path = f"output/chunks/chunk_{i}.wav"
                        chunk.export(chunk_path, format="wav")
                        chunks_paths.append(chunk_path)
                    # 用于保存每段文字结果
                    results = [""] * total_chunks
                    threads = []

                    # --- 定义转写函数 ---
                    def transcribe_one(i, chunk_path):
                        transcriber = Transcriber(model_name="turbo")
                        text = transcriber.transcribe(chunk_path,language="zh")
                        results[i] = f"{text.strip()}\n\n"

                        os.remove(chunk_path)
                        # 强制释放内存
                        gc.collect()
                        # ✅ 更新进度（回到主线程）
                        self.root.after(0, lambda: self.status_label.config(
                            text=f"🎙️ 正在处理第 {i + 1} / {total_chunks} 段"
                        ))

                    # --- 并发处理 ---
                    for i, chunk_path in enumerate(chunks_paths):
                        t = threading.Thread(target=transcribe_one, args=(i, chunk_path), daemon=True)
                        t.start()
                        threads.append(t)
                    # 等待所有线程完成
                    for t in threads:
                        t.join()
                    # --- 保存最终结果 ---
                    with open("output/output.txt", "w", encoding="utf-8") as f:
                        f.writelines(results)

                    self.root.after(0, lambda: (
                        self.status_label.config(text="✅ 转写完成"),
                        messagebox.showinfo("完成", "文字已保存到 output/output.txt")
                    ))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showerror("错误", f"转写失败：{e}"))

            threading.Thread(target=transcribe_chunks, daemon=True).start()
        else:
            messagebox.showwarning("警告", "当前未在录音中")




def startup():
    root = tk.Tk()
    app = RecorderApp(root)
    root.geometry("300x350")
    root.iconbitmap('tools.ico')
    root.resizable(False, False)
    root.mainloop()

