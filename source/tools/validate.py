import json, sys, re
from html.parser import HTMLParser
VOID={'br','hr','img','input','meta','link','wbr'}
class P(HTMLParser):
    def __init__(s): super().__init__(); s.stack=[]; s.err=[]
    def handle_starttag(s,t,a):
        if t in ('script','style','img'): s.err.append('forbidden tag '+t)
        for k,v in a:
            if k=='style': s.err.append('inline style')
        if t not in VOID: s.stack.append(t)
    def handle_endtag(s,t):
        if t in VOID: return
        if not s.stack or s.stack[-1]!=t: s.err.append(f'mismatched </{t}> (open: {s.stack[-3:]})'); 
        if t in s.stack:
            while s.stack and s.stack.pop()!=t: pass
def chk(h,where,errs):
    p=P(); p.feed(h); p.close()
    if p.stack: errs.append(f'{where}: unclosed {p.stack}')
    errs += [f'{where}: {e}' for e in p.err]
    if re.search(r'[֐-׿]"[֐-׿]',re.sub(r'<[^>]*>','',h)) : errs.append(f'{where}: ASCII " inside Hebrew word (use ״)')
    if re.search(r"[֐-׿]'[֐-׿\s]",re.sub(r'<[^>]*>','',h)): errs.append(f"{where}: ASCII ' after Hebrew letter (use ׳)")
    if '**' in h: errs.append(f'{where}: markdown ** found')
def main(fn):
    errs=[]
    d=json.load(open(fn,encoding='utf-8'))
    for k in ['num','slug','title','short','lead','period','main_ideas','sections','mistakes','check','workbook','terms']:
        if k not in d: errs.append('missing '+k)
    secs=d.get('sections',[])
    if not 4<=len(secs)<=6: errs.append('sections must be 4-6')
    ids=[s['id'] for s in secs]
    if ids!=[f's{i+1}' for i in range(len(secs))]: errs.append('section ids must be s1..sN')
    for s in secs: chk(s['html'],'section '+s['id'],errs)
    if len(d.get('check',[]))!=8: errs.append('check must have 8')
    for i,c in enumerate(d.get('check',[])): chk(c['q'],f'check{i}q',errs); chk(c['a'],f'check{i}a',errs)
    for L in 'ABC':
        w=d.get('workbook',{}).get(L,[])
        if len(w)!=10: errs.append(f'workbook {L} must have 10 (has {len(w)})')
        for i,c in enumerate(w): chk(c['q'],f'{L}{i+1}q',errs); chk(c['a'],f'{L}{i+1}a',errs)
    for i,m in enumerate(d.get('mistakes',[])): chk(m,f'mistake{i}',errs)
    if not 4<=len(d.get('mistakes',[]))<=6: errs.append('mistakes 4-6')
    smap={s['id']:s['html'] for s in secs}
    tags={"רעיונות","פוליטיקה ומשטר","חברה וכלכלה","תולדות ישראל","אירועים ומסמכים","אישים","תרבות ואמנות"}
    if not 6<=len(d.get('terms',[]))<=14: errs.append('terms 6-14')
    for t in d.get('terms',[]):
        for k in ['he','en','def','extra','section','area_tag']:
            if k not in t: errs.append(f'term {t.get("he")} missing {k}')
        if t.get('area_tag') not in tags: errs.append(f'term {t.get("he")} bad area_tag')
        h=smap.get(t.get('section'),'')
        strongs=re.findall(r'<strong>(.*?)</strong>',h,re.S)
        if not any(t['he'] in re.sub(r'<[^>]*>','',x) for x in strongs):
            errs.append(f'term "{t["he"]}" not in a <strong> in section {t.get("section")}')
    words=sum(len(re.sub(r'<[^>]*>',' ',s['html']).split()) for s in secs)
    print(f'{fn}: sections={len(secs)} words={words} terms={len(d.get("terms",[]))}')
    if errs: print('ERRORS:'); [print(' -',e) for e in errs]; sys.exit(1)
    print('OK')
for f in sys.argv[1:]: main(f)
