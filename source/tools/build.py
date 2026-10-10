#!/usr/bin/env python3
"""Build the History grade 8 study site from data/NN.json + units.json into site/."""
import json, glob, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.dirname(ROOT) if os.path.basename(ROOT) == 'source' else os.path.join(ROOT, 'site')
PLAN = json.load(open(os.path.join(ROOT, 'units.json'), encoding='utf-8'))
AREAS = {a['id']: a for a in PLAN['areas']}
UNITS = []
for f in sorted(glob.glob(os.path.join(ROOT, 'data', '*.json'))):
    d = json.load(open(f, encoding='utf-8'))
    plan = next(u for u in PLAN['units'] if u['num'] == d['num'])
    d['area'] = plan['area']; d['syl'] = plan['syl']; d['optional'] = plan['optional']; d['slug'] = plan['slug']
    UNITS.append(d)
UNITS.sort(key=lambda u: u['num'])

SUBJ = 'היסטוריה'
GRADE = 'כיתה ח׳'
CURR = 'curriculum-history-grade08.html'
TOTAL_TASKS = sum(len(u['workbook'][L]) for u in UNITS for L in 'ABC')

def nn(u): return f"{u['num']:02d}"
def exp_file(u): return f"{nn(u)}-{u['slug']}-explanation.html"
def wb_file(u): return f"{nn(u)}-{u['slug']}-workbook.html"
def esc(s): return html.escape(s, quote=True)

HEAD = """<!doctype html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@500;700&family=Assistant:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<div class="wrap">
"""
TAIL = """<footer>היסטוריה לכיתה ח׳ · לפי מפרט התכנים של משרד החינוך לחטיבת הביניים. כדאי לוודא את היקף החומר למבחן מול המורה.</footer>
</div>
<script src="assets/site.js"></script>
</body>
</html>
"""

def toplinks(current, extra=''):
    items = [('index.html', 'דף ראשי'), (CURR, 'תוכנית הלימודים'), ('glossary.html', 'מילון מושגים')]
    out = []
    for href, label in items:
        out.append(f'<span class="here">{label}</span>' if href == current else f'<a href="{href}">{label}</a>')
    if extra: out.append(extra)
    return '<nav class="toplinks" aria-label="ניווט">' + ' · '.join(out) + '</nav>\n'

def write(name, content):
    with open(os.path.join(SITE, name), 'w', encoding='utf-8') as f: f.write(content)

def eyebrow(u):
    return f"{SUBJ} · {GRADE} · {AREAS[u['area']]['title']} · יחידה {u['num']}"

def opt_badge(u): return '<span class="badge">רשות</span>' if u['optional'] else ''

# ---------------- explanation pages ----------------
def explanation(u, i):
    prev_u = UNITS[i-1] if i > 0 else None
    next_u = UNITS[i+1] if i+1 < len(UNITS) else None
    h = HEAD.format(title=esc(f"{u['title']} · {SUBJ} {GRADE}"), desc=esc(u['short']))
    h += toplinks(None, f'<a href="{wb_file(u)}">חוברת עבודה ליחידה</a>')
    h += f'''<header><span class="eyebrow">{eyebrow(u)}</span><h1>{esc(u["title"])}{opt_badge(u)}</h1>
<p class="lead">{u["lead"]}</p>
<p class="syl"><b>בתוכנית הלימודים:</b> {esc(u["syl"])} · <b>תקופה:</b> {esc(u["period"])}</p></header>
'''
    h += '<nav class="contents" aria-label="תוכן הדף"><strong>תוכן</strong><ol>'
    for s in u['sections']: h += f'<li><a href="#{s["id"]}">{esc(s["title"])}</a></li>'
    h += '<li><a href="#mistakes">טעויות נפוצות</a></li><li><a href="#check">בדקו את עצמכם</a></li></ol></nav>\n'
    for k, s in enumerate(u['sections'], 1):
        h += f'<section class="ch" id="{s["id"]}"><h2><span class="num">{u["num"]}.{k}</span>{esc(s["title"])}</h2>\n{s["html"]}\n</section>\n'
    h += '<section class="ch" id="mistakes"><h2>טעויות נפוצות</h2><ul class="mistakes">'
    for m in u['mistakes']: h += f'<li>{m}</li>'
    h += '</ul></section>\n'
    h += '<section class="ch" id="check"><h2>בדקו את עצמכם</h2><p class="level-lead">שמונה שאלות קצרות. ענו לבד, ואז פתחו את התשובה.</p><ol class="exercises">'
    for c in u['check']:
        h += f'<li><div class="task"><div>{c["q"]}</div><details><summary>הצג תשובה</summary><div class="sol">{c["a"]}</div></details></div></li>'
    h += '</ol>'
    h += f'<p>רוצים לתרגל עוד? ב<a href="{wb_file(u)}">חוברת העבודה</a> יש 30 משימות בשלוש רמות.</p></section>\n'
    h += '<nav class="pager" aria-label="יחידות">'
    h += f'<a href="{exp_file(prev_u)}"><small>→ היחידה הקודמת</small>{prev_u["num"]}. {esc(prev_u["title"])}</a>' if prev_u else '<span></span>'
    h += f'<a href="{exp_file(next_u)}"><small>היחידה הבאה ←</small>{next_u["num"]}. {esc(next_u["title"])}</a>' if next_u else '<span></span>'
    h += '</nav>\n' + TAIL
    write(exp_file(u), h)

