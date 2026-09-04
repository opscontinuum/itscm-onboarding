"""Both reference diagrams, generated from their data rather than drawn by hand.

Why generated
-------------
The reference plan ships two SVGs. Reading their source showed that neither is art: the tier
ladder is a pure function of the tier table in ``docs/02`` section 2, and the timeline is a
fixed conceptual illustration with five substitutable strings whose bar widths carry no
data at all. A hand-drawn diagram goes stale the first time a number moves and nobody
notices, so both are functions here.

The recovered geometry
----------------------
The tier ladder plots maximum tolerable downtime on a logarithmic axis. Fitting the four bar
widths the reference draws against the four downtimes the table beside it states gives

    width(hours) = round(DECADE_WIDTH * log10(hours))

anchored at :data:`ORIGIN_X`, the one-hour position. Only a narrow band of
:data:`DECADE_WIDTH` reproduces all four widths exactly, which is why the constant is
pinned by a test rather than eyeballed.

The reference's axis does not obey its own geometry. Its four gridlines are evenly spaced,
so they sit up to 35 pixels from the positions the bars are drawn at, and a reader lining a
bar end up against a gridline reads the wrong number off the page. This generator puts each
gridline at its own logarithmic position instead. That is a deliberate divergence from the
reference and ``tests/test_diagrams`` records both sides of it.

Provenance in the picture
-------------------------
The reference plan hedges its cost percentages and its work recovery times in the prose
beside the chart, calling them shape-of-the-answer rather than a quote, and then draws them
on a chart carrying no hedge whatsoever. A bar has the visual authority of a measurement.
Putting an unattributed figure in one, unmarked, is how a guess becomes a design target that
somebody signs.

So an unsourced figure is marked in three independent channels:

* a dagger in the text,
* a dashed outline on the shape,
* a footnote on the drawing naming what the dagger means.

Three and not one, because roughly one man in twelve has a red or green colour deficiency
and these documents get photocopied for audits. Colour is never load-bearing here. Whether a
figure counts as sourced is not the drawing's opinion: the caller passes the provenance that
the answer store recorded, and an empty provenance is an unsourced figure.

The realisation states obey the same rule. Each of the five carries a distinct fill, a
distinct dash pattern and a literal word, so a photocopy still distinguishes a gap from a
conformant component. The default is ``unknown``; a state nobody recognises is never
conformant.
"""
from __future__ import annotations

import sys

if sys.version_info < (3, 11):
    raise RuntimeError(
        "itscp-author needs Python 3.11 or newer (this is "
        f"{sys.version_info.major}.{sys.version_info.minor}). There is no pip dependency to "
        "install; run the plugin under a newer interpreter."
    )

import math
from dataclasses import dataclass
from xml.sax.saxutils import escape

import itscp_realisation as realisation
import itscp_store as store

# --------------------------------------------------------------------- shared drawing


@dataclass(frozen=True)
class Point:
    """Where a piece of text is anchored."""

    x: float
    y: float


@dataclass(frozen=True)
class Box:
    """Where a shape sits and how big it is."""

    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class Canvas:
    """One drawing's size and the sentence a screen reader is given for it."""

    width: int
    height: int
    description: str


#: The one glyph that means "no recorded source", and the sentence that explains it. Both
#: appear on any drawing carrying an unsourced figure, and neither appears on one that is
#: not, so the mark never becomes decoration a reader learns to skip.
UNSOURCED_MARK = "†"
UNSOURCED_FOOTNOTE = ("† No recorded source. This figure is an engineering judgement rather "
                      "than a measurement, and its outline is dashed for the same reason.")

_STYLE_SHEET = """
  .bg   { fill: #ffffff; }
  .txt  { fill: #1a1a1a; font-family: ui-sans-serif, Helvetica, Arial, sans-serif; }
  .mut  { fill: #5c6470; font-family: ui-sans-serif, Helvetica, Arial, sans-serif; }
  .grid { stroke: #c2c8d0; }
  .ttl  { font-size: 15px; font-weight: 700; }
  .nm   { font-size: 13.5px; font-weight: 700; }
  .sub  { font-size: 11px; }
  .val  { font-size: 12.5px; font-weight: 700; }
"""


