"""Plain terminal table formatting."""

import shutil
from dataclasses import dataclass
from typing import Literal


Align = Literal["left", "right"]


@dataclass(frozen=True)
class Column:
    header: str
    width: int
    align: Align = "left"
    shrinkable: bool = False


def truncate(value: str, width: int) -> str:
    if len(value) <= width:
        return value
    if width <= 1:
        return value[:width]
    return value[: width - 1] + "."


def fit_columns(columns: list[Column], terminal_width: int) -> list[Column]:
    if not columns:
        return columns

    separator_width = 2 * (len(columns) - 1)
    target = max(40, terminal_width - separator_width)
    widths = [column.width for column in columns]
    overflow = sum(widths) - target

    while overflow > 0:
        changed = False
        for index, column in sorted(
            enumerate(columns),
            key=lambda item: item[1].width,
            reverse=True,
        ):
            floor = len(column.header)
            if not column.shrinkable or widths[index] <= floor:
                continue
            widths[index] -= 1
            overflow -= 1
            changed = True
            if overflow <= 0:
                break
        if not changed:
            break

    return [
        Column(column.header, width, column.align, column.shrinkable)
        for column, width in zip(columns, widths)
    ]


def format_cell(value: str, column: Column) -> str:
    clipped = truncate(value, column.width)
    if column.align == "right":
        return clipped.rjust(column.width)
    return clipped.ljust(column.width)


def aligned_table(
    columns: list[Column],
    rows: list[list[str]],
    *,
    terminal_width: int | None = None,
) -> str:
    width = terminal_width or shutil.get_terminal_size((120, 20)).columns
    fitted = fit_columns(columns, width)
    lines = [
        "  ".join(format_cell(column.header, column) for column in fitted),
        "  ".join("-" * column.width for column in fitted),
    ]
    for row in rows:
        lines.append(
            "  ".join(format_cell(value, column) for value, column in zip(row, fitted))
        )
    return "\n".join(lines)


def natural_columns(
    headers: list[str],
    rows: list[list[str]],
    *,
    right_align: set[str] | None = None,
    shrinkable: set[str] | None = None,
    max_widths: dict[str, int] | None = None,
) -> list[Column]:
    right_align = right_align or set()
    shrinkable = shrinkable or set()
    max_widths = max_widths or {}
    columns: list[Column] = []
    for index, header in enumerate(headers):
        natural_width = max([len(header), *(len(row[index]) for row in rows)] or [len(header)])
        width = min(natural_width, max_widths.get(header, natural_width))
        columns.append(
            Column(
                header,
                width,
                "right" if header in right_align else "left",
                header in shrinkable,
            )
        )
    return columns
