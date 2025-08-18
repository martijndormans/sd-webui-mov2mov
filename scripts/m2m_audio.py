import os
import tempfile
import numpy as np
import wave
import logging

logger = logging.getLogger("m2m_audio")

def get_audio(video_path, audio, reuse_audio):
    # If reuse_audio is checked, extract audio from the input video
    audio_path = None
    should_cleanup_audio = False
    if reuse_audio:
        audio_path = video_path
    else:
        if not audio:
            logger.warning("No audio provided.")
            return
        if isinstance(audio, str) and os.path.isfile(audio):
            audio_path = audio
        elif isinstance(audio, dict) and "name" in audio and os.path.isfile(audio["name"]):
            audio_path = audio["name"]
        elif isinstance(audio, tuple) and len(audio) == 2:
            # (sample_rate, np.ndarray)
            sr, data = audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                audio_path = f.name
                should_cleanup_audio = True
                # Save numpy array as wav
                if data.dtype != np.int16:
                    data = (data * 32767).astype(np.int16)
                with wave.open(f, "wb") as wf:
                    wf.setnchannels(1 if len(data.shape) == 1 else data.shape[1])
                    wf.setsampwidth(2)
                    wf.setframerate(sr)
                    wf.writeframes(data.tobytes())
        elif isinstance(audio, np.ndarray):
            # Assume 44100 Hz mono
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                audio_path = f.name
                should_cleanup_audio = True
                data = audio
                if data.dtype != np.int16:
                    data = (data * 32767).astype(np.int16)
                with wave.open(f, "wb") as wf:
                    wf.setnchannels(1 if len(data.shape) == 1 else data.shape[1])
                    wf.setsampwidth(2)
                    wf.setframerate(44100)
                    wf.writeframes(data.tobytes())
        else:
            logger.error(f"Unsupported audio input type: {type(audio)}")
            return
    return [audio_path, should_cleanup_audio]

def cleanup_audio(audio_path):
    if cleanup_audio and audio_path and os.path.isfile(audio_path):
        os.remove(audio_path)

def choose_audio(pitch_audio, pitched_audio, reuse_audio, audio):
    if (pitch_audio and pitched_audio):
        logging.info("Using pitched audio after video generation")
        return [pitched_audio, False]
    else:
        if (reuse_audio):
            logging.info("Using audio of the video input after video generation")
        else:
            logging.info("Using give audio (if valid) after video generation")
        return [audio, reuse_audio]