def _document(canvas: Canvas, body: list[str]) -> str:
    """One SVG file. Deterministic, so a regenerated diagram diffs only where data moved."""
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas.width} '
            f'{canvas.height}" width="{canvas.width}" height="{canvas.height}" role="img" '
            f'aria-label="{escape(canvas.description)}">')
    background = f'<rect class="bg" x="0" y="0" width="{canvas.width}" height="{canvas.height}"/>'
    return "\n".join([head, f"  <style>{_STYLE_SHEET}  </style>", f"  {background}",
                      *body, "</svg>", ""])


def _text(at: Point, style: str, content: str) -> str:
    return (f'  <text class="{style}" x="{_number(at.x)}" y="{_number(at.y)}">'
            f'{escape(content)}</text>')


def _rect(box: Box, style: str, extra: str = "") -> str:
    return (f'  <rect class="{style}" x="{_number(box.x)}" y="{_number(box.y)}" '
            f'width="{_number(box.width)}" height="{_number(box.height)}"{extra}/>')


def _number(value: float) -> str:
    """A coordinate as the shortest exact text, so whole numbers do not render as floats."""
    return str(int(value)) if float(value).is_integer() else str(value)


def _dash(provenance: str) -> str:
    """The dashed outline an unsourced shape wears, and nothing when the figure has a source."""
    return "" if provenance else f' stroke-dasharray="{UNSOURCED_DASHES}"'


def _dagger(text: str, provenance: str) -> str:
    """A label, with the dagger appended when the figure behind it has no recorded source."""
    return text if provenance else f"{text} {UNSOURCED_MARK}"


#: The dash pattern an unsourced outline wears. Long enough to read after a photocopy.
UNSOURCED_DASHES = "8 3"

#: Where a drawing's own text starts, on either drawing.
_MARGIN_X = 24

#: What a drawing says when the data behind it was never elicited. The answer store's rule
#: about a missing value applies to a missing drawing too: a chart with an axis and no bars
#: reads as "nothing is at risk here", which is a plausible default wearing a graph.
UNRECORDED_LADDER = "No tier table has been recorded for this plan."
UNRECORDED_TIMELINE = "No recovery activities have been recorded for this plan."


def _unrecorded(canvas: Canvas, title: str, note: str) -> str:
    """A drawing with nothing behind it: the store's own marker, never an empty chart."""
    return _document(canvas, [
        _text(Point(_MARGIN_X, 30), "txt ttl", title),
        _text(Point(_MARGIN_X, 60), "txt val", store.status_marker(None)),
        _text(Point(_MARGIN_X, 84), "mut sub", note),
    ])


# ------------------------------------------------------------------------ tier ladder

#: The one-hour position, and how far one decade of hours travels. Recovered by fitting the
#: reference chart's four bar widths against the four downtimes its table states; see the
#: module docstring. Do not round these without re-running section 7.
ORIGIN_X = 250
DECADE_WIDTH = 233.6

#: The axis, as pairs of hours and the words the reference uses for them. The words are
#: declared rather than computed so the drawing never invents a unit.
AXIS_TICKS: tuple[tuple[float, str], ...] = (
    (1, "1 hr"), (4, "4 hr"), (24, "1 day"), (72, "3 days"),
)
AXIS_TICK_HOURS: tuple[float, ...] = tuple(hours for hours, _ in AXIS_TICKS)

LADDER_CANVAS = Canvas(1040, 400,
                       "Recovery tiers plotted by maximum tolerable downtime on a "
                       "logarithmic axis against relative run cost")

LADDER_TITLE = "Recovery tiers by maximum tolerable downtime against relative run cost"
LADDER_SUBTITLE = ("The downtime axis is logarithmic and every gridline sits at its own "
                   "position on it.")
COST_COLUMN_HEADING = "run cost"

#: Every string this drawing may write that did not come from a tier.
LADDER_CHROME: tuple[str, ...] = (
    (LADDER_TITLE, LADDER_SUBTITLE, COST_COLUMN_HEADING, UNSOURCED_FOOTNOTE,
     UNRECORDED_LADDER, store.status_marker(None))
    + tuple(label for _, label in AXIS_TICKS)
)

#: The class marking a tier's downtime bar and its run-cost pill, so a test can find them.
BAR_CLASS = "bar"
COST_CLASS = "cost"