LEVELS = [('A', 'רמה א׳: בסיס', 'ידע והבנה: מושגים, אישים, אירועים וסדר זמנים.'),
          ('B', 'רמה ב׳: תרגול', 'הסבר סיבות ותוצאות, השוואה וקישור בין מושג לדוגמה.'),
          ('C', 'רמה ג׳: רמת מבחן', 'ניתוח מקורות, השוואה לפי היבטים, הבעת עמדה ונימוקה.')]

def workbook(u):
    h = HEAD.format(title=esc(f"חוברת עבודה: {u['title']} · {SUBJ} {GRADE}"), desc=esc('30 משימות עם פתרונות: ' + u['short']))
    h += toplinks(None, f'<a href="{exp_file(u)}">דף ההסבר ליחידה</a>')
    h += f'''<header><span class="eyebrow">{eyebrow(u)} · חוברת עבודה</span><h1>חוברת עבודה: {esc(u["title"])}{opt_badge(u)}</h1>
<p class="lead">לומדים תוך כדי עשייה: 30 משימות בשלוש רמות. נסו לענות בכתב לפני שאתם פותחים את התשובה, ואז השוו לתשובה לדוגמה. סמנו "פתרתי" ליד כל משימה שסיימתם.</p></header>
'''
    h += '<nav class="contents" aria-label="תוכן הדף"><strong>תוכן</strong><ol>'
    for L, t, _ in LEVELS: h += f'<li><a href="#lvl{L}">{t}</a></li>'
    h += '</ol></nav>\n'
    h += '<div class="toolbar" role="toolbar" aria-label="כלי תרגול"><button type="button" data-act="toggle">הצגת כל הפתרונות</button><button type="button" data-act="clear">ניקוי הסימונים</button><span class="progress" aria-live="polite"></span></div>\n'
    n = 0
    for L, t, lead in LEVELS:
        tasks = u['workbook'][L]
        h += f'<section class="ch" id="lvl{L}"><h2>{t} <small class="level-lead" style="font-size:.9rem">משימות {n+1}–{n+len(tasks)}</small></h2><p class="level-lead">{lead}</p><ol class="exercises" start="{n+1}">'
        for task in tasks:
            n += 1
            h += (f'<li id="t{n}"><div class="task"><div>{task["q"]}</div>'
                  f'<label class="tick"><input type="checkbox" data-id="t{n}"> פתרתי</label>'
                  f'<details><summary>הצג פתרון</summary><div class="sol">{task["a"]}</div></details></div></li>')
        h += '</ol></section>\n'
    h += f'<nav class="pager" aria-label="ניווט"><a href="{exp_file(u)}"><small>→ חזרה</small>דף ההסבר: {esc(u["title"])}</a><a href="index.html"><small>←</small>לדף הראשי</a></nav>\n'
    h = h.replace(' style="font-size:.9rem"', '')
    h += TAIL
    write(wb_file(u), h)

