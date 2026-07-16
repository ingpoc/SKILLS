#!/usr/bin/env python3
"""Generate the operator-facing knowledge-base browser.

Reads every article in $CODEX_HOME/knowledge/raw/*.md and writes a single
self-contained HTML view to $CODEX_HOME/knowledge/knowledge-browser.html.

Dual-surface pattern (html-artifact skill): the canonical source stays in
raw/*.md, queried by agents via `workflow knowledge`. The HTML embeds two
JSON blocks:
  - #artifact-data    metadata (name/title/tags/date/source) — the CHEAP block
                      an agent extracts for re-read.
  - #artifact-bodies  full article markdown, name -> body — OPERATOR-ONLY, used
                      by the in-page reading drawer. Agents should NOT parse it;
                      use `workflow knowledge read <slug>` instead.

Tag filters intersect (AND): selecting multiple tags shows articles carrying ALL
of them. A Match toggle switches to ANY.

Run after any KB mutation (REFRESH Phase E, INGEST I3, MAINTAIN fixes):
    python3 ~/.codex/skills/knowledge-base/scripts/build_browser.py
Idempotent. No args. Exit 0 on success.
"""
import json
import os
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
KB = CODEX_HOME / "knowledge"
RAW = KB / "raw"
OUT = KB / "knowledge-browser.html"


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    out = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip()
        if k == "tags":
            out[k] = [t.strip() for t in v.strip("[]").split(",") if t.strip()]
        else:
            out[k] = v.strip('"')
    return out


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:].lstrip("\n")
    return text


def collect():
    arts, bodies = [], {}
    for f in sorted(RAW.glob("*.md")):
        text = f.read_text(encoding="utf-8")
        d = parse_frontmatter(text)
        arts.append({
            "name": f.stem,
            "title": d.get("title", f.stem),
            "tags": d.get("tags", []),
            "date": d.get("date_published") or d.get("date_processed") or f.stem[:10],
            "source_url": d.get("source_url", ""),
            "source_title": d.get("source_title", ""),
            "source_author": d.get("source_author", ""),
        })
        bodies[f.stem] = strip_frontmatter(text)
    data = {"generated": date.today().isoformat(), "count": len(arts), "articles": arts}
    return data, bodies


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Knowledge Base — __COUNT__ articles</title>
<style>
:root {
  --ivory:#FAF9F5; --paper:#FFFFFF; --slate:#141413;
  --clay:#D97757; --clay-d:#B85C3E; --oat:#E3DACC; --olive:#788C5D; --rust:#B04A3F;
  --gray-150:#F0EEE6; --gray-300:#D1CFC5; --gray-500:#87867F; --gray-700:#3D3D3A;
  --serif:ui-serif,Georgia,"Times New Roman",Times,serif;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  --mono:ui-monospace,"SF Mono",Menlo,Monaco,Consolas,monospace;
}
* { box-sizing:border-box; }
html,body { overflow-x:clip; }
body {
  margin:0; background:var(--ivory); color:var(--gray-700);
  font-family:var(--sans); font-size:15px; line-height:1.55;
  padding:48px 24px 96px;
}
.wrap { max-width:1120px; margin:0 auto; }
.eyebrow {
  font-family:var(--mono); font-size:11px; letter-spacing:0.1em;
  text-transform:uppercase; color:var(--gray-500); margin-bottom:10px;
}
h1 {
  font-family:var(--serif); font-weight:500; font-size:clamp(30px,4vw,38px);
  letter-spacing:-0.012em; margin:0 0 12px; color:var(--slate);
}
h1 em { font-style:italic; color:var(--clay); }
.lead { font-size:14.5px; line-height:1.6; color:var(--gray-700); max-width:660px; margin:0 0 32px; }
.toolbar {
  position:sticky; top:0; z-index:20; margin:0 -24px 0; padding:14px 24px;
  background:rgba(250,249,245,0.94); backdrop-filter:blur(8px);
  border-bottom:1.5px solid var(--gray-300);
  display:flex; gap:12px; align-items:center; flex-wrap:wrap;
}
.search {
  flex:1; min-width:220px; font-family:var(--sans); font-size:14px;
  padding:9px 13px; border:1.5px solid var(--gray-300); border-radius:9px;
  background:var(--paper); color:var(--slate);
}
.search:focus { outline:none; border-color:var(--clay); }
.ctrl {
  font-family:var(--mono); font-size:11px; letter-spacing:0.06em; text-transform:uppercase;
  padding:9px 12px; border:1.5px solid var(--gray-300); border-radius:9px;
  background:var(--paper); color:var(--gray-700); cursor:pointer;
}
.ctrl:hover { border-color:var(--clay); color:var(--slate); }
select.ctrl { -webkit-appearance:none; appearance:none; padding-right:26px;
  background-image:linear-gradient(45deg,transparent 50%,var(--gray-500) 50%),linear-gradient(135deg,var(--gray-500) 50%,transparent 50%);
  background-position:calc(100% - 14px) 16px,calc(100% - 9px) 16px; background-size:5px 5px; background-repeat:no-repeat; }
