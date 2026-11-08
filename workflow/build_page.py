"""Build the static workflow page from README.md using the Python standard library."""
from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parent


def inline(text):
    text = html.escape(text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)', r'<a href="\2">\1</a>', text)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)


def render(source):
    lines = source.splitlines()
    out, toc = [], []
    i = 0
    section = False
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.startswith('# '):
            i += 1
            continue
        if line.startswith('```'):
            language = line[3:]
            i += 1
            code = []
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i])
                i += 1
            out.append('<pre><code class="language-' + html.escape(language) + '">' + html.escape('\n'.join(code)) + '</code></pre>')
            i += 1
            continue
        heading = re.match(r'^(#{2,3}) (.*)', line)
        if heading:
            level, title = len(heading[1]), heading[2]
            if level == 2:
                if section:
                    out.append('</section>')
                anchor = 'step-' + title[:2]
                toc.append((anchor, title))
                out.append('<section class="chapter" id="' + anchor + '">')
                section = True
            out.append(f'<h{level}>' + inline(title) + f'</h{level}>')
            i += 1
            continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+', c) for c in cells):
                    rows.append(cells)
                i += 1
            table = '<div class="table-wrap" tabindex="0" role="region" aria-label="可横向滚动的对照表"><table><thead><tr>'
            table += ''.join('<th scope="col">' + inline(c) + '</th>' for c in rows[0])
            table += '</tr></thead><tbody>'
            for row in rows[1:]:
                table += '<tr>' + ''.join('<td>' + inline(c) + '</td>' for c in row) + '</tr>'
            out.append(table + '</tbody></table></div>')
            continue
        if line.startswith('- '):
            items = []
            while i < len(lines) and lines[i].startswith('- '):
                items.append('<li>' + inline(lines[i][2:]) + '</li>')
                i += 1
            out.append('<ul>' + ''.join(items) + '</ul>')
            continue
        paragraph = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '|', '- ', '```')):
            paragraph.append(lines[i])
            i += 1
        out.append('<p>' + inline(' '.join(paragraph)) + '</p>')
    if section:
        out.append('</section>')
    return '\n'.join(out), toc


CSS = '''
:root{--ink:#111e1b;--panel:#1a2c26;--paper:#eee6d5;--muted:#b5c3b6;--gold:#cfb578;--red:#d18c7f;--line:#43584a}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:28px}body{margin:0;color:var(--paper);background:var(--ink);font:16px/1.9 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}a{color:var(--gold);text-underline-offset:5px}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid var(--gold);outline-offset:5px}header,.layout,footer{max-width:1390px;margin:auto;padding:30px 36px}nav,.downloads{display:flex;flex-wrap:wrap;gap:12px 24px}nav{font-size:14px}h1{font-size:clamp(42px,6vw,78px);line-height:1.15;letter-spacing:-2px;margin:25px 0}.eyebrow{color:var(--gold);font-size:12px;letter-spacing:3px;margin-top:65px}.lead{font-size:21px;color:var(--muted);max-width:870px}.stats{display:flex;gap:36px;flex-wrap:wrap;margin:30px 0}.stats strong{display:block;font-size:31px;line-height:1.4;color:var(--gold)}.stats small{color:var(--muted);font-size:13px}.downloads a,.downloads button{border:1px solid var(--line);padding:9px 16px;text-decoration:none;font:inherit;background:transparent;color:var(--gold);cursor:pointer}.downloads .primary{color:var(--ink);background:var(--gold);border-color:var(--gold)}.route{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-top:40px;list-style:none;padding:0}.route li{padding:17px 14px;background:var(--panel);border-top:2px solid var(--gold);font-size:14px;line-height:1.6}.route span{display:block;font-size:11px;color:var(--gold);letter-spacing:2px}.layout{display:grid;grid-template-columns:230px minmax(0,1fr);gap:55px;padding-top:0}.toc{position:sticky;top:24px;align-self:start;max-height:92vh;overflow:auto}.toc summary{cursor:pointer;color:var(--gold);font-weight:650}.toc ol{list-style:none;padding:0}.toc a{display:block;padding:8px 0;color:var(--muted);text-decoration:none;font-size:14px;border-bottom:1px solid #43584a55;line-height:1.6}.toc a:hover{color:var(--gold)}article{min-width:0}article>p:first-child{font-size:13px;color:var(--gold)}article>p:nth-child(2){color:var(--muted);border-left:3px solid var(--red);padding-left:20px}.chapter{border-top:1px solid var(--line);padding:25px 0 38px}.chapter h2{font-size:30px;line-height:1.45;color:var(--gold);margin:12px 0 24px}.chapter h3{margin:34px 0 15px;font-size:21px;color:var(--red)}p{margin:17px 0}.chapter li{margin:9px 0}strong{color:#f2d49a}code{font-size:.9em}pre{padding:22px;background:#091410;border:1px solid var(--line);overflow:auto;line-height:1.7}pre code{font-size:13px;color:#dfd8c7}.table-wrap{overflow-x:auto;margin:24px 0}table{border-collapse:collapse;width:100%;min-width:540px;font-size:15px}th,td{vertical-align:top;text-align:left;padding:15px 16px;border-bottom:1px solid var(--line)}th{color:var(--gold);background:var(--panel)}td:first-child{font-weight:600;color:#d1d9ca;width:22%}footer{font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-bottom:55px}.copy-status{font-size:13px;color:var(--muted);min-height:25px}::selection{background:#b39b66;color:#102018}
@media(max-width:1000px){.layout{grid-template-columns:195px minmax(0,1fr);gap:25px}.route{grid-template-columns:repeat(3,1fr)}}
@media(max-width:720px){header,.layout,footer{padding:24px 20px}.layout{display:block;padding-top:0}.toc{position:static;max-height:none;border:1px solid var(--line);padding:14px 18px;margin:10px 0 30px}.toc ol{columns:2;column-gap:20px}.toc a{break-inside:avoid;font-size:13px}.eyebrow{margin-top:36px;font-size:10px;letter-spacing:2px}h1{letter-spacing:-1px}.lead{font-size:18px}.stats{gap:18px 30px}.stats strong{font-size:26px}.route{grid-template-columns:repeat(2,1fr)}.chapter h2{font-size:25px}.chapter h3{font-size:20px}th,td{padding:12px 10px}.downloads a,.downloads button{font-size:14px;padding:8px 12px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
'''


