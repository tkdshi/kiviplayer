# coding: utf-8

from os.path import basename

from kivy.core.audio import SoundLoader
from kivy.core.window import Window

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

from kivy.clock import Clock
from decimal import Decimal, ROUND_HALF_UP



import wave
import numpy as np
import sys
import struct
import pyaudio

# ファイル参照部ライブラリ
import os, tkinter, tkinter.filedialog, tkinter.messagebox


class MusicPlayer(BoxLayout):
    FILE = ''
    file_path = ''
    sound_path = ''
    sound = None
    popup = None
    is_playing = False
    is_pausing = False
    pause_pos = 0
    value_before = 0
    lengh = 0
    low_value = 1
    mid_value = 1
    high_value = 1
    pitch_value = 0
    speed_value = 1
    vol_value = 1
    fs = ''

    def __init__(self, **kwargs):
        print('__init__')
        super(MusicPlayer, self).__init__(**kwargs)

        self._file = Window.bind(
            on_dropfile=self._on_file_drop
        )

    # ファイル参照部
    def FileSelect(self):
        root = tkinter.Tk()
        root.withdraw()
        # fTyp = [("", "*")]
        fTyp = [("", "*.wav")]
        iDir = os.path.abspath(os.path.dirname(__file__))
        try:
            self.FILE = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir=iDir)
            self.select(self.FILE)
        except FileNotFoundError:
            return

    def wavRead(self, path):
        print('wavRead')
        wf = wave.open(path, "r")
        channels = wf.getnchannels()
        self.fs = wf.getframerate()

        buf = wf.readframes(wf.getnframes())

        data = np.frombuffer(buf, dtype="int16")
        return data, channels, self.fs

    def effect(self, path):
        print('effect')
        data, channels, self.fs = self.wavRead(path)
        out = []

        # キーの変更
        r = 1.059463094
        self.fs = int((self.fs) * (r ** self.pitch_value))
        # self.fs = int(self.fs*(r**self.pitch_value))

        # イコライザの実装
        ## dataとbを畳み込み
        out1 = np.convolve(data, self.filter_low(self.fs), 'same')
        out2 = np.convolve(data, self.filter_mid(self.fs), 'same')
        out3 = np.convolve(data, self.filter_high(self.fs), 'same')
        out = (out1 * self.low_value + out2 * self.mid_value + out3 * self.high_value)
        self.wavWrite(out.astype(np.int16), channels, self.fs)

    ####### sinc関数
    def sinc(self, x):
        if x == 0.0:
            return 1.0
        else:
            return np.sin(x) / x

    ####### フィルタ係数bの決定（ローパスフィルタ）
    # fs, サンプリング周波数
    # cutoff, カットオフ周波数
    # delta, 遷移帯域幅
    def filter_low(self, fs):
        print('filter_low')
        cutoff = 500
        delta = 1000
        cutoff = float(cutoff) / self.fs  # カットオフ周波数の正規化
        delta = float(delta) / self.fs  # 遷移帯域幅の正規化

        # タップ数（フィルタ係数J+1の数）J+1は奇数になるように
        J = round(3.1 / delta) - 1
        if (J + 1) % 2 == 0:
            J += 1
        J = int(J)

        # タップ数の確認（遷移帯域幅と反比例）
        print("filter coefficients: " + str(J + 1))

        # フィルタ係数の計算
        b = []
        for m in range(int(-J / 2), int(J / 2 + 1)):
            b.append(2.0 * cutoff * self.sinc(2.0 * np.pi * cutoff * m))

        # ハニング窓関数をかける（窓関数法）
        hanningWindow = np.hanning(J + 1)
        b = b * hanningWindow

        return b

    def filter_mid(self, fs):
        print('filter_mid')
        cutoff1 = 500
        cutoff2 = 5000
        delta = 1000
        cutoff1 = float(cutoff1) / self.fs  # カットオフ周波数の正規化
        cutoff2 = float(cutoff2) / self.fs  # カットオフ周波数の正規化
        delta = float(delta) / self.fs  # 遷移帯域幅の正規化

        # タップ数（フィルタ係数J+1の数）J+1は奇数になるように
        J = round(3.1 / delta) - 1
        if (J + 1) % 2 == 0:
            J += 1
        J = int(J)

        # タップ数の確認（遷移帯域幅と反比例）
        print("filter coefficients: " + str(J + 1))

        # フィルタ係数の計算
        b = []
        for m in range(int(-J / 2), int(J / 2 + 1)):
            b.append(2.0 * cutoff2 * self.sinc(2.0 * np.pi * cutoff2 * m) - 2.0 * cutoff1 * self.sinc(
                2.0 * np.pi * cutoff1 * m))

        # ハミング窓関数をかける（窓関数法）
        hanningWindow = np.hanning(J + 1)
        b = b * hanningWindow

        return b

    def filter_high(self, fs):
        print('filter_high')
        cutoff = 5000
        delta = 1000
        cutoff = float(cutoff) / self.fs  # カットオフ周波数の正規化
        delta = float(delta) / self.fs  # 遷移帯域幅の正規化

        # タップ数（フィルタ係数J+1の数）J+1は奇数になるように
        J = round(3.1 / delta) - 1
        if (J + 1) % 2 == 0:
            J += 1
        J = int(J)

        # タップ数の確認（遷移帯域幅と反比例）
        print("filter coefficients: " + str(J + 1))

        # フィルタ係数の計算
        b = []
        for m in range(int(-J / 2), int(J / 2 + 1)):
            b.append(self.sinc(np.pi * m) - 2 * cutoff * self.sinc(2 * np.pi * cutoff * m))

        # ハミング窓関数をかける（窓関数法）
        hanningWindow = np.hanning(J + 1)
        b = b * hanningWindow

        return b

    ####### ファイル保存
    def wavWrite(self, data, channels, fs):
        print('wavWrite')
        binaryData = struct.pack("h" * len(data), *data)
        out = wave.Wave_write('out.wav')
        param = (channels, 2, self.fs, len(binaryData), 'NONE', 'not compressed')
        out.setparams(param)
        out.writeframes(binaryData)
        out.close()

    def _on_file_drop(self, window, file_path):
        print('_on_file_drop')
        self.file_path = file_path.decode('utf-8')
        self.select(self.file_path)
        # self.select(file_path.decode('utf-8'))
        return

    def cancel(self):
        print('cancel')
        self.popup.dismiss()

    def select(self, path):
        print('select')
        if self.sound:
            self._stop()

        self.effect(path)

        # self.sound = SoundLoader.load(path)
        self.sound_path = 'out.wav'
        self.sound = SoundLoader.load('out.wav')
        self.sound_name = basename(path)

        try:
            # パラメータの初期値
            # self._volume(100)
            # self._low(100)
            # self._mid(100)
            # self._high(100)
            self._start()
        finally:
            if self.popup:
                self.popup.dismiss()

    def play_or_stop(self):
        print('play_or_stop')
        if not self.sound:
            self.status.text = 'Select music file'
            return

        if self.sound.state == "play":
            self._pause()
        elif self.sound.state == 'stop':
            self._restart()

    def stop(self):
        print('stop')
        if self.is_playing:
            self._stop()

    def _time_string(self, now, end):
        now_m, now_s = map(int, divmod(now, 60))
        now_str = "{0:d}:{1:02d}".format(now_m, now_s)

        end_m, end_s = map(int, divmod(end, 60))
        end_str = "{0:d}:{1:02d}".format(end_m, end_s)

        return "{}/{}".format(now_str, end_str)

    def _timer(self, val):
        if not self.sound:
            return False
        elif self.time_bar.value >= self.time_bar.max:
            self._stop()
            return False
        else:
            self.value_before = self.time_bar.value
            self.time_bar.value += 0.1

            self.time_text.text = self._time_string(
                self.time_bar.value,
                self.lengh
            )

    # イコライザのパラメータ実装部分
    def _low(self, low):  # 低域
        print('_low')
        low = round(low)
        self.low_value = low / 100

        self.low_text.text = str(low)
        self.low_bar.value = low
        print(self.sound_path)
        if self.FILE != '':
            self.effect(self.FILE)

    def _mid(self, mid):  # 中域
        print('_mid')
        mid = round(mid)
        self.mid_value = mid / 100

        self.mid_text.text = str(mid)
        self.mid_bar.value = mid
        if self.FILE != '':
            self.effect(self.FILE)

    def _high(self, high):  # 高域
        print('_high')
        high = round(high)
        self.high_value = high / 100

        self.high_text.text = str(high)
        self.high_bar.value = high

        if self.FILE != '':
            self.effect(self.FILE)

    def _pitch(self, pitch):  # 音階
        print('_pitch')
        pitch = round(pitch)
        self.pitch_value = pitch

        self.pitch_text.text = str(pitch)
        self.pitch_bar.value = pitch

        if self.FILE != '':
            self.effect(self.FILE)

    def _speed(self, speed):
        print('_speed')
        speed = round(speed)
        self.speed_value = speed / 100

        self.speed_text.text = str(speed)
        self.speed_bar.value = speed

    def _volume(self, vol):
        print('_volume')
        vol = round(vol)
        self.vol_value = vol / 100

        self.volume_text.text = str(vol)
        self.volume_bar.value = vol

        if not self.sound:
            return

        self.sound.volume = self.vol_value

    def time_change(self, value):
        if not self.sound:
            self.status.text = 'Select music file'
            return

        elif self.is_playing and value != self.value_before + 0.1:
            self._pause()
            self._restart(value)

    # パラメータの変更を検出
    def volume_change(self, value):
        self._volume(value)

    def low_change(self, value):
        self._low(value)

    def mid_change(self, value):
        self._mid(value)

    def high_change(self, value):
        self._high(value)

    def pitch_change(self, value):
        self._pitch(value)

    def speed_change(self, value):
        self._speed(value)

    # 音楽プレーヤーの機能部分
    def _start(self):
        print('_start')
        self.sound.play()
        self.is_playing = True
        self.is_pausing = False
        Clock.schedule_interval(self._timer, 0.1)

        self.time_bar.max = self.sound.length

        self.play_button.text = 'Pause'
        self.status.text = 'Playing {}'.format(self.sound_name)

        self.lengh = self.sound.length

    def _restart(self, pos=None):
        print('_restart')
        self._start()
        self.sound.seek(pos if pos else self.pause_pos)
        self.pause_pos = 0

    def _stop(self, pause=False):
        print('_stop')

        self.sound.stop()
        Clock.unschedule(self._timer)

        if not pause:
            self.is_pausing = False
            self.is_playing = False
            self.pause_pos = 0
            self.time_bar.value = 0

            self.time_text.text = self._time_string(
                self.time_bar.value,
                self.lengh
            )

        self.play_button.text = 'Play'
        self.status.text = 'Stop {}'.format(self.sound_name)

    def _pause(self):
        print('_pause')
        self.pause_pos = self.sound.get_pos()
        self._stop(True)
        self.is_pausing = True
