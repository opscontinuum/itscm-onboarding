"""Write a whole plan repository to disk: the documents, and the drawings they embed.

:mod:`itscp_render` is a pure function and does no input or output; :mod:`itscp_diagrams`
is the same. This module is the one that touches the filesystem, and it exists so that the
structural guarantee belongs to the toolkit rather than to whoever remembers to call both.

The guarantee is the point. ``repo-scaffold`` requires that a generated plan never points at
a file that is not there, and the reference plan fails that today on five files. A build
step that wrote the documents and left the caller to produce the drawings would reproduce
exactly that failure, one directory down: two documents embedding two images nobody wrote.

So which drawings get written is not a list kept here. It is read from the renderer's own
figure declarations, which are the same declarations that produce the links. A document
cannot embed a drawing this module does not write, because both come from one place, and a
drawing with no data behind it is still written, carrying the answer store's MISSING marker
in place of a chart.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    raise RuntimeError(
        "itscp-author needs Python 3.11 or newer (this is "
        f"{sys.version_info.major}.{sys.version_info.minor}). There is no pip dependency to "
        "install; run the plugin under a newer interpreter."
    )

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import itscp_diagrams as diagrams
import itscp_render as render


class BuildError(Exception):
    """The plan cannot be written completely. Reported, never written half way."""


@dataclass(frozen=True)
class Plan:
    """Everything one plan repository is generated from.

    ``answers`` is the answer store and is the only part that is required; a plan with no
    tier table and no timeline labels is a plan early in its interview, and it still builds.
    The drawings then say so rather than showing an empty chart.
    """

    answers: dict
    tiers: tuple[diagrams.Tier, ...] = ()
    timeline: diagrams.TimelineLabels | None = None


#: How each embedded drawing is produced. Keyed by filename, so adding a drawing is adding a
#: figure to the scaffold and an entry here, and forgetting the entry is a build failure
#: rather than a document pointing at nothing.
_GENERATORS: dict[str, Callable[[Plan], str]] = {
    "tier-ladder.svg": lambda plan: diagrams.tier_ladder_svg(plan.tiers),
    "mtd-timeline.svg": lambda plan: diagrams.mtd_timeline_svg(plan.timeline),
}


def figure_targets() -> dict[str, str]:
    """Every drawing a generated document embeds, as filename against path from the root.

    Read from the renderer's figure declarations rather than listed again, because those
    declarations are what write the links. One source, so the link and the file agree.
    """
    targets: dict[str, str] = {}
    for page in render.SCAFFOLD:
        directory = PurePosixPath(page.path).parent
        for figure in page.figures:
            target = directory / figure.path
            targets[target.name] = str(target)
    return targets


#: The drawings this build step writes, by filename.
DIAGRAMS: tuple[str, ...] = tuple(figure_targets())


def build_plan(root: Path, plan: Plan) -> tuple[str, ...]:
    """Write the whole repository under ``root``. Returns every path written, in order.

    Directories are created as needed and existing files are replaced, because a plan is
    regenerated after every interview and a build that refused to overwrite would make the
    second interview a manual merge.
    """
    written = [_write(root, page.path, page.text)
               for page in render.render(plan.answers)]
    written.extend(_write(root, target, _drawing(name, plan))
                   for name, target in figure_targets().items())
    return tuple(written)


def _drawing(name: str, plan: Plan) -> str:
    generator = _GENERATORS.get(name)
    if generator is None:
        raise BuildError(
            f"{name} is embedded in a generated document and nothing here writes it. A plan "
            f"that links a drawing nobody produced is the failure this module exists to "
            f"prevent; add a generator for it to _GENERATORS.")
    return generator(plan)


def _write(root: Path, path: str, text: str) -> str:
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return path
