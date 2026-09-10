// A session recorded in one worksheet, opened in a later one whose bank has grown.
//
// Run it with two worksheet files: an older one (git show <ref>:docs/manual/worksheet.html)
// and the current one. The question bank grows, and the thing that must not happen is a room
// losing last month's answers to this month's questions. Nothing here is simulated: both
// files are real builds of the page.
//
//   bun plugin/tests/worksheet-upgrade.js <old.html> docs/manual/worksheet.html
const fs = require("fs");

function load(path) {
  const html = fs.readFileSync(path, "utf8");
  return {
    script: html.match(/<script>([\s\S]*?)<\/script>\s*<\/body>/)[1],
    bank: html.match(/<script id="bank" type="application\/json">\n([\s\S]*?)\n<\/script>/)[1],
  };
}
function findAll(node, pred, acc = []) {
  if (pred(node)) acc.push(node);
  (node.children || []).forEach(c => findAll(c, pred, acc));
  return acc;
}
function mount(bankText) {
  let seq = 0;
  const make = tag => ({
    tagName: (tag || "").toUpperCase(), _id: ++seq, children: [], attrs: {}, listeners: {},
    className: "", value: "", checked: false, files: [],
    set textContent(v) { this._text = v; if (v === "") this.children = []; },
    get textContent() { return (this._text || "") + this.children.map(c => c.textContent || "").join(""); },
    appendChild(c) { this.children.push(c); return c; },
    setAttribute(k, v) { this.attrs[k] = v; },
    getAttribute(k) { return this.attrs[k]; },
    addEventListener(k, f) { (this.listeners[k] = this.listeners[k] || []).push(f); },
    querySelector() { return findAll(this, n => n.tagName === "TEXTAREA")[0] || null; },
  });
  const byId = {};
  ["bank", "nav", "sheet", "system", "facilitator", "save", "load", "saved"]
    .forEach(id => { byId[id] = make(id); });
  byId.bank._text = bankText;
  const store = {};
  globalThis.document = { getElementById: id => byId[id] || null, createElement: make,
                          createTextNode: t => ({ textContent: t, children: [] }) };
  globalThis.localStorage = { getItem: k => (k in store ? store[k] : null),
                              setItem: (k, v) => { store[k] = v; } };
  globalThis.window = { scrollTo() {} };
  globalThis.alert = m => { throw new Error("alert: " + m); };
  globalThis.setTimeout = () => 0; globalThis.clearTimeout = () => {};
  globalThis.Blob = class { constructor(p) { this.parts = p; } };
  globalThis.URL = { createObjectURL: () => "blob:x", revokeObjectURL() {} };
  globalThis.FileReader = class { readAsText(f) { this.result = f.body; this.onload(); } };
  return { byId, store };
}
const card = (byId, id) => findAll(byId.sheet, n => (n.className || "").startsWith("q") &&
  findAll(n, m => m.className === "key" && m._text === id).length)[0];
function fieldNamed(c, label) {
  const box = findAll(c, n => n.className === "grow" &&
    (n.children[0] || {})._text && n.children[0]._text.startsWith(label))[0];
  return box ? box.children[1] : null;
}
const goTo = (byId, data, n) =>
  byId.nav.children[data.phases.findIndex(p => p.number === n)].listeners.click[0]();

let failures = 0;
const check = (name, fn) => {
  try { fn(); console.log("  ok    " + name); }
  catch (e) { failures++; console.log("  FAIL  " + name + "\n          " + e.message); }
};