.count { font-family:var(--mono); font-size:11px; color:var(--gray-500); white-space:nowrap; }
.tags { display:flex; flex-wrap:wrap; gap:7px; margin:22px 0 26px; }
.tag {
  font-family:var(--mono); font-size:11px; letter-spacing:0.04em;
  padding:5px 10px; border:1.5px solid var(--gray-300); border-radius:999px;
  background:var(--paper); color:var(--gray-700); cursor:pointer; user-select:none;
  transition:background .12s,border-color .12s,color .12s;
}
.tag .n { color:var(--gray-500); margin-left:5px; }
.tag:hover { border-color:var(--clay); }
.tag.on { background:var(--slate); color:var(--ivory); border-color:var(--slate); }
.tag.on .n { color:var(--oat); }
.list { border-top:1.5px solid var(--gray-300); }
.row {
  display:grid; grid-template-columns:96px minmax(0,1fr) auto;
  gap:18px; align-items:baseline;
  padding:15px 4px; border-bottom:1.5px solid var(--gray-300);
}
.row .date { font-family:var(--mono); font-size:11px; color:var(--gray-500); padding-top:2px; }
.row .main { min-width:0; }
.row .title { font-size:15.5px; line-height:1.4; color:var(--slate); cursor:pointer; font-weight:500; background:none; border:0; padding:0; text-align:left; font-family:inherit; }
.row .title:hover { color:var(--clay); text-decoration:underline; text-underline-offset:3px; }
.row .meta { margin-top:6px; display:flex; flex-wrap:wrap; gap:6px 10px; align-items:center; }
.row .rtag {
  font-family:var(--mono); font-size:10px; letter-spacing:0.04em; color:var(--gray-700);
  background:var(--gray-150); border-radius:999px; padding:2px 8px; cursor:pointer;
}
.row .rtag:hover { background:var(--oat); }
.row .src { font-size:12px; color:var(--gray-500); font-style:italic; }
.row .actions { display:flex; gap:6px; }
.iconbtn {
  font-family:var(--mono); font-size:10px; letter-spacing:0.05em; text-transform:uppercase;
  border:1.5px solid var(--gray-300); background:var(--paper); color:var(--gray-700);
  border-radius:7px; padding:5px 8px; cursor:pointer; white-space:nowrap;
}
.iconbtn:hover { background:var(--clay); color:var(--ivory); border-color:var(--clay); }
.empty { padding:48px 4px; color:var(--gray-500); font-style:italic; }
mark { background:linear-gradient(transparent 55%,var(--oat) 55%); color:inherit; padding:0 1px; }
.pill {
  position:fixed; bottom:20px; left:50%; transform:translateX(-50%);
  font-family:var(--mono); font-size:11px; color:var(--ivory); background:var(--slate);
  padding:8px 14px; border-radius:999px; opacity:0; transition:opacity .2s; pointer-events:none; z-index:60;
}
.pill.show { opacity:1; }
.footnote { margin-top:34px; font-size:12px; color:var(--gray-500); line-height:1.6; border-top:1.5px solid var(--gray-300); padding-top:16px; }
.footnote code { font-family:var(--mono); font-size:11px; background:var(--gray-150); padding:1px 5px; border-radius:4px; color:var(--gray-700); }