# ---------------- glossary ----------------
def slugify(s):
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
    return s or 'term'

def build_terms():
    merged = {}
    order = []
    for u in UNITS:
        for t in u['terms']:
            k = re.sub(r'[\s״׳"\'־-]', '', t['he'])
            link = (exp_file(u) + '#' + t['section'], f"{u['num']}. {u['title']}")
            if k in merged:
                if link not in merged[k]['links']: merged[k]['links'].append(link)
                continue
            e = dict(t); e['links'] = [link]; e['unit'] = u['num']
            merged[k] = e; order.append(k)
    used = set()
    for k in order:
        e = merged[k]
        base = 'term-' + slugify(e['en'].split('(')[0])
        sid = base; i = 2
        while sid in used: sid = f'{base}-{i}'; i += 1
        used.add(sid); e['id'] = sid
    return [merged[k] for k in order]

HEB_LETTERS = 'אבגדהוזחטיכלמנסעפצקרשת'
def first_letter(s):
    for ch in s:
        if ch in HEB_LETTERS: return ch
        if ch in 'ךםןףץ': return 'כמנפצ'['ךםןףץ'.index(ch)]
        if ch.isalpha(): return ch.upper()
    return '#'

def sortkey(s): return re.sub(r'[״׳"\'()\s־-]', '', s)

CATS = ["רעיונות", "פוליטיקה ומשטר", "חברה וכלכלה", "אירועים ומסמכים", "אישים", "תולדות ישראל", "תרבות ואמנות"]

def entry_html(e, with_id=True):
    idattr = f' id="{e["id"]}"' if with_id else ''
    links = ', '.join(f'<a href="{href}">{esc(t)}</a>' for href, t in e['links'])
    extra = f'<dd class="extra">{e["extra"]}</dd>' if e.get('extra') else ''
    return (f'<div class="entry"{idattr}><dt>{esc(e["he"])}<span class="en">{esc(e["en"])}</span><span class="cat">{esc(e["area_tag"])}</span></dt>'
            f'<dd>{e["def"]}</dd>{extra}<dd class="where">נלמד ב: {links}</dd></div>')

def glossary(terms):
    terms_sorted = sorted(terms, key=lambda e: sortkey(e['he']))
    groups = {}
    for e in terms_sorted: groups.setdefault(first_letter(e['he']), []).append(e)
    letters = [l for l in HEB_LETTERS if l in groups] + [l for l in groups if l not in HEB_LETTERS]
    h = HEAD.format(title=esc(f'מילון מושגים · {SUBJ} {GRADE}'), desc=esc(f'{len(terms)} מושגים, אישים ואירועים מכל יחידות האתר'))
    h += toplinks('glossary.html')
    h += f'''<header><span class="eyebrow">{SUBJ} · {GRADE} · מסמך עזר</span><h1>מילון מושגים</h1>
<p class="lead">{len(terms)} מושגים, אישים, אירועים ומסמכים שמופיעים באתר. לכל ערך: הגדרה קצרה, השם באנגלית, פרט מזהה (תאריך, דוגמה) וקישור ליחידה שבה הוא מוסבר. אפשר לחפש בעברית או באנגלית.</p></header>
<div class="gl-tools"><label for="gl-search"><strong>חיפוש</strong></label><input type="search" id="gl-search" placeholder="לדוגמה: אמנציפציה, Napoleon, 1789" autocomplete="off"><span id="gl-count" class="syl" aria-live="polite"></span>
<div class="views" role="group" aria-label="תצוגה"><button type="button" data-view="abc" aria-pressed="true">לפי א״ב</button><button type="button" data-view="cat" aria-pressed="false">לפי תחום</button></div>
<nav class="letters" aria-label="אותיות">'''
    for l in letters: h += f'<a href="#letter-{l}">{l}</a>'
    h += '</nav></div>\n<div id="view-abc">'
    for l in letters:
        h += f'<h2 class="letter-head" id="letter-{l}">{l}</h2><dl class="terms">' + ''.join(entry_html(e) for e in groups[l]) + '</dl>'
    h += '</div>\n<div id="view-cat" class="hidden">'
    for c in CATS:
        es = [e for e in terms_sorted if e['area_tag'] == c]
        if not es: continue
        h += f'<h2 class="letter-head cat-head">{c} <small class="syl">({len(es)})</small></h2><dl class="terms">' + ''.join(entry_html(e, False) for e in es) + '</dl>'
    h += '</div>\n' + TAIL
    write('glossary.html', h)

