# Spontaneous Speech Experiment

A full-screen PyQt6 experiment GUI for eliciting spontaneous speech descriptions of images from participants, designed for simultaneous EEG/BCI recording via Lab Streaming Layer (LSL).

---

## Overview

Participants view images one at a time and describe what they see aloud. Each session consists of a short practice round followed by 20 sets of 10 images. Timing markers are streamed in real time to any connected EEG recording software, allowing precise alignment between neural data and stimulus events.

---

## Requirements

### Python packages

```bash
pip install PyQt6==6.11.0 pylsl==1.18.1 deep-translator
```

| Package | Purpose |
|---|---|
| `PyQt6` | Full-screen GUI framework |
| `pylsl` | Lab Streaming Layer — sends timing markers to EEG software |
| `deep-translator` | Auto-translates COCO captions (English → Spanish); **optional** — the app runs fine without it using the pre-built cache |

### Python version

Python 3.11 or later (uses `list[str]` and `X | Y` type hints).

---

## Folder structure

```
spontaneousSpeech/
│
├── spontaneous_speech.py          # Entry point — run this
├── config.py                     # All tunable parameters
├── image_manager.py              # Deterministic set assignment + randomised order
├── annotation_loader.py          # Loads COCO captions from JSON files
├── translator.py                 # EN→ES translation with persistent cache
├── lsl_manager.py                # LSL marker stream wrapper
├── translations_cache.json       # Pre-translated captions (auto-generated)
│
├── gui/
│   ├── main_window.py            # State machine + QMainWindow
│   └── screens/
│       ├── instruction_screen.py # Welcome screen
│       ├── tutorial_screen.py    # Practice session (3 images + captions)
│       ├── trial_screen.py       # Image display + fixation cross
│       ├── between_set_screen.py # Break screen between sets
│       └── end_screen.py         # Final completion screen
│
└── coco2017/
    ├── selection/                # 217 experiment images (.jpg)
    └── train2017/
        ├── img/                  # 974 practice images (.jpg)
        └── ann/                  # 974 annotation files (.json) with COCO captions
```

---

## Running the experiment

```bash
python spontaneous_speech.py
```

The window opens full-screen. No arguments are needed — the experiment always starts from Set 1 after the practice session.

To exit at any time press **ESC**.

---

## Experiment flow

```
Welcome screen
    SPACE
      │
      ▼
┌─────────────────────────────────────────────┐
│  PRACTICE SESSION  (3 images)               │
│                                             │
│  Image shown full-screen                    │
│  → participant describes aloud              │
│  PAGE DOWN                                  │
│  → same image + 5 Spanish example captions │
│  PAGE DOWN → next practice image           │
│  (repeat × 3)                               │
│                                             │
│  "Práctica completada"                      │
│  SPACE                                      │
└─────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────┐
│  MAIN EXPERIMENT  (Sets 1 – 20)             │
│                                             │
│  For each of the 10 images in the set:      │
│    1. Image shown full-screen               │
│    2. Participant describes aloud           │
│    3. PAGE DOWN → 2 s fixation cross (+)   │
│    4. Next image automatically              │
│                                             │
│  After set:  "Set N de 20 completado"       │
│    SPACE → continue  │  ESC → exit         │
└─────────────────────────────────────────────┘
      │
      ▼
   "Fin del experimento — Ha completado los 20 sets"
```

### Key bindings

| Key | When | Action |
|---|---|---|
| `SPACE` | Welcome screen | Begin practice session |
| `SPACE` | End of practice (done slide) | Start Set 1 |
| `SPACE` | Between sets | Start next set |
| `PAGE DOWN` or `↓` | Practice — image phase | Reveal example captions |
| `PAGE DOWN` or `↓` | Practice — caption phase | Next practice image |
| `PAGE DOWN` or `↓` | Trial | End trial, show fixation cross |
| `ESC` | Any screen | Exit and send `experimentEnded;ESC pressed` to LSL |

---

## Image sets