/* reading drawer */
.overlay { position:fixed; inset:0; background:rgba(20,20,19,.34); opacity:0; pointer-events:none; transition:opacity .2s; z-index:40; }
.overlay.show { opacity:1; pointer-events:auto; }
.drawer {
  position:fixed; top:0; right:0; height:100%; width:min(760px,94vw);
  background:var(--ivory); border-left:1.5px solid var(--gray-300);
  box-shadow:0 12px 32px rgba(20,20,19,.18);
  transform:translateX(100%); transition:transform .24s ease; z-index:50;
  display:flex; flex-direction:column;
}
.drawer.show { transform:translateX(0); }
.drawer .dhead { padding:24px 30px 16px; border-bottom:1.5px solid var(--gray-300); position:relative; }
.drawer .deyebrow { font-family:var(--mono); font-size:11px; letter-spacing:0.08em; text-transform:uppercase; color:var(--gray-500); margin-bottom:8px; padding-right:40px; }
.drawer h2 { font-family:var(--serif); font-weight:500; font-size:23px; line-height:1.3; letter-spacing:-0.01em; color:var(--slate); margin:0 0 10px; padding-right:20px; }
.drawer .dsrc { font-size:12.5px; color:var(--gray-500); }
.drawer .dsrc a { color:var(--clay); }
.dclose { position:absolute; top:20px; right:24px; font-family:var(--mono); font-size:18px; line-height:1; border:1.5px solid var(--gray-300); background:var(--paper); color:var(--gray-700); border-radius:8px; width:32px; height:32px; cursor:pointer; }
.dclose:hover { background:var(--clay); color:var(--ivory); border-color:var(--clay); }
.dbody { padding:22px 30px 60px; overflow-y:auto; }
.dbody h1,.dbody h2,.dbody h3,.dbody h4 { font-family:var(--serif); font-weight:500; color:var(--slate); line-height:1.3; margin:22px 0 8px; }
.dbody h1 { font-size:21px; } .dbody h2 { font-size:18px; } .dbody h3 { font-size:16px; } .dbody h4 { font-size:14px; }
.dbody p { margin:10px 0; }
.dbody ul,.dbody ol { margin:10px 0; padding-left:22px; }
.dbody li { margin:4px 0; }
.dbody code { font-family:var(--mono); font-size:12.5px; background:var(--gray-150); padding:1px 5px; border-radius:4px; color:var(--gray-700); }
.dbody pre { background:var(--slate); color:var(--ivory); border-radius:10px; padding:14px 16px; overflow-x:auto; margin:12px 0; }
.dbody pre code { background:none; color:inherit; font-size:12.5px; padding:0; }
.dbody a { color:var(--clay); }
.dbody blockquote { border-left:3px solid var(--oat); margin:12px 0; padding:2px 0 2px 16px; color:var(--gray-700); font-style:italic; }
.dbody hr { border:0; border-top:1.5px solid var(--gray-300); margin:20px 0; }
.dbody table { border-collapse:collapse; width:100%; margin:14px 0; font-size:13px; }
.dbody th,.dbody td { border:1.5px solid var(--gray-300); padding:6px 10px; text-align:left; vertical-align:top; }
.dbody th { background:var(--gray-150); font-family:var(--mono); font-size:11px; letter-spacing:0.04em; text-transform:uppercase; color:var(--gray-700); }
.dfoot { padding:14px 30px; border-top:1.5px solid var(--gray-300); display:flex; gap:10px; align-items:center; }