# ---------------- curriculum page ----------------
SOURCES = [
    ('מפרט התכנים לכיתה ח׳ – היסטוריה, חטיבת הביניים (פורטל עובדי הוראה, משרד החינוך)', 'https://pop.education.gov.il/learning-plans/history/junior-high/grade-8/'),
    ('תוכנית הלימודים בהיסטוריה לחטיבת הביניים, ממלכתי (מסמך PDF, משרד החינוך, התשע״ז)', 'http://meyda.education.gov.il/files/Mazkirut_Pedagogit/Historya/hatab_tashaz.pdf'),
    ('עדכון תוכנית הלימודים בהיסטוריה – ועדת "הסיפור השלם" (משרד החינוך)', 'https://pop.education.gov.il/complete-story-program/applied-program-curriculum/history/'),
    ('אתר הייחוס לעיצוב: מתמטיקה יא׳ 5 יחידות', 'https://ofernarkis10.github.io/math11grade/index.html'),
]

def curriculum():
    h = HEAD.format(title=esc(f'תוכנית הלימודים · {SUBJ} {GRADE}'), desc='רשימת הנושאים לכיתה ח׳ בהיסטוריה לפי משרד החינוך')
    h += toplinks(CURR)
    h += f'''<header><span class="eyebrow">{SUBJ} · {GRADE} · מסמך עזר</span><h1>תוכנית הלימודים בהיסטוריה לכיתה ח׳</h1>
<p class="lead">נושא השנה לפי משרד החינוך: <strong>"העת החדשה – יצירת חברה חדשה והתפתחות המדינה המודרנית ומקומם של היהודים בתהליכים אלה"</strong> (כ־60 שעות לימוד). כאן החומר מחולק ל־{len(UNITS)} יחידות לימוד, בשני פרקים, לפי סדר התוכנית. לכל יחידה יש דף הסבר וחוברת עבודה.</p></header>
<nav class="contents" aria-label="תוכן"><strong>תוכן</strong><ol><li><a href="#goals">מטרות השנה</a></li><li><a href="#overview">טבלת סדר ההוראה</a></li>'''
    for a in PLAN['areas']: h += f'<li><a href="#area-{a["id"]}">{esc(a["title"])}</a></li>'
    h += '<li><a href="#not-this-year">מה לא נלמד השנה</a></li><li><a href="#sources">מקורות</a></li></ol></nav>\n'
    h += '''<section class="ch" id="goals"><h2>מטרות השנה</h2>
<p>לפי מפרט התכנים, בסוף השנה התלמידים יבינו:</p>
<ul><li>את החידוש שבמהפכה המדעית: גישה חקרנית המבוססת על עובדות, ניסוי ותצפית.</li>
<li>את עקרונות הנאורות ואת השפעתם על עיצוב חברות ומדינות חדשות, ואת היחס החדש בין היחיד למדינה.</li>
<li>את השפעת הנאורות על יהדות אירופה: מעמד היהודים, המשכילים, הרפורמה הדתית וההתנגדות לה (ולפי בחירה: החסידות ומתנגדיה).</li>
<li>את הסיבות למהפכה הצרפתית, את ערכיה ואת חשיבותה, ואת משמעות המהפכה התעשייתית לחיי היחיד והחברה.</li>
<li>את ההשלכות של השתלבות היהודים בחברה המודרנית: זהות, סולידריות, התבוללות ואנטישמיות.</li>
<li>את הלאומיות המודרנית, את תהליכי הדמוקרטיזציה והפרלמנטריזם, ואת הפתרונות השונים לשאלת הקיום היהודי בגולה.</li></ul>
<div class="note"><strong>שימו לב:</strong> נושאים שמסומנים "רשות" הם בחירה של המורה. בנושא "היהודים בין רפורמה ונאורות" בוחרים אחת משתי חלופות (יחידה 4 או יחידה 5).</div></section>
'''
    h += '<section class="ch" id="overview"><h2>טבלת סדר ההוראה</h2><div class="tablebox"><table><thead><tr><th>#</th><th>יחידה</th><th>נושא בתוכנית</th><th>תקופה</th><th>דפים</th></tr></thead><tbody>'
    for u in UNITS:
        h += (f'<tr><td>{u["num"]}</td><td><a href="#unit-{nn(u)}">{esc(u["title"])}</a>{opt_badge(u)}</td><td>{esc(u["syl"])}</td>'
              f'<td>{esc(u["period"])}</td><td><a href="{exp_file(u)}">הסבר</a> · <a href="{wb_file(u)}">חוברת</a></td></tr>')
    h += '</tbody></table></div></section>\n'
    for a in PLAN['areas']:
        us = [u for u in UNITS if u['area'] == a['id']]
        h += f'<section class="topic" id="area-{a["id"]}"><div class="topic-head"><h2>{esc(a["title"])}</h2><span>{esc(a["sub"])} · {len(us)} יחידות</span></div>'
        for u in us:
            h += f'<div class="unit-card" id="unit-{nn(u)}"><h3>{u["num"]}. {esc(u["title"])}{opt_badge(u)}</h3><p class="syl"><b>בתוכנית הלימודים:</b> {esc(u["syl"])}</p><ul>'
            for m in u['main_ideas']: h += f'<li>{m}</li>'
            h += f'</ul><p class="pages">דפים: <a href="{exp_file(u)}">דף הסבר</a> · <a href="{wb_file(u)}">חוברת עבודה (30 משימות)</a></p></div>'
        h += '</section>\n'
    h += '''<section class="ch" id="not-this-year"><h2>מה לא נלמד השנה</h2>
<ul><li><strong>לפני כיתה ח׳ (כיתות ו׳–ז׳):</strong> העולם העתיק וימי הביניים, וראשית העת החדשה. כאן הם מופיעים רק כרקע קצר.</li>
<li><strong>בכיתה ט׳:</strong> המאה ה־20, כולל הקולוניאליזם והאימפריאליזם, מלחמות העולם, המשטרים הטוטליטריים והשואה, והמשך התנועה הציונית.</li>
<li><strong>בחטיבה העליונה:</strong> הלאומיות בישראל ובעמים לעומק (נושא "לאומיות בישראל ובעמים").</li></ul>
<p class="syl">החלוקה לפי מסמכי משרד החינוך. היקף החומר למבחנים נקבע בבית הספר ועשוי להשתנות משנה לשנה.</p></section>
'''
    h += '<section class="ch" id="sources"><h2>מקורות</h2><ul>'
    for t, url in SOURCES: h += f'<li><a href="{url}" target="_blank" rel="noopener">{esc(t)}</a></li>'
    h += '<li>אין ספר לימוד מחייב באתר זה: הסדר והמונחים לפי מפרט התכנים. ההסברים, המשימות והתרגומים החופשיים של המקורות נכתבו במיוחד לאתר.</li></ul></section>\n'
    h += TAIL
    write(CURR, h)