_FIRST_ROW_Y = 82
_ROW_PITCH = 65
_BAR_HEIGHT = 30
#: The run-cost column. Far enough right that the widest bar and its label clear it,
#: because a label that overlaps a shape is a label somebody will read wrongly.
_COST_PILL = Box(900, 0, 120, 26)
_AXIS_TOP_Y = 70
_AXIS_BOTTOM_Y = 336
_AXIS_LABEL_Y = 352
_FOOTNOTE_Y = 382
_LABEL_GAP = 14


@dataclass(frozen=True)
class Tier:
    """One recovery tier, as the tier table states it.

    ``mtd_provenance`` and ``cost_provenance`` are the provenance strings the answer store
    recorded for those two figures. Empty means no recorded source, which is what the
    reference plan's own prose says about its cost percentages, and it is what makes the
    drawing mark them.
    """

    name: str
    posture: str
    mtd_hours: float
    mtd_label: str
    cost_label: str
    mtd_provenance: str = ""
    cost_provenance: str = ""


def bar_width(hours: float) -> int:
    """How wide a bar for this many hours of downtime is, on the recovered logarithmic axis."""
    return round(DECADE_WIDTH * math.log10(hours))


def tick_x(hours: float) -> int:
    """Where the gridline for this many hours sits: its own position on that same axis."""
    return round(ORIGIN_X + DECADE_WIDTH * math.log10(hours))


def tier_ladder_svg(tiers: tuple[Tier, ...]) -> str:
    """The tier ladder as SVG, one row per tier, drawn from the tier table alone.

    No tier table is an unanswered question rather than an empty chart, so it draws the
    store's MISSING marker instead of an axis with nothing on it.
    """
    if not tiers:
        return _unrecorded(LADDER_CANVAS, LADDER_TITLE, UNRECORDED_LADDER)
    body = _ladder_heading() + _ladder_axis()
    for position, tier in enumerate(tiers):
        body.extend(_ladder_row(tier, _FIRST_ROW_Y + position * _ROW_PITCH))
    if any(not tier.cost_provenance or not tier.mtd_provenance for tier in tiers):
        body.append(_text(Point(_MARGIN_X, _FOOTNOTE_Y), "mut sub", UNSOURCED_FOOTNOTE))
    return _document(LADDER_CANVAS, body)


def _ladder_heading() -> list[str]:
    return [_text(Point(_MARGIN_X, 30), "txt ttl", LADDER_TITLE),
            _text(Point(_MARGIN_X, 49), "mut sub", LADDER_SUBTITLE),
            _text(Point(_COST_PILL.x, _AXIS_TOP_Y), "mut sub", COST_COLUMN_HEADING)]


def _ladder_axis() -> list[str]:
    lines = []
    for hours, label in AXIS_TICKS:
        position = tick_x(hours)
        lines.append(f'  <line class="grid" x1="{position}" y1="{_AXIS_TOP_Y}" '
                     f'x2="{position}" y2="{_AXIS_BOTTOM_Y}" stroke-width="1"/>')
        lines.append(_text(Point(position, _AXIS_LABEL_Y), "mut sub", label))
    return lines


def _ladder_row(tier: Tier, top: float) -> list[str]:
    width = bar_width(tier.mtd_hours)
    cost = Box(_COST_PILL.x, top + 2, _COST_PILL.width, _COST_PILL.height)
    return [
        _text(Point(_MARGIN_X, top + _LABEL_GAP), "txt nm", tier.name),
        _text(Point(_MARGIN_X, top + 30), "mut sub", tier.posture),
        _rect(Box(ORIGIN_X, top, width, _BAR_HEIGHT), BAR_CLASS,
              f' fill="#c2c8d0" stroke="#1a1a1a" stroke-width="1.2"'
              f'{_dash(tier.mtd_provenance)}'),
        _text(Point(ORIGIN_X + width + _LABEL_GAP, top + 20), "txt val",
              _dagger(tier.mtd_label, tier.mtd_provenance)),
        _rect(cost, COST_CLASS,
              f' rx="13" fill="#ffffff" stroke="#1a1a1a" stroke-width="1.2"'
              f'{_dash(tier.cost_provenance)}'),
        _text(Point(cost.x + 8, cost.y + 18), "mut val",
              _dagger(tier.cost_label, tier.cost_provenance)),
    ]


