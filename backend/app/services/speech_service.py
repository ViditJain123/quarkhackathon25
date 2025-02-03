# app/services/speech_service.py
import tempfile
import os
from faster_whisper import WhisperModel
from gtts import gTTS
import logging
from pathlib import Path

class SpeechService:
    def __init__(self):
        # Initialize Whisper model (using faster-whisper)
        self.model = WhisperModel("base", device="cpu", compute_type="int8")
        self.logger = logging.getLogger(__name__)

    async def speech_to_text(self, audio_content: bytes) -> str:
        """Convert speech to text using Whisper"""
        try:
            # Save audio content to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file.write(audio_content)
                temp_path = temp_file.name

            # Transcribe using Whisper
            segments, _ = self.model.transcribe(temp_path)
            transcript = " ".join([segment.text for segment in segments])

            # Clean up temporary file
            os.unlink(temp_path)

            return transcript.strip()

        except Exception as e:
            self.logger.error(f"Error in speech to text conversion: {str(e)}")
            raise

    async def text_to_speech(self, text: str, lang_code: str) -> bytes:
        """Convert text to speech using gTTS"""
        try:
            # Create temporary file for audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                # Convert text to speech
                tts = gTTS(text=text, lang=lang_code)
                tts.save(temp_file.name)
                
                # Read the audio content
                with open(temp_file.name, 'rb') as audio_file:
                    audio_content = audio_file.read()

            # Clean up temporary file
            os.unlink(temp_file.name)

            return audio_content

        except Exception as e:
            self.logger.error(f"Error in text to speech conversion: {str(e)}")
            raise