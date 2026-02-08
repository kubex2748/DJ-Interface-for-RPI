import wave
import struct
import numpy as np
import librosa

class Analyse:
    def __init__(self, path, sampling_rate):
        self.path = path
        self.sampling_rate = sampling_rate

    def wave_form(self, num_pixels):
        wf = wave.open(self.path, 'rb')

        # Pobierz prawdziwe sampling rate, jeśli nie ustawiono
        if self.sampling_rate is None:
            self.sampling_rate = wf.getframerate()

        n_frames = wf.getnframes()
        n_channels = wf.getnchannels()
        frames_per_pixel = max(1, n_frames // num_pixels)

        waveform = []

        for i in range(num_pixels):
            min_val = 1.0
            max_val = -1.0

            frames = wf.readframes(frames_per_pixel)
            if len(frames) < n_channels * 2:
                break  # koniec pliku

            samples = []
            for k in range(0, len(frames), n_channels*2):
                if n_channels == 2:
                    left, right = struct.unpack('<hh', frames[k:k+4])
                    sample = (left + right) / 2.0 / 32768
                else:
                    sample, = struct.unpack('<h', frames[k:k+2])
                    sample = sample / 32768

                min_val = min(min_val, sample)
                max_val = max(max_val, sample)
                samples.append(sample)

            # --- oblicz średnią częstotliwość w bloku ---
            if samples:
                fft = np.fft.rfft(samples)
                magnitude = np.abs(fft)
                freqs = np.fft.rfftfreq(len(samples), d=1/self.sampling_rate)

                bass = np.sum(magnitude[(freqs >= 20) & (freqs < 200)])
                mid = np.sum(magnitude[(freqs >= 200) & (freqs < 2000)])
                treble = np.sum(magnitude[freqs >= 2000])

                total = bass + mid + treble + 1e-6  # żeby nie dzielić przez 0

                r = (bass / total) * 1.4   # boost basu
                g = (mid / total) * 1.0    # normal
                b = (treble / total) * 0.6 # stłum wysokie
                
                energy = np.sqrt(np.mean(np.square(samples)))   # energia sygnału (RMS)

                waveform.append([(min_val, max_val), (r, g, b), energy])

        wf.close()
        return waveform

    def analyseBpmKey(self):
        y, sr = librosa.load(self.path, sr=None, mono=True, offset=0.0, duration=60.0)

        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        bpm = float(tempo)

        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key_index = np.argmax(chroma.mean(axis=1))
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = notes[key_index]

        track_duration_sec = len(y) / sr

        return bpm, key, track_duration_sec
    