def tier_ladder_mermaid(tiers: tuple[Tier, ...]) -> str:
    """The same ladder as Mermaid, which a plan repository renders with no build step."""
    if not tiers:
        return _unrecorded_mermaid(LADDER_TITLE, UNRECORDED_LADDER)
    lines = ["flowchart TB", f'    LADDER["{_mermaid_safe(LADDER_TITLE)}"]']
    previous = "LADDER"
    for position, tier in enumerate(tiers):
        node = f"T{position}"
        lines.append(f'    {node}["{_ladder_node_text(tier)}"]')
        lines.append(f"    {previous} --> {node}")
        previous = node
    lines.extend(_MERMAID_SOURCE_CLASSES)
    for position, tier in enumerate(tiers):
        sourced = tier.mtd_provenance and tier.cost_provenance
        lines.append(f"    class T{position} {'sourced' if sourced else 'unsourced'}")
    if any(not tier.cost_provenance or not tier.mtd_provenance for tier in tiers):
        lines.append(f'    NOTE["{_mermaid_safe(UNSOURCED_FOOTNOTE)}"]')
        lines.append(f"    {previous} --- NOTE")
    return "\n".join(lines) + "\n"


def _ladder_node_text(tier: Tier) -> str:
    parts = (tier.name, tier.posture,
             _dagger(tier.mtd_label, tier.mtd_provenance),
             f"{COST_COLUMN_HEADING} {_dagger(tier.cost_label, tier.cost_provenance)}")
    return "<br/>".join(_mermaid_safe(part) for part in parts)


_MERMAID_SOURCE_CLASSES = (
    "    classDef sourced fill:#ffffff,stroke:#1a1a1a,stroke-width:2px,color:#1a1a1a",
    f"    classDef unsourced fill:#ffffff,stroke:#1a1a1a,stroke-width:2px,"
    f"stroke-dasharray:{UNSOURCED_DASHES},color:#1a1a1a",
)


# --------------------------------------------------------------------- the MTD timeline

TIMELINE_CANVAS = Canvas(880, 330,
                         "Timeline showing the recovery point objective before the "
                         "incident, then recovery time and work recovery time after it, "
                         "with maximum tolerable downtime spanning both")

TIMELINE_TITLE = "Maximum tolerable downtime is recovery time plus work recovery time"
TIMELINE_SUBTITLE = ("The recovery point objective is measured backwards from the incident. "
                     "Only the maximum tolerable downtime is felt by the business.")

#: The four spans and the three events the timeline names. Conceptual and fixed: this
#: drawing illustrates an order of events, so no estate changes any of these words.
DATA_AT_RISK_HEADING = "RPO, data at risk"
RECOVERY_HEADING = "RTO"
WORK_RECOVERY_HEADING = "WRT"
TOTAL_HEADING = "MTD"
INCIDENT_CAPTION = "INCIDENT"
AVAILABLE_CAPTION = "SYSTEMS AVAILABLE"
USABLE_CAPTION = "BUSINESS USABLE"

TIMELINE_CHROME: tuple[str, ...] = (
    TIMELINE_TITLE, TIMELINE_SUBTITLE, DATA_AT_RISK_HEADING, RECOVERY_HEADING,
    WORK_RECOVERY_HEADING, TOTAL_HEADING, INCIDENT_CAPTION, AVAILABLE_CAPTION,
    USABLE_CAPTION,
)

#: The three bar widths. They carry no data whatsoever: this is a conceptual illustration,
#: not a plot, and a reader who measures them learns nothing. Fixed here so that nothing in
#: the substitutable strings can resize one and imply a measurement that was never taken.
_DATA_AT_RISK_BAR = Box(110, 86, 190, 30)
_RECOVERY_BAR = Box(300, 146, 240, 34)
_WORK_RECOVERY_BAR = Box(540, 146, 250, 34)
_TOTAL_BAR = Box(470, 236, 150, 28)
_BASELINE_Y = 286
_CAPTION_Y = 308


@dataclass(frozen=True)
class TimelineLabels:
    """The five strings this drawing substitutes. Everything else on it is conceptual."""

    data_at_risk: str
    recovery_activities: str
    recovery_owner: str
    work_recovery_activities: str
    work_recovery_owner: str


