import asyncio
import tempfile
import os
import subprocess
import json
import wave
from vosk import Model, KaldiRecognizer  # for Vosk usage
from gtts import gTTS
import logging
from pathlib import Path
from pydantic import BaseModel  # needed for TextResponse

class SpeechService:
    def __init__(self):
        # Initialize Vosk model (adjust the model path as needed)
        model_path = os.path.join(os.path.dirname(__file__), "../models/audioModel/vosk-model-en-us-0.22-lgraph")
        model_path = os.path.abspath(model_path)
        if not os.path.exists(model_path):
            raise Exception(f"Vosk model path not found: {model_path}")
        self.model = Model(model_path)
        self.logger = logging.getLogger(__name__)

    async def speech_to_text(self, audio_content: bytes) -> str:
        """Convert speech to text using Vosk. Expects an mp3 file in bytes."""
        # Save incoming mp3 audio to a temporary file.
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_mp3:
            temp_mp3.write(audio_content)
            mp3_path = temp_mp3.name

        # Create a temporary wav file path.
        wav_path = mp3_path.rsplit(".", 1)[0] + ".wav"
        try:
            # Convert mp3 to wav using ffmpeg (16kHz, mono).
            # Note: The "-y" flag is placed right after "ffmpeg" to force overwrite.
            command = [
                "ffmpeg",
                "-y",
                "-i", mp3_path,
                "-ar", "16000",
                "-ac", "1",
                "-f", "wav",
                wav_path
            ]
            await asyncio.to_thread(subprocess.run, command, check=True)

            # Run the blocking Vosk transcription on a separate thread.
            transcription = await asyncio.to_thread(self._transcribe, wav_path)

            # Optionally, print the transcription if non-empty.
            if transcription:
                print("Transcription:", transcription)

            return transcription

        except Exception as e:
            self.logger.error(f"Error in speech to text conversion: {str(e)}")
            raise

        finally:
            # Clean up temporary files.
            if os.path.exists(mp3_path):
                os.unlink(mp3_path)
            if os.path.exists(wav_path):
                os.unlink(wav_path)

    def _transcribe(self, wav_path: str) -> str:
        """Helper method to transcribe a wav file using Vosk."""
        results = []
        with wave.open(wav_path, "rb") as wf:
            rec = KaldiRecognizer(self.model, wf.getframerate())
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    results.append(res.get("text", ""))
            final_result = json.loads(rec.FinalResult())
            results.append(final_result.get("text", ""))
        transcription = " ".join(results).strip()
        return transcription

    async def text_to_speech(self, text: str, lang_code: str) -> bytes:
        """Convert text to speech using gTTS and return an mp3 file in bytes."""
        return await asyncio.to_thread(self._generate_tts, text, lang_code)

    def _generate_tts(self, text: str, lang_code: str) -> bytes:
        """Helper method to generate TTS audio and return its bytes."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_filename = temp_file.name
        try:
            tts = gTTS(text=text, lang=lang_code)
            tts.save(temp_filename)
            with open(temp_filename, 'rb') as f:
                audio_content = f.read()
            return audio_content
        except Exception as e:
            self.logger.error(f"Error in text to speech generation: {str(e)}")
            raise
        finally:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)

class TextResponse(BaseModel):
    response: str
    detected_language: str