"""DERIVED: the capture sheet, as one file that opens in a browser and needs nothing else.

``docs/manual/worksheet.html`` is what the facilitator actually types into during a session.
It carries the same questions as the printed worksheets, from the same bank, and it exists
because a Markdown table with empty cells is a form only in the sense that a napkin is one:
you cannot tab through it, it cannot tell you which cells are still blank, and typing into
pipe-delimited columns while somebody is talking is miserable.

**The questions are baked in at generation time, not read at runtime.** Opening a local file
and fetching sibling documents is blocked by every current browser, because a ``file://``
page has a null origin. A capture sheet that needs a web server is a capture sheet that does
not work in a meeting room with no wifi and a laptop somebody borrowed, which is the room
this is for. So the bank is serialized into the page, and the only cost is regenerating when
the bank changes, which is the same cost the Markdown already has and the same test catches
it.

Everything the page needs is inside it: no stylesheet, no font, no script, no image, no call
out to anything. It saves to the browser's local storage as you type, so a closed tab is not
a lost session, and it writes a JSON file on demand, so a dead laptop is not one either.

A question holds as many answers as the room gave it. Two people contradicting each other is
the finding the method most wants kept, so the page records both and asks whose decision it
is, rather than making the facilitator choose in the moment or bury the second one in a note.

The JSON it writes is the answer store's record shape with the worksheet's own column names:
what was said, who said it, confidence, the mechanism behind a figure, the read-back, and an
owner where nobody in the room could answer. That is what makes the session's output something
an organization can later transcribe into the toolkit rather than retype.

Rendered by :mod:`itscp_manual`, which owns the phase sequence and passes it in. This module
knows about questions and HTML and nothing about where a phase sits.
"""
from __future__ import annotations

import json
from typing import Any

import itscp_questions as bank

#: The confidence rubric as a facilitator marks it, and the vocabulary the store uses. H, M
#: and L are what fits in a column and what people say out loud; the store wants words.
CONFIDENCE_CHOICES: tuple[tuple[str, str, str], ...] = (
    ("high", "H", "Measured, or read off a screen while you waited"),
    ("medium", "M", "Confident from experience, never measured"),
    ("low", "L", "Worked out in the room just now"),
)

#: What a row can be, beyond answered. The four the method allows, in the order a facilitator
#: reaches for them: most answers are answered, and the next most common outcome by far is
#: that nobody in the room knows.
STATUS_CHOICES: tuple[tuple[str, str, str], ...] = (
    ("ANSWERED", "Answered", ""),
    ("MISSING", "Nobody knew", "Name whoever can answer"),
    ("DEFERRED", "Deferred", "Name an owner and a date"),
    ("NOT_APPLICABLE", "Not applicable", "State why, in a sentence"),
)


def _question_payload(question: bank.Question) -> dict[str, Any]:
    """One question, as the page needs it. Nothing the page does not render."""
    payload: dict[str, Any] = {
        "id": question.id,
        "prompt": question.prompt,
        "records": question.records,
        "owner": question.owner_role,
        "kind": question.kind,
        "row": question.coverage_row,
        "writtenTo": question.written_to,
    }
    if question.unit:
        payload["unit"] = question.unit
    if question.guidance:
        payload["guidance"] = question.guidance
    if question.options:
        payload["options"] = list(question.options)
    if question.columns:
        payload["columns"] = list(question.columns)
    if question.enum_columns:
        payload["columnOptions"] = {name: list(values)
                                    for name, values in question.enum_columns.items()}
    if question.mechanism_required:
        payload["mechanism"] = question.mechanism_prompt
    if question.readback_required:
        payload["readback"] = True
    if question.seedable:
        payload["seeded"] = True
    return payload


