import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

class AudioRecorder:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_data = []

    def start_recording(self):
        """Start recording audio."""
        self.recording = True
        self.audio_data = []  # Clear previous audio data
        print("Recording started...")

        def callback(indata, frames, time, status):
            if status:
                print(status)
            self.audio_data.append(indata.copy())

        # Start the recording stream
        self.stream = sd.InputStream(samplerate=self.sample_rate, channels=1, callback=callback)
        self.stream.start()

    def stop_recording(self, file_path='recording.wav'):
        """Stop recording audio and save to a file."""
        self.recording = False
        print("Recording stopped.")
        
        # Stop and close the stream
        self.stream.stop()
        self.stream.close()

        # Concatenate the recorded audio data
        self.audio_data = np.concatenate(self.audio_data, axis=0)
        
        # Save the recorded audio data to a WAV file
        write(file_path, self.sample_rate, self.audio_data)
        print(f"Audio saved to {file_path}.")