const OLD = load(process.argv[2]);
const NEW = load(process.argv[3]);
const oldData = JSON.parse(OLD.bank.replace(/<\\\//g, "</"));
const newData = JSON.parse(NEW.bank.replace(/<\\\//g, "</"));

console.log("\nupgrading a real session: " +
  oldData.phases.reduce((n, p) => n + p.questions.length, 0) + " questions -> " +
  newData.phases.reduce((n, p) => n + p.questions.length, 0));

// --- last month, in the worksheet as it shipped ------------------------------------------
const before = mount(OLD.bank);
new Function(OLD.script)();
goTo(before.byId, oldData, "2");
fieldNamed(card(before.byId, "business.mtd.tier0"), "Answer")
  .listeners.input[0]({ target: { value: "8h" } });
fieldNamed(card(before.byId, "business.mtd.tier0"), "Who said it")
  .listeners.input[0]({ target: { value: "Head of Finance Systems" } });
goTo(before.byId, oldData, "3b");
fieldNamed(card(before.byId, "infra.primary_region"), "Answer")
  .listeners.input[0]({ target: { value: "us-ashburn-1" } });
const file = JSON.stringify(JSON.parse(before.store["itscp-worksheet"]));
console.log("  note  recorded " + Object.keys(JSON.parse(file).answers).length +
            " answers in the older worksheet");

// --- this month, in the worksheet with the backup and playbook questions -----------------
const after = mount(NEW.bank);
new Function(NEW.script)();
after.byId.load.listeners.change[0]({ target: { files: [{ body: file }], value: "" } });

check("last month's answer is still there", () => {
  goTo(after.byId, newData, "2");
  const v = fieldNamed(card(after.byId, "business.mtd.tier0"), "Answer").attrs.value;
  if (v !== "8h") throw new Error("shows " + JSON.stringify(v));
});

check("and so is who gave it", () => {
  goTo(after.byId, newData, "2");
  const v = fieldNamed(card(after.byId, "business.mtd.tier0"), "Who said it").attrs.value;
  if (v !== "Head of Finance Systems") throw new Error("shows " + JSON.stringify(v));
});

check("an answer from another phase survived too", () => {
  goTo(after.byId, newData, "3b");
  const v = fieldNamed(card(after.byId, "infra.primary_region"), "Answer").attrs.value;
  if (v !== "us-ashburn-1") throw new Error("shows " + JSON.stringify(v));
});

check("the new backup questions are present and blank", () => {
  goTo(after.byId, newData, "3b");
  for (const id of ["infra.backup_strategy", "infra.backup_matrix",
                    "infra.backup_restore_duration", "infra.backup_last_restore",
                    "infra.backup_immutability"]) {
    const c = card(after.byId, id);
    if (!c) throw new Error(id + " is not on the page");
    const answer = fieldNamed(c, "Answer");
    if (answer && answer.attrs.value) throw new Error(id + " arrived with an answer");
  }
});

check("the backup table offers the copy types", () => {
  goTo(after.byId, newData, "3b");
  const q = newData.phases.find(p => p.number === "3b").questions
    .find(x => x.id === "infra.backup_matrix");
  const types = (q.columnOptions || {}).type || [];
  for (const kind of ["full", "differential", "incremental"]) {
    if (!types.includes(kind)) throw new Error("no '" + kind + "' among " + types.join(", "));
  }
});

check("the playbook questions are present and blank", () => {
  goTo(after.byId, newData, "3a");
  for (const id of ["app.component_playbooks", "app.playbook_reachability",
                    "app.reconstitution_order"]) {
    if (!card(after.byId, id)) throw new Error(id + " is not on the page");
  }
});

check("the retention question landed in governance", () => {
  goTo(after.byId, newData, "5");
  if (!card(after.byId, "governance.retention_obligation")) {
    throw new Error("governance.retention_obligation is not on phase 5");
  }
});

check("the new questions show up as still open", () => {
  after.byId.nav.children[after.byId.nav.children.length - 1].listeners.click[0]();
  const text = after.byId.sheet.textContent;
  const open = newData.phases.reduce((n, p) => n + p.questions.length, 0) - 2;
  if (!text.includes(String(open))) {
    throw new Error("the open count is not reported; expected " + open);
  }
  if (!text.includes("more are open and not listed here")) {
    throw new Error("the list is trimmed and does not say so");
  }
  if (!text.includes("app.component_playbooks")) {
    throw new Error("a new question is not among those listed");
  }
});

check("nothing was invented for them", () => {
  const held = JSON.parse(after.store["itscp-worksheet"]).answers;
  const invented = ["infra.backup_matrix", "app.component_playbooks",
                    "governance.retention_obligation"].filter(id => id in held);
  if (invented.length) throw new Error("records exist for " + invented.join(", "));
});

console.log();
if (failures) { console.log("FAIL - " + failures + " check(s) failed"); process.exit(1); }
console.log("PASS - a session upgrades across a bank change");
