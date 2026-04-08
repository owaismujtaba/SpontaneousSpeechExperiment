import os
import random
from pathlib import Path

from config import IMG_PATH, TRIALS_PER_SET


class ImageManager:
    """
    Manages image sets with deterministic pool assignment and
    randomised display order per run.

    - The pool of images belonging to each set number is always the same
      (sorted filenames → sliced by set index), so set 1 is always the
      same 10 images regardless of when the experiment is run.
    - The display *order* within a set is shuffled fresh every run.
    - Images shown in previous sets are never repeated in later sets.
    """

    def __init__(self):
        self._all_images: list[str] = sorted(
            f for f in os.listdir(IMG_PATH)
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def num_sets(self) -> int:
        """Number of complete sets available."""
        return len(self._all_images) // TRIALS_PER_SET

    def get_set(self, set_number: int) -> list[str]:
        """
        Return the image filenames for *set_number* in a randomised order.

        Args:
            set_number: 1-based set index (1 … num_sets).

        Returns:
            Shuffled list of *TRIALS_PER_SET* filenames.
        """
        if not 1 <= set_number <= self.num_sets:
            raise ValueError(
                f"set_number must be between 1 and {self.num_sets}, got {set_number}"
            )
        start = (set_number - 1) * TRIALS_PER_SET
        pool  = list(self._all_images[start : start + TRIALS_PER_SET])
        random.shuffle(pool)
        return pool

    def get_image_path(self, filename: str) -> Path:
        return IMG_PATH / filename