@media (max-width:720px) {
  .row { grid-template-columns:1fr; gap:6px; }
  .row .date { order:-1; }
  .row .actions { margin-top:8px; }
}
@media (prefers-reduced-motion:reduce) { *,*::before,*::after { transition-duration:.01ms!important; } }
@media print { .toolbar,.actions,.iconbtn,.overlay,.drawer { display:none; } body { padding:0; } }
</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">Knowledge base · __COUNT__ articles · __TAGCOUNT__ tags · generated __GEN__</div>
  <h1>The <em>knowledge</em> base</h1>
  <p class="lead">Every research insight in <code>~/.claude/knowledge/</code>, browsable. Click a title (or <b>read</b>) to read the article here. Filter by tag (tags intersect — articles must carry <em>all</em> selected tags), search, or open the original source. Canonical source stays in <code>raw/*.md</code> — this is a generated view.</p>
  <div class="toolbar">
    <input class="search" id="q" type="search" placeholder="Search titles, sources, authors, slugs…" autocomplete="off">
    <select class="ctrl" id="sort">
      <option value="new">Newest first</option>
      <option value="old">Oldest first</option>
      <option value="az">Title A–Z</option>
    </select>
    <button class="ctrl" id="match" data-mode="all" title="Toggle tag combination">Match: ALL</button>
    <button class="ctrl" id="reset">Reset</button>
    <span class="count" id="count"></span>
  </div>
  <div class="tags" id="tags"></div>
  <div class="list" id="list"></div>
  <p class="footnote">
    Agent re-read: don't parse this file — extract the <code>#artifact-data</code> metadata block, or query the canonical surface with
    <code>workflow knowledge search "&lt;query&gt;"</code> / <code>workflow knowledge read &lt;slug&gt;</code>.
    The <code>#artifact-bodies</code> block is operator-only (powers the reading drawer); agents should use the CLI, not parse it.
  </p>
</div>

<div class="overlay" id="overlay"></div>
<aside class="drawer" id="drawer" aria-hidden="true">
  <div class="dhead">
    <button class="dclose" id="dclose" title="Close (Esc)">×</button>
    <div class="deyebrow" id="deyebrow"></div>
    <h2 id="dtitle"></h2>
    <div class="dsrc" id="dsrc"></div>
  </div>
  <div class="dbody" id="dbody"></div>
  <div class="dfoot">
    <button class="iconbtn" id="dcopy">⧉ copy read cmd</button>
    <a class="iconbtn" id="dsource" target="_blank" rel="noopener" style="text-decoration:none; display:none;">↗ open source</a>
  </div>
</aside>

<div class="pill" id="pill"></div>
<script type="application/json" id="artifact-data">__DATA__</script>
<script type="application/json" id="artifact-bodies">__BODIES__</script>
<script>
const DB = JSON.parse(document.getElementById('artifact-data').textContent);
const BODIES = JSON.parse(document.getElementById('artifact-bodies').textContent);
const ALL = DB.articles;
const BYNAME = Object.fromEntries(ALL.map(a=>[a.name,a]));
const state = { q:'', tags:new Set(), sort:'new', mode:'all' };

const tagCounts = {};
for (const a of ALL) for (const t of a.tags) tagCounts[t] = (tagCounts[t]||0)+1;
const tagOrder = Object.keys(tagCounts).sort((x,y)=>tagCounts[y]-tagCounts[x]);

const esc = s => (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function hl(text){
  const q = state.q.trim();
  if(!q) return esc(text);
  const re = new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','ig');
  return esc(text).replace(re,'<mark>$1</mark>');
}

/* minimal markdown -> html for the reading drawer */
function mdInline(s){
  return s
    .replace(/`([^`]+)`/g,'<code>$1</code>')
    .replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*]+)\*(?!\*)/g,'$1<em>$2</em>')
    .replace(/\[([^\]]+)\]\(([^)\s]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>');
}
function md(src){
  const lines = (src||'').replace(/\r/g,'').split('\n');
  const out=[]; let i=0;
  const isBlock = l => /^(#{1,6}\s|```|>\s?|\s*[-*+]\s|\s*\d+\.\s)/.test(l) || l.includes('|');
  while(i<lines.length){
    let line=lines[i];
    if(/^```/.test(line)){
      const code=[]; i++;
      while(i<lines.length && !/^```/.test(lines[i])){ code.push(lines[i]); i++; }
      i++; out.push('<pre><code>'+esc(code.join('\n'))+'</code></pre>'); continue;
    }
    if(line.includes('|') && i+1<lines.length && /-/.test(lines[i+1]) && /^[\s:|\-]+$/.test(lines[i+1].trim())){
      const cells = r => r.replace(/^\s*\|/,'').replace(/\|\s*$/,'').split('|').map(c=>c.trim());
      const head=cells(line); i+=2; const rows=[];
      while(i<lines.length && lines[i].includes('|')){ rows.push(cells(lines[i])); i++; }
      out.push('<table><thead><tr>'+head.map(h=>'<th>'+mdInline(esc(h))+'</th>').join('')+'</tr></thead><tbody>'
        +rows.map(r=>'<tr>'+r.map(c=>'<td>'+mdInline(esc(c))+'</td>').join('')+'</tr>').join('')+'</tbody></table>');
      continue;
    }
    let h=line.match(/^(#{1,6})\s+(.*)$/);
    if(h){ const lv=Math.min(h[1].length,4); out.push('<h'+lv+'>'+mdInline(esc(h[2]))+'</h'+lv+'>'); i++; continue; }
    if(/^---+$/.test(line.trim())){ out.push('<hr>'); i++; continue; }
    if(/^>\s?/.test(line)){ const q=[]; while(i<lines.length && /^>\s?/.test(lines[i])){ q.push(lines[i].replace(/^>\s?/,'')); i++; } out.push('<blockquote>'+mdInline(esc(q.join(' ')))+'</blockquote>'); continue; }
    if(/^\s*[-*+]\s+/.test(line)){ const it=[]; while(i<lines.length && /^\s*[-*+]\s+/.test(lines[i])){ it.push(lines[i].replace(/^\s*[-*+]\s+/,'')); i++; } out.push('<ul>'+it.map(x=>'<li>'+mdInline(esc(x))+'</li>').join('')+'</ul>'); continue; }
    if(/^\s*\d+\.\s+/.test(line)){ const it=[]; while(i<lines.length && /^\s*\d+\.\s+/.test(lines[i])){ it.push(lines[i].replace(/^\s*\d+\.\s+/,'')); i++; } out.push('<ol>'+it.map(x=>'<li>'+mdInline(esc(x))+'</li>').join('')+'</ol>'); continue; }
    if(line.trim()===''){ i++; continue; }
    const para=[line]; i++;
    while(i<lines.length && lines[i].trim()!=='' && !isBlock(lines[i])){ para.push(lines[i]); i++; }
    out.push('<p>'+mdInline(esc(para.join(' ')))+'</p>');
  }
  return out.join('\n');
}

