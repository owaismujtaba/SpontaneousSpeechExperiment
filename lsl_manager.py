import time as _time
import datetime as _datetime

from config import LSL_STREAM_NAME, LSL_STREAM_TYPE, LSL_STREAM_ID

try:
    from pylsl import StreamInfo, StreamOutlet as _StreamOutlet, local_clock as _local_clock
    _LSL_AVAILABLE = True
except ImportError:
    _LSL_AVAILABLE = False


class LSLManager:
    """
    Thin wrapper around pylsl to push string markers.

    If pylsl is not installed or no recording software is connected,
    the manager runs in offline mode — markers are printed to the
    console only and the experiment proceeds normally.
    """

    def __init__(self):
        self._outlet = None
        if _LSL_AVAILABLE:
            try:
                info = StreamInfo(LSL_STREAM_NAME, LSL_STREAM_TYPE, 1, 0, 'string', LSL_STREAM_ID)
                self._outlet = _StreamOutlet(info)
                print("[LSL] Stream outlet created — ready to record.")
            except Exception as e:
                print(f"[LSL] Could not create outlet ({e}). Running in offline mode.")
        else:
            print("[LSL] pylsl not installed. Running in offline mode (markers printed only).")

    def clock(self) -> float:
        """
        Returns the current LSL clock time (seconds).
        Uses pylsl.local_clock() when available so the timestamp is
        on the same timeline as the recorded EEG stream.
        Falls back to time.time() in offline mode.
        """
        return _local_clock() if _LSL_AVAILABLE else _time.time()

    def marker(self, event: str, image: str) -> str:
        """
        Build a marker string with both timestamps:
          {event}_{image}_lsl{lsl_clock:.6f}_wall{YYYY-MM-DDTHH:MM:SS.ffffff}

        - lsl_clock  → synced with EEG amplifier, use for neural alignment
        - wall       → human-readable, use for log review / cross-referencing
        """
        lsl_t  = self.clock()
        wall_t = _datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        return f"{event}_{image}_lsl{lsl_t:.6f}_wall{wall_t}"

    def push(self, marker: str) -> None:
        print(f"[LSL] {marker}")
        if self._outlet is not None:
            self._outlet.push_sample([marker])
