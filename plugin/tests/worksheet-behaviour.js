// Execute the worksheet's own script against a minimal DOM and assert what it built.
// Not a browser, but enough of one to prove the script parses, runs, renders every phase,
// and round-trips an answer through its own save/load path.
const fs = require("fs");
const html = fs.readFileSync(process.argv[2], "utf8");

const script = html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/)[1];
const bank = html.match(/<script id="bank" type="application\/json">\n([\s\S]*?)\n<\/script>/)[1];

// --- the smallest DOM the script touches -----------------------------------------------
let idSeq = 0;
function makeNode(tag) {
  return {
    tagName: (tag || "").toUpperCase(), _id: ++idSeq, children: [], attrs: {}, listeners: {},
    className: "", value: "", checked: false, files: [],
    set textContent(v) { this._text = v; if (v === "") this.children = []; },
    get textContent() {
      return (this._text || "") + this.children.map(c => c.textContent || "").join("");
    },
    appendChild(c) { this.children.push(c); return c; },
    setAttribute(k, v) { this.attrs[k] = v; },
    getAttribute(k) { return this.attrs[k]; },
    addEventListener(k, fn) { (this.listeners[k] = this.listeners[k] || []).push(fn); },
    querySelector() { return findAll(this, n => n.tagName === "TEXTAREA")[0] || null; },
  };
}
function findAll(node, pred, acc = []) {
  if (pred(node)) acc.push(node);
  (node.children || []).forEach(c => findAll(c, pred, acc));
  return acc;
}
const byId = {};
for (const id of ["bank", "nav", "sheet", "system", "facilitator", "save", "load", "saved"]) {
  byId[id] = makeNode(id === "bank" ? "script" : "div");
}
byId.bank._text = bank;

const store = {};
globalThis.document = {
  getElementById: id => byId[id] || null,
  createElement: makeNode,
  createTextNode: t => ({ textContent: t, children: [] }),
};
globalThis.localStorage = {
  getItem: k => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = v; },
};
globalThis.window = { scrollTo() {} };
globalThis.alert = m => { throw new Error("alert: " + m); };
globalThis.setTimeout = () => 0;
globalThis.clearTimeout = () => {};
globalThis.Blob = class { constructor(parts) { this.parts = parts; } };
globalThis.URL = { createObjectURL: () => "blob:x", revokeObjectURL() {} };
globalThis.FileReader = class { readAsText() {} };

// --- run it -----------------------------------------------------------------------------
let failures = 0;
function check(name, fn) {
  try { fn(); console.log("  ok    " + name); }
  catch (e) { failures++; console.log("  FAIL  " + name + "\n          " + e.message); }
}

console.log("\n12. the browser worksheet");
check("the page's script parses and runs", () => { new Function(script)(); });