function renderTags(){
  document.getElementById('tags').innerHTML = tagOrder.map(t=>
    `<span class="tag${state.tags.has(t)?' on':''}" data-t="${esc(t)}">${esc(t)}<span class="n">${tagCounts[t]}</span></span>`
  ).join('');
}
function matches(a){
  if(state.tags.size){
    const hit = [...state.tags].filter(t=>a.tags.includes(t));
    if(state.mode==='all'){ if(hit.length!==state.tags.size) return false; }
    else { if(hit.length===0) return false; }
  }
  const q = state.q.trim().toLowerCase();
  if(q){
    const hay = (a.title+' '+a.source_title+' '+a.source_author+' '+a.name+' '+a.tags.join(' ')).toLowerCase();
    if(!hay.includes(q)) return false;
  }
  return true;
}
function render(){
  let rows = ALL.filter(matches);
  rows.sort((a,b)=> state.sort==='az' ? a.title.localeCompare(b.title)
    : state.sort==='old' ? a.date.localeCompare(b.date)
    : b.date.localeCompare(a.date));
  document.getElementById('count').textContent = `${rows.length} / ${ALL.length}`;
  const list = document.getElementById('list');
  if(!rows.length){ list.innerHTML = '<div class="empty">No articles match.</div>'; return; }
  list.innerHTML = rows.map(a=>{
    const tags = a.tags.map(t=>`<span class="rtag" data-t="${esc(t)}">${esc(t)}</span>`).join('');
    const src = a.source_title
      ? `<span class="src">${hl(a.source_title)}${a.source_author?' — '+hl(a.source_author):''}</span>` : '';
    return `<div class="row">
      <div class="date">${esc(a.date)}</div>
      <div class="main">
        <button class="title" data-read="${esc(a.name)}">${hl(a.title)}</button>
        <div class="meta">${tags}${src}</div>
      </div>
      <div class="actions"><button class="iconbtn" data-read="${esc(a.name)}">read</button></div>
    </div>`;
  }).join('');
}
function toast(msg){
  const p=document.getElementById('pill'); p.textContent=msg; p.classList.add('show');
  clearTimeout(p._t); p._t=setTimeout(()=>p.classList.remove('show'),1500);
}

