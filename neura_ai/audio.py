import speech_recognition as sr
import pyttsx3

class NeuraVoice:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 185)
        self.engine.setProperty("volume", 1.0)
        self._set_voice_pt()

    def _set_voice_pt(self):
        for voice in self.engine.getProperty("voices"):
            if "brazil" in voice.name.lower() or "portuguese" in voice.name.lower():
                self.engine.setProperty("voice", voice.id)
                break

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                print("🎧 Ouvindo...")
                audio = recognizer.listen(source)
                text = recognizer.recognize_google(audio, language="pt-BR")
                return text
            except Exception:
                return None