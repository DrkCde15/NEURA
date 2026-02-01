import speech_recognition as sr
import pyttsx3
import logging
from typing import Optional
from .config import NeuraConfig

logger = logging.getLogger("NeuraVoice")

class NeuraVoice:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", NeuraConfig.TTS_RATE)
            self.engine.setProperty("volume", NeuraConfig.TTS_VOLUME)
            self._set_voice_pt()
        except Exception as e:
            logger.error(f"Erro ao inicializar motor de voz: {e}")

    def _set_voice_pt(self) -> None:
        try:
            for voice in self.engine.getProperty("voices"):
                if any(k in voice.name.lower() for k in NeuraConfig.VOICE_KEYWORDS):
                    self.engine.setProperty("voice", voice.id)
                    break
        except Exception as e:
            logger.warning(f"Não foi possível configurar voz em português: {e}")

    def speak(self, text: str) -> None:
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Erro ao falar: {e}")

    def listen(self) -> Optional[str]:
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                print("🎧 Ouvindo...")
                # Timeout evita que o programa trave para sempre se houver silêncio
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                text = recognizer.recognize_google(audio, language=NeuraConfig.LANGUAGE)
                return text
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except Exception as e:
                logger.error(f"Erro no reconhecimento de voz: {e}")
                return None