import pyaudio as pa
import struct
from scipy.fft import rfft


class AudioAnalysis:  # A class that analyzes audio input
    def __init__(self):
        self.CHUNK = 1024 * 2
        self.FORMAT = pa.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.length, self.width = (1024, 512)

    def start_stream(self):  # Starts listening stream
        p = pa.PyAudio()
        self.stream = p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK
        )

    def close_stream(self):  # closes the stream
        self.stream.stop_stream()
        self.stream.close()

    # Returns sound wave data without separating the frequency
    def analyze_amplitude(self):
        data = self.stream.read(self.CHUNK)
        data_int = struct.unpack(str(self.CHUNK)+"h", data)
        return data_int

    def analyze_fft(self):  # separates the frequencies of the sound wave using FFT
        data = self.stream.read(self.CHUNK)
        data_int = struct.unpack(str(self.CHUNK)+"h", data)
        y_fft = rfft(data_int)
        y_data = ((abs(y_fft)*2/(256*self.CHUNK))*self.width/2)[20:]
        return y_data
