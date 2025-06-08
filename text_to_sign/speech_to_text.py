import speech_recognition as sr

class SpeechRecognizer:
    def __init__(self):
        self.r = sr.Recognizer()
        self.r.pause_threshold = 1.5
        self.r.energy_threshold = 0

    def setup_mic(self):
        with sr.Microphone() as source:
            self.r.adjust_for_ambient_noise(source)
            if self.r.energy_threshold < 1:
                self.r.energy_threshold = 0
                raise RuntimeError("Microphone may be muted or not working properly.")

    def listen(self, duration=10):
        # print(f"Please speak (max {duration} sec)...")
        with sr.Microphone() as source:
            audio = self.r.listen(source, phrase_time_limit=duration)
        # print("Audio captured, processing...")

        try:
            # print("Recognizing using Google Speech Recognition...")
            text = self.r.recognize_google(audio)
            return text

        except sr.RequestError:
            raise ConnectionError("Google API unavailable. Check your internet connection.")

        except sr.UnknownValueError:
            raise ValueError("Google Speech Recognition could not understand the audio.")
