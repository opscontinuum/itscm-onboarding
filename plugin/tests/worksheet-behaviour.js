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

check("typing an answer reaches local storage", () => {
  goToPhase("2");
  const input = fieldNamed(cardFor("business.mtd.tier0"), "Answer");
  input.listeners.input[0]({ target: { value: "8h" } });
  const saved = JSON.parse(store["itscp-worksheet"]).answers;
  if ((saved["business.mtd.tier0"] || {}).value !== "8h") {
    throw new Error("not persisted: " + JSON.stringify(saved["business.mtd.tier0"]));
  }
});

check("who said it and how sure are captured beside the answer", () => {
  goToPhase("2");
  const card = cardFor("business.mtd.tier0");
  fieldNamed(card, "Who said it").listeners.input[0]({ target: { value: "Head of Finance" } });
  const sure = findAll(card, n => n.className === "sure")[0];
  sure.children[1].listeners.click[0]();          // M
  const a = JSON.parse(store["itscp-worksheet"]).answers["business.mtd.tier0"];
  if (a.who !== "Head of Finance" || a.confidence !== "medium") {
    throw new Error("not captured: " + JSON.stringify(a));
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
  byId.sheet.textContent = "";
  byId.nav.textContent = "";
  new Function(script)();
  goToPhase("2");
  const input = fieldNamed(cardFor("business.mtd.tier0"), "Answer");
  if (input.attrs.value !== "8h") {
    throw new Error("restored page shows " + JSON.stringify(input.attrs.value));
  }
});

check("every question in the bank is on some phase", () => {
  const ids = new Set();
  data.phases.forEach(p => p.questions.forEach(q => ids.add(q.id)));
  if (ids.size !== 82) throw new Error("expected 82 questions, embedded " + ids.size);
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
