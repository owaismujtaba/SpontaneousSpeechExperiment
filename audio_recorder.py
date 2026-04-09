"""
AudioRecorder — continuous microphone recording to a single WAV file.

Usage:
    recorder = AudioRecorder(output_dir=Path("recordings"))
    recorder.start()   # call once when the tutorial begins
    recorder.stop()    # call once at experiment end or ESC
"""

import threading
from pathlib import Path
from datetime import datetime

try:
    import numpy as np
    import sounddevice as sd
    import soundfile as sf
    _AUDIO_AVAILABLE = True
except ImportError:
    _AUDIO_AVAILABLE = False


class AudioRecorder:
    """Records from the default microphone into memory, then saves a WAV on stop."""

    SAMPLE_RATE = 44_100
    CHANNELS    = 1

    def __init__(self, output_dir: Path):
        self._output_dir     = output_dir
        self._frames: list   = []
        self._stream         = None
        self._lock           = threading.Lock()
        self._filename_prefix = "recording"


    def start(self, filename_prefix: str = "recording") -> None:
        """Begin recording from the default microphone.

        Args:
            filename_prefix: Prefix for the saved WAV file (e.g. "sub_P01_sess_S01").
        """
        if not _AUDIO_AVAILABLE:
            print("[AudioRecorder] sounddevice/soundfile not installed — audio disabled")
            return

        self._filename_prefix = filename_prefix

        self._frames.clear()

        def _callback(indata, frames, time, status):  # noqa: ARG001
            if status:
                print(f"[AudioRecorder] {status}")
            with self._lock:
                self._frames.append(indata.copy())

        self._stream = sd.InputStream(
            samplerate=self.SAMPLE_RATE,
            channels=self.CHANNELS,
            callback=_callback,
        )
        self._stream.start()
        print("[AudioRecorder] Recording started")

    def stop(self) -> Path | None:
        """Stop recording and write a WAV file. Returns the saved path, or None."""
        if not _AUDIO_AVAILABLE or self._stream is None:
            return None

        self._stream.stop()
        self._stream.close()
        self._stream = None

        with self._lock:
            frames = list(self._frames)

        if not frames:
            print("[AudioRecorder] No audio captured — file not saved")
            return None

        self._output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path  = self._output_dir / f"{self._filename_prefix}_{timestamp}.wav"

        audio = np.concatenate(frames, axis=0)
        sf.write(str(out_path), audio, self.SAMPLE_RATE)
        print(f"[AudioRecorder] Saved → {out_path}")
        return out_path
