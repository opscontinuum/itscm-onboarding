"""Both reference diagrams are generatable, and neither may launder an unsourced number.

The tier ladder is a pure function of the tier table. Its geometry was recovered by fitting
the four bar widths in ``docs/diagrams/tier-ladder.svg`` against the four maximum tolerable
downtimes the table beside it states, and it is a clean logarithmic fit: a bar for a
downtime of ``h`` hours is ``round(DECADE_WIDTH * log10(h))`` pixels wide, anchored at the
one-hour origin. :func:`_the_recovered_geometry_reproduces_the_reference` pins that against
the four widths the reference actually draws, so the constant cannot drift.

The reference's own axis does not obey that geometry. Its four gridlines are evenly spaced,
so they sit up to 35 pixels away from the positions the bars are drawn at, and a reader
lining a bar end against a gridline reads the wrong number off the page.
:func:`_gridlines_sit_at_their_own_log_positions` asserts the property the generator holds
to, and :func:`_the_reference_axis_does_not_hold_the_property` records what the reference
does instead, so the difference is a documented decision rather than a silent divergence.

The other half of this section is provenance. The reference plan hedges its cost
percentages and its work recovery times in prose, in the document the chart sits in, and
then draws them on a chart that carries no hedge at all. A number that arrives with the
visual authority of a measured bar is a number a reader will act on, so the generator marks
an unsourced figure in three independent channels: a dagger in the text, a dashed stroke on
the shape, and a footnote naming what the dagger means. Three, because roughly one man in
twelve has a red or green deficiency and these documents get photocopied for audits, so
neither colour nor a single glyph is enough on its own.

The realisation states are held to the same rule. Each of the five carries a distinct fill,
a distinct dash pattern and a literal word, and the checks below assert that no two states
are distinguishable by fill alone. The default is unknown; a state nobody recognises is
never conformant.
"""
from __future__ import annotations

import math
import sys
import xml.etree.ElementTree as ElementTree
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import itscp_diagrams as diagrams
import itscp_realisation as realisation
import itscp_store as store
from harness import Section, equal

#: The four maximum tolerable downtimes the reference tier table states, in hours, and the
#: four bar widths the reference chart draws for them. The geometry has to reproduce these.
REFERENCE_TIER_HOURS: tuple[float, ...] = (2, 6, 24, 120)
REFERENCE_BAR_WIDTHS: tuple[int, ...] = (70, 182, 322, 486)

#: Where the reference draws its four axis gridlines, and the downtimes it labels them with.
#: Evenly spaced, which is the defect: they are not the log positions of those downtimes.
REFERENCE_TICK_HOURS: tuple[float, ...] = (1, 4, 24, 72)
REFERENCE_TICK_POSITIONS: tuple[int, ...] = (250, 407, 563, 719)

SVG = "{http://www.w3.org/2000/svg}"


def main() -> None:
    section = Section("7", "generated diagrams")

    section.check("the recovered geometry reproduces the reference bars",
                  _the_recovered_geometry_reproduces_the_reference)
    section.check("gridlines sit at their own log positions",
                  _gridlines_sit_at_their_own_log_positions)
    section.check("the reference axis does not hold that property",
                  _the_reference_axis_does_not_hold_the_property)
    section.check("the ladder is well-formed SVG", _the_ladder_is_well_formed)
    section.check("the ladder draws one bar per tier at its own width",
                  _the_ladder_draws_a_bar_per_tier)
    section.check("every string on the ladder comes from the tiers or the chrome",
                  _the_ladder_says_nothing_of_its_own)
    section.check("an unsourced figure is marked in the text", _unsourced_carries_the_dagger)
    section.check("an unsourced figure is marked in the stroke", _unsourced_carries_dashes)
    section.check("an unsourced figure is explained in a footnote", _unsourced_carries_a_note)
    section.check("a sourced ladder carries no dagger and no dashes", _sourced_is_unmarked)
    section.check("the ladder renders as Mermaid too", _the_ladder_renders_as_mermaid)
    section.check("a ladder with no tier table says so, in the store's own words",
                  _an_unrecorded_ladder_says_so)

    section.check("the timeline is well-formed SVG", _the_timeline_is_well_formed)
    section.check("the timeline substitutes exactly five strings",
                  _the_timeline_substitutes_five_strings)
    section.check("the timeline's bar widths carry no data",
                  _the_timeline_widths_are_fixed)
    section.check("the timeline renders as Mermaid too", _the_timeline_renders_as_mermaid)
    section.check("a timeline with no labels says so, in the store's own words",
                  _an_unrecorded_timeline_says_so)

    section.check("every realisation state has a fill", _states_have_distinct_fills)
    section.check("every realisation state has its own dash pattern",
                  _states_have_distinct_dashes)
    section.check("every realisation state has a literal label", _states_have_literal_labels)
    section.check("no state is distinguishable by colour alone", _colour_is_never_the_only_cue)
    section.check("an unrecognised state is unknown, never conformant",
                  _the_default_state_is_unknown)
    section.check("a reconciliation renders with its state's label", _reconciliations_render)

    section.check("Mermaid output carries no fence-breaking backtick", _mermaid_is_fence_safe)
    section.check("generating twice produces the same bytes", _generation_is_deterministic)

    section.finish()