# ---------------- index ----------------
def index(terms):
    h = HEAD.format(title=esc(f'{SUBJ} · {GRADE}'), desc='אתר לימוד בהיסטוריה לכיתה ח׳: דפי הסבר, חוברות עבודה ומילון מושגים')
    h += f'''<header><span class="eyebrow">אתר לימוד · {SUBJ} · {GRADE} · חטיבת הביניים</span><h1>היסטוריה לכיתה ח׳</h1>
<p class="lead">העת החדשה: מהמהפכה המדעית והנאורות, דרך המהפכות הגדולות, ועד שאלת הקיום היהודי בסוף המאה ה־19. {len(UNITS)} יחידות לפי תוכנית הלימודים של משרד החינוך. לכל יחידה דף הסבר וחוברת עבודה עם 30 משימות ותשובות לדוגמה.</p></header>
<nav class="toc" id="toc" aria-label="תוכן עניינים"><h2>תוכן עניינים</h2><ol></ol></nav>
<div class="about">
<div><h3>שני דפים לכל יחידה</h3><p>דף הסבר: רקע, מושגים, ציר זמן, מקורות, טעויות נפוצות ו־8 שאלות "בדקו את עצמכם". חוברת עבודה: 30 משימות בשלוש רמות.</p></div>
<div><h3>איך לתרגל</h3><p>התשובות מוסתרות. כתבו תשובה לבד, ואז פתחו את התשובה לדוגמה והשוו. סמנו "פתרתי" כדי לעקוב אחרי ההתקדמות.</p></div>
<div><h3>סדר מומלץ</h3><p>לפי המספור, כי כל יחידה נשענת על הקודמות. יחידות "רשות" לפי בחירת המורה. מושג לא מוכר? חפשו במילון.</p></div>
</div>
<section class="topic" id="reference"><div class="topic-head"><h2>מסמכי עזר</h2><span>3 מסמכים</span></div><ul class="docs">
<li><a href="{CURR}"><span class="no">00</span><span class="t">תוכנית הלימודים לכיתה ח׳</span><span class="q">מסמך עזר</span><span class="d">מטרות השנה, טבלת סדר ההוראה, רעיונות מרכזיים לכל יחידה, מה לא נלמד השנה ומקורות.</span></a></li>
<li><a href="glossary.html"><span class="no">00</span><span class="t">מילון מושגים</span><span class="q">{len(terms)} מושגים</span><span class="d">כל המושגים, האישים, האירועים והמסמכים באתר, לפי א״ב ולפי תחום, עם חיפוש וקישור ליחידה שבה כל מושג מוסבר.</span></a></li>
<li><a href="README.md"><span class="no">00</span><span class="t">על האתר (README)</span><span class="q">מסמך טכני</span><span class="d">מטרת האתר, המקורות, מבנה הדפים והתיקיות ואיך מוסיפים יחידה.</span></a></li>
</ul></section>
'''
    for a in PLAN['areas']:
        us = [u for u in UNITS if u['area'] == a['id']]
        h += f'<section class="topic" id="area-{a["id"]}"><div class="topic-head"><h2>{esc(a["title"])}</h2><span>{len(us)} יחידות · {len(us)*2} דפים</span></div><ul class="docs">'
        for u in us:
            tag = 'רשות · ' if u['optional'] else ''
            h += f'<li><a href="{exp_file(u)}"><span class="no">{nn(u)}</span><span class="t">{esc(u["title"])}</span><span class="q">{tag}דף הסבר</span><span class="d">{esc(u["short"])}</span></a></li>'
            h += f'<li><a href="{wb_file(u)}"><span class="no">{nn(u)}</span><span class="t">חוברת עבודה: {esc(u["title"])}</span><span class="q">30 משימות</span><span class="d">תרגול בשלוש רמות: בסיס, תרגול ורמת מבחן (ניתוח מקורות והבעת עמדה), עם תשובה לדוגמה לכל משימה.</span></a></li>'
        h += '</ul></section>\n'
    h += '<a class="to-top" href="#toc">↑ תוכן עניינים</a>\n'
    h += '''<script>
(function(){var ol=document.querySelector('#toc ol');if(!ol)return;var s='';
document.querySelectorAll('section.topic[id]').forEach(function(sec){var h=sec.querySelector('h2');var c=sec.querySelector('.topic-head span');
s+='<li><a href="#'+sec.id+'">'+h.textContent+(c?'<small>'+c.textContent+'</small>':'')+'</a></li>';});ol.innerHTML=s;})();
</script>
'''
    h += TAIL
    write('index.html', h)

