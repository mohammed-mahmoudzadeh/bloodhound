"""Web UI — HTML/CSS/JS as a single Jinja2 template string.

FAVICON_SVG and TEMPLATE are used by routes.browse() via render_template_string().
"""
from __future__ import annotations


FAVICON_SVG = (
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Cpath d='M4 8a2 2 0 0 1 2-2h6.5l2.2 2.5H26a2 2 0 0 1 2 2V23a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8z' "
    "fill='%23fbbf24'/%3E"
    "%3Cpath d='M4 10h24' stroke='%23f59e0b' stroke-width='1.2'/%3E"
    "%3C/svg%3E"
)

TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#000000">
<title>Shared Files</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,__FAVICON__">
<link rel="apple-touch-icon" href="data:image/svg+xml,__FAVICON__">
<script>
  (function(){
    try {
      var KEY = 'shared_files_theme';
      var saved = localStorage.getItem(KEY);
      var theme;
      if (saved === 'dark' || saved === 'light') {
        theme = saved;
      } else {
        var mq = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)');
        theme = (mq && mq.matches) ? 'light' : 'dark';
        localStorage.setItem(KEY, theme);
      }
      document.documentElement.setAttribute('data-theme', theme);
    } catch(e) {
      document.documentElement.setAttribute('data-theme', 'dark');
    }
  })();