# ------------------------------------------------------------------------- test data

def _tiers(cost_provenance: str = "") -> tuple[diagrams.Tier, ...]:
    """The reference plan's four tiers. Cost provenance is empty unless a check supplies one.

    Empty is the honest default and the reference's own position: its cost percentages are
    marked in prose as shape-of-the-answer rather than a quote.
    """
    names = ("Tier 0 - Platinum", "Tier 1 - Gold", "Tier 2 - Silver", "Tier 3 - Bronze")
    postures = ("hot standby", "warm pilot light", "cold pre-staged", "backup and restore")
    labels = ("MTD 2 hr or less", "MTD 6 hr or less", "MTD 24 hr or less",
              "MTD 5 days or less")
    costs = ("90 to 100 per cent", "45 to 60 per cent", "20 to 30 per cent",
             "5 to 10 per cent")
    return tuple(
        diagrams.Tier(name=name, posture=posture, mtd_hours=hours, mtd_label=label,
                      cost_label=cost, mtd_provenance="interview:business-owner:2026-09-03",
                      cost_provenance=cost_provenance)
        for name, posture, hours, label, cost
        in zip(names, postures, REFERENCE_TIER_HOURS, labels, costs))


def _labels(**overrides) -> diagrams.TimelineLabels:
    fields = {
        "data_at_risk": "committed work not yet replicated",
        "recovery_activities": "database open, application tier up, traffic steered",
        "recovery_owner": "owner: infrastructure owner",
        "work_recovery_activities": "queue cleanup, interface replay, reconciliation",
        "work_recovery_owner": "owner: business owner",
    }
    fields.update(overrides)
    return diagrams.TimelineLabels(**fields)


def _reconciliations() -> tuple[realisation.Reconciliation, ...]:
    return tuple(
        realisation.Reconciliation(
            identity=f"component-{position}", source="oci-discovery", state=state,
            reason="derived for this check", owner="infrastructure owner",
            consequence="the tier 0 recovery time objective",
            differing=("shape",) if state == "drift" else ())
        for position, state in enumerate(realisation.REALISATION_STATES))


def _rects(svg: str) -> list[ElementTree.Element]:
    return list(ElementTree.fromstring(svg).iter(f"{SVG}rect"))


def _texts(svg: str) -> list[str]:
    return [(element.text or "").strip()
            for element in ElementTree.fromstring(svg).iter(f"{SVG}text")]


# --------------------------------------------------------------------- the geometry

def _the_recovered_geometry_reproduces_the_reference() -> None:
    equal(tuple(diagrams.bar_width(hours) for hours in REFERENCE_TIER_HOURS),
          REFERENCE_BAR_WIDTHS,
          "the generated bar widths against the four the reference draws")


def _gridlines_sit_at_their_own_log_positions() -> None:
    for hours in diagrams.AXIS_TICK_HOURS:
        expected = diagrams.ORIGIN_X + diagrams.DECADE_WIDTH * math.log10(hours)
        equal(diagrams.tick_x(hours), round(expected),
              f"the gridline for {hours} hours")


