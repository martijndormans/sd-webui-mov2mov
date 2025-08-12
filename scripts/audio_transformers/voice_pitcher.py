import librosa
import soundfile as sf
import tempfile
import logging
from scripts.m2m_audio import get_audio

logger = logging.getLogger("voice_pitcher")

def generate_pitched_audio(init_mov, audio_path, reuse_audio, pitch_steps):
    logger.info("Starting pitch transformation")

    pitched_audio_path = None
    audio_path, should_cleanup_audio = get_audio(init_mov, audio_path, reuse_audio)

    if (audio_path):
        try:
            y, sr = librosa.load(audio_path)
            y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_steps)  # 1 semitone up
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                pitched_audio_path = f.name
                sf.write(f.name, y_shifted, sr)
        except Exception as e:
            logger.warning("Something went wrong when trying to transform the audio")
            return None

    logger.info("Pitch transformation complete")
    return pitched_audio_path