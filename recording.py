import pyaudio
import wave
import os
import threading
import time

class SoundRecording:
    def __init__(self, output_path="output/output.wav"):
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk = 1024
        self.output_path = output_path
        self.frames = []
        self.is_recording = False
        self.is_paused = False
        self._thread = None
        self._pyaudio = pyaudio.PyAudio()

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

    def _record(self):
        stream = self._pyaudio.open(format=self.format,
                                    channels=self.channels,
                                    rate=self.rate,
                                    input=True,
                                    frames_per_buffer=self.chunk)

        while self.is_recording:
            if not self.is_paused:
                data = stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            else:
                time.sleep(0.1)

        stream.stop_stream()
        stream.close()
        self._save_wave()
        self._pyaudio.terminate()

    def _save_wave(self):
        with wave.open(self.output_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self._pyaudio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))

    def start(self):
        if self.is_recording:
            return False
        self.frames = []
        self.is_recording = True
        self.is_paused = False
        self._thread = threading.Thread(target=self._record)
        self._thread.start()
        return True

    def pause(self):
        if self.is_recording and not self.is_paused:
            self.is_paused = True
            return True
        return False

    def resume(self):
        if self.is_recording and self.is_paused:
            self.is_paused = False
            return True
        return False

    def stop(self):
        if self.is_recording:
            self.is_recording = False
            if self._thread:
                self._thread.join()
            return True
        return False