def mtd_timeline_svg(labels: TimelineLabels | None) -> str:
    """The recovery timeline as SVG. Five strings vary; the geometry never does.

    No labels is an unanswered question, and draws the store's MISSING marker for the same
    reason the ladder does.
    """
    if labels is None:
        return _unrecorded(TIMELINE_CANVAS, TIMELINE_TITLE, UNRECORDED_TIMELINE)
    body = [
        _text(Point(28, 34), "txt ttl", TIMELINE_TITLE),
        _text(Point(28, 54), "mut sub", TIMELINE_SUBTITLE),
        *_timeline_span(_DATA_AT_RISK_BAR, DATA_AT_RISK_HEADING, labels.data_at_risk),
        *_timeline_span(_RECOVERY_BAR, RECOVERY_HEADING, labels.recovery_activities),
        _text(Point(_RECOVERY_BAR.x + 8, 211), "mut sub", labels.recovery_owner),
        *_timeline_span(_WORK_RECOVERY_BAR, WORK_RECOVERY_HEADING,
                        labels.work_recovery_activities),
        _text(Point(_WORK_RECOVERY_BAR.x + 8, 211), "mut sub", labels.work_recovery_owner),
        _rect(_TOTAL_BAR, "grid", ' rx="6" fill="#ffffff" stroke="#1a1a1a" stroke-width="1.5"'),
        _text(Point(_TOTAL_BAR.x + 10, _TOTAL_BAR.y + 19), "txt val", TOTAL_HEADING),
        f'  <line class="grid" x1="110" y1="{_BASELINE_Y}" x2="850" y2="{_BASELINE_Y}" '
        f'stroke-width="1.5"/>',
        *_timeline_event(_RECOVERY_BAR.x, INCIDENT_CAPTION),
        *_timeline_event(_WORK_RECOVERY_BAR.x, AVAILABLE_CAPTION),
        *_timeline_event(_WORK_RECOVERY_BAR.x + _WORK_RECOVERY_BAR.width, USABLE_CAPTION),
    ]
    return _document(TIMELINE_CANVAS, body)


def _timeline_span(box: Box, heading: str, detail: str) -> list[str]:
    return [
        _rect(box, "grid", ' rx="6" fill="#ffffff" stroke="#1a1a1a" stroke-width="1.5"'),
        _text(Point(box.x + 10, box.y + 21), "txt val", heading),
        _text(Point(box.x + 8, box.y + box.height + 16), "mut sub", detail),
    ]


def _timeline_event(x: float, caption: str) -> list[str]:
    return [f'  <circle cx="{_number(x)}" cy="{_BASELINE_Y}" r="5" fill="#1a1a1a"/>',
            _text(Point(x, _CAPTION_Y), "txt sub", caption)]


def mtd_timeline_mermaid(labels: TimelineLabels | None) -> str:
    """The same timeline as Mermaid, for a repository that renders fences and builds nothing."""
    if labels is None:
        return _unrecorded_mermaid(TIMELINE_TITLE, UNRECORDED_TIMELINE)
    spans = ((DATA_AT_RISK_HEADING, labels.data_at_risk, ""),
             (RECOVERY_HEADING, labels.recovery_activities, labels.recovery_owner),
             (WORK_RECOVERY_HEADING, labels.work_recovery_activities,
              labels.work_recovery_owner))
    lines = ["flowchart LR", f'    START(["{_mermaid_safe(INCIDENT_CAPTION)}"])']
    for position, (heading, detail, owner) in enumerate(spans):
        parts = [heading, detail] + ([owner] if owner else [])
        lines.append(f'    S{position}["' + "<br/>".join(
            _mermaid_safe(part) for part in parts) + '"]')
    lines.extend((
        f'    MID(["{_mermaid_safe(AVAILABLE_CAPTION)}"])',
        f'    END_(["{_mermaid_safe(USABLE_CAPTION)}"])',
        "    S0 --> START",
        "    START --> S1 --> MID --> S2 --> END_",
        f'    TOTAL["{_mermaid_safe(TOTAL_HEADING)}: {_mermaid_safe(TIMELINE_TITLE)}"]',
        "    START -.-> TOTAL",
        "    END_ -.-> TOTAL",
    ))
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ realisation states

