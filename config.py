from pathlib import Path

BASE_DIR = Path(__file__).parent

# Experiment parameters
TRIALS_PER_SET       = 10
TOTAL_SETS           = 20
FIXATION_DURATION_MS = 2000

# Paths — main experiment
IMG_PATH = BASE_DIR / 'coco2017' / 'selection'

# Paths — tutorial (practice session)
TUTORIAL_IMG_PATH    = BASE_DIR / 'coco2017' / 'train2017' / 'img'
TUTORIAL_ANN_PATH    = BASE_DIR / 'coco2017' / 'train2017' / 'ann'
TUTORIAL_NUM_IMAGES  = 3          # number of practice images shown

# Audio recordings output directory
RECORDINGS_DIR = BASE_DIR / 'recordings'

# LSL stream
LSL_STREAM_NAME = 'ImagesMarkerStream'
LSL_STREAM_TYPE = 'Markers'
LSL_STREAM_ID   = 'emuidw22'
