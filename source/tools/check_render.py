"""Render every page in Chromium: errors, raw markup visible as text, sideways scroll at 390px, broken local links/anchors."""
import asyncio, os, re, sys, glob
from urllib.parse import urlparse, unquote
from playwright.async_api import async_playwright

SITE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'site')
pages = sorted(glob.glob(os.path.join(SITE, '*.html')))
problems = []

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ids_cache = {}
        for width in (390, 1200):
            ctx = await b.new_context(viewport={'width': width, 'height': 900})
            pg = await ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.route(re.compile(r'^https?://'), lambda r: r.abort())  # offline: fonts not needed
            for f in pages:
                name = os.path.basename(f)
                errs.clear()
                await pg.goto('file://' + f)
                if errs: problems.append(f'{name} [{width}] JS error: {errs}')
                sw = await pg.evaluate('document.documentElement.scrollWidth')
                cw = await pg.evaluate('document.documentElement.clientWidth')
                if sw > cw + 1:
                    wide = await pg.evaluate('''() => { const W=document.documentElement.clientWidth; const out=[];
                      document.querySelectorAll('body *').forEach(e=>{const r=e.getBoundingClientRect(); if((r.right>W+1||r.left<-1) && !e.closest('.tablebox')) out.push(e.tagName+'.'+e.className+' '+(e.textContent||'').slice(0,40));}); return out.slice(0,5); }''')
                    problems.append(f'{name} [{width}] horizontal scroll {sw}>{cw}: {wide}')
                if width == 1200:
                    text = await pg.evaluate('document.body.innerText')
                    m = re.findall(r'</?[a-zA-Z][a-zA-Z0-9]*[^>\n]{0,40}>|&[a-z]+;|\*\*', text)
                    if m: problems.append(f'{name}: raw markup visible: {m[:5]}')
                    ids_cache[name] = set(await pg.evaluate('[...document.querySelectorAll("[id]")].map(e=>e.id)'))
                    links = await pg.evaluate('[...document.querySelectorAll("a[href]")].map(a=>a.getAttribute("href"))')
                    for href in links:
                        if href.startswith(('http', 'mailto')): continue
                        ids_cache.setdefault('_links', []).append((name, href))
            await ctx.close()
        for name, href in ids_cache.get('_links', []):
            path, _, frag = href.partition('#')
            target = path or name
            if not os.path.exists(os.path.join(SITE, unquote(target))):
                problems.append(f'{name}: missing file {href}'); continue
            if frag and target.endswith('.html') and frag not in ids_cache.get(target, set()):
                problems.append(f'{name}: missing anchor {href}')
        await b.close()

asyncio.run(main())
print(f'{len(pages)} pages checked')
print('\n'.join(problems) if problems else 'NO PROBLEMS')
