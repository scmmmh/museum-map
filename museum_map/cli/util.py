"""Utility functionality for the cli."""
import click

from threading import Thread
from time import sleep


class ClickIndeterminate(Thread):
    """A thread that shows a indeterminate busy animation using the cli."""

    def __init__(self, label):
        super().__init__()
        self._label = label
        self._active = False

    def run(self):
        """Run the animation sequence."""
        anim = ['\u28fe', '\u28f7', '\u28ef', '\u28df', '\u287f', '\u28bf', '\u28fb', '\u28fd']
        anim.reverse()
        self._active = True
        click.echo(f'{self._label}  ', nl=False)
        while self._active:
            click.echo(f'\b{anim[-1]}', nl=False)
            anim.insert(0, anim.pop())
            sleep(0.15)

    def stop(self):
        """Stop the animation sequence."""
        self._active = False
        click.echo(f'\b\u2713')