def _the_reference_axis_does_not_hold_the_property() -> None:
    """Recorded, not asserted away: the reference's gridlines are evenly spaced.

    Kept as a check so that if somebody ever "corrects" the generator to match the
    reference's axis, this fails and says why that would be the wrong direction.
    """
    spacings = {second - first for first, second
                in zip(REFERENCE_TICK_POSITIONS, REFERENCE_TICK_POSITIONS[1:])}
    assert max(spacings) - min(spacings) <= 1, (
        "the reference's gridlines are not evenly spaced after all; re-derive the axis")
    drifts = [abs(position - (diagrams.ORIGIN_X
                              + diagrams.DECADE_WIDTH * math.log10(hours)))
              for hours, position in zip(REFERENCE_TICK_HOURS, REFERENCE_TICK_POSITIONS)]
    assert max(drifts) > diagrams.DECADE_WIDTH / 10, (
        f"the reference's gridlines are within {max(drifts):.1f}px of their log positions, "
        f"so the defect this generator fixes may no longer exist")


def _the_ladder_is_well_formed() -> None:
    ElementTree.fromstring(diagrams.tier_ladder_svg(_tiers()))


def _the_ladder_draws_a_bar_per_tier() -> None:
    widths = [int(rect.get("width")) for rect in _rects(diagrams.tier_ladder_svg(_tiers()))
              if rect.get("class") == diagrams.BAR_CLASS]
    equal(tuple(widths), REFERENCE_BAR_WIDTHS, "the bar widths the ladder draws")


def _the_ladder_says_nothing_of_its_own() -> None:
    tiers = _tiers()
    permitted = set(diagrams.LADDER_CHROME)
    for tier in tiers:
        permitted.update((tier.name, tier.posture, tier.mtd_label, tier.cost_label))
        permitted.update((f"{tier.mtd_label} {diagrams.UNSOURCED_MARK}",
                          f"{tier.cost_label} {diagrams.UNSOURCED_MARK}"))
    for text in _texts(diagrams.tier_ladder_svg(tiers)):
        assert text in permitted, f"the ladder wrote a string of its own: {text!r}"


# ------------------------------------------------------------------- the provenance

def _unsourced_carries_the_dagger() -> None:
    texts = _texts(diagrams.tier_ladder_svg(_tiers()))
    marked = [text for text in texts if text.endswith(diagrams.UNSOURCED_MARK)]
    equal(len(marked), len(REFERENCE_TIER_HOURS),
          "the cost labels marked as unsourced, one per tier")


def _unsourced_carries_dashes() -> None:
    pills = [rect for rect in _rects(diagrams.tier_ladder_svg(_tiers()))
             if rect.get("class") == diagrams.COST_CLASS]
    equal(len(pills), len(REFERENCE_TIER_HOURS), "the cost pills the ladder draws")
    for pill in pills:
        assert pill.get("stroke-dasharray"), (
            "an unsourced cost pill is drawn with a solid stroke, so it survives greyscale "
            "looking exactly like a measured one")


def _unsourced_carries_a_note() -> None:
    assert diagrams.UNSOURCED_FOOTNOTE in diagrams.tier_ladder_svg(_tiers()), (
        "the ladder carries unsourced figures and no footnote saying so")


def _sourced_is_unmarked() -> None:
    svg = diagrams.tier_ladder_svg(_tiers("document:finance/tier-costs.md"))
    assert diagrams.UNSOURCED_MARK not in svg, "a fully sourced ladder still carries a dagger"
    assert diagrams.UNSOURCED_FOOTNOTE not in svg, "a fully sourced ladder still footnotes one"
    for rect in _rects(svg):
        assert not rect.get("stroke-dasharray"), "a fully sourced ladder still dashes a shape"


def _the_ladder_renders_as_mermaid() -> None:
    mermaid = diagrams.tier_ladder_mermaid(_tiers())
    for tier in _tiers():
        for text in (tier.name, tier.mtd_label, tier.cost_label):
            assert text in mermaid, f"the Mermaid ladder omits {text!r}"
    assert diagrams.UNSOURCED_MARK in mermaid, "the Mermaid ladder drops the unsourced mark"
    assert "stroke-dasharray" in mermaid, "the Mermaid ladder drops the unsourced stroke"


# --------------------------------------------------------------------- the timeline

def _an_unrecorded_ladder_says_so() -> None:
    """No tier table is an unanswered question, not an empty chart.

    A chart with an axis and no bars reads as "nothing is at risk". The same rule the answer
    store applies to a missing value applies to a missing drawing: it renders as the marker.
    """
    svg = diagrams.tier_ladder_svg(())
    ElementTree.fromstring(svg)
    assert store.status_marker(None) in svg, (
        "an unrecorded ladder drew an empty chart instead of the store's MISSING marker")
    assert diagrams.UNRECORDED_LADDER in svg, "an unrecorded ladder says nothing about why"