Images are loaded from `coco2017/selection/` (217 files). They are sorted alphabetically and divided into fixed pools of 10:

| Property | Behaviour |
|---|---|
| **Same set content across runs** | Set 1 always contains the same 10 images, Set 2 the next 10, etc. |
| **Randomised display order** | The order within a set is shuffled fresh every run |
| **No repeats** | Each image appears in exactly one set; sets never overlap |

Total available sets: 21 (only the first 20 are used). To change set size or count, edit `config.py`.

---

## Configuration

All tunable parameters are in `config.py`:

```python
TRIALS_PER_SET       = 10      # images per set
TOTAL_SETS           = 20      # how many sets to run
FIXATION_DURATION_MS = 2000    # fixation cross duration (ms)
TUTORIAL_NUM_IMAGES  = 3       # practice images shown before experiment
```

---

## LSL markers

Markers are pushed to a stream named `ImagesMarkerStream` (type `Markers`). Every marker includes dual timestamps:

```
start_000000004296.jpg_lsl1295669.336459_wall2026-04-07T22:40:07.155485
end_000000004296.jpg_lsl1295671.436693_wall2026-04-07T22:40:09.255721
```

| Field | Purpose |
|---|---|
| `lsl…` | LSL clock (same timeline as EEG amplifier — use for neural alignment) |
| `wall…` | Wall-clock datetime (use for logs and cross-referencing) |

### Full marker reference

| Marker | Sent when |
|---|---|
| `tutorialStarted` | Practice session begins |
| `tutorialImage_{file}_{ts}` | A practice image is shown |
| `tutorialCaption_{file}_{ts}` | Example captions are revealed |
| `tutorialEnded` | Practice completion slide shown |
| `setStarted;{N}` | Set N begins |
| `start_{file}_lsl{ts}_wall{ts}` | Trial image appears on screen |
| `end_{file}_lsl{ts}_wall{ts}` | Participant presses PAGE DOWN (fixation begins) |
| `setEnded;{N}` | All 10 images in Set N completed |
| `experimentEnded` | All 20 sets completed normally |
| `experimentEnded;ESC pressed` | Participant or operator pressed ESC |

### Offline mode

If `pylsl` is not installed or no recording software is listening, the app runs normally and all markers are printed to the console only.

---

## Practice session captions

The 3 practice images come from `coco2017/train2017/img/`. Their COCO captions are loaded from `coco2017/train2017/ann/`, automatically translated from English to Spanish using Google Translate via `deep-translator`, and cached to `translations_cache.json`. On all subsequent runs the cache is used — no internet connection is required.

To force a fresh translation, delete `translations_cache.json` and restart.

---

## Architecture

The application follows a strict **model–view–state-machine** pattern:

```
spontaneousSpeech.py
    └── MainWindow  (state machine + key dispatcher)
            ├── ImageManager     (image set logic)
            ├── LSLManager       (marker streaming)
            ├── AnnotationLoader (caption loading + translation)
            └── QStackedWidget
                    ├── InstructionScreen
                    ├── TutorialScreen
                    ├── TrialScreen
                    ├── BetweenSetScreen
                    └── EndScreen
```

Screen widgets are **pure display components** — they hold no experiment logic. All state transitions, LSL calls, and timers live exclusively in `MainWindow`.

---

## Extending the experiment

**Change the number of practice images**
Edit `TUTORIAL_NUM_IMAGES` in `config.py` (must not exceed the number of images in `train2017/img/`).

**Use a different image set**
Point `IMG_PATH` in `config.py` to any folder of `.jpg` / `.png` files.

**Change the caption language**
In `gui/main_window.py`, find `Translator(source="en", target="es")` and change `target` to any [BCP-47 language code](https://cloud.google.com/translate/docs/languages) (e.g. `"nl"` for Dutch, `"fr"` for French). Delete `translations_cache.json` to force re-translation.

**Adjust fixation duration**
Edit `FIXATION_DURATION_MS` in `config.py`.