def build():
    body, toc = render((ROOT / 'README.md').read_text())
    navigation = ''.join('<li><a href="#' + anchor + '">' + html.escape(title) + '</a></li>' for anchor, title in toc)
    page = '''<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="从小说、人物与电影风格、剧情分镜、Muse素材、配音对齐到Remotion高速导出和AAC声音验收的12步实操。"><title>Moonveil · 从小说到有声成片</title><style>''' + CSS + '''</style></head><body>
<header><nav aria-label="站点导航"><a href="../">← 制作流程库</a><a href="../motion-atlas/">65项效果能力库</a><a href="../vox-story/">剧情驱动Vox样片</a><a href="https://github.com/jackcui2004/moonveil-remotion-library/tree/main/workflow">GitHub 文档与模板 ↗</a></nav>
<p class="eyebrow">MOONVEIL / NOVEL TO FILM / 2026.11.08</p><h1>拿到一篇小说，<br>怎样把每一镜设计出来。</h1><p class="lead">先读人物与剧情，再决定画面让观众看懂什么。将本次长片从素材预算到有声交付的做法，整理为下一篇可执行的12步流程。</p>
<div class="stats"><div><strong>28张＋2段</strong><small>本次实际源素材</small></div><div><strong>212镜</strong><small>87个语义节点展开</small></div><div><strong>25类</strong><small>本篇运行布局</small></div><div><strong>83:33</strong><small>完整配音成片时长</small></div></div>
<div class="downloads"><a class="primary" href="#step-04">先看镜头怎么编排</a><a href="README.md" download>下载完整流程 Markdown</a><a href="templates/director-brief.txt" download>下载模型执行入口</a><button id="copy-brief" type="button">复制执行入口</button></div><p id="copy-status" class="copy-status" role="status" aria-live="polite"></p>
<ol class="route" aria-label="制作主线"><li><span>01 / STORY</span>固定正文与人物</li><li><span>02 / DIRECT</span>语义节点与逐镜理由</li><li><span>03 / ASSETS</span>去重预算与Muse任务</li><li><span>04 / ALIGN</span>实际素材与配音对齐</li><li><span>05 / BUILD</span>组件实施与样片</li><li><span>06 / DELIVER</span>稳定导出与声音验收</li></ol></header>
<div class="layout"><details class="toc" open><summary>12步执行目录</summary><ol>''' + navigation + '''</ol></details><main id="content"><article>''' + body + '''</article></main></div>
<footer>这是一份经过长片实践整理的方法与空白模板，非任意小说无人审阅的一键导演系统。公开内容不含本篇全文、完整音轨／字幕、人物素材或成片。既有获认可样片仍在Vox页面。<br>构建方式：在本目录运行 python3 build_page.py，从 README.md 更新此页。</footer>
<script>document.getElementById('copy-brief').addEventListener('click',async()=>{const status=document.getElementById('copy-status');try{const r=await fetch('templates/director-brief.txt');if(!r.ok)throw Error('download');await navigator.clipboard.writeText(await r.text());status.textContent='已复制执行入口，可连同本篇小说和参考图交接。';}catch{status.textContent='当前浏览器未允许复制，请使用旁边的下载入口。';}});</script></body></html>'''
    (ROOT / 'index.html').write_text(page)
    print('Built workflow/index.html:', len(toc), 'sections,', len(page.encode()), 'bytes')


if __name__ == '__main__':
    build()