/* drawer */
let current=null;
function openArticle(name){
  const a=BYNAME[name]; if(!a) return;
  current=a;
  document.getElementById('deyebrow').textContent = `${a.date} · ${a.tags.join(' · ')}`;
  document.getElementById('dtitle').textContent = a.title;
  const dsrc=document.getElementById('dsrc');
  dsrc.innerHTML = a.source_title
    ? `Source: ${a.source_url?`<a href="${esc(a.source_url)}" target="_blank" rel="noopener">${esc(a.source_title)}</a>`:esc(a.source_title)}${a.source_author?' — '+esc(a.source_author):''}`
    : `<span style="font-family:var(--mono);font-size:11px;">${esc(a.name)}</span>`;
  document.getElementById('dbody').innerHTML = md(BODIES[name] || '_No body found._');
  document.getElementById('dbody').scrollTop = 0;
  const ds=document.getElementById('dsource');
  if(a.source_url){ ds.style.display='inline-block'; ds.href=a.source_url; } else { ds.style.display='none'; }
  document.getElementById('overlay').classList.add('show');
  document.getElementById('drawer').classList.add('show');
  document.getElementById('drawer').setAttribute('aria-hidden','false');
}
function closeDrawer(){
  document.getElementById('overlay').classList.remove('show');
  document.getElementById('drawer').classList.remove('show');
  document.getElementById('drawer').setAttribute('aria-hidden','true');
  current=null;
}

document.getElementById('q').addEventListener('input',e=>{state.q=e.target.value; render();});
document.getElementById('sort').addEventListener('change',e=>{state.sort=e.target.value; render();});
document.getElementById('match').addEventListener('click',e=>{
  state.mode = state.mode==='all'?'any':'all';
  e.target.textContent = 'Match: '+state.mode.toUpperCase();
  e.target.dataset.mode = state.mode; render();
});
document.getElementById('reset').addEventListener('click',()=>{
  state.q=''; state.tags.clear(); state.sort='new'; state.mode='all';
  document.getElementById('q').value=''; document.getElementById('sort').value='new';
  document.getElementById('match').textContent='Match: ALL';
  renderTags(); render();
});
document.getElementById('tags').addEventListener('click',e=>{
  const t=e.target.closest('.tag'); if(!t) return;
  const k=t.dataset.t; state.tags.has(k)?state.tags.delete(k):state.tags.add(k);
  renderTags(); render();
});
document.getElementById('list').addEventListener('click',e=>{
  const rd=e.target.closest('[data-read]');
  if(rd){ openArticle(rd.dataset.read); return; }
  const rt=e.target.closest('.rtag');
  if(rt){ const k=rt.dataset.t; if(!state.tags.has(k)){state.tags.add(k); renderTags(); render();} }
});
document.getElementById('dclose').addEventListener('click',closeDrawer);
document.getElementById('overlay').addEventListener('click',closeDrawer);
document.addEventListener('keydown',e=>{ if(e.key==='Escape') closeDrawer(); });
document.getElementById('dcopy').addEventListener('click',()=>{
  if(!current) return;
  const cmd='workflow knowledge read '+current.name;
  navigator.clipboard.writeText(cmd).then(()=>toast('Copied — '+cmd)).catch(()=>toast('Copy failed'));
});

renderTags(); render();
</script>
</body>
</html>
"""


def main() -> int:
    if not RAW.is_dir():
        print(f"KB raw dir not found: {RAW}", file=sys.stderr)
        return 1
    data, bodies = collect()
    tag_count = len(Counter(t for a in data["articles"] for t in a["tags"]))
    html = (TEMPLATE
            .replace("__COUNT__", str(data["count"]))
            .replace("__TAGCOUNT__", str(tag_count))
            .replace("__GEN__", data["generated"])
            .replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
            .replace("__BODIES__", json.dumps(bodies, ensure_ascii=False, separators=(",", ":"))))
    OUT.write_text(html, encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT} ({kb:.0f} KB, {data['count']} articles, {tag_count} tags)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