@dataclass(frozen=True)
class RealisationStyle:
    """How one realisation state is drawn, in three channels that survive a photocopy."""

    fill: str
    stroke: str
    dashes: str
    label: str


#: One style per state of :mod:`itscp_realisation`. Distinct fills, distinct dash patterns
#: and distinct words, so that no two states differ by colour alone. ``unknown`` is first
#: because it is the default and the one a reader meets most often.
REALISATION_STYLES: dict[str, RealisationStyle] = {
    "unknown": RealisationStyle("#f1f3f5", "#5c6470", "2 4", "unknown, not checked"),
    "conformant": RealisationStyle("#e3f5e8", "#0d652d", "0", "conformant, as designed"),
    "gap": RealisationStyle("#fdecea", "#a50e0e", "8 3", "gap, required and not found"),
    "shadow": RealisationStyle("#e6f0fd", "#0b57d0", "1 3", "shadow, found and not required"),
    "drift": RealisationStyle("#fef4e0", "#a15800", "10 3 2 3", "drift, found and differing"),
}

REALISATION_LEGEND_HEADING = "Realisation, derived from a read-only source"


def style_for(state: str) -> RealisationStyle:
    """How one state is drawn. A state nobody recognises is unknown, and never conformant."""
    return REALISATION_STYLES.get(state, REALISATION_STYLES["unknown"])


def realisation_mermaid(reconciliations: tuple[realisation.Reconciliation, ...]) -> str:
    """Reconciled components as Mermaid, each carrying its state as a word and a stroke.

    The legend is always drawn, including for states nothing is currently in, because a
    reader who has never seen a drift needs to know the pattern means something.
    """
    lines = ["flowchart TB", f'    subgraph LEGEND["{_mermaid_safe(REALISATION_LEGEND_HEADING)}"]']
    for state, style in REALISATION_STYLES.items():
        lines.append(f'    KEY_{state}["{_mermaid_safe(style.label)}"]')
    lines.append("    end")
    for position, reconciliation in enumerate(reconciliations):
        lines.append(f'    N{position}["{_reconciliation_node_text(reconciliation)}"]')
    lines.extend(f"    classDef {state} fill:{style.fill},stroke:{style.stroke},"
                 f"stroke-width:2px,stroke-dasharray:{style.dashes},color:#1a1a1a"
                 for state, style in REALISATION_STYLES.items())
    lines.extend(f"    class KEY_{state} {state}" for state in REALISATION_STYLES)
    lines.extend(f"    class N{position} {style_state(reconciliation)}"
                 for position, reconciliation in enumerate(reconciliations))
    return "\n".join(lines) + "\n"


def style_state(reconciliation: realisation.Reconciliation) -> str:
    """The state this reconciliation is drawn as: its own, or unknown if it names no style."""
    return reconciliation.state if reconciliation.state in REALISATION_STYLES else "unknown"


def _reconciliation_node_text(reconciliation: realisation.Reconciliation) -> str:
    """The identity, the state as a literal word, and what the state costs where it costs.

    The reconciliation's own label repeats the bare state word for the three states that
    carry no consequence, so it is only added where it says something the style's label
    does not: which recovery target a gap invalidates, or which attribute drifted.
    """
    parts = [reconciliation.identity, style_for(reconciliation.state).label]
    if reconciliation.label != reconciliation.state:
        parts.append(reconciliation.label)
    return "<br/>".join(_mermaid_safe(part) for part in parts)


def _unrecorded_mermaid(title: str, note: str) -> str:
    """The Mermaid form of a drawing with nothing behind it."""
    return "\n".join((
        "flowchart TB",
        f'    UNRECORDED["{_mermaid_safe(title)}<br/>'
        f'{_mermaid_safe(store.status_marker(None))}<br/>{_mermaid_safe(note)}"]',
    )) + "\n"


def _mermaid_safe(text: str) -> str:
    """One string as Mermaid node text.

    Quotation marks end a node label and backticks close the fence the diagram is written
    inside, which spills it into the document as source. Both are replaced rather than
    escaped, because Mermaid has no escape for either.
    """
    return text.replace('"', "'").replace("`", "'")