def payload(phases: tuple[Any, ...]) -> dict[str, Any]:
    """Everything the page renders, in the order it renders it."""
    sheets = []
    for phase in phases:
        questions = [entry for namespace in phase.namespaces
                     for entry in bank.for_namespace(namespace)]
        sheets.append({
            "number": phase.number,
            "title": phase.title,
            "room": phase.room.replace("**", ""),
            "produces": phase.produces,
            "questions": [_question_payload(question) for question in questions],
        })
    return {
        "statuses": [{"key": key, "label": label, "hint": hint}
                     for key, label, hint in STATUS_CHOICES],
        "confidence": [{"key": key, "short": short, "hint": hint}
                       for key, short, hint in CONFIDENCE_CHOICES],
        "phases": sheets,
    }


def _embed(data: dict[str, Any]) -> str:
    """JSON, safe to sit inside a script element."""
    return json.dumps(data, indent=1, ensure_ascii=False).replace("</", "<\\/")


_STYLE = """
*, *::before, *::after { box-sizing: border-box; }
:root {
  --ink: #1a1c1e; --dim: #5b6166; --faint: #8b9299; --line: #d9dee2;
  --page: #fbfbfa; --card: #ffffff; --accent: #14507a; --warn: #8a5300;
  --warn-bg: #fdf5e6; --ok: #1c6b45;
}
body {
  margin: 0; background: var(--page); color: var(--ink);
  font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}
header {
  position: sticky; top: 0; z-index: 5; background: var(--card);
  border-bottom: 1px solid var(--line); padding: 12px 20px;
}
.bar { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
.bar h1 { font-size: 17px; margin: 0; letter-spacing: -0.01em; }
.bar .spacer { flex: 1 1 auto; }
.meta { display: flex; gap: 8px; flex-wrap: wrap; }
.meta input { width: 190px; }
input, select, textarea {
  font: inherit; color: inherit; background: var(--card);
  border: 1px solid var(--line); border-radius: 5px; padding: 6px 8px;
}
input:focus, select:focus, textarea:focus { outline: 2px solid var(--accent); outline-offset: -1px; }
textarea { width: 100%; resize: vertical; min-height: 2.6em; }
button {
  font: inherit; cursor: pointer; background: var(--card); color: var(--ink);
  border: 1px solid var(--line); border-radius: 5px; padding: 6px 12px;
}
button:hover { border-color: var(--accent); color: var(--accent); }
button.primary { background: var(--accent); color: #fff; border-color: var(--accent); }
button.primary:hover { filter: brightness(1.12); color: #fff; }
nav { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
nav button { padding: 4px 10px; font-size: 14px; }
nav button[aria-current="true"] { background: var(--ink); color: #fff; border-color: var(--ink); }
nav .count { color: var(--faint); font-variant-numeric: tabular-nums; margin-left: 6px; }
nav button[aria-current="true"] .count { color: #c9ced3; }
main { max-width: 880px; margin: 0 auto; padding: 24px 20px 96px; }
.room { color: var(--dim); font-size: 15px; margin: 0 0 20px; }
.group { margin: 30px 0 10px; font-size: 13px; letter-spacing: 0.07em;
         text-transform: uppercase; color: var(--faint); }
.q { background: var(--card); border: 1px solid var(--line); border-radius: 8px;
     padding: 16px 18px; margin-bottom: 14px; }
.q.done { border-left: 3px solid var(--ok); }
.q.flagged { border-left: 3px solid var(--warn); }
.ask { font-size: 17px; margin: 0 0 4px; }
.records { color: var(--dim); font-size: 14px; margin: 0 0 12px; }
.key { float: right; color: var(--faint); font-size: 12px; font-family: ui-monospace, Menlo, Consolas, monospace; }
.field { display: flex; flex-wrap: wrap; gap: 10px; align-items: flex-end; margin-bottom: 10px; }
.field label { display: block; font-size: 12px; color: var(--dim); margin-bottom: 3px; }
.field .grow { flex: 1 1 240px; }
.field .grow input, .field .grow select { width: 100%; }
.sure { display: flex; gap: 4px; }
.sure button { padding: 6px 10px; min-width: 34px; }
.sure button[aria-pressed="true"] { background: var(--ink); color: #fff; border-color: var(--ink); }
.note { font-size: 14px; color: var(--dim); border-left: 2px solid var(--line);
        padding-left: 10px; margin: 10px 0; }
.then { background: var(--warn-bg); border: 1px solid #ecd9b0; border-radius: 6px;
        padding: 10px 12px; margin: 10px 0; font-size: 15px; }
.then strong { color: var(--warn); }
.readback { display: flex; gap: 7px; align-items: center; font-size: 15px; margin-top: 8px; }
.entry + .entry { border-top: 1px dashed var(--line); margin-top: 14px; padding-top: 12px; }
.entry-head { display: flex; align-items: center; gap: 10px; font-size: 12px;
              color: var(--faint); margin-bottom: 6px; }
.entry-head button { padding: 1px 7px; font-size: 12px; color: var(--faint); }
.add-answer { margin-top: 4px; font-size: 14px; }
.disagree { background: var(--warn-bg); border: 1px solid #ecd9b0; border-radius: 6px;
            padding: 10px 12px; margin-top: 12px; font-size: 15px; }
.status { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 10px; }
.status button { font-size: 13px; padding: 3px 9px; }
.status button[aria-pressed="true"] { background: var(--ink); color: #fff; border-color: var(--ink); }
table.rows { border-collapse: collapse; width: 100%; font-size: 14px; margin-bottom: 8px; }
table.rows th { text-align: left; font-weight: 600; color: var(--dim); font-size: 12px;
                padding: 4px 6px; border-bottom: 1px solid var(--line); }
table.rows td { padding: 3px 4px; }
table.rows input, table.rows select { width: 100%; }
.summary { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 18px; }
.summary ul { margin: 8px 0 0; padding-left: 20px; }
.summary li { margin-bottom: 4px; }
.saved { color: var(--faint); font-size: 13px; }
@media print {
  header { position: static; } nav, .status, button, .saved { display: none !important; }
  body { background: #fff; } .q { break-inside: avoid; border-left: none; }
  main { max-width: none; padding: 0; }
}
"""

