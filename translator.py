import json
from pathlib import Path

try:
    from deep_translator import GoogleTranslator as _GT
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False

CACHE_FILE = Path(__file__).parent / "translations_cache.json"


class Translator:
    """
    Translates text via Google Translate (deep-translator) with a
    persistent JSON cache so the network is only hit once per unique string.

    If deep-translator is unavailable or the request fails, the original
    text is returned unchanged (graceful degradation).
    """

    def __init__(self, source: str = "en", target: str = "es"):
        self._source = source
        self._target = target
        self._cache: dict[str, str] = self._load_cache()

    # ── Public ─────────────────────────────────────────────────────────────

    def translate(self, text: str) -> str:
        """Return *text* translated to the target language."""
        key = f"{self._source}>{self._target}:{text}"
        if key in self._cache:
            return self._cache[key]

        if not _AVAILABLE:
            return text

        try:
            result = _GT(source=self._source, target=self._target).translate(text)
            if result:
                self._cache[key] = result
                self._save_cache()
                return result
        except Exception as exc:
            print(f"[Translator] Could not translate '{text[:40]}…': {exc}")

        return text  # fallback

    def translate_list(self, texts: list[str]) -> list[str]:
        return [self.translate(t) for t in texts]

    # ── Private ────────────────────────────────────────────────────────────

    def _load_cache(self) -> dict[str, str]:
        if CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, encoding="utf-8") as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, OSError):
                pass
        return {}

    def _save_cache(self) -> None:
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as fh:
                json.dump(self._cache, fh, ensure_ascii=False, indent=2)
        except OSError as exc:
            print(f"[Translator] Could not save cache: {exc}")