const data = JSON.parse(bank.replace(/<\\\//g, "</"));
const withQuestions = data.phases.filter(p => p.questions.length);

check("the first phase with questions rendered its cards", () => {
  const cards = findAll(byId.sheet, n => (n.className || "").startsWith("q"));
  if (!cards.length) throw new Error("no question cards were built");
});

check("every phase renders without throwing", () => {
  const navButtons = byId.nav.children.filter(c => c.listeners.click);
  if (navButtons.length !== data.phases.length + 1) {
    throw new Error("expected " + (data.phases.length + 1) + " nav buttons, got " + navButtons.length);
  }
  navButtons.forEach((b, i) => b.listeners.click.forEach(fn => fn()));
});

check("a phase with no questions says so instead of rendering nothing", () => {
  const empty = data.phases.findIndex(p => !p.questions.length);
  byId.nav.children[empty].listeners.click[0]();
  if (!byId.sheet.textContent.includes("Nothing is captured here")) {
    throw new Error("empty phase rendered nothing useful");
  }
});

function cardFor(id) {
  const card = findAll(byId.sheet, n => (n.className || "").startsWith("q") &&
    findAll(n, m => m.className === "key" && m._text === id).length)[0];
  if (!card) throw new Error("no card rendered for " + id);
  return card;
}
function fieldNamed(card, label) {
  const box = findAll(card, n => n.className === "grow" &&
    (n.children[0] || {})._text && n.children[0]._text.startsWith(label))[0];
  if (!box) throw new Error("no field labelled " + label);
  return box.children[1];
}
function goToPhase(number) {
  const i = data.phases.findIndex(p => p.number === number);
  byId.nav.children[i].listeners.click[0]();
}

check("an untouched worksheet records nothing", () => {
  const raw = store["itscp-worksheet"];
  const saved = raw ? JSON.parse(raw).answers : {};
  const invented = Object.keys(saved);
  if (invented.length) {
    throw new Error(invented.length + " answers exist that nobody typed: " +
      invented.slice(0, 3).join(", "));
  }
});

function stored(id) { return JSON.parse(store["itscp-worksheet"]).answers[id] || {}; }

check("typing an answer reaches local storage", () => {
  goToPhase("2");
  const input = fieldNamed(cardFor("business.mtd.tier0"), "Answer");
  input.listeners.input[0]({ target: { value: "8h" } });
  const a = stored("business.mtd.tier0");
  if (!a.said || a.said[0].value !== "8h") {
    throw new Error("not persisted: " + JSON.stringify(a));
  }
});

check("who said it and how sure are captured beside the answer", () => {
  goToPhase("2");
  const card = cardFor("business.mtd.tier0");
  fieldNamed(card, "Who said it").listeners.input[0]({ target: { value: "Head of Finance" } });
  findAll(card, n => n.className === "sure")[0].children[1].listeners.click[0]();   // M
  const first = stored("business.mtd.tier0").said[0];
  if (first.who !== "Head of Finance" || first.confidence !== "medium") {
    throw new Error("not captured: " + JSON.stringify(first));
  }
});

check("a second person's answer is added beside the first, not over it", () => {
  goToPhase("2");
  const add = findAll(cardFor("business.mtd.tier0"),
                      n => n.className === "add-answer")[0];
  if (!add) throw new Error("no way to add a second answer");
  add.listeners.click[0]();
  goToPhase("2");
  const card = cardFor("business.mtd.tier0");
  const blocks = findAll(card, n => n.className === "entry");
  if (blocks.length !== 2) throw new Error("expected 2 answer blocks, got " + blocks.length);
  const second = blocks[1];
  fieldNamed(second, "Answer").listeners.input[0]({ target: { value: "24h" } });
  fieldNamed(second, "Who said it").listeners.input[0]({ target: { value: "Application owner" } });
  const a = stored("business.mtd.tier0");
  if (a.said.length !== 2 || a.said[0].value !== "8h" || a.said[1].value !== "24h") {
    throw new Error("both answers not kept: " + JSON.stringify(a.said));
  }
  if (a.said[0].who !== "Head of Finance" || a.said[1].who !== "Application owner") {
    throw new Error("attribution crossed over: " + JSON.stringify(a.said));
  }
});

check("each answer carries its own mechanism", () => {
  goToPhase("2");
  const blocks = findAll(cardFor("business.mtd.tier0"), n => n.className === "entry");
  const boxes = blocks.map(b => findAll(b, n => n.className === "then")[0]);
  if (boxes.some(b => !b)) throw new Error("an answer has no mechanism follow-up");
  boxes[1].children[1].listeners.input[0]({ target: { value: "Batch cannot rebuild in a day" } });
  const a = stored("business.mtd.tier0");
  if (a.said[1].mechanism !== "Batch cannot rebuild in a day" || a.said[0].mechanism) {
    throw new Error("mechanism landed on the wrong answer: " + JSON.stringify(a.said));
  }
});

check("two answers raise the question of who decides", () => {
  goToPhase("2");
  const card = cardFor("business.mtd.tier0");
  if (!findAll(card, n => n.className === "disagree").length) {
    throw new Error("two answers did not raise the decision question");
  }
  if (!(card.className || "").includes("flagged")) {
    throw new Error("an unresolved pair of answers is not flagged");
  }
});

check("a pair is settled only when everything the method wants is there", () => {
  // Both answers explained, both read back, and a named decision owner. Until all of that is
  // present the card stays flagged, which is the point: it is the list of what is still owed.
  goToPhase("2");
  let card = cardFor("business.mtd.tier0");
  const blocks = findAll(card, n => n.className === "entry");
  findAll(blocks[0], n => n.className === "then")[0]
    .children[1].listeners.input[0]({ target: { value: "Bank file cuts at 18:00" } });
  goToPhase("2");
  findAll(cardFor("business.mtd.tier0"), n => n.className === "readback")
    .forEach(label => label.children[0].listeners.change[0]({ target: { checked: true } }));
  goToPhase("2");
  card = cardFor("business.mtd.tier0");
  if (!(card.className || "").includes("flagged")) {
    throw new Error("nobody has been named to decide, yet nothing is flagged");
  }
  fieldNamed(card, "Whose decision").listeners.input[0]({ target: { value: "Business owner" } });
  goToPhase("2");
  if ((cardFor("business.mtd.tier0").className || "").includes("flagged")) {
    throw new Error("still flagged with both answers explained, read back and a decider named");
  }
  if (stored("business.mtd.tier0").decision !== "Business owner") {
    throw new Error("decision owner not recorded");
  }
});

check("a file written before answers could differ still loads", () => {
  const old = { "business.rpo.tier0": { status: "ANSWERED", value: "15m",
                                        who: "Head of Finance", confidence: "high" } };
  store["itscp-worksheet"] = JSON.stringify({ answers: old });
  byId.sheet.textContent = ""; byId.nav.textContent = "";
  new Function(script)();
  goToPhase("2");
  const card = cardFor("business.rpo.tier0");
  if (fieldNamed(card, "Answer").attrs.value !== "15m") {
    throw new Error("an older session was lost: the answer is not on the page");
  }
  if (fieldNamed(card, "Who said it").attrs.value !== "Head of Finance") {
    throw new Error("an older session lost its attribution");
  }
  // and once anything is touched, what gets written back is the new shape
  fieldNamed(card, "Answer").listeners.input[0]({ target: { value: "15m" } });
  const a = stored("business.rpo.tier0");
  if (!a.said || a.said[0].who !== "Head of Finance" || a.value !== undefined) {
    throw new Error("migrated record written back wrong: " + JSON.stringify(a));
  }
});

check("a figure asks for what breaks at that number", () => {
  goToPhase("2");
  const card = cardFor("business.mtd.tier0");
  const then = findAll(card, n => n.className === "then")[0];
  if (!then) throw new Error("no mechanism follow-up on a duration that requires one");
  if (!then.textContent.includes("Then ask")) throw new Error("follow-up is not prompted");
});

check("nobody knew turns the answer into a name", () => {
  goToPhase("4");
  const card = cardFor("continuity.declaration_authority");
  const status = findAll(card, n => n.className === "status")[0];
  status.children[1].listeners.click[0]();        // Nobody knew
  const owner = fieldNamed(cardFor("continuity.declaration_authority"), "Who can answer");
  owner.listeners.input[0]({ target: { value: "Ops Director" } });
  const a = JSON.parse(store["itscp-worksheet"]).answers["continuity.declaration_authority"];
  if (a.status !== "MISSING" || a.owner !== "Ops Director") {
    throw new Error("gap not owned: " + JSON.stringify(a));
  }
});

check("a table question keeps the cell you typed in", () => {
  goToPhase("2");
  const table = findAll(cardFor("business.processes"), n => n.tagName === "TABLE")[0];
  const firstCell = findAll(table, n => n.tagName === "INPUT")[0];
  firstCell.listeners.input[0]({ target: { value: "Order to cash" } });
  const a = JSON.parse(store["itscp-worksheet"]).answers["business.processes"];
  if (!a.rows || a.rows[0].name !== "Order to cash") {
    throw new Error("row cell lost: " + JSON.stringify(a));
  }
});

check("a reopened page restores what was typed", () => {
  store["itscp-worksheet"] = JSON.stringify({ answers: {
    "business.mtd.tier0": { status: "ANSWERED", said: [{ value: "8h", who: "Head of Finance" }] } } });
  byId.sheet.textContent = ""; byId.nav.textContent = "";
  new Function(script)();
  goToPhase("2");
  const input = fieldNamed(cardFor("business.mtd.tier0"), "Answer");
  if (input.attrs.value !== "8h") {
    throw new Error("restored page shows " + JSON.stringify(input.attrs.value));
  }
});

check("every question appears once, on exactly one phase", () => {
  // How many there should be is checked in Python against the bank itself. Pinning the
  // number here as well would be a second copy of it, drifting the first time one is added.
  const seen = new Map();
  data.phases.forEach(p => p.questions.forEach(q => {
    if (seen.has(q.id)) throw new Error(q.id + " is on phase " + seen.get(q.id) + " and " + p.number);
    seen.set(q.id, p.number);
  }));
  if (!seen.size) throw new Error("the page carries no questions at all");
});

check("the exported file is the record shape", () => {
  const saved = JSON.parse(store["itscp-worksheet"]);
  const one = Object.values(saved.answers)[0];
  for (const key of ["status"]) {
    if (!(key in one)) throw new Error("an answer has no " + key);
  }
});

console.log();
if (failures) { console.log("FAIL - " + failures + " check(s) failed in section 12"); process.exit(1); }
console.log("PASS - section 12: the browser worksheet");