_SCRIPT = r"""
const DATA = JSON.parse(document.getElementById('bank').textContent);
const KEY = 'itscp-worksheet';
let state = { system: '', facilitator: '', answers: {} };
let current = DATA.phases.findIndex(p => p.questions.length) || 0;

// Reading a question must never create an answer for it. Rendering touches every question on
// a phase, so a mutating lookup would fill the file with 82 records claiming ANSWERED before
// anybody had said anything, which is the exact failure the whole method exists to prevent:
// a plausible answer nobody gave. `view` is the read; `edit` is the only thing that writes.
const BLANK = { status: 'ANSWERED' };
function view(id) { return state.answers[id] || BLANK; }
function edit(id, change) {
  const a = state.answers[id] || (state.answers[id] = { status: 'ANSWERED' });
  change(a);
  save();
}
function blankRows(n) { return Array.from({ length: n }, () => ({})); }

// A question holds every answer the room gave it, in the order they were given. One is the
// ordinary case and the list still has one entry; two is a contradiction, which the method
// wants recorded openly with the name of whoever decides between them, never averaged and
// never quietly resolved by whoever is holding the pen.
function said(a) { return (a.said && a.said.length) ? a.said : [{}]; }
function setSaid(id, index, key, value) {
  edit(id, x => {
    x.said = (x.said && x.said.length) ? x.said : [{}];
    while (x.said.length <= index) x.said.push({});
    x.said[index][key] = value;
  });
}
function addSaid(id) {
  edit(id, x => { x.said = (x.said && x.said.length) ? x.said : [{}]; x.said.push({}); });
  render();
}
function dropSaid(id, index) {
  edit(id, x => { if (x.said && x.said.length > 1) x.said.splice(index, 1); });
  render();
}
// A file written before a question could hold more than one answer. Fold the single answer
// into the list rather than dropping it: somebody's session is in there.
function migrate(answers) {
  for (const id in answers) {
    const a = answers[id];
    if (a.said) continue;
    const only = {};
    for (const key of ['value', 'who', 'confidence', 'mechanism', 'readback']) {
      if (a[key] !== undefined) { only[key] = a[key]; delete a[key]; }
    }
    if (Object.keys(only).length) a.said = [only];
  }
  return answers;
}
function cell(q, index, column, value) {
  edit(q.id, x => {
    x.rows = x.rows || blankRows(3);
    while (x.rows.length <= index) x.rows.push({});
    x.rows[index][column] = value;
  });
}
function isDone(q) {
  const a = state.answers[q.id];
  if (!a) return false;
  if (a.status === 'MISSING' || a.status === 'DEFERRED') return !!a.owner;
  if (a.status === 'NOT_APPLICABLE') return !!a.reason;
  if (q.kind === 'rows') return Array.isArray(a.rows) && a.rows.some(r => Object.values(r).some(v => v));
  return said(a).some(s => s.value && String(s.value).trim());
}
function isFlagged(q) {
  const a = state.answers[q.id];
  if (!a || !isDone(q) || a.status !== 'ANSWERED') return false;
  const given = said(a).filter(s => s.value && String(s.value).trim());
  if (given.length > 1 && !(a.decision || '').trim()) return true;
  if (q.mechanism && given.some(s => !(s.mechanism || '').trim())) return true;
  if (q.readback && given.some(s => !s.readback)) return true;
  return false;
}
function save() {
  try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
  const el = document.getElementById('saved');
  el.textContent = 'saved';
  clearTimeout(save.t);
  save.t = setTimeout(() => { el.textContent = ''; }, 1200);
}
function restore() {
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      state = Object.assign(state, JSON.parse(raw));
      state.answers = migrate(state.answers || {});
    }
  } catch (e) {}
}

function el(tag, attrs, kids) {
  const node = document.createElement(tag);
  for (const k in (attrs || {})) {
    if (k === 'class') node.className = attrs[k];
    else if (k === 'text') node.textContent = attrs[k];
    else if (k.startsWith('on')) node.addEventListener(k.slice(2), attrs[k]);
    else if (attrs[k] !== null && attrs[k] !== undefined) node.setAttribute(k, attrs[k]);
  }
  (kids || []).forEach(kid => kid && node.appendChild(kid));
  return node;
}
function field(labelText, control) {
  return el('div', { class: 'grow' }, [el('label', { text: labelText }), control]);
}
function textInput(value, oninput, placeholder) {
  return el('input', { type: 'text', value: value || '', placeholder: placeholder || '',
                       oninput: e => { oninput(e.target.value); save(); } });
}

function statusRow(q) {
  const a = view(q.id);
  const buttons = DATA.statuses.map(s => el('button', {
    type: 'button', 'aria-pressed': String(a.status === s.key), title: s.hint, text: s.label,
    onclick: () => { edit(q.id, x => { x.status = s.key; }); render(); }
  }));
  return el('div', { class: 'status' }, buttons);
}

function answerControls(q) {
  const a = view(q.id);
  if (a.status === 'MISSING' || a.status === 'DEFERRED') {
    const kids = [field('Who can answer',
      textInput(a.owner, v => edit(q.id, x => { x.owner = v; }), 'a role, not a name'))];
    if (a.status === 'DEFERRED') {
      kids.push(field('By when', el('input', { type: 'date', value: a.due || '',
        oninput: e => edit(q.id, x => { x.due = e.target.value; }) })));
    }
    kids.push(field('Why', textInput(a.reason, v => edit(q.id, x => { x.reason = v; }),
                                     'what is blocking it')));
    return el('div', { class: 'field' }, kids);
  }
  if (a.status === 'NOT_APPLICABLE') {
    return el('div', { class: 'field' },
      [field('Why it does not apply', textInput(a.reason, v => edit(q.id, x => { x.reason = v; }),
        'a stated reason, not a judgment call'))]);
  }
  if (q.kind === 'rows') return rowsTable(q, a);

  const list = said(a);
  const kids = list.map((entry, i) => answerBlock(q, entry, i, list.length));
  kids.push(el('button', { class: 'add-answer', type: 'button',
    text: '+ another answer', title: 'Somebody else in the room said something different',
    onclick: () => addSaid(q.id) }));
  if (list.filter(s => s.value && String(s.value).trim()).length > 1) {
    kids.push(el('div', { class: 'disagree' }, [
      el('div', { text: 'Two answers is a finding, not a problem. Record both, and name who '
                      + 'decides between them. Never average them, and never quietly keep one.' }),
      el('div', { class: 'field' }, [field('Whose decision is it',
        textInput(a.decision, v => { edit(q.id, x => { x.decision = v; }); },
                  'the role who chooses, not the louder person'))])
    ]));
  }
  return el('div', {}, kids);
}

function answerBlock(q, entry, index, total) {
  let control;
  if (q.kind === 'enum') {
    control = el('select', { onchange: e => { setSaid(q.id, index, 'value', e.target.value); render(); } },
      [el('option', { value: '', text: '—' })].concat(
        q.options.map(o => el('option', { value: o, text: o,
                                          selected: entry.value === o ? 'selected' : null }))));
  } else if (q.kind === 'narrative' || q.kind === 'code') {
    control = el('textarea', { rows: '4', placeholder: 'in their words',
      oninput: e => setSaid(q.id, index, 'value', e.target.value) });
    control.value = entry.value || '';
  } else if (q.kind === 'date') {
    control = el('input', { type: 'date', value: entry.value || '',
      oninput: e => { setSaid(q.id, index, 'value', e.target.value); render(); } });
  } else {
    control = textInput(entry.value, v => setSaid(q.id, index, 'value', v),
                        q.unit ? ('in ' + q.unit) : '');
    control.addEventListener('change', render);
  }
  const kids = [];
  if (total > 1) {
    kids.push(el('div', { class: 'entry-head' }, [
      el('span', { text: 'Answer ' + (index + 1) + ' of ' + total }),
      el('button', { type: 'button', text: 'remove', onclick: () => dropSaid(q.id, index) })
    ]));
  }
  kids.push(el('div', { class: 'field' }, [
    field(q.unit ? 'Answer (' + q.unit + ')' : 'Answer', control),
    field('Who said it', textInput(entry.who, v => setSaid(q.id, index, 'who', v),
                                   'the role in the room')),
    el('div', {}, [el('label', { text: 'Sure?' }), sureButtons(q, index, entry)])
  ]));
  if (q.mechanism) {
    const box = el('div', { class: 'then' }, [
      el('div', {}, [el('strong', { text: 'Then ask: ' }), document.createTextNode(q.mechanism)]),
      el('textarea', { rows: '2', placeholder: 'what breaks at that number',
                       oninput: e => setSaid(q.id, index, 'mechanism', e.target.value) })
    ]);
    box.querySelector('textarea').value = entry.mechanism || '';
    kids.push(box);
  }
  if (q.readback) {
    const box = el('input', { type: 'checkbox',
      onchange: e => { setSaid(q.id, index, 'readback', e.target.checked); render(); } });
    box.checked = !!entry.readback;
    kids.push(el('label', { class: 'readback' },
      [box, document.createTextNode('Said it back in one sentence and got a yes')]));
  }
  return el('div', { class: 'entry' }, kids);
}

function sureButtons(q, index, entry) {
  return el('div', { class: 'sure' }, DATA.confidence.map(c => el('button', {
    type: 'button', title: c.hint, text: c.short,
    'aria-pressed': String(entry.confidence === c.key),
    onclick: () => {
      setSaid(q.id, index, 'confidence', entry.confidence === c.key ? '' : c.key);
      render();
    }
  })));
}

function rowsTable(q, a) {
  const rows = (a.rows && a.rows.length) ? a.rows : blankRows(3);
  const head = el('tr', {}, q.columns.map(c => el('th', { text: c.replace(/_/g, ' ') }))
    .concat([el('th', { text: 'who' }), el('th', { text: 'sure?' })]));
  const body = rows.map((row, i) => el('tr', {}, q.columns.map(c => {
    const opts = (q.columnOptions || {})[c];
    if (opts) {
      return el('td', {}, [el('select', { onchange: e => cell(q, i, c, e.target.value) },
        [el('option', { value: '', text: '—' })].concat(
          opts.map(o => el('option', { value: o, text: o,
                                       selected: row[c] === o ? 'selected' : null }))))]);
    }
    return el('td', {}, [textInput(row[c], v => cell(q, i, c, v), '')]);
  }).concat([
    el('td', {}, [textInput(row.__who, v => cell(q, i, '__who', v), '')]),
    el('td', {}, [el('select', { onchange: e => cell(q, i, '__sure', e.target.value) },
      [el('option', { value: '', text: '—' })].concat(
        DATA.confidence.map(c => el('option', { value: c.key, text: c.short,
          selected: row.__sure === c.key ? 'selected' : null }))))])
  ])));
  return el('div', {}, [
    el('table', { class: 'rows' }, [el('thead', {}, [head]), el('tbody', {}, body)]),
    el('button', { type: 'button', text: '+ row',
                   onclick: () => {
                     edit(q.id, x => { x.rows = x.rows || blankRows(3); x.rows.push({}); });
                     render();
                   } })
  ]);
}

function questionCard(q) {
  const a = view(q.id);
  const cls = 'q' + (isFlagged(q) ? ' flagged' : (isDone(q) ? ' done' : ''));
  const kids = [
    el('div', { class: 'key', text: q.id }),
    el('p', { class: 'ask', text: q.prompt.startsWith('Not asked') ? q.prompt : '“' + q.prompt + '”' }),
    el('p', { class: 'records', text: 'Records: ' + q.records + ' · ' + q.owner + ' answers' }),
    statusRow(q),
    answerControls(q)
  ];
  if (q.seeded) {
    kids.push(el('div', { class: 'note', text:
      'Often already on the inventory the room brought. Read it back for correction rather than asking cold.' }));
  }
  if (q.guidance) kids.push(el('div', { class: 'note', text: q.guidance }));
  kids.push(el('div', { class: 'field' },
    [field('Notes', textInput(a.notes, v => edit(q.id, x => { x.notes = v; }),
                              'who was in the room, what was contested'))]));
  return el('div', { class: cls }, kids);
}

// A list long enough to need trimming says what it trimmed. A page that shows forty of
// eighty-nine and stops reads as if forty were all of them, which is the wrong thing to
// believe about your own gaps.
const SHOWN = 40;
function listing(kids, items) {
  kids.push(el('ul', {}, items.slice(0, SHOWN).map(t => el('li', { text: t }))));
  if (items.length > SHOWN) {
    kids.push(el('p', { class: 'saved',
      text: 'Showing the first ' + SHOWN + '. ' + (items.length - SHOWN) +
            ' more are open and not listed here.' }));
  }
}

function whyFlagged(q) {
  const a = state.answers[q.id];
  const given = said(a).filter(s => s.value && String(s.value).trim());
  if (given.length > 1 && !(a.decision || '').trim()) return 'two answers, nobody named to decide';
  if (q.mechanism && given.some(s => !(s.mechanism || '').trim())) return 'no mechanism';
  return 'not read back';
}

function summary() {
  const open = [], unsure = [];
  DATA.phases.forEach(p => p.questions.forEach(q => {
    if (!isDone(q)) open.push('Phase ' + p.number + ' · ' + q.id);
    else if (isFlagged(q)) unsure.push('Phase ' + p.number + ' · ' + q.id +
      ' (' + whyFlagged(q) + ')');
  }));
  const kids = [el('p', { text: open.length
    ? open.length + ' answer(s) with nothing written against them. A blank is not a result; ' +
      'an answer nobody has is a name.'
    : 'Every answer has something written against it.' })];
  if (open.length) listing(kids, open);
  if (unsure.length) {
    kids.push(el('p', { text: unsure.length + ' answered without the thing that makes it hold up:' }));
    listing(kids, unsure);
  }
  return el('div', { class: 'summary' }, kids);
}

function render() {
  const nav = document.getElementById('nav');
  nav.textContent = '';
  DATA.phases.forEach((p, i) => {
    const done = p.questions.filter(isDone).length;
    nav.appendChild(el('button', {
      type: 'button', 'aria-current': String(i === current),
      onclick: () => { current = i; render(); window.scrollTo(0, 0); }
    }, [document.createTextNode('Phase ' + p.number),
        el('span', { class: 'count', text: p.questions.length ? done + '/' + p.questions.length : '—' })]));
  });
  nav.appendChild(el('button', {
    type: 'button', 'aria-current': String(current === -1),
    onclick: () => { current = -1; render(); window.scrollTo(0, 0); }, text: 'What is still open'
  }));

  const main = document.getElementById('sheet');
  main.textContent = '';
  if (current === -1) { main.appendChild(summary()); return; }
  const phase = DATA.phases[current];
  main.appendChild(el('h2', { text: 'Phase ' + phase.number + ' — ' + phase.title }));
  main.appendChild(el('p', { class: 'room', text: phase.room }));
  if (!phase.questions.length) {
    main.appendChild(el('div', { class: 'summary' }, [el('p', { text:
      'Nothing is captured here. This phase produces ' + (phase.produces || 'no recorded answers') +
      ', and the page for it in the manual carries what to do.' })]));
    return;
  }
  let group = null;
  phase.questions.forEach(q => {
    if (q.row !== group) { group = q.row; main.appendChild(el('div', { class: 'group', text: group })); }
    main.appendChild(questionCard(q));
  });
}

function download() {
  const answers = {};
  for (const id in state.answers) {
    const a = state.answers[id];
    const typed = Object.keys(a).some(k => {
      if (k === 'status') return false;
      const v = a[k];
      if (Array.isArray(v)) return v.some(r => Object.values(r).some(cell => cell));
      return v !== '' && v !== false && v !== undefined;
    });
    if (typed) answers[id] = a;
  }
  const out = { schema: 'itscp-worksheet/2', system: state.system,
                facilitator: state.facilitator, answers: answers };
  const blob = new Blob([JSON.stringify(out, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = (state.system || 'itscp') .replace(/[^A-Za-z0-9._-]+/g, '-') + '-worksheet.json';
  a.click();
  URL.revokeObjectURL(a.href);
}
function upload(file) {
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const loaded = JSON.parse(reader.result);
      state.answers = migrate(loaded.answers || {});
      state.system = loaded.system || '';
      state.facilitator = loaded.facilitator || '';
      document.getElementById('system').value = state.system;
      document.getElementById('facilitator').value = state.facilitator;
      render(); save();
    } catch (e) { alert('That file is not a worksheet this page wrote.'); }
  };
  reader.readAsText(file);
}

restore();
document.getElementById('system').value = state.system;
document.getElementById('facilitator').value = state.facilitator;
document.getElementById('system').addEventListener('input', e => { state.system = e.target.value; save(); });
document.getElementById('facilitator').addEventListener('input', e => { state.facilitator = e.target.value; save(); });
document.getElementById('save').addEventListener('click', download);
document.getElementById('load').addEventListener('change', e => {
  if (e.target.files[0]) upload(e.target.files[0]);
  e.target.value = '';
});
render();
"""


def render(phases: tuple[Any, ...]) -> str:
    """The whole page: markup, style, behavior and the bank, in one file."""
    data = _embed(payload(phases))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ITSCP worksheet</title>
<style>{_STYLE}</style>
</head>
<body>
<header>
  <div class="bar">
    <h1>ITSCP worksheet</h1>
    <div class="meta">
      <input id="system" type="text" placeholder="system or suite">
      <input id="facilitator" type="text" placeholder="facilitator">
    </div>
    <span class="spacer"></span>
    <span id="saved" class="saved"></span>
    <button id="save" class="primary" type="button">Save JSON</button>
    <label class="button" for="load" style="display:inline-block">
      <button type="button" onclick="document.getElementById('load').click()">Load JSON</button>
    </label>
    <input id="load" type="file" accept="application/json,.json" hidden>
  </div>
  <nav id="nav"></nav>
</header>
<main id="sheet"></main>
<script id="bank" type="application/json">
{data}
</script>
<script>{_SCRIPT}</script>
</body>
</html>
"""
