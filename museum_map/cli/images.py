"""Image manipulation CLI commands."""

import os
import shutil
import subprocess

from rich.progress import Progress
from typer import Typer

group = Typer(help="Image commands")


@group.command()
def load_images(source, target):
    """Load and convert images."""
    with Progress() as progress:
        task = progress.add_task("Scanning files", total=None)
        total = 0
        for _basepath, _, filenames in os.walk(source):
            for filename in filenames:
                if filename.endswith(".jpg"):
                    total = total + 1
        progress.update(task, total=total, completed=total)
        task = progress.add_task("Loading images", total=total)
        for basepath, _, filenames in os.walk(source):
            for filename in filenames:
                if filename.endswith(".jpg"):
                    image_id = filename[: filename.find(".")]
                    os.makedirs(os.path.join(target, *image_id), exist_ok=True)
                    image_source = os.path.join(basepath, filename)
                    image_target = os.path.join(target, *image_id, filename)
                    shutil.copy(image_source, image_target)
                    subprocess.run(  # noqa:S603
                        [  # noqa: S607
                            "gm",
                            "convert",
                            image_source,
                            "-resize",
                            "240x240",
                            image_target.replace(".jpg", "-240.jpg"),
                        ],
                        check=True,
                    )
                    subprocess.run(  # noqa:S603
                        [  # noqa: S607
                            "gm",
                            "convert",
                            image_source,
                            "-resize",
                            "320x320",
                            image_target.replace(".jpg", "-320.jpg"),
                        ],
                        check=True,
                    )
                    progress.update(task, advance=1)