</script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  :root, [data-theme="dark"] {
    --bg: #000000;
    --bg-grad: radial-gradient(ellipse 60% 40% at 50% 0%, rgba(255,255,255,0.04), transparent 70%);
    --card: #0a0a0a;
    --card-hover: #111111;
    --border: #1a1a1a;
    --border-hover: #2a2a2a;
    --text: #f5f5f7;
    --text-dim: #d4d4d8;
    --muted: #6b6b75;
    --muted-2: #4a4a52;
    --chip: #080808;
    --btn-bg: #0a0a0a;
    --menu-bg: rgba(10,10,10,0.95);
    --overlay: rgba(0,0,0,0.96);
    --topbar-bg: rgba(0,0,0,0.5);
    --green: #34d399;
    --scroll-thumb: #2a2a2e;
    --scroll-thumb-hover: #3a3a40;
    --scroll-track: transparent;
    --gap-xs: 0.375rem;
    --gap-sm: 0.625rem;
    --gap-md: 1rem;
    --gap-lg: 1.5rem;
    --gap-xl: 2.25rem;
    --page-x: 1.5rem;
    --page-y: 3rem;
    --radius: 12px;
    --radius-sm: 10px;
  }
  [data-theme="light"] {
    --bg: #ffffff;
    --bg-grad: radial-gradient(ellipse 60% 40% at 50% 0%, rgba(0,0,0,0.035), transparent 70%);
    --card: #fafafa;
    --card-hover: #f1f1f3;
    --border: #e6e6ea;
    --border-hover: #d4d4d8;
    --text: #18181b;
    --text-dim: #3f3f46;
    --muted: #71717a;
    --muted-2: #a1a1aa;
    --chip: #f4f4f5;
    --btn-bg: #fafafa;
    --menu-bg: rgba(255,255,255,0.97);
    --overlay: rgba(255,255,255,0.97);
    --topbar-bg: rgba(255,255,255,0.7);
    --green: #10b981;
    --scroll-thumb: #d4d4d8;
    --scroll-thumb-hover: #a1a1aa;
    --scroll-track: transparent;
  }

  html, body { background: var(--bg); }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, sans-serif;
    color: var(--text);
    min-height: 100vh;
    padding: var(--page-y) var(--page-x);
    background: var(--bg);
    background-image: var(--bg-grad);
    -webkit-font-smoothing: antialiased;
    transition: background-color 0.25s, color 0.25s;
  }
  .container { max-width: 1000px; margin: 0 auto; }

  @media (min-width: 900px) {
    html, body, * {
      scrollbar-width: thin;
      scrollbar-color: var(--scroll-thumb) var(--scroll-track);
    }
    ::-webkit-scrollbar { width: 12px; height: 12px; }
    ::-webkit-scrollbar-track { background: var(--scroll-track); border-radius: 999px; }
    ::-webkit-scrollbar-thumb {
      background: var(--scroll-thumb);
      border-radius: 999px;
      border: 3px solid var(--bg);
      background-clip: padding-box;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: var(--scroll-thumb-hover);
      background-clip: padding-box;
      border: 3px solid var(--bg);
    }
    ::-webkit-scrollbar-thumb:active {
      background: var(--text-dim);
      background-clip: padding-box;
      border: 3px solid var(--bg);
    }
    ::-webkit-scrollbar-corner { background: transparent; }
  }
  @media (max-width: 899px) {
    ::-webkit-scrollbar { width: 0; height: 0; }
    * { scrollbar-width: none; }
  }

  header { margin-bottom: var(--gap-xl); }
  h1 {
    font-size: 1.5rem; font-weight: 600;
    letter-spacing: -0.02em;
    display: flex; align-items: center;
    gap: var(--gap-sm); flex-wrap: wrap;
    color: var(--text); line-height: 1.2;
  }
  h1 .badge {
    font-size: 0.72rem; font-weight: 500;
    background: var(--chip); color: var(--muted);
    padding: 0.35rem 0.75rem;
    border-radius: 999px; border: 1px solid var(--border);
    letter-spacing: 0; line-height: 1;
    display: inline-flex; align-items: center;
    margin-left: var(--gap-xs); white-space: nowrap;
  }
  .subtitle {
    color: var(--muted); font-size: 0.85rem;
    margin-top: var(--gap-md);
    display: flex; align-items: center;
    gap: var(--gap-sm); flex-wrap: wrap;
  }
  .path-chip {
    background: var(--chip); border: 1px solid var(--border);
    padding: 0.3rem 0.7rem; border-radius: 6px;
    font-family: ui-monospace, 'SF Mono', Menlo, monospace;
    font-size: 0.78rem; color: var(--text-dim);
    word-break: break-all; line-height: 1.4;
  }

  .toolbar {
    display: flex; gap: var(--gap-sm);
    margin-bottom: var(--gap-lg);
    flex-wrap: wrap; align-items: stretch;
  }
  .toolbar input {
    flex: 1; min-width: 200px;
    background: var(--chip); border: 1px solid var(--border);
    color: var(--text); padding: 0 1rem;
    height: 44px; border-radius: var(--radius-sm);
    font-size: 0.9rem; outline: none;
  }
  .toolbar input::placeholder { color: var(--muted-2); }
  .toolbar input:focus { border-color: var(--border-hover); }
  .stat {
    background: var(--chip); border: 1px solid var(--border);
    padding: 0 1rem; height: 44px;
    border-radius: var(--radius-sm);
    font-size: 0.82rem; color: var(--muted);
    white-space: nowrap; display: flex; align-items: center;
  }
  .stat b { color: var(--text-dim); font-weight: 500; margin-left: 0.4rem; }

  .view-toggle, .theme-toggle, .hidden-toggle {
    display: flex; background: var(--chip);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 3px; gap: 2px; height: 44px; align-items: center;
  }
  .view-toggle button, .theme-toggle button, .hidden-toggle button {
    background: transparent; border: none;
    color: var(--muted); width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 7px; cursor: pointer;
  }
  .view-toggle button:hover, .theme-toggle button:hover, .hidden-toggle button:hover { color: var(--text-dim); }
  .view-toggle button.active, .theme-toggle button.active, .hidden-toggle button.active {
    background: var(--card-hover); color: var(--text);
    box-shadow: inset 0 0 0 1px var(--border);
  }
  .view-toggle button svg, .theme-toggle button svg, .hidden-toggle button svg {
    width: 18px; height: 18px;
    stroke: currentColor; stroke-width: 1.7;
    fill: none; stroke-linecap: round; stroke-linejoin: round;
  }

  ul.files { list-style: none; display: flex; flex-direction: column; gap: var(--gap-xs); }
  ul.files li a {
    display: flex; align-items: center;
    gap: var(--gap-md); padding: 0.85rem 1rem;
    background: var(--card); border: 1px solid var(--border);
    border-radius: var(--radius); text-decoration: none;
    color: var(--text); cursor: pointer;
    transition: background 0.15s, border-color 0.15s, transform 0.15s;
  }
  ul.files li a:hover {
    background: var(--card-hover);
    border-color: var(--border-hover);
    transform: translateX(2px);
  }
  .icon {
    width: 38px; height: 38px;
    display: flex; align-items: center; justify-content: center;
    border-radius: var(--radius-sm); flex-shrink: 0;
    background: var(--chip); border: 1px solid var(--border);
  }
  ul.files li a:hover .icon { border-color: var(--border-hover); }
  .icon svg {
    width: 20px; height: 20px;
    stroke: currentColor; stroke-width: 1.6;
    stroke-linecap: round; stroke-linejoin: round; fill: none;
  }

  /* ============================================================
     THUMBNAILS
     ============================================================ */
  .thumb {
    width: 56px;
    height: 56px;
    border-radius: var(--radius-sm);
    overflow: hidden;
    flex-shrink: 0;
    background: var(--chip);
    border: 1px solid var(--border);
    position: relative;
    transition: border-color 0.15s;
  }
  ul.files li a:hover .thumb { border-color: var(--border-hover); }
  .thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
  .thumb::after {
    content: '';
    position: absolute;
    inset: 0;
    pointer-events: none;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04);
    border-radius: inherit;
  }

  /* Video thumb gets a small play overlay */
  ul.files li a.file-row[data-kind="video"] .thumb::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 20px;
    height: 20px;
    background: rgba(0,0,0,0.55);
    border-radius: 50%;
    z-index: 2;
    pointer-events: none;
    backdrop-filter: blur(2px);
    -webkit-backdrop-filter: blur(2px);
  }
  ul.files li a.file-row[data-kind="video"] .thumb::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 0;
    height: 0;
    border-left: 6px solid #fff;
    border-top: 4px solid transparent;
    border-bottom: 4px solid transparent;
    transform: translate(-30%, -50%);
    z-index: 3;
    pointer-events: none;
    box-shadow: none;
  }

  /* Grid view: bigger thumbnails */
  body.view-grid ul.files li a .thumb {
    width: 100%;
    height: 96px;
    border-radius: var(--radius);
  }
  body.view-grid ul.files li a.file-row[data-kind="video"] .thumb::before {
    width: 32px;
    height: 32px;
  }
  body.view-grid ul.files li a.file-row[data-kind="video"] .thumb::after {
    border-left-width: 10px;
    border-top-width: 6px;
    border-bottom-width: 6px;
  }

  @media (max-width: 640px) {
    body.view-grid ul.files li a .thumb {
      width: 56px;
      height: 56px;
    }
  }

  .info { flex: 1; min-width: 0; }
  .name {
    font-weight: 500; font-size: 0.92rem;
    white-space: nowrap; overflow: hidden;
    text-overflow: ellipsis; color: var(--text);
    letter-spacing: -0.01em;
  }
  .meta {
    color: var(--muted); font-size: 0.75rem;
    margin-top: 0.3rem; display: flex;
    gap: 0.85rem; flex-wrap: wrap; align-items: center;
    font-variant-numeric: tabular-nums;
  }
  .meta span::before {
    content: ''; display: inline-block;
    width: 3px; height: 3px; border-radius: 50%;
    background: var(--muted-2); margin-right: 0.5rem;
    vertical-align: middle;
  }
  .meta span:first-child::before { display: none; }
  .meta .quality-badge::before,
  .meta .search-path::before { display: none; }

  .quality-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.1rem 0.5rem;
    border-radius: 999px;
    background: var(--chip);
    color: var(--text-dim);
    border: 1px solid var(--border-hover);
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    line-height: 1.4;
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
  }
  .quality-badge .quality-tag {
    margin-left: 0.35rem;
    padding: 0.02rem 0.3rem;
    border-radius: 4px;
    background: rgba(255,255,255,0.07);
    color: var(--text-dim);
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.04em;
  }
  [data-theme="light"] .quality-badge .quality-tag {
    background: rgba(0,0,0,0.06);
  }
  body.view-grid .meta .quality-badge {
    align-self: flex-start;
  }

  .arrow {
    color: var(--muted-2); display: flex; align-items: center;
    flex-shrink: 0;
  }
  .arrow svg { width: 16px; height: 16px; stroke: currentColor; stroke-width: 1.8; fill: none; stroke-linecap: round; stroke-linejoin: round; }
  ul.files li a:hover .arrow { color: var(--text-dim); transform: translateX(3px); }
  ul.files li a:hover .arrow svg.dl { transform: translateY(2px); }
  .arrow svg.dl { transition: transform 0.15s; }

  ul.files li.parent-item a {
    display: flex; align-items: center; gap: var(--gap-md);
    padding: 0.75rem 1rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    color: var(--text-dim);
    text-decoration: none; cursor: pointer;
    transition: background 0.15s, border-color 0.15s, transform 0.15s;
    margin-bottom: var(--gap-sm);
  }
  ul.files li.parent-item a:hover {
    background: var(--card-hover);
    border-color: var(--border-hover);
    transform: translateX(-2px);
  }
  ul.files li.parent-item .icon {
    width: 38px; height: 38px; border-radius: var(--radius-sm);
    background: var(--chip); border: 1px solid var(--border);
    color: var(--muted);
    transition: border-color 0.15s, color 0.15s;
  }
  ul.files li.parent-item a:hover .icon {
    border-color: var(--border-hover);
    color: var(--text-dim);
  }
  ul.files li.parent-item .name {
    color: var(--text); font-weight: 500;
  }
  ul.files li.parent-item .meta {
    margin-top: 0.2rem; color: var(--muted);
    font-size: 0.72rem;
  }
  ul.files li.parent-item .arrow svg {
    transition: transform 0.2s;
    transform: rotate(180deg);
  }
  ul.files li.parent-item a:hover .arrow {
    color: var(--text-dim); transform: translateX(-3px);
  }
  ul.files li.parent-item a:hover .arrow svg { transform: rotate(180deg); }

  body.view-grid ul.files li.parent-item {
    grid-column: 1 / -1;
  }
  body.view-grid ul.files li.parent-item a {
    flex-direction: row; align-items: center;
    min-height: auto;
  }

  @media (max-width: 640px) {
    ul.files li.parent-item a { padding: 0.7rem 0.9rem; }
    ul.files li.parent-item .icon { width: 34px; height: 34px; }
  }

  /* ============================================================
     SEARCH
     ============================================================ */
  .search-panel {
    display: none;
    margin-bottom: var(--gap-lg);
  }
  .search-panel.active {
    display: block;
  }
  .search-status {
    font-size: 0.8rem;
    color: var(--muted);
    margin-bottom: var(--gap-md);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-variant-numeric: tabular-nums;
  }
  .search-status .spin {
    width: 12px;
    height: 12px;
    border: 2px solid var(--border-hover);
    border-top-color: var(--text-dim);
    border-radius: 50%;
    animation: searchSpin 0.7s linear infinite;
    display: none;
  }
  .search-status.loading .spin { display: inline-block; }
  @keyframes searchSpin {
    to { transform: rotate(360deg); }
  }
  .search-path {
    color: var(--muted-2);
    font-family: ui-monospace, 'SF Mono', Menlo, monospace;
    font-size: 0.72rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 380px;
  }
  .search-empty {
    padding: 3rem 1rem;
    text-align: center;
    color: var(--muted);
    font-size: 0.85rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
  }
  .search-truncated {
    padding: 0.75rem 1rem;
    background: var(--chip);
    border: 1px dashed var(--border-hover);
    border-radius: var(--radius-sm);
    color: var(--muted);
    font-size: 0.78rem;
    text-align: center;
    margin-top: var(--gap-md);
  }

  body.view-grid ul.files {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: var(--gap-sm);
  }
  body.view-grid ul.files li a {
    flex-direction: column; align-items: flex-start;
    padding: 0.75rem; gap: var(--gap-sm);
    height: 100%; transform: none; min-height: 180px;
  }
  body.view-grid ul.files li a:hover { transform: translateY(-2px); }
  body.view-grid .icon { width: 46px; height: 46px; border-radius: var(--radius); }
  body.view-grid .icon svg { width: 24px; height: 24px; }
  body.view-grid .info {
    width: 100%; display: flex; flex-direction: column;
    gap: 0.35rem; margin-top: auto;
  }
  body.view-grid .name {
    white-space: normal; overflow: hidden;
    display: -webkit-box; -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-height: 1.35; word-break: break-word;
  }
  body.view-grid .meta {
    margin-top: 0; flex-direction: column;
    gap: 0.2rem; font-size: 0.72rem;
    align-items: flex-start;
  }
  body.view-grid .meta span::before { display: none; }
  body.view-grid .arrow { display: none; }

  @media (max-width: 640px) {
    body { padding: 2rem 1rem; }
    h1 { font-size: 1.25rem; }
    .stat { display: none; }
    body.view-grid ul.files {
      display: flex; flex-direction: column; gap: var(--gap-xs);
    }
    body.view-grid ul.files li a {
      flex-direction: row; align-items: center;
      padding: 0.85rem 1rem; min-height: auto;
      gap: var(--gap-md); transform: none;
    }
    body.view-grid .icon { width: 38px; height: 38px; border-radius: var(--radius-sm); }
    body.view-grid .icon svg { width: 20px; height: 20px; }
    body.view-grid .info { width: auto; flex: 1; margin-top: 0; gap: 0; }
    body.view-grid .name { white-space: nowrap; display: block; -webkit-line-clamp: unset; }
    body.view-grid .meta {
      flex-direction: row; gap: 0.85rem;
      margin-top: 0.3rem; font-size: 0.75rem;
      align-items: center;
    }
    body.view-grid .meta span::before { display: inline-block; }
    body.view-grid .meta span:first-child::before { display: none; }
    body.view-grid .arrow { display: flex; }
    .view-toggle { display: none; }
  }

  .empty {
    text-align: center; padding: 4rem 1rem;
    color: var(--muted); grid-column: 1 / -1;
  }
  .empty .big {
    width: 64px; height: 64px;
    margin: 0 auto var(--gap-md); opacity: 0.35;
  }
  .empty .big svg { width: 100%; height: 100%; stroke: currentColor; stroke-width: 1.2; fill: none; stroke-linecap: round; stroke-linejoin: round; }

  footer {
    margin-top: var(--gap-xl);
    padding-top: var(--gap-lg);
    border-top: 1px solid var(--border);
    text-align: center;
    color: var(--muted-2); font-size: 0.75rem;
    letter-spacing: 0.02em;
    display: flex; align-items: center;
    justify-content: center; gap: 0.5rem; line-height: 1;
  }
  footer .pulse {
    display: inline-block;
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--green); box-shadow: 0 0 8px var(--green);
    animation: pulse 2s ease-in-out infinite; flex-shrink: 0;
  }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  .fs-fab {
    position: fixed;
    right: 1rem;
    bottom: 1rem;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: var(--card);
    color: var(--text);
    border: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 900;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    transition: background 0.15s, border-color 0.15s, transform 0.15s;
  }
  .fs-fab:hover {
    background: var(--card-hover);
    border-color: var(--border-hover);
    transform: scale(1.05);
  }
  .fs-fab:active {
    transform: scale(0.95);
  }
  .fs-fab svg {
    width: 20px;
    height: 20px;
    stroke: currentColor;
    stroke-width: 1.8;
    fill: none;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
  .fs-fab.hidden {
    opacity: 0;
    pointer-events: none;
  }

  .viewer {
    position: fixed; inset: 0;
    background: var(--overlay);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    z-index: 1000; display: none; flex-direction: column;
    opacity: 0; transition: opacity 0.2s ease;
  }
  .viewer.open { display: flex; opacity: 1; }

  .viewer-top {
    display: flex; align-items: center;
    gap: var(--gap-md); padding: 1rem 1.25rem;
    border-bottom: 1px solid var(--border);
    background: var(--topbar-bg); z-index: 3;
    transition: opacity 0.25s ease, transform 0.25s ease, padding 0.25s ease, border-color 0.25s ease;
  }
  .viewer.video-fullscreen .viewer-top {
    opacity: 0; transform: translateY(-8px);
    padding-top: 0; padding-bottom: 0;
    border-color: transparent; pointer-events: none;
    height: 0; overflow: hidden;
  }
  .viewer-title {
    flex: 1; min-width: 0; color: var(--text);
    font-size: 0.9rem; font-weight: 500;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  }
  .viewer-meta {
    color: var(--muted); font-size: 0.75rem;
    white-space: nowrap; font-variant-numeric: tabular-nums;
  }
  .viewer-btn {
    width: 38px; height: 38px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 10px; color: var(--text-dim);
    background: var(--btn-bg); border: 1px solid var(--border);
    cursor: pointer; text-decoration: none;
    flex-shrink: 0;
  }
  .viewer-btn:hover { color: var(--text); border-color: var(--border-hover); }
  .viewer-btn svg {
    width: 18px; height: 18px;
    stroke: currentColor; stroke-width: 1.7;
    fill: none; stroke-linecap: round; stroke-linejoin: round;
  }
  .viewer-body {
    flex: 1; position: relative;
    display: flex; align-items: center; justify-content: center;
    overflow: hidden; padding: 1.5rem;
  }
  .viewer-content {
    max-width: 100%; max-height: 100%;
    display: flex; align-items: center; justify-content: center;
    width: 100%; height: 100%;
  }
  .viewer-content img {
    max-width: 100%; max-height: 100%;
    object-fit: contain; border-radius: 8px; user-select: none;
    filter: contrast(1.06) saturate(1.10);
  }
  .viewer-content iframe {
    width: 100%; height: 100%;
    border: none; border-radius: 8px;
    background: var(--card);
  }
  .viewer-content pre {
    width: 100%; height: 100%; overflow: auto;
    background: var(--card); border: 1px solid var(--border);
    border-radius: 10px; padding: 1.25rem;
    color: var(--text-dim);
    font-family: ui-monospace, 'SF Mono', Menlo, monospace;
    font-size: 0.82rem; line-height: 1.6;
    white-space: pre-wrap; word-break: break-word;
  }

  .video-wrap {
    position: relative; width: 100%; height: 100%;
    display: flex; align-items: center; justify-content: center;
    background: #000; border-radius: 10px; overflow: hidden;
  }
  .video-wrap:focus { outline: none; }
  .video-wrap:focus-visible { outline: 2px solid var(--border-hover); outline-offset: 2px; }
  .video-wrap video {
    width: 100%; height: 100%; max-height: 100%;
    object-fit: contain; background: #000; display: block;
    filter: contrast(1.10) saturate(1.15);
  }

  .v-ctrl {
    position: absolute; left: 0; right: 0; bottom: 0;
    padding: 3rem 1rem 0.9rem;
    background: linear-gradient(to top, rgba(0,0,0,0.9), rgba(0,0,0,0.5) 60%, transparent);
    display: flex; flex-direction: column; gap: 0.5rem;
    opacity: 1; transform: translateY(0);
    transition: opacity 0.35s ease, transform 0.35s ease;
    pointer-events: auto; color: #fff;
  }
  .video-wrap.idle .v-ctrl {
    opacity: 0; transform: translateY(12px);
    pointer-events: none;
  }
  .video-wrap.hide-cursor { cursor: none; }

  .v-progress {
    position: relative; height: 14px;
    cursor: pointer; display: flex; align-items: center;
  }
  .v-progress-track {
    position: relative; width: 100%; height: 4px;
    background: rgba(255,255,255,0.15);
    border-radius: 999px; overflow: hidden;
    transition: height 0.15s;
  }
  .v-progress:hover .v-progress-track { height: 6px; }
  .v-buffered {
    position: absolute; top: 0; left: 0; bottom: 0;
    background: rgba(255,255,255,0.2); width: 0%;
  }
  .v-played {
    position: absolute; top: 0; left: 0; bottom: 0;
    background: #fff; width: 0%; border-radius: 999px;
  }
  .v-thumb {
    position: absolute; top: 50%;
    width: 12px; height: 12px; background: #fff;
    border-radius: 50%;
    transform: translate(-50%, -50%) scale(0);
    transition: transform 0.15s;
    box-shadow: 0 0 0 4px rgba(255,255,255,0.15);
    pointer-events: none;
  }
  .v-progress:hover .v-thumb { transform: translate(-50%, -50%) scale(1); }

  .v-time-tooltip {
    position: absolute;
    bottom: 22px;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.9);
    color: #fff;
    font-size: 0.72rem;
    font-weight: 500;
    padding: 0.25rem 0.5rem;
    border-radius: 6px;
    white-space: nowrap;
    pointer-events: none;
    opacity: 0;
    transition: opacity 0.12s ease;
    font-variant-numeric: tabular-nums;
    z-index: 6;
    border: 1px solid rgba(255,255,255,0.1);
  }
  .v-time-tooltip.show { opacity: 1; }
  .video-wrap.idle .v-time-tooltip { opacity: 0 !important; }

  .v-row {
    display: flex; align-items: center;
    gap: 0.4rem; color: #fff;
    flex-wrap: nowrap;
  }
  .v-row button {
    background: transparent; border: none;
    color: #fff; width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 8px; cursor: pointer;
    flex-shrink: 0;
  }
  .v-row button:hover { background: rgba(255,255,255,0.1); }
  .v-row button:active { transform: scale(0.92); }
  .v-row button svg {
    width: 20px; height: 20px;
    stroke: currentColor; stroke-width: 1.7;
    fill: none; stroke-linecap: round; stroke-linejoin: round;
  }
  .v-time {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.85);
    font-variant-numeric: tabular-nums;
    padding: 0 0.4rem;
    user-select: none;
    white-space: nowrap;
  }
  .v-spacer { flex: 1; }

  .v-volume { display: flex; align-items: center; gap: 0.4rem; }
  .v-volume-slider {
    width: 0; overflow: hidden;
    transition: width 0.2s;
    display: flex; align-items: center;
  }
  .v-volume:hover .v-volume-slider,
  .v-volume-slider.active { width: 80px; }
  .v-volume-slider input {
    width: 80px;
    -webkit-appearance: none;
    appearance: none;
    height: 4px;
    background: rgba(255,255,255,0.2);
    border-radius: 999px;
    outline: none; cursor: pointer;
  }
  .v-volume-slider input::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 12px; height: 12px;
    background: #fff; border-radius: 50%; cursor: pointer;
  }
  .v-volume-slider input::-moz-range-thumb {
    width: 12px; height: 12px;
    background: #fff; border-radius: 50%;
    border: none; cursor: pointer;
  }

  .v-bigplay {
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 96px; height: 96px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.15);
    border: 2.5px solid rgba(255, 255, 255, 0.95);
    color: #ffffff;
    display: none;
    align-items: center; justify-content: center;
    padding: 0; cursor: pointer;
    transition: transform 0.2s ease, border-color 0.2s ease, background 0.2s ease;
    z-index: 2;
    backdrop-filter: blur(2px);
    -webkit-backdrop-filter: blur(2px);
  }
  .v-bigplay.show { display: flex; }
  .v-bigplay:hover {
    transform: translate(-50%, -50%) scale(1.06);
    border-color: #ffffff;
    background: rgba(0, 0, 0, 0.28);
  }
  .v-bigplay:active { transform: translate(-50%, -50%) scale(0.97); }
  .v-bigplay svg {
    width: 38px; height: 38px;
    display: block;
    fill: none;
    stroke: #ffffff;
    stroke-width: 2;
    stroke-linejoin: round;
    stroke-linecap: round;
    margin-left: 3px;
  }
  .video-wrap.idle .v-bigplay.show {
    opacity: 0; pointer-events: none;
    transition: opacity 0.4s ease;
  }
  .v-loading {
    position: absolute; top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    width: 40px; height: 40px;
    border: 3px solid rgba(255,255,255,0.15);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    display: none; z-index: 2;
  }
  .v-loading.show { display: block; }
  @keyframes spin { to { transform: translate(-50%,-50%) rotate(360deg); } }

  .v-error {
    position: absolute;
    inset: 0;
    display: none;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    color: #fff;
    background: rgba(0,0,0,0.85);
    text-align: center;
    padding: 2rem;
    z-index: 4;
  }
  .v-error.show { display: flex; }
  .v-error svg {
    width: 42px; height: 42px;
    stroke: #f87171; stroke-width: 1.6;
    fill: none; stroke-linecap: round; stroke-linejoin: round;
  }
  .v-error .v-error-title { font-size: 0.95rem; font-weight: 600; }
  .v-error .v-error-msg { font-size: 0.78rem; color: rgba(255,255,255,0.65); max-width: 320px; line-height: 1.4; }

  .v-seek-indicator {
    position: absolute;
    top: 50%;
    transform: translateY(-50%) scale(0.9);
    width: 78px; height: 78px;
    border-radius: 50%;
    background: rgba(0,0,0,0.5);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    gap: 0.15rem;
    color: #fff;
    font-size: 0.75rem;
    font-weight: 600;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s, transform 0.2s;
    z-index: 3;
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
  }
  .v-seek-indicator.left  { left: 8%; }
  .v-seek-indicator.right { right: 8%; }
  .v-seek-indicator.show {
    opacity: 1;
    transform: translateY(-50%) scale(1);
  }
  .v-seek-indicator svg {
    width: 22px; height: 22px;
    stroke: currentColor; stroke-width: 2;
    fill: none; stroke-linecap: round; stroke-linejoin: round;
  }

  .v-resume-toast {
    position: absolute;
    top: 1rem;
    left: 50%;
    transform: translate(-50%, -8px);
    background: rgba(20, 20, 22, 0.95);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.12);
    color: #fff;
    padding: 0.55rem 0.7rem 0.55rem 0.9rem;
    border-radius: 999px;
    font-size: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    z-index: 7;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.25s, transform 0.25s;
    white-space: nowrap;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
  }
  .v-resume-toast.show {
    opacity: 1;
    transform: translate(-50%, 0);
    pointer-events: auto;
  }
  .audio-card .v-resume-toast { top: 0.75rem; }
  .v-resume-toast .v-resume-restart {
    background: rgba(255,255,255,0.1);
    border: none;
    color: #fff;
    padding: 0.25rem 0.65rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 500;
    cursor: pointer;
    font-family: inherit;
  }
  .v-resume-toast .v-resume-restart:hover { background: rgba(255,255,255,0.2); }
  .video-wrap.idle .v-resume-toast { opacity: 0; }

  .v-menu {
    position: absolute;
    bottom: 60px; right: 1rem;
    background: var(--menu-bg);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 6px;
    display: none; flex-direction: column;
    gap: 2px; z-index: 5; min-width: 90px;
    max-height: 70%;
    overflow-y: auto;
  }
  .video-wrap.idle .v-menu { opacity: 0; pointer-events: none; }
  .v-menu.show { display: flex; }
  .v-menu button {
    background: transparent; border: none;
    color: var(--text-dim);
    text-align: left;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.82rem;
    white-space: nowrap;
  }
  .v-menu button:hover { background: var(--card-hover); color: var(--text); }
  .v-menu button.active { color: var(--text); font-weight: 500; }

  .v-picture-menu {
    min-width: 220px;
    padding: 0.75rem;
    gap: 0.6rem;
  }
  .v-picture-row {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  .v-picture-row label {
    font-size: 0.72rem;
    color: var(--muted);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .v-picture-row label span:last-child {
    color: var(--text-dim);
    font-variant-numeric: tabular-nums;
    font-size: 0.7rem;
  }
  .v-picture-row input[type="range"] {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 4px;
    background: var(--border-hover);
    border-radius: 999px;
    outline: none;
    cursor: pointer;
  }
  .v-picture-row input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 12px; height: 12px;
    background: var(--text);
    border-radius: 50%;
    cursor: pointer;
  }
  .v-picture-row input[type="range"]::-moz-range-thumb {
    width: 12px; height: 12px;
    background: var(--text);
    border-radius: 50%;
    border: none;
    cursor: pointer;
  }
  .v-picture-reset {
    background: var(--chip) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-dim) !important;
    padding: 0.4rem !important;
    border-radius: 6px !important;
    font-size: 0.72rem !important;
    text-align: center !important;
    margin-top: 0.25rem;
  }
  .v-picture-reset:hover {
    background: var(--card-hover) !important;
    color: var(--text) !important;
  }

  .v-preset-overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.55);
    backdrop-filter: blur(6px);
    -webkit-backdrop-filter: blur(6px);
    display: none;
    align-items: center;
    justify-content: center;
    z-index: 20;
    opacity: 0;
    transition: opacity 0.2s ease;
  }
  .v-preset-overlay.show {
    display: flex;
    opacity: 1;
  }
  .v-preset-panel {
    background: var(--menu-bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.25rem;
    width: min(90%, 500px);
    max-height: 80%;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    transform: translateY(10px) scale(0.98);
    transition: transform 0.2s ease;
  }
  .v-preset-overlay.show .v-preset-panel {
    transform: translateY(0) scale(1);
  }
  .v-preset-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.9rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.6rem;
  }
  .v-preset-title button {
    background: transparent;
    border: none;
    color: var(--muted);
    width: 28px;
    height: 28px;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    transition: background 0.15s, color 0.15s;
  }
  .v-preset-title button:hover {
    background: var(--card-hover);
    color: var(--text);
  }
  .v-preset-title button svg {
    width: 16px; height: 16px;
    stroke: currentColor; stroke-width: 2;
    fill: none; stroke-linecap: round; stroke-linejoin: round;
  }
  .v-preset-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 0.6rem;
  }
  .v-preset-item {
    background: var(--chip);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.75rem 0.85rem;
    cursor: pointer;
    text-align: left;
    transition: background 0.15s, border-color 0.15s, transform 0.1s;
    color: var(--text);
    font-family: inherit;
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
  }
  .v-preset-item:hover {
    background: var(--card-hover);
    border-color: var(--border-hover);
    transform: translateY(-1px);
  }
  .v-preset-item.active {
    border-color: var(--green);
    box-shadow: inset 0 0 0 1px var(--green);
  }
  .v-preset-item .v-preset-name {
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: -0.01em;
  }
  .v-preset-item .v-preset-desc {
    font-size: 0.7rem;
    color: var(--muted);
    line-height: 1.3;
  }
  .v-preset-item .v-preset-swatch {
    height: 4px;
    border-radius: 2px;
    margin-top: 0.15rem;
    background: linear-gradient(90deg, #1a1a1a, #f5f5f5);
  }
  .v-preset-item[data-preset="cinema"] .v-preset-swatch {
    background: linear-gradient(90deg, #0a0a14, #c8b89a);
  }
  .v-preset-item[data-preset="animation"] .v-preset-swatch {
    background: linear-gradient(90deg, #1a0a14, #ff7eb9, #ffd54f);
  }
  .v-preset-item[data-preset="anime"] .v-preset-swatch {
    background: linear-gradient(90deg, #0d0a1a, #a78bfa, #f472b6);
  }
  .v-preset-item[data-preset="sport"] .v-preset-swatch {
    background: linear-gradient(90deg, #0a1410, #34d399, #60a5fa);
  }
  .v-preset-item[data-preset="bw"] .v-preset-swatch {
    background: linear-gradient(90deg, #000, #fff);
  }
  .v-preset-item[data-preset="dark-room"] .v-preset-swatch {
    background: linear-gradient(90deg, #000, #2a2a35);
  }
  .v-preset-item[data-preset="hdr"] .v-preset-swatch {
    background: linear-gradient(90deg, #000, #f5b544, #e879f9);
  }
  .v-preset-item[data-preset="washed"] .v-preset-swatch {
    background: linear-gradient(90deg, #2a2a2a, #f5d59a);
  }

  .v-preset-btn {
    width: auto !important;
    padding: 0 0.6rem !important;
    gap: 0.35rem;
    font-size: 0.75rem;
    font-weight: 500;
    display: inline-flex !important;
    align-items: center;
  }
  .v-preset-btn svg {
    width: 16px !important;
    height: 16px !important;
  }
  .v-preset-btn .v-preset-btn-label {
    display: inline-block;
    white-space: nowrap;
  }
  @media (max-width: 640px) and (orientation: portrait) {
    .v-preset-btn .v-preset-btn-label { display: none; }
    .v-preset-btn { padding: 0 !important; width: 34px !important; }
    .v-preset-grid { grid-template-columns: 1fr 1fr; }
  }

  .v-quality {
    width: auto !important;
    padding: 0 0.6rem !important;
    gap: 0.4rem;
    font-size: 0.78rem;
    font-weight: 500;
    cursor: default !important;
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    position: relative;
    overflow: hidden;
    border-radius: 8px;
    pointer-events: none;
    display: inline-flex;
    align-items: center;
    color: #fff;
  }
  .v-quality::after {
    content: '';
    position: absolute;
    top: 0; bottom: 0;
    left: -40%;
    width: 40%;
    background: linear-gradient(90deg,
      rgba(255,255,255,0) 0%,
      rgba(255,255,255,0.18) 50%,
      rgba(255,255,255,0) 100%);
    filter: blur(6px);
    animation: qshine 3.2s ease-in-out infinite;
    pointer-events: none;
    border-radius: inherit;
  }
  @keyframes qshine {
    0%   { left: -40%; }
    60%  { left: 100%; }
    100% { left: 100%; }
  }
  .v-quality .v-quality-label {
    min-width: 2.6rem;
    text-align: left;
    white-space: nowrap;
    position: relative;
    z-index: 1;
  }
  .v-quality .v-quality-tag {
    display: inline-block;
    padding: 0.05rem 0.35rem;
    border-radius: 4px;
    background: rgba(255,255,255,0.08);
    color: #fff;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    position: relative;
    z-index: 1;
  }

  .audio-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    width: min(100%, 520px);
    display: flex; flex-direction: column; gap: 1.25rem;
    position: relative;
  }
  .audio-head { display: flex; align-items: center; gap: 1rem; }
  .audio-head .a-icon {
    width: 56px; height: 56px;
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    background: var(--chip); border: 1px solid var(--border);
    color: #f472b6; flex-shrink: 0;
  }
  .audio-head .a-icon svg { width: 26px; height: 26px; stroke: currentColor; stroke-width: 1.6; fill: none; stroke-linecap: round; stroke-linejoin: round; }
  .audio-head .a-name {
    font-size: 0.95rem; font-weight: 500;
    word-break: break-word; line-height: 1.35;
    color: var(--text);
  }
  .audio-card .v-ctrl {
    background: none;
    padding: 0;
    transform: none;
    color: var(--text);
    position: static;
  }
  .audio-card .v-row { color: var(--text); }
  .audio-card .v-row button { color: var(--text); }
  .audio-card .v-row button:hover { background: var(--card-hover); }
  .audio-card .v-time { color: var(--muted); }
  .audio-card .v-progress-track { background: var(--border-hover); }
  .audio-card .v-played { background: var(--text); }
  .audio-card .v-thumb { background: var(--text); box-shadow: 0 0 0 4px rgba(139,92,246,0.14); }
  .audio-card .v-volume-slider input { background: var(--border-hover); }
  .audio-card .v-volume-slider input::-webkit-slider-thumb { background: var(--text); }
  .audio-card .v-volume-slider input::-moz-range-thumb { background: var(--text); }
  .audio-card .v-menu {
    bottom: auto;
    top: 50%;
    right: 1rem;
    transform: translateY(-50%);
  }

  .video-wrap:fullscreen,
  .video-wrap:-webkit-full-screen {
    border-radius: 0;
    width: 100vw; height: 100vh;
  }
  .video-wrap:fullscreen .v-ctrl,
  .video-wrap:-webkit-full-screen .v-ctrl {
    padding-bottom: calc(0.9rem + env(safe-area-inset-bottom, 0px));
  }

  @media (max-width: 640px) and (orientation: portrait) {
    .v-hide-mobile { display: none !important; }
    .v-row { gap: 0.2rem; }
    .v-row button { width: 34px; height: 34px; }
    .v-row button svg { width: 19px; height: 19px; }
    .v-time { font-size: 0.72rem; padding: 0 0.25rem; }
    .v-ctrl { padding: 2rem 0.75rem 0.75rem; }
    .v-quality { padding: 0 0.45rem !important; font-size: 0.72rem; }
    .v-quality .v-quality-label { min-width: 2rem; }
    .v-bigplay { width: 78px; height: 78px; border-width: 2px; }
    .v-bigplay svg { width: 32px; height: 32px; margin-left: 2px; }
    .v-menu { bottom: 54px; right: 0.5rem; }
  }
  @media (max-width: 380px) and (orientation: portrait) {
    .v-hide-narrow { display: none !important; }
  }

  .splash {
    position: fixed; inset: 0;
    background: var(--bg); background-image: var(--bg-grad);
    z-index: 9999;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    gap: 1.5rem;
    opacity: 1; transition: opacity 0.55s ease;
  }
  .splash.hidden { opacity: 0; pointer-events: none; }
  .splash-icon {
    width: 88px; height: 88px; border-radius: 22px;
    background: var(--chip); border: 1px solid var(--border);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    animation: splash-pop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  [data-theme="light"] .splash-icon { box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08); }
  .splash-icon svg { width: 46px; height: 46px; }
  .splash-title {
    font-size: 1.35rem; font-weight: 600;
    letter-spacing: -0.02em; color: var(--text);
    animation: splash-fade-up 0.7s ease 0.15s backwards;
  }
  .splash-sub {
    font-size: 0.78rem; color: var(--muted);
    letter-spacing: 0.02em;
    animation: splash-fade-up 0.7s ease 0.25s backwards;
  }
  .splash-bar {
    width: 140px; height: 3px;
    border-radius: 999px; background: var(--border);
    overflow: hidden; position: relative;
    margin-top: 0.25rem;
    animation: splash-fade-up 0.7s ease 0.35s backwards;
  }
  .splash-bar::after {
    content: '';
    position: absolute; top: 0; left: -40%;
    width: 40%; height: 100%;
    border-radius: 999px;
    background: var(--text); opacity: 0.75;
    animation: splash-slide 1.4s ease-in-out infinite;
  }
  @keyframes splash-pop {
    0%   { transform: scale(0.85); opacity: 0; }
    100% { transform: scale(1);    opacity: 1; }
  }
  @keyframes splash-fade-up {
    0%   { transform: translateY(6px); opacity: 0; }
    100% { transform: translateY(0);   opacity: 1; }
  }
  @keyframes splash-slide {
    0%   { left: -40%; }
    100% { left: 100%; }
  }
</style>
</head>
<body class="view-grid">

<div class="splash" id="splash">
  <div class="splash-icon">
    <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
      <path d="M4 8a2 2 0 0 1 2-2h6.5l2.2 2.5H26a2 2 0 0 1 2 2V23a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V8z" fill="#fbbf24"/>
      <path d="M4 10h24" stroke="#f59e0b" stroke-width="1.2"/>
    </svg>
  </div>
  <div class="splash-title">Shared Files</div>
  <div class="splash-sub">Loading your library…</div>
  <div class="splash-bar"></div>
</div>

<button class="fs-fab" id="fsFab" title="Fullscreen" aria-label="Toggle fullscreen">
  <svg viewBox="0 0 24 24">
    <path d="M3 9V3h6"/>
    <path d="M15 3h6v6"/>
    <path d="M9 21H3v-6"/>
    <path d="M21 15v6h-6"/>
  </svg>
</button>

<div class="container">
  <header>
    <h1>
      <span class="title">Shared Files</span>
      <span class="badge">{{ count }} items</span>
    </h1>
    <div class="subtitle">
      <span>Path</span>
      <span class="path-chip">{{ display_path }}</span>
    </div>
  </header>

  <div class="toolbar">
    <input type="text" id="search" placeholder="Search across all subfolders..." autocomplete="off">
    <div class="stat">Total <b>{{ total_size }}</b></div>
    <div class="view-toggle" role="group" aria-label="View mode">
      <button type="button" data-view="grid" title="Grid view" aria-label="Grid view">
        <svg viewBox="0 0 24 24">{{ icons.grid[0]|safe }}</svg>
      </button>
      <button type="button" data-view="list" title="List view" aria-label="List view">
        <svg viewBox="0 0 24 24">{{ icons.list[0]|safe }}</svg>
      </button>
    </div>
    <div class="hidden-toggle" role="group" aria-label="Hidden files">
      <button type="button" id="hiddenBtn" title="Show hidden files" aria-label="Toggle hidden files">
        <svg viewBox="0 0 24 24"></svg>
      </button>
    </div>
    <div class="theme-toggle" role="group" aria-label="Theme">
      <button type="button" data-theme-value="dark" title="Dark theme" aria-label="Dark theme">
        <svg viewBox="0 0 24 24">{{ icons.moon[0]|safe }}</svg>
      </button>
      <button type="button" data-theme-value="light" title="Light theme" aria-label="Light theme">
        <svg viewBox="0 0 24 24">{{ icons.sun[0]|safe }}</svg>
      </button>
    </div>
  </div>

  <div class="search-panel" id="searchPanel">
    <div class="search-status" id="searchStatus">
      <span class="spin"></span>
      <span class="search-status-text">Searching…</span>
    </div>
    <ul class="files" id="searchResults"></ul>
    <div class="search-truncated" id="searchTruncated" style="display:none;">
      Showing first N results. Refine your search.
    </div>
  </div>

  <ul class="files" id="fileList">
    {% if parent is not none %}
    <li class="parent-item" data-name="__parent__">
      <a href="{{ url_for('browse', subpath=parent) }}" class="nav-link">
        <div class="icon">
          <svg viewBox="0 0 24 24">
            <path d="M12 19V5"/>
            <path d="M5 12l7-7 7 7"/>
          </svg>
        </div>
        <div class="info">
          <div class="name">Back to parent folder</div>
          <div class="meta">Go up one level</div>
        </div>
        <div class="arrow">
          <svg viewBox="0 0 24 24">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </div>
      </a>
    </li>
    {% endif %}

    {% for item in items %}
    <li data-name="{{ item.name|lower }}">
      {% if item.is_dir %}
      <a href="{{ item.url }}" class="nav-link">
        <div class="icon" style="color: {{ item.color }};"><svg viewBox="0 0 24 24">{{ item.svg|safe }}</svg></div>
        <div class="info">
          <div class="name">{{ item.name }}/</div>
          <div class="meta"><span>{{ item.mtime }}</span></div>
        </div>
        <div class="arrow"><svg viewBox="0 0 24 24">{{ icons.right[0]|safe }}</svg></div>
      </a>
      {% else %}
      <a href="{{ item.url }}"
         class="file-row"
         data-url="{{ item.url }}"
         data-name="{{ item.name }}"
         data-kind="{{ item.kind or '' }}"
         data-size="{{ item.size }}"
         data-quality="{{ item.quality or '' }}"
         data-quality-tag="{{ item.quality_tag or '' }}"
         {% if not item.kind %}download{% endif %}>
        {% if item.thumb %}
        <div class="thumb">
          <img src="{{ item.thumb }}" alt="" loading="lazy" decoding="async">
        </div>
        {% else %}
        <div class="icon" style="color: {{ item.color }};"><svg viewBox="0 0 24 24">{{ item.svg|safe }}</svg></div>
        {% endif %}
        <div class="info">
          <div class="name">{{ item.name }}</div>
          <div class="meta">
            <span>{{ item.size }}</span>
            <span>{{ item.mtime }}</span>
            {% if item.quality %}<span class="quality-badge">{{ item.quality }}{% if item.quality_tag %}<span class="quality-tag">{{ item.quality_tag }}</span>{% endif %}</span>{% endif %}
          </div>
        </div>
        <div class="arrow">
          {% if item.kind %}
          <svg viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>
          {% else %}
          <svg class="dl" viewBox="0 0 24 24">{{ icons.down[0]|safe }}</svg>
          {% endif %}
        </div>
      </a>
      {% endif %}
    </li>
    {% endfor %}
  </ul>

  {% if not items and parent is none %}
  <div class="empty">
    <div class="big">
      <svg viewBox="0 0 24 24">
        <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>
        <path d="M9 14l3 3 3-3"/>
      </svg>
    </div>
    <div>No files found in this directory</div>
  </div>
  {% endif %}

  <footer>
    <span>Local server</span>
    <span class="pulse"></span>
    <span>port {{ port }}</span>
  </footer>
</div>

<div class="viewer" id="viewer">
  <div class="viewer-top">
    <div class="viewer-title" id="vTitle"></div>
    <div class="viewer-meta" id="vMeta"></div>
    <a class="viewer-btn" id="vDownload" href="#" download title="Download">
      <svg viewBox="0 0 24 24"><path d="M12 5v14"/><path d="M19 12l-7 7-7-7"/></svg>
    </a>
    <button class="viewer-btn" id="vClose" title="Close (Esc)">
      <svg viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg>
    </button>
  </div>
  <div class="viewer-body">
    <div class="viewer-content" id="vContent"></div>
  </div>
</div>

<script>
  // ============================================================
  // SPLASH
  // ============================================================
  (function(){
    const splash = document.getElementById('splash');
    if (!splash) return;
    const MIN_SHOW_MS = 1400;
    const startTime = performance.now();
    let hidden = false;
    function hideSplash(){
      if (hidden) return;
      hidden = true;
      const remaining = Math.max(0, MIN_SHOW_MS - (performance.now() - startTime));
      setTimeout(() => {
        splash.classList.add('hidden');
        setTimeout(() => { try { splash.remove(); } catch(e){} }, 700);
      }, remaining);
    }
    if (document.readyState === 'complete') hideSplash();
    else {
      window.addEventListener('load', hideSplash);
      setTimeout(hideSplash, 3500);
    }
  })();

  // ============================================================
  // THEME
  // ============================================================
  const THEME_KEY = 'shared_files_theme';
  const themeButtons = document.querySelectorAll('.theme-toggle button');

  function getSavedTheme(){
    try {
      const v = localStorage.getItem(THEME_KEY);
      return (v === 'dark' || v === 'light') ? v : 'dark';
    } catch { return 'dark'; }
  }
  function applyTheme(theme){
    document.documentElement.setAttribute('data-theme', theme);
    themeButtons.forEach(b => b.classList.toggle('active', b.dataset.themeValue === theme));
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) metaThemeColor.setAttribute('content', theme === 'light' ? '#ffffff' : '#000000');
  }
  themeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const theme = btn.dataset.themeValue;
      try { localStorage.setItem(THEME_KEY, theme); } catch {}
      applyTheme(theme);
    });
  });
  applyTheme(getSavedTheme());

  // ============================================================
  // HIDDEN TOGGLE
  // ============================================================
  const HIDDEN_KEY = 'shared_files_hidden';
  const hiddenBtn = document.getElementById('hiddenBtn');

  const EYE_OPEN = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
  const EYE_CLOSED = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>';

  function isHiddenEnabled(){
    try {
      const u = new URL(location.href);
      if (u.searchParams.get('hidden') === '1') return true;
      if (u.searchParams.get('hidden') === '0') return false;
    } catch {}
    try { return localStorage.getItem(HIDDEN_KEY) === '1'; } catch { return false; }
  }
  function setHiddenEnabled(v){
    try { localStorage.setItem(HIDDEN_KEY, v ? '1' : '0'); } catch {}
  }
  function applyHiddenButton(){
    const on = isHiddenEnabled();
    hiddenBtn.classList.toggle('active', on);
    hiddenBtn.title = on ? 'Hide hidden files' : 'Show hidden files';
    hiddenBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
    hiddenBtn.querySelector('svg').innerHTML = on ? EYE_OPEN : EYE_CLOSED;
  }
  function withHiddenParam(url){
    try {
      const u = new URL(url, location.origin);
      if (isHiddenEnabled()) u.searchParams.set('hidden', '1');
      else u.searchParams.delete('hidden');
      const q = u.searchParams.toString();
      return u.pathname + (q ? '?' + q : '');
    } catch { return url; }
  }
  hiddenBtn.addEventListener('click', () => {
    const next = !isHiddenEnabled();
    setHiddenEnabled(next);
    try {
      const u = new URL(location.href);
      if (next) u.searchParams.set('hidden', '1');
      else u.searchParams.delete('hidden');
      history.replaceState(history.state, '', u.pathname + u.search);
    } catch {}
    applyHiddenButton();
    navigateTo(location.pathname, false);
  });
  applyHiddenButton();

  // ============================================================
  // FULLSCREEN
  // ============================================================
  const fsFab = document.getElementById('fsFab');
  function isFS(){
    return !!(document.fullscreenElement || document.webkitFullscreenElement || document.msFullscreenElement);
  }
  function requestFS(el){
    const fn = el.requestFullscreen || el.webkitRequestFullscreen || el.msRequestFullscreen;
    if (!fn) return;
    try {
      const p = fn.call(el, { navigationUI: 'hide' });
      if (p && p.catch) p.catch(() => {});
    } catch(e){}
  }
  function exitFS(){
    fsGuardActive = false;
    const fn = document.exitFullscreen || document.webkitExitFullscreen || document.msExitFullscreen;
    if (!fn) return;
    try { const p = fn.call(document); if (p && p.catch) p.catch(() => {}); } catch(e){}
  }
  function updateFab(){
    const fs = isFS();
    if (fs) {
      fsFab.querySelector('svg').innerHTML =
        '<path d="M9 3v6H3"/>' +
        '<path d="M15 3h6v6"/>' +
        '<path d="M3 15h6v6"/>' +
        '<path d="M21 15v6h-6"/>';
    } else {
      fsFab.querySelector('svg').innerHTML =
        '<path d="M3 9V3h6"/>' +
        '<path d="M15 3h6v6"/>' +
        '<path d="M9 21H3v-6"/>' +
        '<path d="M21 15v6h-6"/>';
    }
    fsFab.title = fs ? 'Exit fullscreen' : 'Fullscreen';
    fsFab.classList.toggle('hidden', document.getElementById('viewer').classList.contains('open'));
  }
  fsFab.addEventListener('click', () => {
    if (isFS()) exitFS();
    else requestFS(document.documentElement);
  });

  // ------------------------------------------------------------
  // Fullscreen history guard
  // ------------------------------------------------------------
  const FS_GUARD_KEY = '__fs_guard__';
  let fsGuardActive = false;
  let fsGuardPushed = false;
  let lastFsGuardTime = 0;

  function pushFsGuard(){
    if (fsGuardPushed) return;
    try {
      history.pushState(
        { ...(history.state || {}), [FS_GUARD_KEY]: true, url: location.pathname + location.search },
        '',
        location.href
      );
      fsGuardPushed = true;
      fsGuardActive = true;
      lastFsGuardTime = Date.now();
    } catch(e){}
  }

  function handleFsGuardPop(){
    const now = Date.now();

    if (fsGuardActive && now - lastFsGuardTime < 500) {
      fsGuardActive = false;
      fsGuardPushed = false;
      return false;
    }

    if (isFS() && fsGuardActive) {
      lastFsGuardTime = now;
      fsGuardPushed = false;
      pushFsGuard();
      const el = document.fullscreenElement
              || document.webkitFullscreenElement
              || document.msFullscreenElement;
      if (el) requestFS(el);
      else requestFS(document.documentElement);
      return true;
    }

    if (!isFS()) {
      fsGuardActive = false;
      fsGuardPushed = false;
    }
    return false;
  }

  function onFullscreenChange(){
    const fs = isFS();

    if (fs) {
      pushFsGuard();
    } else {
      fsGuardPushed = false;
      fsGuardActive = false;
      refreshFileList();
    }

    updateFab();
    viewer.classList.toggle('video-fullscreen', fs);
  }
  document.addEventListener('fullscreenchange', onFullscreenChange);
  document.addEventListener('webkitfullscreenchange', onFullscreenChange);
  updateFab();

  // ============================================================
  // VIEW TOGGLE
  // ============================================================
  const STORAGE_KEY = 'shared_files_view';
  function applyView(view) {
    const isMobile = window.matchMedia('(max-width: 640px)').matches;
    const effective = isMobile ? 'list' : view;
    document.body.classList.remove('view-grid', 'view-list');
    document.body.classList.add('view-' + effective);
    document.querySelectorAll('.view-toggle button').forEach(b => {
      b.classList.toggle('active', b.dataset.view === effective);
    });
  }
  function getSavedView() {
    try { return localStorage.getItem(STORAGE_KEY) || 'grid'; } catch { return 'grid'; }
  }
  function bindViewToggle(){
    document.querySelectorAll('.view-toggle button').forEach(btn => {
      if (btn.dataset.bound === '1') return;
      btn.dataset.bound = '1';
      btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        try { localStorage.setItem(STORAGE_KEY, view); } catch {}
        applyView(view);
      });
    });
  }
  bindViewToggle();
  applyView(getSavedView());
  let rt;
  window.addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(() => applyView(getSavedView()), 100); });

  // ============================================================
  // RESUME HELPERS
  // ============================================================
  const RESUME_PREFIX = 'sf_resume:';

  function resumeKeyFor(src) {
    try {
      const u = new URL(src, location.origin);
      return RESUME_PREFIX + u.pathname;
    } catch {
      return RESUME_PREFIX + src;
    }
  }
  function saveResumeTime(src, time, duration) {
    if (!src) return;
    if (!isFinite(time) || time < 2) return;
    if (isFinite(duration) && duration > 0 && time > duration - 5) {
      clearResumeTime(src);
      return;
    }
    try {
      localStorage.setItem(resumeKeyFor(src), JSON.stringify({
        t: time,
        d: isFinite(duration) ? duration : 0,
        at: Date.now(),
      }));
    } catch (e) {}
  }
  function loadResumeTime(src) {
    if (!src) return 0;
    try {
      const raw = localStorage.getItem(resumeKeyFor(src));
      if (!raw) return 0;
      const obj = JSON.parse(raw);
      if (obj.at && Date.now() - obj.at > 30 * 24 * 3600 * 1000) {
        clearResumeTime(src);
        return 0;
      }
      return obj.t || 0;
    } catch { return 0; }
  }
  function clearResumeTime(src) {
    if (!src) return;
    try { localStorage.removeItem(resumeKeyFor(src)); } catch (e) {}
  }

  // ============================================================
  // PICTURE PRESETS
  // ============================================================
  const PICTURE_STORAGE_KEY = 'sf_picture_settings';
  const DEFAULT_PICTURE = {
    contrast: 1.10,
    saturate: 1.15,
    brightness: 1.00,
    sepia: 0.00,
  };

  const PICTURE_PRESET_LIST = [
    { key: 'off',       name: 'Off',         desc: 'Original image',           values: { contrast: 1.00, saturate: 1.00, brightness: 1.00, sepia: 0.00 } },
    { key: 'balanced',  name: 'Balanced',    desc: 'Best for most content',    values: { contrast: 1.10, saturate: 1.15, brightness: 1.00, sepia: 0.00 } },
    { key: 'punchy',    name: 'Punchy',      desc: 'Sports, docs, nature',     values: { contrast: 1.20, saturate: 1.25, brightness: 1.00, sepia: 0.00 } },
    { key: 'vivid',     name: 'Vivid',       desc: 'Maximum pop',              values: { contrast: 1.30, saturate: 1.30, brightness: 1.02, sepia: 0.03 } },
    { key: 'night',     name: 'Night',       desc: 'Dim room, no eye strain',  values: { contrast: 1.15, saturate: 1.10, brightness: 0.95, sepia: 0.00 } },
    { key: 'cinema',    name: 'Cinema',      desc: 'Movies, film look',        values: { contrast: 1.08, saturate: 1.10, brightness: 1.00, sepia: 0.00 } },
    { key: 'animation', name: 'Animation',   desc: 'Cartoons, bright colors',  values: { contrast: 1.12, saturate: 1.25, brightness: 1.02, sepia: 0.00 } },
    { key: 'anime',     name: 'Anime',       desc: 'Vivid with warm tint',     values: { contrast: 1.15, saturate: 1.30, brightness: 1.02, sepia: 0.02 } },
    { key: 'sport',     name: 'Sport',       desc: 'Fast action, sharp',       values: { contrast: 1.10, saturate: 1.15, brightness: 1.00, sepia: 0.00 } },
    { key: 'bw',        name: 'B&W Classic', desc: 'Black and white films',    values: { contrast: 1.15, saturate: 0.00, brightness: 1.05, sepia: 0.00 } },
    { key: 'dark-room', name: 'Dark Room',   desc: 'Pitch-black environment',  values: { contrast: 1.15, saturate: 1.10, brightness: 0.90, sepia: 0.00 } },
    { key: 'hdr',       name: 'HDR→SDR',     desc: 'HDR content on SDR screen',values: { contrast: 1.15, saturate: 1.25, brightness: 0.98, sepia: 0.00 } },
    { key: 'washed',    name: 'Washed Fix',  desc: 'Fix dull / faded video',   values: { contrast: 1.20, saturate: 1.30, brightness: 1.02, sepia: 0.02 } },
  ];

  function loadPictureSettings() {
    try {
      const raw = localStorage.getItem(PICTURE_STORAGE_KEY);
      if (!raw) return { ...DEFAULT_PICTURE };
      return { ...DEFAULT_PICTURE, ...JSON.parse(raw) };
    } catch { return { ...DEFAULT_PICTURE }; }
  }
  function savePictureSettings(s) {
    try { localStorage.setItem(PICTURE_STORAGE_KEY, JSON.stringify(s)); } catch {}
  }
  function buildFilterString(s) {
    const parts = [];
    if (s.contrast !== 1)   parts.push(`contrast(${s.contrast})`);
    if (s.saturate !== 1)   parts.push(`saturate(${s.saturate})`);
    if (s.brightness !== 1) parts.push(`brightness(${s.brightness})`);
    if (s.sepia !== 0)      parts.push(`sepia(${s.sepia})`);
    return parts.length ? parts.join(' ') : 'none';
  }
  function applyPictureTo(el, s) {
    if (!el) return;
    el.style.filter = buildFilterString(s);
  }

  const globalPicture = loadPictureSettings();

  // ============================================================
  // MEDIA VIEWER
  // ============================================================
  const viewer    = document.getElementById('viewer');
  const vTitle    = document.getElementById('vTitle');
  const vMeta     = document.getElementById('vMeta');
  const vContent  = document.getElementById('vContent');
  const vDownload = document.getElementById('vDownload');
  const vClose    = document.getElementById('vClose');
  let currentPlayerCleanup = null;

  function openViewer(data) {
    vTitle.textContent = data.name;
    vMeta.textContent = data.size || '';
    vDownload.href = data.url;
    vContent.innerHTML = '';
    if (currentPlayerCleanup) { try { currentPlayerCleanup(); } catch(e){} currentPlayerCleanup = null; }

    const kind = data.kind;
    const src  = data.url;

    if (kind === 'image') {
      const img = document.createElement('img');
      img.src = src; img.alt = data.name;
      applyPictureTo(img, globalPicture);
      vContent.appendChild(img);
    } else if (kind === 'video') {
      const r = buildVideoPlayer(src, data.name, data.quality || '', data.qualityTag || '');
      currentPlayerCleanup = r.cleanup;
      vContent.appendChild(r.el);
    } else if (kind === 'audio') {
      const r = buildAudioPlayer(src, data.name);
      currentPlayerCleanup = r.cleanup;
      vContent.appendChild(r.el);
    } else if (kind === 'pdf') {
      const iframe = document.createElement('iframe');
      iframe.src = src;
      vContent.appendChild(iframe);
    } else if (kind === 'text') {
      const pre = document.createElement('pre');
      pre.textContent = 'Loading...';
      vContent.appendChild(pre);
      fetch(src).then(r => r.text()).then(t => { pre.textContent = t; })
               .catch(() => { pre.textContent = 'Could not load file.'; });
    }

    viewer.classList.add('open');
    document.body.style.overflow = 'hidden';
    updateFab();
  }

  function closeViewer() {
    viewer.classList.remove('open');
    viewer.classList.remove('video-fullscreen');
    document.body.style.overflow = '';
    vContent.querySelectorAll('video, audio').forEach(m => {
      try {
        m.pause();
        m.removeAttribute('src');
        m.load();
      } catch(e){}
    });
    if (currentPlayerCleanup) { try { currentPlayerCleanup(); } catch(e){} currentPlayerCleanup = null; }
    setTimeout(() => { vContent.innerHTML = ''; }, 200);
    updateFab();
  }

  vClose.addEventListener('click', closeViewer);
  viewer.addEventListener('click', (e) => {
    if (e.target === viewer || e.target.classList.contains('viewer-body')) closeViewer();
  });
  document.addEventListener('keydown', (e) => {
    if (!viewer.classList.contains('open')) return;
    if (e.key === 'Escape' && !isFS()) closeViewer();
  });

  // ============================================================
  // SPA NAV
  // ============================================================
  let navInProgress = false;

  async function navigateTo(url, pushState = true) {
    if (navInProgress) return;
    navInProgress = true;
    const target = withHiddenParam(url);
    try {
      const res = await fetch(target, {
        headers: { 'X-Requested-With': 'spa-nav' },
        cache: 'no-store'
      });
      if (!res.ok) { window.location.href = target; return; }
      const html = await res.text();
      const doc = new DOMParser().parseFromString(html, 'text/html');

      const newList = doc.getElementById('fileList');
      const oldList = document.getElementById('fileList');
      if (newList && oldList) oldList.replaceWith(newList);

      const newHeader = doc.querySelector('header');
      const oldHeader = document.querySelector('header');
      if (newHeader && oldHeader) oldHeader.replaceWith(newHeader);

      const newStat = doc.querySelector('.stat');
      const oldStat = document.querySelector('.stat');
      if (newStat && oldStat) oldStat.replaceWith(newStat);

      const newEmpty = doc.querySelector('.empty');
      const oldEmpty = document.querySelector('.empty');
      if (newEmpty && oldEmpty) oldEmpty.replaceWith(newEmpty);
      else if (newEmpty && !oldEmpty) {
        const listParent = document.getElementById('fileList')?.parentNode;
        if (listParent) listParent.appendChild(newEmpty);
      } else if (!newEmpty && oldEmpty) {
        oldEmpty.remove();
      }

      if (pushState) history.pushState({ url: target }, '', target);
      window.scrollTo({ top: 0, behavior: 'smooth' });

      const sInput = document.getElementById('search');
      if (sInput && sInput.value) {
        sInput.value = '';
        hideSearchPanel();
      }

      bindNavLinks();
      bindFileRows();
      rebindSearch();
      bindViewToggle();
    } catch (err) {
      window.location.href = target;
    } finally {
      navInProgress = false;
    }
  }

  function bindNavLinks() {
    document.querySelectorAll('a.nav-link').forEach(a => {
      if (a.dataset.navBound === '1') return;
      a.dataset.navBound = '1';
      a.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const href = a.getAttribute('href');
        if (!href) return;
        navigateTo(href);
      });
    });
  }

  function bindFileRows() {
    document.querySelectorAll('a.file-row').forEach(a => {
      if (a.dataset.bound === '1') return;
      a.dataset.bound = '1';
      if (!a.dataset.kind) return;
      a.addEventListener('click', (e) => {
        e.preventDefault();
        if (!isFS()) requestFS(document.documentElement);
        openViewer({
          url:  a.dataset.url,
          name: a.dataset.name,
          kind: a.dataset.kind,
          size: a.dataset.size,
          quality: a.dataset.quality,
          qualityTag: a.dataset.qualityTag,
        });
      });
    });
  }

  // ============================================================
  // RECURSIVE SEARCH
  // ============================================================
  const searchPanel    = document.getElementById('searchPanel');
  const searchResults  = document.getElementById('searchResults');
  const searchStatus   = document.getElementById('searchStatus');
  const searchStatusTx = searchStatus.querySelector('.search-status-text');
  const searchTrunc    = document.getElementById('searchTruncated');
  const filesListEl    = document.getElementById('fileList');

  let searchDebounceTimer = null;
  let searchAbortController = null;
  let searchIsActive = false;

  const SEARCH_DEBOUNCE_MS = 250;

  const ICON_FALLBACK_FOLDER =
    '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/>';
  const ICON_FALLBACK_FILE =
    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>';

  function setSearchLoading(loading) {
    searchStatus.classList.toggle('loading', loading);
  }

  function showSearchPanel() {
    searchPanel.classList.add('active');
    filesListEl.style.display = 'none';
    searchIsActive = true;
  }

  function hideSearchPanel() {
    searchPanel.classList.remove('active');
    filesListEl.style.display = '';
    searchResults.innerHTML = '';
    searchTrunc.style.display = 'none';
    searchIsActive = false;
  }

  function buildSearchResultItem(item) {
    const li = document.createElement('li');
    li.dataset.name = item.name.toLowerCase();
    li.dataset.fullpath = item.path.toLowerCase();

    const a = document.createElement('a');
    a.href = item.url;
    a.className = item.is_dir ? 'nav-link' : 'file-row';

    if (!item.is_dir) {
      a.dataset.url = item.url;
      a.dataset.name = item.name;
      a.dataset.kind = item.kind || '';
      a.dataset.size = item.size || '';
      a.dataset.quality = item.quality || '';
      a.dataset.qualityTag = item.quality_tag || '';
      if (!item.kind) a.setAttribute('download', '');
    }

    const svg = item.svg || (item.is_dir ? ICON_FALLBACK_FOLDER : ICON_FALLBACK_FILE);
    const color = item.color || 'var(--muted)';

    let iconEl;
    if (item.thumb) {
      iconEl = document.createElement('div');
      iconEl.className = 'thumb';
      const img = document.createElement('img');
      img.src = item.thumb;
      img.alt = '';
      img.loading = 'lazy';
      img.decoding = 'async';
      iconEl.appendChild(img);
    } else {
      iconEl = document.createElement('div');
      iconEl.className = 'icon';
      iconEl.style.color = color;
      iconEl.innerHTML = '<svg viewBox="0 0 24 24">' + svg + '</svg>';
    }

    const infoDiv = document.createElement('div');
    infoDiv.className = 'info';

    const nameDiv = document.createElement('div');
    nameDiv.className = 'name';
    nameDiv.textContent = item.name + (item.is_dir ? '/' : '');

    const metaDiv = document.createElement('div');
    metaDiv.className = 'meta';

    if (!item.is_dir && item.size) {
      const s = document.createElement('span');
      s.textContent = item.size;
      metaDiv.appendChild(s);
    }
    if (item.mtime) {
      const s = document.createElement('span');
      s.textContent = item.mtime;
      metaDiv.appendChild(s);
    }
    if (item.quality) {
      const s = document.createElement('span');
      s.className = 'quality-badge';
      s.textContent = item.quality;
      if (item.quality_tag) {
        const t = document.createElement('span');
        t.className = 'quality-tag';
        t.textContent = item.quality_tag;
        s.appendChild(t);
      }
      metaDiv.appendChild(s);
    }

    const pathDiv = document.createElement('div');
    pathDiv.className = 'search-path';
    const parentPath = item.path.includes('/')
      ? '/' + item.path.split('/').slice(0, -1).join('/')
      : '/';
    pathDiv.textContent = parentPath;
    pathDiv.title = '/' + item.path;
    metaDiv.appendChild(pathDiv);

    infoDiv.appendChild(nameDiv);
    infoDiv.appendChild(metaDiv);

    const arrowDiv = document.createElement('div');
    arrowDiv.className = 'arrow';
    if (item.is_dir) {
      arrowDiv.innerHTML = '<svg viewBox="0 0 24 24"><path d="M9 18l6-6-6-6"/></svg>';
    } else if (item.kind) {
      arrowDiv.innerHTML = '<svg viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
    } else {
      arrowDiv.innerHTML = '<svg class="dl" viewBox="0 0 24 24"><path d="M12 5v14"/><path d="M19 12l-7 7-7-7"/></svg>';
    }

    a.appendChild(iconEl);
    a.appendChild(infoDiv);
    a.appendChild(arrowDiv);
    li.appendChild(a);

    return li;
  }

  async function performSearch(query) {
    if (!query) {
      hideSearchPanel();
      return;
    }

    if (searchAbortController) {
      try { searchAbortController.abort(); } catch(e){}
    }
    searchAbortController = new AbortController();

    showSearchPanel();
    setSearchLoading(true);
    searchStatusTx.textContent = 'Searching for "' + query + '"…';
    searchTrunc.style.display = 'none';
    searchResults.innerHTML = '';

    try {
      const res = await fetch(
        '/api/search?q=' + encodeURIComponent(query),
        { signal: searchAbortController.signal, cache: 'no-store' }
      );

      if (!res.ok) {
        searchStatusTx.textContent = 'Search failed.';
        setSearchLoading(false);
        return;
      }

      const data = await res.json();
      const results = data.results || [];

      searchResults.innerHTML = '';

      if (results.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'search-empty';
        empty.textContent = 'No results for "' + query + '"';
        searchResults.appendChild(empty);
      } else {
        const frag = document.createDocumentFragment();
        results.forEach(item => frag.appendChild(buildSearchResultItem(item)));
        searchResults.appendChild(frag);
      }

      setSearchLoading(false);
      searchStatusTx.textContent =
        results.length + ' result' + (results.length === 1 ? '' : 's') + ' for "' + query + '"';

      if (data.truncated) {
        searchTrunc.textContent =
          'Showing first ' + results.length + ' results. Refine your search for more.';
        searchTrunc.style.display = '';
      }

      bindNavLinks();
      bindFileRows();
    } catch (err) {
      if (err.name === 'AbortError') return;
      setSearchLoading(false);
      searchStatusTx.textContent = 'Search error.';
    }
  }

  function rebindSearch() {
    const s = document.getElementById('search');
    if (!s) return;
    if (s.dataset.bound === '1') return;
    s.dataset.bound = '1';

    s.addEventListener('input', (e) => {
      const q = e.target.value.trim();
      clearTimeout(searchDebounceTimer);

      if (!q) {
        hideSearchPanel();
        return;
      }

      searchDebounceTimer = setTimeout(() => {
        performSearch(q);
      }, SEARCH_DEBOUNCE_MS);
    });

    s.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        s.value = '';
        hideSearchPanel();
        s.blur();
      }
    });
  }

  window.addEventListener('popstate', (e) => {
    if (handleFsGuardPop()) return;

    if (e.state && e.state.url) {
      navigateTo(e.state.url, false);
    } else {
      navigateTo(location.pathname + location.search, false);
    }
  });

  if (!history.state) {
    history.replaceState(
      { url: location.pathname + location.search },
      '',
      location.href
    );
  }

  bindNavLinks();
  bindFileRows();
  rebindSearch();

  // ============================================================
  // SILENT FILE LIST REFRESH
  // ============================================================
  let refreshInProgress = false;
  let lastRefreshAt = 0;
  const REFRESH_MIN_GAP = 800;

  async function refreshFileList(opts = {}) {
    if (refreshInProgress) return;
    if (navInProgress) return;
    if (viewer.classList.contains('open')) return;
    if (searchIsActive) return;

    const searchEl = document.getElementById('search');
    if (searchEl && document.activeElement === searchEl) return;

    const now = Date.now();
    if (now - lastRefreshAt < REFRESH_MIN_GAP) return;
    lastRefreshAt = now;
    refreshInProgress = true;

    try {
      const target = withHiddenParam(location.pathname + location.search);
      const res = await fetch(target, {
        headers: { 'X-Requested-With': 'spa-nav' },
        cache: 'no-store',
      });
      if (!res.ok) return;

      const html = await res.text();
      const doc = new DOMParser().parseFromString(html, 'text/html');

      const newList = doc.getElementById('fileList');
      const oldList = document.getElementById('fileList');
      if (newList && oldList) oldList.replaceWith(newList);

      const newHeader = doc.querySelector('header');
      const oldHeader = document.querySelector('header');
      if (newHeader && oldHeader) oldHeader.replaceWith(newHeader);

      const newStat = doc.querySelector('.stat');
      const oldStat = document.querySelector('.stat');
      if (newStat && oldStat) oldStat.replaceWith(newStat);

      const newEmpty = doc.querySelector('.empty');
      const oldEmpty = document.querySelector('.empty');
      if (newEmpty && oldEmpty) {
        oldEmpty.replaceWith(newEmpty);
      } else if (newEmpty && !oldEmpty) {
        const listParent = document.getElementById('fileList')?.parentNode;
        if (listParent) listParent.appendChild(newEmpty);
      } else if (!newEmpty && oldEmpty) {
        oldEmpty.remove();
      }

      bindNavLinks();
      bindFileRows();
      rebindSearch();
      bindViewToggle();
    } catch (err) {
      // silent
    } finally {
      refreshInProgress = false;
    }
  }

  // ============================================================
  // SSE — real-time updates
  // ============================================================
  let sseSource = null;
  let sseReconnectTimer = null;
  let sseReconnectDelay = 1000;
  const SSE_MAX_DELAY = 30000;

  let refreshDebounceTimer = null;
  const REFRESH_DEBOUNCE_MS = 300;

  function scheduleRefresh() {
    clearTimeout(refreshDebounceTimer);
    refreshDebounceTimer = setTimeout(() => {
      refreshFileList();
    }, REFRESH_DEBOUNCE_MS);
  }

  function connectSSE() {
    if (sseSource) {
      try { sseSource.close(); } catch(e){}
      sseSource = null;
    }
    clearTimeout(sseReconnectTimer);

    try {
      sseSource = new EventSource('/events');
    } catch (e) {
      scheduleReconnect();
      return;
    }

    sseSource.addEventListener('open', () => {
      sseReconnectDelay = 1000;
    });

    sseSource.addEventListener('changed', () => {
      scheduleRefresh();
    });

    sseSource.addEventListener('error', () => {
      try { sseSource.close(); } catch(e){}
      sseSource = null;
      scheduleReconnect();
    });
  }

  function scheduleReconnect() {
    clearTimeout(sseReconnectTimer);
    sseReconnectTimer = setTimeout(() => {
      sseReconnectDelay = Math.min(sseReconnectDelay * 1.5, SSE_MAX_DELAY);
      connectSSE();
    }, sseReconnectDelay);
  }

  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      if (!sseSource || sseSource.readyState === EventSource.CLOSED) {
        sseReconnectDelay = 1000;
        connectSSE();
      }
    }
  });

  document.addEventListener('keydown', (e) => {
    const tag = (e.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea') return;
    if (viewer.classList.contains('open')) return;

    if (e.key === 'r' || e.key === 'R') {
      e.preventDefault();
      refreshFileList();
    }
  });

  connectSSE();

  // ============================================================
  // VIDEO PLAYER
  // ============================================================
  function buildVideoPlayer(src, name, quality, qualityTag) {
    const wrap = document.createElement('div');
    wrap.className = 'video-wrap';

    const labelText = quality || '—';
    const tagText = qualityTag || '';

    wrap.innerHTML = `
      <video playsinline webkit-playsinline preload="auto" src="${src}"></video>
      <div class="v-loading"></div>
      <div class="v-error">
        <svg viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="10"/>
          <path d="M12 8v5M12 16h.01"/>
        </svg>
        <div class="v-error-title">Cannot play this file</div>
        <div class="v-error-msg">Your browser may not support this format or codec. Try downloading it or use another player.</div>
      </div>
      <button class="v-bigplay show" aria-label="Play">
        <svg viewBox="0 0 24 24"><path d="M9 5.5v13l11-6.5z"/></svg>
      </button>
      <div class="v-seek-indicator left">
        <svg viewBox="0 0 24 24"><path d="M11 19l-9-7 9-7v14zM22 19l-9-7 9-7v14z"/></svg>
        <span class="v-seek-text"></span>
      </div>
      <div class="v-seek-indicator right">
        <svg viewBox="0 0 24 24"><path d="M13 5l9 7-9 7V5zM2 5l9 7-9 7V5z"/></svg>
        <span class="v-seek-text"></span>
      </div>
      <div class="v-menu v-speed-menu">
        ${[0.5,0.75,1,1.25,1.5,2].map(s =>
          `<button data-speed="${s}" class="${s===1?'active':''}">${s}x</button>`).join('')}
      </div>
      <div class="v-menu v-picture-menu">
        <div class="v-picture-row">
          <label>Contrast <span data-val="contrast">110%</span></label>
          <input type="range" min="0.7" max="1.5" step="0.01" data-filter="contrast">
        </div>
        <div class="v-picture-row">
          <label>Saturation <span data-val="saturate">115%</span></label>
          <input type="range" min="0" max="2" step="0.01" data-filter="saturate">
        </div>
        <div class="v-picture-row">
          <label>Brightness <span data-val="brightness">100%</span></label>
          <input type="range" min="0.7" max="1.4" step="0.01" data-filter="brightness">
        </div>
        <div class="v-picture-row">
          <label>Warmth <span data-val="sepia">0%</span></label>
          <input type="range" min="0" max="0.3" step="0.01" data-filter="sepia">
        </div>
        <button class="v-picture-reset" type="button">Reset</button>
      </div>
      <div class="v-preset-overlay">
        <div class="v-preset-panel">
          <div class="v-preset-title">
            <span>Picture Presets</span>
            <button class="v-preset-close" title="Close" type="button">
              <svg viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="v-preset-grid"></div>
        </div>
      </div>
      <div class="v-ctrl">
        <div class="v-progress">
          <div class="v-progress-track">
            <div class="v-buffered"></div>
            <div class="v-played"></div>
          </div>
          <div class="v-thumb"></div>
          <div class="v-time-tooltip">0:00</div>
        </div>
        <div class="v-row">
          <button class="v-play" title="Play / Pause (Space)">
            <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
          </button>
          <button class="v-skip v-back v-hide-narrow" title="Back 10s">
            <svg viewBox="0 0 24 24"><path d="M11 19l-9-7 9-7v14zM22 19l-9-7 9-7v14z"/></svg>
          </button>
          <button class="v-skip v-fwd v-hide-narrow" title="Forward 10s">
            <svg viewBox="0 0 24 24"><path d="M13 5l9 7-9 7V5zM2 5l9 7-9 7V5z"/></svg>
          </button>
          <span class="v-time" data-role="time">0:00 / 0:00</span>
          <div class="v-spacer"></div>
          <div class="v-volume">
            <button class="v-mute" title="Mute (M)">
              <svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
            </button>
            <div class="v-volume-slider">
              <input type="range" min="0" max="1" step="0.01" value="1">
            </div>
          </div>
          <button class="v-quality v-hide-mobile" tabindex="-1" aria-disabled="true">
            <svg viewBox="0 0 24 24">
              <path d="M4 6h16M4 12h16M4 18h16"/>
              <circle cx="8" cy="6" r="2"/>
              <circle cx="16" cy="12" r="2"/>
              <circle cx="10" cy="18" r="2"/>
            </svg>
            <span class="v-quality-label">${labelText}</span>
            ${tagText ? `<span class="v-quality-tag">${tagText}</span>` : ''}
          </button>
          <button class="v-picture v-hide-mobile" title="Picture settings (C to cycle)">
            <svg viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="9"/>
              <path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor" stroke="none"/>
            </svg>
          </button>
          <button class="v-preset-btn v-hide-mobile" title="Presets (P)">
            <svg viewBox="0 0 24 24">
              <path d="M4 6h16M4 12h16M4 18h16"/>
              <circle cx="9" cy="6" r="2" fill="currentColor"/>
              <circle cx="15" cy="12" r="2" fill="currentColor"/>
              <circle cx="7" cy="18" r="2" fill="currentColor"/>
            </svg>
            <span class="v-preset-btn-label">Presets</span>
          </button>
          <button class="v-speed" title="Playback speed">
            <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
          </button>
          <button class="v-pip v-hide-mobile" title="Picture in Picture">
            <svg viewBox="0 0 24 24"><rect x="2" y="4" width="20" height="16" rx="2"/><rect x="12" y="12" width="8" height="6" rx="1"/></svg>
          </button>
          <button class="v-full v-hide-mobile" title="Fullscreen (F)">
            <svg viewBox="0 0 24 24"><path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M16 3h3a2 2 0 0 1 2 2v3"/><path d="M8 21H5a2 2 0 0 1-2-2v-3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/></svg>
          </button>
        </div>
      </div>
    `;

    const video       = wrap.querySelector('video');
    const loading     = wrap.querySelector('.v-loading');
    const errorBox    = wrap.querySelector('.v-error');
    const bigPlay     = wrap.querySelector('.v-bigplay');
    const played      = wrap.querySelector('.v-played');
    const buffered    = wrap.querySelector('.v-buffered');
    const prog        = wrap.querySelector('.v-progress');
    const thumb       = wrap.querySelector('.v-thumb');
    const tooltip     = wrap.querySelector('.v-time-tooltip');
    const timeEl      = wrap.querySelector('[data-role=time]');
    const btnPlay     = wrap.querySelector('.v-play');
    const btnBack     = wrap.querySelector('.v-back');
    const btnFwd      = wrap.querySelector('.v-fwd');
    const btnMute     = wrap.querySelector('.v-mute');
    const volIn       = wrap.querySelector('.v-volume-slider input');
    const btnSpeed    = wrap.querySelector('.v-speed');
    const speedMenu   = wrap.querySelector('.v-speed-menu');
    const btnPicture  = wrap.querySelector('.v-picture');
    const pictureMenu = wrap.querySelector('.v-picture-menu');
    const btnPreset   = wrap.querySelector('.v-preset-btn');
    const presetOverlay = wrap.querySelector('.v-preset-overlay');
    const presetGrid    = wrap.querySelector('.v-preset-grid');
    const presetClose   = wrap.querySelector('.v-preset-close');
    const btnPip      = wrap.querySelector('.v-pip');
    const btnFull     = wrap.querySelector('.v-full');
    const indLeft     = wrap.querySelector('.v-seek-indicator.left');
    const indRight    = wrap.querySelector('.v-seek-indicator.right');
    const seekLeft    = indLeft.querySelector('.v-seek-text');
    const seekRight   = indRight.querySelector('.v-seek-text');

    const ICON_PLAY  = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
    const ICON_PAUSE = '<svg viewBox="0 0 24 24"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>';

    function fmt(t){
      if (!isFinite(t) || t < 0) return '0:00';
      const h = Math.floor(t/3600), m = Math.floor((t%3600)/60), s = Math.floor(t%60);
      return (h ? h+':'+String(m).padStart(2,'0') : m) + ':' + String(s).padStart(2,'0');
    }
    function safeDuration(){
      return isFinite(video.duration) && video.duration > 0 ? video.duration : 0;
    }
    function updateTime(){
      timeEl.textContent = fmt(video.currentTime) + ' / ' + fmt(safeDuration());
    }
    function updateProgress(){
      const d = safeDuration();
      const p = d ? (video.currentTime / d) * 100 : 0;
      played.style.width = p + '%';
      thumb.style.left = p + '%';
      try {
        if (video.buffered.length && d) {
          const b = video.buffered.end(video.buffered.length - 1);
          buffered.style.width = Math.min(100, (b / d) * 100) + '%';
        }
      } catch(e) {}
    }
    function playPause(){
      if (video.paused) {
        const p = video.play();
        if (p && p.catch) {
          p.catch(err => {
            console.warn('Playback failed:', err);
            loading.classList.remove('show');
            bigPlay.classList.add('show');
            errorBox.classList.add('show');
          });
        }
      } else {
        video.pause();
      }
    }

    const pictureSettings = loadPictureSettings();
    applyPictureTo(video, pictureSettings);

    const pictureInputs = pictureMenu.querySelectorAll('input[data-filter]');
    function refreshPictureUI(){
      pictureInputs.forEach(inp => {
        const key = inp.dataset.filter;
        const v = pictureSettings[key];
        inp.value = v;
        const valEl = pictureMenu.querySelector(`[data-val="${key}"]`);
        if (valEl) valEl.textContent = Math.round(v * 100) + '%';
      });
    }
    pictureInputs.forEach(inp => {
      const key = inp.dataset.filter;
      inp.value = pictureSettings[key];
      const valEl = pictureMenu.querySelector(`[data-val="${key}"]`);
      if (valEl) valEl.textContent = Math.round(pictureSettings[key] * 100) + '%';
      inp.addEventListener('input', () => {
        const v = parseFloat(inp.value);
        pictureSettings[key] = v;
        applyPictureTo(video, pictureSettings);
        savePictureSettings(pictureSettings);
        if (valEl) valEl.textContent = Math.round(v * 100) + '%';
        refreshPresetActive();
      });
    });
    const resetBtn = pictureMenu.querySelector('.v-picture-reset');
    if (resetBtn) {
      resetBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        Object.assign(pictureSettings, DEFAULT_PICTURE);
        applyPictureTo(video, pictureSettings);
        savePictureSettings(pictureSettings);
        refreshPictureUI();
        refreshPresetActive();
      });
    }
    function onPictureClick(e){
      e.stopPropagation();
      speedMenu.classList.remove('show');
      pictureMenu.classList.toggle('show');
    }
    if (btnPicture) btnPicture.addEventListener('click', onPictureClick);

    function buildPresetGrid(){
      presetGrid.innerHTML = '';
      PICTURE_PRESET_LIST.forEach(p => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'v-preset-item';
        btn.dataset.preset = p.key;
        btn.innerHTML = `
          <span class="v-preset-name">${p.name}</span>
          <span class="v-preset-desc">${p.desc}</span>
          <span class="v-preset-swatch"></span>
        `;
        btn.addEventListener('click', () => {
          Object.assign(pictureSettings, p.values);
          applyPictureTo(video, pictureSettings);
          savePictureSettings(pictureSettings);
          refreshPictureUI();
          refreshPresetActive();
          showPlayerToast('Preset: ' + p.name, false);
          setTimeout(closePresetOverlay, 250);
        });
        presetGrid.appendChild(btn);
      });
      refreshPresetActive();
    }

    function refreshPresetActive(){
      const match = PICTURE_PRESET_LIST.find(p =>
        p.values.contrast.toFixed(2) === pictureSettings.contrast.toFixed(2) &&
        p.values.saturate.toFixed(2) === pictureSettings.saturate.toFixed(2) &&
        p.values.brightness.toFixed(2) === pictureSettings.brightness.toFixed(2) &&
        p.values.sepia.toFixed(2) === (pictureSettings.sepia || 0).toFixed(2)
      );
      presetGrid.querySelectorAll('.v-preset-item').forEach(el => {
        el.classList.toggle('active', !!match && el.dataset.preset === match.key);
      });
    }

    function openPresetOverlay(){
      speedMenu.classList.remove('show');
      pictureMenu.classList.remove('show');
      presetOverlay.classList.add('show');
      refreshPresetActive();
    }
    function closePresetOverlay(){
      presetOverlay.classList.remove('show');
    }

    if (btnPreset) {
      btnPreset.addEventListener('click', (e) => {
        e.stopPropagation();
        openPresetOverlay();
      });
    }
    if (presetClose) {
      presetClose.addEventListener('click', (e) => {
        e.stopPropagation();
        closePresetOverlay();
      });
    }
    presetOverlay.addEventListener('click', (e) => {
      if (e.target === presetOverlay) closePresetOverlay();
    });

    function onPresetEsc(e){
      if (e.key === 'Escape' && presetOverlay.classList.contains('show')) {
        e.stopPropagation();
        closePresetOverlay();
      }
    }
    document.addEventListener('keydown', onPresetEsc);

    buildPresetGrid();

    function showPlayerToast(html, withRestart) {
      const toast = document.createElement('div');
      toast.className = 'v-resume-toast';
      toast.innerHTML = `
        <svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;">
          <path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>
        </svg>
        <span>${html}</span>
      `;
      if (withRestart) {
        const btn = document.createElement('button');
        btn.className = 'v-resume-restart';
        btn.type = 'button';
        btn.textContent = 'Start over';
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          clearTimeout(hideTimer);
          video.currentTime = 0;
          clearResumeTime(src);
          remove();
        });
        toast.appendChild(btn);
      }
      wrap.appendChild(toast);
      requestAnimationFrame(() => toast.classList.add('show'));
      const remove = () => {
        toast.classList.remove('show');
        setTimeout(() => { try { toast.remove(); } catch(e){} }, 300);
      };
      const hideTimer = setTimeout(remove, 4000);
      const onInteract = () => { clearTimeout(hideTimer); remove(); };
      wrap.addEventListener('pointerdown', onInteract, { once: true });
    }

    function onPlay(){ btnPlay.innerHTML = ICON_PAUSE; bigPlay.classList.remove('show'); }
    function onPause(){
      btnPlay.innerHTML = ICON_PLAY;
      bigPlay.classList.add('show');
      saveResumeTime(src, video.currentTime, video.duration);
    }
    function onEnded(){
      btnPlay.innerHTML = ICON_PLAY;
      bigPlay.classList.add('show');
      clearResumeTime(src);
    }
    function onTimeUpdate(){ updateTime(); updateProgress(); saveResume(); }
    function onProgressBar(){ updateProgress(); }
    function onLoadedMeta(){
      updateTime();
      const saved = loadResumeTime(src);
      const dur = safeDuration();
      if (saved > 2 && (!dur || saved < dur - 5)) {
        video.currentTime = saved;
        showPlayerToast('Resumed at ' + fmt(saved), true);
      }
    }
    function onWaiting(){ loading.classList.add('show'); }
    function onPlaying(){ loading.classList.remove('show'); errorBox.classList.remove('show'); }
    function onCanPlay(){ loading.classList.remove('show'); }
    function onVideoError(){
      loading.classList.remove('show');
      bigPlay.classList.remove('show');
      errorBox.classList.add('show');
    }
    function onVideoClick(e){ if (e.target === video) playPause(); }

    let resumeSaveTimer = null;
    function saveResume(){
      clearTimeout(resumeSaveTimer);
      resumeSaveTimer = setTimeout(() => {
        if (!video.paused) saveResumeTime(src, video.currentTime, video.duration);
      }, 1000);
    }

    video.addEventListener('play', onPlay);
    video.addEventListener('pause', onPause);
    video.addEventListener('ended', onEnded);
    video.addEventListener('timeupdate', onTimeUpdate);
    video.addEventListener('progress', onProgressBar);
    video.addEventListener('loadedmetadata', onLoadedMeta);
    video.addEventListener('waiting', onWaiting);
    video.addEventListener('playing', onPlaying);
    video.addEventListener('canplay', onCanPlay);
    video.addEventListener('error', onVideoError);
    video.addEventListener('click', onVideoClick);

    bigPlay.addEventListener('click', playPause);
    btnPlay.addEventListener('click', playPause);

    function onBack(){ video.currentTime = Math.max(0, video.currentTime - 10); }
    function onFwd(){
      const d = safeDuration();
      video.currentTime = d ? Math.min(d, video.currentTime + 10) : video.currentTime + 10;
    }
    if (btnBack) btnBack.addEventListener('click', onBack);
    if (btnFwd)  btnFwd .addEventListener('click', onFwd);

    let seeking = false;

    function timeFromEvent(e){
      const rect = prog.getBoundingClientRect();
      const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
      const ratio = Math.max(0, Math.min(1, x / rect.width));
      return { ratio, time: ratio * safeDuration() };
    }
    function seekFromEvent(e){
      const d = safeDuration();
      if (!d) return;
      video.currentTime = timeFromEvent(e).time;
    }
    function onProgDown(e){ seeking = true; seekFromEvent(e); }
    function onWinMove(e){ if (seeking) seekFromEvent(e); }
    function onWinUp(){ seeking = false; }
    function onProgTouch(e){ seekFromEvent(e); }

    function onProgMove(e){
      if (seeking || !safeDuration()) return;
      const { ratio, time } = timeFromEvent(e);
      tooltip.textContent = fmt(time);
      tooltip.style.left = (ratio * 100) + '%';
      tooltip.classList.add('show');
    }
    function onProgLeave(){ tooltip.classList.remove('show'); }

    function onProgTouchMove(e){
      if (!safeDuration()) return;
      const { ratio, time } = timeFromEvent(e);
      tooltip.textContent = fmt(time);
      tooltip.style.left = (ratio * 100) + '%';
      tooltip.classList.add('show');
    }
    function onProgTouchEnd(){ tooltip.classList.remove('show'); }

    prog.addEventListener('mousedown', onProgDown);
    window.addEventListener('mousemove', onWinMove);
    window.addEventListener('mouseup', onWinUp);
    prog.addEventListener('mousemove', onProgMove);
    prog.addEventListener('mouseleave', onProgLeave);
    prog.addEventListener('touchstart', onProgTouch, { passive: true });
    prog.addEventListener('touchmove', (e) => {
      onProgTouch(e);
      onProgTouchMove(e);
    }, { passive: true });
    prog.addEventListener('touchend', onProgTouchEnd);

    function updateMuteIcon(){
      btnMute.innerHTML = (video.muted || video.volume === 0)
        ? '<svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M22 9l-6 6M16 9l6 6"/></svg>'
        : '<svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>';
    }
    function onMuteClick(){
      video.muted = !video.muted;
      volIn.value = video.muted ? 0 : video.volume;
      updateMuteIcon();
    }
    function onVolInput(){
      video.volume = parseFloat(volIn.value);
      video.muted = video.volume === 0;
      updateMuteIcon();
    }
    btnMute.addEventListener('click', onMuteClick);
    volIn.addEventListener('input', onVolInput);

    function onSpeedClick(e){ e.stopPropagation(); pictureMenu.classList.remove('show'); speedMenu.classList.toggle('show'); }
    btnSpeed.addEventListener('click', onSpeedClick);
    const speedButtons = Array.from(speedMenu.querySelectorAll('button'));
    function onSpeedBtnClick(e){
      const b = e.currentTarget;
      video.playbackRate = parseFloat(b.dataset.speed);
      speedButtons.forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      speedMenu.classList.remove('show');
    }
    speedButtons.forEach(b => b.addEventListener('click', onSpeedBtnClick));

    let idleTimer = null;
    function wake(){
      wrap.classList.remove('idle');
      wrap.classList.remove('hide-cursor');
      clearTimeout(idleTimer);
      if (!video.paused && !presetOverlay.classList.contains('show')) {
        idleTimer = setTimeout(() => {
          wrap.classList.add('idle');
          wrap.classList.add('hide-cursor');
          speedMenu.classList.remove('show');
          pictureMenu.classList.remove('show');
        }, 3000);
      }
    }
    function onVideoPauseClear(){
      clearTimeout(idleTimer);
      wrap.classList.remove('idle');
      wrap.classList.remove('hide-cursor');
    }
    wrap.addEventListener('mousemove', wake);
    wrap.addEventListener('mousedown', wake);
    wrap.addEventListener('touchstart', wake, { passive: true });
    wrap.addEventListener('touchmove', wake, { passive: true });
    video.addEventListener('play', wake);
    video.addEventListener('pause', onVideoPauseClear);
    speedMenu.addEventListener('mousemove', wake);
    pictureMenu.addEventListener('mousemove', wake);

    function onDocClick(){ speedMenu.classList.remove('show'); pictureMenu.classList.remove('show'); }
    document.addEventListener('click', onDocClick);
    function onWrapClick(e){ e.stopPropagation(); }
    wrap.addEventListener('click', onWrapClick);

    async function onPipClick(){
      try {
        if (document.pictureInPictureElement) await document.exitPictureInPicture();
        else if (video.requestPictureInPicture) await video.requestPictureInPicture();
      } catch(e){}
    }
    if (btnPip) btnPip.addEventListener('click', onPipClick);

    function onFullClick(){
      if (isFS()) exitFS();
      else requestFS(wrap);
    }
    if (btnFull) btnFull.addEventListener('click', onFullClick);

    function cyclePicturePreset(){
      const CORE = PICTURE_PRESET_LIST.slice(0, 5);
      const currentContrast = pictureSettings.contrast.toFixed(2);
      let idx = CORE.findIndex(p => p.values.contrast.toFixed(2) === currentContrast);
      idx = (idx + 1) % CORE.length;
      Object.assign(pictureSettings, CORE[idx].values);
      applyPictureTo(video, pictureSettings);
      savePictureSettings(pictureSettings);
      refreshPictureUI();
      refreshPresetActive();
      showPlayerToast('Picture: ' + CORE[idx].name, false);
    }

    function onWrapKeydown(e){
      const tag = (e.target.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea') return;

      if (presetOverlay.classList.contains('show') && e.key !== 'Escape') {
        return;
      }

      wake();
      if (e.key === ' ' || e.key === 'k' || e.key === 'K') {
        e.preventDefault();
        playPause();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        const d = safeDuration();
        video.currentTime = d ? Math.min(d, video.currentTime + 5) : video.currentTime + 5;
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        video.currentTime = Math.max(0, video.currentTime - 5);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        video.volume = Math.min(1, video.volume + 0.05);
        volIn.value = video.volume;
        video.muted = false;
        updateMuteIcon();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        video.volume = Math.max(0, video.volume - 0.05);
        volIn.value = video.volume;
        updateMuteIcon();
      } else if (e.key === 'm' || e.key === 'M') {
        video.muted = !video.muted;
        updateMuteIcon();
      } else if (e.key === 'f' || e.key === 'F') {
        if (isFS()) exitFS(); else requestFS(wrap);
      } else if (e.key === 'c' || e.key === 'C') {
        cyclePicturePreset();
      } else if (e.key === 'p' || e.key === 'P') {
        e.preventDefault();
        if (presetOverlay.classList.contains('show')) closePresetOverlay();
        else openPresetOverlay();
      }
    }
    wrap.tabIndex = 0;
    wrap.addEventListener('keydown', onWrapKeydown);

    let lastTapTime = 0;
    let tapTimer = null;
    let tapSide = null;
    let tapCount = 0;

    function triggerSeekIndicator(side){
      const el = side === 'left' ? indLeft : indRight;
      const txt = side === 'left' ? seekLeft : seekRight;
      el.classList.add('show');
      clearTimeout(el._hideTimer);
      el._hideTimer = setTimeout(() => el.classList.remove('show'), 700);
      return txt;
    }

    function onVideoTouchStart(e){
      const now = Date.now();
      const touch = e.touches[0];
      const rect = video.getBoundingClientRect();
      const x = touch.clientX - rect.left;
      const side = x < rect.width / 2 ? 'left' : 'right';

      if (now - lastTapTime < 300 && side === tapSide) {
        tapCount++;
        const step = 10;
        if (side === 'left') {
          video.currentTime = Math.max(0, video.currentTime - step);
        } else {
          const d = safeDuration();
          video.currentTime = d ? Math.min(d, video.currentTime + step) : video.currentTime + step;
        }
        const txt = triggerSeekIndicator(side);
        txt.textContent = (side === 'left' ? '−' : '+') + (step * tapCount) + 's';
        clearTimeout(tapTimer);
        tapTimer = setTimeout(() => { tapCount = 0; }, 800);
      } else {
        clearTimeout(tapTimer);
        tapCount = 0;
        tapTimer = setTimeout(() => {
          if (tapCount === 0) playPause();
        }, 280);
      }
      lastTapTime = now;
      tapSide = side;
    }
    video.addEventListener('touchstart', onVideoTouchStart, { passive: true });

    try {
      if ('mediaSession' in navigator && window.MediaMetadata) {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: name || 'Video',
          artist: 'Shared Files',
        });
        navigator.mediaSession.setActionHandler('play', () => video.play());
        navigator.mediaSession.setActionHandler('pause', () => video.pause());
        navigator.mediaSession.setActionHandler('seekbackward', () => {
          video.currentTime = Math.max(0, video.currentTime - 10);
        });
        navigator.mediaSession.setActionHandler('seekforward', () => {
          const d = safeDuration();
          video.currentTime = d ? Math.min(d, video.currentTime + 10) : video.currentTime + 10;
        });
      }
    } catch(e){}

    function onVisibilityChange(){
      if (document.hidden) {
        saveResumeTime(src, video.currentTime, video.duration);
        if (!video.paused) video.pause();
      }
    }
    document.addEventListener('visibilitychange', onVisibilityChange);

    function onBeforeUnload(){
      saveResumeTime(src, video.currentTime, video.duration);
    }
    window.addEventListener('beforeunload', onBeforeUnload);
    window.addEventListener('pagehide', onBeforeUnload);

    updateMuteIcon();
    refreshPictureUI();
    setTimeout(() => wrap.focus(), 100);
    wake();

    function cleanup(){
      if (video && video.currentTime > 0) {
        saveResumeTime(src, video.currentTime, video.duration);
      }
      clearTimeout(idleTimer);
      clearTimeout(resumeSaveTimer);
      clearTimeout(tapTimer);
      clearTimeout(indLeft._hideTimer);
      clearTimeout(indRight._hideTimer);
      window.removeEventListener('mousemove', onWinMove);
      window.removeEventListener('mouseup', onWinUp);
      window.removeEventListener('beforeunload', onBeforeUnload);
      window.removeEventListener('pagehide', onBeforeUnload);
      document.removeEventListener('click', onDocClick);
      document.removeEventListener('visibilitychange', onVisibilityChange);
      document.removeEventListener('keydown', onPresetEsc);
      try {
        if ('mediaSession' in navigator) {
          navigator.mediaSession.setActionHandler('play', null);
          navigator.mediaSession.setActionHandler('pause', null);
          navigator.mediaSession.setActionHandler('seekbackward', null);
          navigator.mediaSession.setActionHandler('seekforward', null);
          navigator.mediaSession.metadata = null;
        }
      } catch(e){}
    }

    return { el: wrap, cleanup };
  }

  // ============================================================
  // AUDIO PLAYER
  // ============================================================
  function buildAudioPlayer(src, name) {
    const card = document.createElement('div');
    card.className = 'audio-card';

    card.innerHTML = `
      <div class="audio-head">
        <div class="a-icon">
          <svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
        </div>
        <div class="a-name"></div>
      </div>
      <div class="video-wrap" style="height:auto; background:transparent; border-radius:0; position:relative;">
        <audio src="${src}" preload="auto"></audio>
        <div class="v-menu v-speed-menu">
          ${[0.5,0.75,1,1.25,1.5,2].map(s =>
            `<button data-speed="${s}" class="${s===1?'active':''}">${s}x</button>`).join('')}
        </div>
        <div class="v-ctrl" style="position:static;">
          <div class="v-progress">
            <div class="v-progress-track">
              <div class="v-buffered"></div>
              <div class="v-played"></div>
            </div>
            <div class="v-thumb"></div>
            <div class="v-time-tooltip">0:00</div>
          </div>
          <div class="v-row">
            <button class="v-play" title="Play / Pause (Space)">
              <svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>
            </button>
            <span class="v-time" data-role="time">0:00 / 0:00</span>
            <div class="v-spacer"></div>
            <div class="v-volume">
              <button class="v-mute" title="Mute (M)">
                <svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>
              </button>
              <div class="v-volume-slider">
                <input type="range" min="0" max="1" step="0.01" value="1">
              </div>
            </div>
            <button class="v-speed" title="Playback speed">
              <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
            </button>
          </div>
        </div>
      </div>
    `;
    card.querySelector('.a-name').textContent = name;

    const audio     = card.querySelector('audio');
    const btnPlay   = card.querySelector('.v-play');
    const played    = card.querySelector('.v-played');
    const buffered  = card.querySelector('.v-buffered');
    const prog      = card.querySelector('.v-progress');
    const thumb     = card.querySelector('.v-thumb');
    const tooltip   = card.querySelector('.v-time-tooltip');
    const timeEl    = card.querySelector('[data-role=time]');
    const btnMute   = card.querySelector('.v-mute');
    const volIn     = card.querySelector('.v-volume-slider input');
    const btnSpeed  = card.querySelector('.v-speed');
    const menu      = card.querySelector('.v-speed-menu');

    const ICON_PLAY  = '<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';
    const ICON_PAUSE = '<svg viewBox="0 0 24 24"><rect x="6" y="5" width="4" height="14" rx="1"/><rect x="14" y="5" width="4" height="14" rx="1"/></svg>';

    function fmt(t){
      if (!isFinite(t) || t < 0) return '0:00';
      const m = Math.floor(t/60), s = Math.floor(t%60);
      return m + ':' + String(s).padStart(2,'0');
    }
    function safeDuration(){
      return isFinite(audio.duration) && audio.duration > 0 ? audio.duration : 0;
    }
    function update(){
      timeEl.textContent = fmt(audio.currentTime) + ' / ' + fmt(safeDuration());
      const d = safeDuration();
      const p = d ? (audio.currentTime/d)*100 : 0;
      played.style.width = p + '%';
      thumb.style.left = p + '%';
      try {
        if (audio.buffered.length && d) {
          const b = audio.buffered.end(audio.buffered.length - 1);
          buffered.style.width = Math.min(100, (b/d)*100) + '%';
        }
      } catch(e){}
    }
    function playPause(){
      if (audio.paused) {
        const p = audio.play();
        if (p && p.catch) p.catch(err => console.warn('Audio playback failed:', err));
      } else {
        audio.pause();
      }
    }
    function onPlay(){ btnPlay.innerHTML = ICON_PAUSE; }
    function onPause(){
      btnPlay.innerHTML = ICON_PLAY;
      saveResumeTime(src, audio.currentTime, audio.duration);
    }
    function onEnded(){
      btnPlay.innerHTML = ICON_PLAY;
      clearResumeTime(src);
    }
    function onLoadedMeta(){
      update();
      const saved = loadResumeTime(src);
      const dur = safeDuration();
      if (saved > 2 && (!dur || saved < dur - 5)) {
        audio.currentTime = saved;
        showAudioToast('Resumed at ' + fmt(saved));
      }
    }
    function showAudioToast(html){
      const toast = document.createElement('div');
      toast.className = 'v-resume-toast';
      toast.innerHTML = `
        <svg viewBox="0 0 24 24" style="width:16px;height:16px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;">
          <path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/>
        </svg>
        <span>${html}</span>
      `;
      const btn = document.createElement('button');
      btn.className = 'v-resume-restart';
      btn.type = 'button';
      btn.textContent = 'Start over';
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearTimeout(hideTimer);
        audio.currentTime = 0;
        clearResumeTime(src);
        remove();
      });
      toast.appendChild(btn);
      card.appendChild(toast);
      requestAnimationFrame(() => toast.classList.add('show'));
      const remove = () => {
        toast.classList.remove('show');
        setTimeout(() => { try { toast.remove(); } catch(e){} }, 300);
      };
      const hideTimer = setTimeout(remove, 4000);
    }

    audio.addEventListener('timeupdate', update);
    audio.addEventListener('loadedmetadata', onLoadedMeta);
    audio.addEventListener('play', onPlay);
    audio.addEventListener('pause', onPause);
    audio.addEventListener('ended', onEnded);
    btnPlay.addEventListener('click', playPause);

    let resumeSaveTimer = null;
    function saveResume(){
      clearTimeout(resumeSaveTimer);
      resumeSaveTimer = setTimeout(() => {
        if (!audio.paused) saveResumeTime(src, audio.currentTime, audio.duration);
      }, 1000);
    }
    audio.addEventListener('timeupdate', saveResume);

    let s = false;
    function timeFromEvent(e){
      const rect = prog.getBoundingClientRect();
      const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
      const ratio = Math.max(0, Math.min(1, x/rect.width));
      return { ratio, time: ratio * safeDuration() };
    }
    function seekFromEvent(e){
      const d = safeDuration();
      if (!d) return;
      audio.currentTime = timeFromEvent(e).time;
    }
    function onDown(e){ s = true; seekFromEvent(e); }
    function onMove(e){ if (s) seekFromEvent(e); }
    function onUp(){ s = false; }
    function onTouch(e){ seekFromEvent(e); }
    function onProgMove(e){
      if (s || !safeDuration()) return;
      const { ratio, time } = timeFromEvent(e);
      tooltip.textContent = fmt(time);
      tooltip.style.left = (ratio * 100) + '%';
      tooltip.classList.add('show');
    }
    function onProgLeave(){ tooltip.classList.remove('show'); }

    prog.addEventListener('mousedown', onDown);
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    prog.addEventListener('mousemove', onProgMove);
    prog.addEventListener('mouseleave', onProgLeave);
    prog.addEventListener('touchstart', onTouch, { passive: true });
    prog.addEventListener('touchmove', onTouch, { passive: true });

    function updateMuteIcon(){
      btnMute.innerHTML = (audio.muted || audio.volume === 0)
        ? '<svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M22 9l-6 6M16 9l6 6"/></svg>'
        : '<svg viewBox="0 0 24 24"><path d="M11 5L6 9H2v6h4l5 4V5z"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/></svg>';
    }
    function onMuteClick(){ audio.muted = !audio.muted; updateMuteIcon(); }
    function onVolInput(){
      audio.volume = parseFloat(volIn.value);
      audio.muted = audio.volume === 0;
      updateMuteIcon();
    }
    btnMute.addEventListener('click', onMuteClick);
    volIn.addEventListener('input', onVolInput);

    function onSpeedClick(e){ e.stopPropagation(); menu.classList.toggle('show'); }
    btnSpeed.addEventListener('click', onSpeedClick);
    const speedButtons = Array.from(menu.querySelectorAll('button'));
    function onSpeedBtnClick(e){
      const b = e.currentTarget;
      audio.playbackRate = parseFloat(b.dataset.speed);
      speedButtons.forEach(x => x.classList.remove('active'));
      b.classList.add('active');
      menu.classList.remove('show');
    }
    speedButtons.forEach(b => b.addEventListener('click', onSpeedBtnClick));

    function onDocClick(){ menu.classList.remove('show'); }
    document.addEventListener('click', onDocClick);

    card.tabIndex = 0;
    card.style.outline = 'none';
    function onCardKeydown(e){
      const tag = (e.target.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea') return;
      if (e.key === ' ' || e.key === 'k' || e.key === 'K') { e.preventDefault(); playPause(); }
      else if (e.key === 'ArrowRight') { e.preventDefault(); audio.currentTime += 5; }
      else if (e.key === 'ArrowLeft')  { e.preventDefault(); audio.currentTime = Math.max(0, audio.currentTime - 5); }
      else if (e.key === 'ArrowUp')    { e.preventDefault(); audio.volume = Math.min(1, audio.volume + 0.05); volIn.value = audio.volume; updateMuteIcon(); }
      else if (e.key === 'ArrowDown')  { e.preventDefault(); audio.volume = Math.max(0, audio.volume - 0.05); volIn.value = audio.volume; updateMuteIcon(); }
      else if (e.key === 'm' || e.key === 'M') { audio.muted = !audio.muted; updateMuteIcon(); }
    }
    card.addEventListener('keydown', onCardKeydown);

    try {
      if ('mediaSession' in navigator && window.MediaMetadata) {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: name || 'Audio',
          artist: 'Shared Files',
        });
        navigator.mediaSession.setActionHandler('play', () => audio.play());
        navigator.mediaSession.setActionHandler('pause', () => audio.pause());
        navigator.mediaSession.setActionHandler('seekbackward', () => {
          audio.currentTime = Math.max(0, audio.currentTime - 10);
        });
        navigator.mediaSession.setActionHandler('seekforward', () => {
          audio.currentTime += 10;
        });
      }
    } catch(e){}

    function onVisibilityChange(){
      if (document.hidden) {
        saveResumeTime(src, audio.currentTime, audio.duration);
        if (!audio.paused) audio.pause();
      }
    }
    document.addEventListener('visibilitychange', onVisibilityChange);

    function onBeforeUnload(){
      saveResumeTime(src, audio.currentTime, audio.duration);
    }
    window.addEventListener('beforeunload', onBeforeUnload);
    window.addEventListener('pagehide', onBeforeUnload);

    updateMuteIcon();

    function cleanup(){
      if (audio && audio.currentTime > 0) {
        saveResumeTime(src, audio.currentTime, audio.duration);
      }
      clearTimeout(resumeSaveTimer);
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
      window.removeEventListener('beforeunload', onBeforeUnload);
      window.removeEventListener('pagehide', onBeforeUnload);
      document.removeEventListener('click', onDocClick);
      document.removeEventListener('visibilitychange', onVisibilityChange);
      try {
        if ('mediaSession' in navigator) {
          navigator.mediaSession.setActionHandler('play', null);
          navigator.mediaSession.setActionHandler('pause', null);
          navigator.mediaSession.setActionHandler('seekbackward', null);
          navigator.mediaSession.setActionHandler('seekforward', null);
          navigator.mediaSession.metadata = null;
        }
      } catch(e){}
    }

    return { el: card, cleanup };
  }
</script>
</body>
</html>

"""