# ---------------- README ----------------
def readme(terms):
    rows = '\n'.join(f"| {u['num']} | {u['title']}{' (רשות)' if u['optional'] else ''} | `{exp_file(u)}` | `{wb_file(u)}` |" for u in UNITS)
    src = '\n'.join(f'- [{t}]({url})' for t, url in SOURCES)
    md = f"""# History8Grade – היסטוריה לכיתה ח׳

אתר לימוד סטטי (HTML) בהיסטוריה לכיתה ח׳ בחטיבת הביניים, לפי מפרט התכנים של משרד החינוך:
**"העת החדשה – יצירת חברה חדשה והתפתחות המדינה המודרנית ומקומם של היהודים בתהליכים אלה"**.
בחטיבת הביניים אין רמות של יחידות לימוד, ולכן שם התיקייה הוא `History8Grade` (בלי "Points").

## מטרה וכללי עבודה
- כל המסמכים בפורמט HTML, בעברית (RTL), וכל דף מופיע ב־`index.html`.
- לכל יחידה שני דפים: דף הסבר וחוברת עבודה (לומדים תוך כדי עשייה).
- תוכן מקורי. ציטוטים קצרים רק ממסמכים היסטוריים שאינם מוגנים (למשל הכרזת העצמאות האמריקנית, הכרזת זכויות האדם והאזרח), בתרגום חופשי.

## מקורות
{src}

אין ספר לימוד מחייב: סדר היחידות והמונחים לפי מפרט התכנים.

## איך צופים באתר
פותחים את `index.html` בדפדפן. אין צורך בשרת. הגופנים נטענים מ־Google Fonts (בלי חיבור לרשת יוצג גופן חלופי).
הסימונים "פתרתי" נשמרים בדפדפן (localStorage) של כל תלמיד.

## תוכן
- {len(UNITS)} יחידות, {len(UNITS)*2} דפי לימוד, {TOTAL_TASKS} משימות בחוברות העבודה, {len(UNITS)*8} שאלות "בדקו את עצמכם"
- מילון מושגים: {len(terms)} ערכים (`glossary.html`)
- תוכנית הלימודים: `{CURR}`

| # | יחידה | דף הסבר | חוברת עבודה |
|---|---|---|---|
{rows}

## מבנה הדפים
- **דף הסבר:** קישורים עליונים → כותרת (תחום · יחידה · נושא בתוכנית) → תוכן → 4–6 פרקים (ציר זמן, שרשרת סיבה־תוצאה, מקורות, טבלאות השוואה) → טעויות נפוצות → 8 שאלות "בדקו את עצמכם" → יחידה קודמת/הבאה.
- **חוברת עבודה:** 30 משימות: רמה א׳ בסיס (10), רמה ב׳ תרגול (10), רמה ג׳ רמת מבחן (10, כולל ניתוח מקורות והבעת עמדה). לכל משימה תשובה לדוגמה מוסתרת, תיבת "פתרתי" ומונה התקדמות.

## מבנה התיקייה
```
History8Grade/
  index.html, {CURR}, glossary.html, README.md
  NN-<slug>-explanation.html, NN-<slug>-workbook.html
  assets/site.css, assets/site.js
  source/            ← מקור הנתונים והמחולל (לא נדרש לצפייה)
    units.json, data/NN.json, tools/build.py, tools/validate.py
```

## איך מוסיפים או משנים יחידה
1. כותבים או עורכים את `source/data/NN.json` (המבנה מתואר ב־`source/SPEC.md`), ומוסיפים את היחידה ל־`source/units.json`.
2. בודקים: `python3 source/tools/validate.py source/data/NN.json`.
3. בונים מחדש: `python3 source/tools/build.py` (יוצר מחדש את כל הדפים, המילון, הדף הראשי והקובץ הזה).
מושגים חדשים נכנסים למילון מתוך השדה `terms` של היחידה.

## הערה
היקף החומר למבחנים נקבע בבית הספר ויכול להשתנות משנה לשנה. כדאי לוודא מול המורה.
"""
    write('README.md', md)

if __name__ == '__main__':
    os.makedirs(SITE, exist_ok=True)
    for i, u in enumerate(UNITS):
        explanation(u, i); workbook(u)
    terms = build_terms()
    glossary(terms); curriculum(); index(terms); readme(terms)
    print(f'units={len(UNITS)} tasks={TOTAL_TASKS} terms={len(terms)}')
