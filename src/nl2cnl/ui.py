from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from typing import TypeVar

from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

T = TypeVar("T")


class CliUI:
    def __init__(self):
        self.console = Console()

    def header(self, model: str, strategy: str) -> None:
        self.console.print(f"[bold cyan]NL2CNL[/] - [dim]model: {model}, strategy: {strategy}[/]\n")

    @contextmanager
    def step(self, label: str) -> Iterator[None]:
        with self.console.status(f"[cyan]{label}...[/]", spinner="dots"):
            yield
        self.console.print(f"[green]✓[/] {label}")

    def iter(self, items: Sequence[T], phase: str) -> Iterator[T]:
        progress = Progress(
            SpinnerColumn("dots", style="cyan"),
            TextColumn("[bold cyan]{task.description:<10}[/]"),
            BarColumn(bar_width=30, complete_style="cyan", finished_style="green"),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=self.console,
        )
        with progress:
            task = progress.add_task(phase, total=len(items))
            for item in items:
                yield item
                progress.update(task, advance=1)

    def print_results(self, items: Sequence) -> None:
        self.console.print()
        for item in items:
            self.console.print(f"[bold]{item.id}:[/] {item.model_output.text}")