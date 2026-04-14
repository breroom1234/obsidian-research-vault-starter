<%*
async function syncVaultWithGit(tp) {
  try {
    const plugins = tp.app?.plugins?.plugins;
    const hasObsidianGit = plugins && plugins["obsidian-git"];
    if (hasObsidianGit) {
      const maybePromise = tp.app.commands.executeCommandById("obsidian-git:pull");
      if (maybePromise && typeof maybePromise.then === "function") {
        await maybePromise;
      }
      return;
    }

    const adapter = tp.app.vault.adapter;
    const basePath = (adapter.getBasePath && adapter.getBasePath()) || adapter.basePath || "";
    if (!basePath) return;

    const result = await tp.system.exec(`git -C "${basePath}" pull --ff-only --no-rebase`);
    if (result?.code && result.code !== 0) {
      console.log(`[Startup] git pull stderr: ${result.stderr || ""}`);
    }
  } catch (error) {
    console.error("[Startup] git pull failed:", error);
  }
}

async function ensureFolder(tp, folderPath) {
  const parts = folderPath.split("/").filter(Boolean);
  let current = "";
  for (const part of parts) {
    current = current ? `${current}/${part}` : part;
    if (!(tp.app.vault.getAbstractFileByPath(current) instanceof tp.obsidian.TFolder)) {
      await tp.app.vault.createFolder(current);
    }
  }
}

async function ensureMonthlyNote(tp, monthlyPath, templatePath) {
  const existing = tp.app.vault.getAbstractFileByPath(monthlyPath);
  if (existing instanceof tp.obsidian.TFile) return existing;

  const folderPath = monthlyPath.slice(0, monthlyPath.lastIndexOf("/"));
  const fileName = monthlyPath.slice(monthlyPath.lastIndexOf("/") + 1).replace(/\.md$/, "");
  await ensureFolder(tp, folderPath);

  const parentFolder = tp.app.vault.getAbstractFileByPath(folderPath);
  const templateFile = tp.file.find_tfile(templatePath);
  if (templateFile && parentFolder instanceof tp.obsidian.TFolder) {
    return await tp.file.create_new(templateFile, fileName, false, parentFolder);
  }

  return await tp.app.vault.create(monthlyPath, `# 月報: ${tp.date.now("YYYY-MM")}\n`);
}

function getFrontmatterRange(text) {
  if (!text.startsWith("---\n")) return null;
  const end = text.indexOf("\n---", 4);
  if (end === -1) return null;
  return { start: 0, end: end + 4 };
}

function readFrontmatterValue(text, key) {
  const range = getFrontmatterRange(text);
  if (!range) return "";
  const fm = text.slice(range.start, range.end);
  const re = new RegExp(`^${key}:\\s*"?([^"\\n]*)"?\\s*$`, "m");
  const m = fm.match(re);
  return m ? (m[1] || "").trim() : "";
}

function upsertFrontmatterValue(text, key, value) {
  const range = getFrontmatterRange(text);
  const line = `${key}: "${value}"`;
  if (!range) return `---\n${line}\n---\n\n${text}`;
  const fm = text.slice(range.start, range.end);
  const body = text.slice(range.end);
  const re = new RegExp(`^${key}:.*$`, "m");
  const nextFm = re.test(fm) ? fm.replace(re, line) : `${fm.slice(0, -4)}\n${line}\n---`;
  return nextFm + body;
}

function toDateOnly(value) {
  if (!value) return null;
  const m = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!m) return null;
  return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
}

async function appendDailySectionIfMissing(tp, monthlyFile, today) {
  const heading = `## ${today}`;
  const current = await tp.app.vault.read(monthlyFile);
  if (current.includes(heading)) return false;

  const section = ["", heading, "", "- [ ] "].join("\n");
  await tp.app.vault.modify(monthlyFile, `${current.trimEnd()}\n${section}\n`);
  return true;
}

async function inheritProgressReviewDateFromPreviousMonth(tp, monthlyFile, year, monthId) {
  const curText = await tp.app.vault.read(monthlyFile);
  const curVal = readFrontmatterValue(curText, "progress_review_last_date");
  if (curVal) return false;

  const ref = new Date(Number(year), Number(monthId.slice(5, 7)) - 1, 1);
  ref.setMonth(ref.getMonth() - 1);
  const prevYear = String(ref.getFullYear());
  const prevMonthId = `${prevYear}-${String(ref.getMonth() + 1).padStart(2, "0")}`;
  const prevPath = `Daily_Notes/${prevYear}/${prevMonthId}_MonthlyReview.md`;
  const prevFile = tp.app.vault.getAbstractFileByPath(prevPath);
  if (!(prevFile instanceof tp.obsidian.TFile)) return false;

  const prevText = await tp.app.vault.read(prevFile);
  const prevVal = readFrontmatterValue(prevText, "progress_review_last_date");
  if (!prevVal) return false;

  const nextText = upsertFrontmatterValue(curText, "progress_review_last_date", prevVal);
  await tp.app.vault.modify(monthlyFile, nextText);
  return true;
}

const year = tp.date.now("YYYY");
const monthId = tp.date.now("YYYY-MM");
const today = tp.date.now("YYYY-MM-DD");
const monthlyPath = `Daily_Notes/${year}/${monthId}_MonthlyReview.md`;

await syncVaultWithGit(tp);
const monthlyFile = await ensureMonthlyNote(tp, monthlyPath, "Templates/Monthly_Note_Template.md");
if (!(monthlyFile instanceof tp.obsidian.TFile)) {
  new Notice("月報ファイルを開けませんでした。", 4000);
  return;
}

const inherited = await inheritProgressReviewDateFromPreviousMonth(tp, monthlyFile, year, monthId);
const isAppended = await appendDailySectionIfMissing(tp, monthlyFile, today);
const leaf = tp.app.workspace.getLeaf(true);
await leaf.openFile(monthlyFile);

if (isAppended) {
  new Notice("月報に本日の見出しと TODO を追加しました。", 3000);
} else {
  new Notice("本日の見出しは既にあります。", 3000);
}
if (inherited) {
  new Notice("先月の progress_review_last_date を今月の月報に引き継ぎました。", 3000);
}
%>