def _an_unrecorded_timeline_says_so() -> None:
    svg = diagrams.mtd_timeline_svg(None)
    ElementTree.fromstring(svg)
    assert store.status_marker(None) in svg, (
        "an unrecorded timeline drew an empty illustration instead of the MISSING marker")
    assert diagrams.UNRECORDED_TIMELINE in svg, "an unrecorded timeline says nothing about why"


def _the_timeline_is_well_formed() -> None:
    ElementTree.fromstring(diagrams.mtd_timeline_svg(_labels()))


def _the_timeline_substitutes_five_strings() -> None:
    substitutable = vars(_labels())
    equal(len(substitutable), 5, "the number of substitutable strings on the timeline")
    baseline = diagrams.mtd_timeline_svg(_labels())
    for name in substitutable:
        changed = diagrams.mtd_timeline_svg(_labels(**{name: "a different string"}))
        assert changed != baseline, f"{name} is declared substitutable and changes nothing"
        assert "a different string" in changed, f"{name} did not reach the drawing"


def _the_timeline_widths_are_fixed() -> None:
    """The bars illustrate an order of events, not a measurement, so nothing may resize them."""
    def widths(labels) -> list[str]:
        return [rect.get("width") for rect in _rects(diagrams.mtd_timeline_svg(labels))]

    equal(widths(_labels(data_at_risk="a very much longer string than the default one")),
          widths(_labels()), "the timeline's bar widths after a label changed")


def _the_timeline_renders_as_mermaid() -> None:
    mermaid = diagrams.mtd_timeline_mermaid(_labels())
    for text in vars(_labels()).values():
        assert text in mermaid, f"the Mermaid timeline omits {text!r}"


# ------------------------------------------------------------------ realisation states

def _styles() -> dict[str, diagrams.RealisationStyle]:
    return diagrams.REALISATION_STYLES


def _states_have_distinct_fills() -> None:
    equal(sorted(_styles()), sorted(realisation.REALISATION_STATES),
          "the styled states against the states that exist")
    fills = [style.fill for style in _styles().values()]
    equal(len(set(fills)), len(fills), "the number of distinct fills")


def _states_have_distinct_dashes() -> None:
    dashes = [style.dashes for style in _styles().values()]
    equal(len(set(dashes)), len(dashes), "the number of distinct dash patterns")


def _states_have_literal_labels() -> None:
    mermaid = diagrams.realisation_mermaid(_reconciliations())
    for state, style in _styles().items():
        assert style.label, f"{state} has no literal label"
        assert style.label in mermaid, f"{state} renders without its literal label"


def _colour_is_never_the_only_cue() -> None:
    """Two states may share nothing but a fill, because a photocopy keeps neither."""
    styles = list(_styles().values())
    for position, style in enumerate(styles):
        for other in styles[position + 1:]:
            assert (style.dashes, style.label) != (other.dashes, other.label), (
                f"{style.label} and {other.label} differ only by colour, so a greyscale "
                f"reader cannot tell a gap from a conformant component")


def _the_default_state_is_unknown() -> None:
    for state in ("", "nonsense", "CONFORMANT"):
        equal(diagrams.style_for(state).label, _styles()["unknown"].label,
              f"the style for the unrecognised state {state!r}")


def _reconciliations_render() -> None:
    mermaid = diagrams.realisation_mermaid(_reconciliations())
    for reconciliation in _reconciliations():
        assert reconciliation.identity in mermaid, (
            f"{reconciliation.identity} is reconciled and does not appear")


# ---------------------------------------------------------------------- both formats

def _mermaid_is_fence_safe() -> None:
    for mermaid in (diagrams.tier_ladder_mermaid(_tiers()),
                    diagrams.mtd_timeline_mermaid(_labels()),
                    diagrams.realisation_mermaid(_reconciliations())):
        assert "`" not in mermaid, (
            "a backtick in Mermaid source closes the fence around it and spills the "
            "diagram into the document as text")


def _generation_is_deterministic() -> None:
    equal(diagrams.tier_ladder_svg(_tiers()), diagrams.tier_ladder_svg(_tiers()),
          "two renderings of the same ladder")
    equal(diagrams.mtd_timeline_svg(_labels()), diagrams.mtd_timeline_svg(_labels()),
          "two renderings of the same timeline")


if __name__ == "__main__":
    main()
