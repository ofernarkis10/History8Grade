# Content spec: History grade 8 study site (Hebrew, RTL)

You write the CONTENT for some units of a Hebrew study site in history for Israeli grade 8 (כיתה ח׳),
following the Ministry of Education grade 8 syllabus
"העת החדשה – יצירת חברה חדשה והתפתחות המדינה המודרנית ומקומם של היהודים בתהליכים אלה".
The plan of all 22 units (with each unit's scope) is in /home/claude/h8/units.json — read it, so you know
what neighbouring units cover and avoid overlapping too much (brief reminders/links to other units are fine).
There is no textbook: follow the syllabus. Readers are 13–14 year olds: clear, lively, accurate Hebrew,
short paragraphs, concrete examples, but real historical depth (names, dates, causes, results).

## Output
One JSON file per unit: /home/claude/h8/data/NN.json (NN = two-digit unit number, e.g. 07.json).
Validate each file with:  python3 /home/claude/h8/tools/validate.py /home/claude/h8/data/NN.json
Fix every error it reports. Write the file with Python (json.dump(obj, f, ensure_ascii=False, indent=1))
or carefully by hand; it must be valid JSON.

IMPORTANT for Hebrew abbreviations: use the Hebrew gershayim ״ (U+05F4) and geresh ׳ (U+05F3),
NEVER the ASCII " or ' inside Hebrew text (e.g. כי״ח, ארה״ב, י״ט, המאה ה־19). Use maqaf ־ for
Hebrew prefixes before numbers/foreign words (ב־1789). Inside HTML attributes use ASCII double quotes.

## JSON schema
{
 "num": 7,                        // unit number (int)
 "slug": "french-revolution-republic-terror",   // exactly as in units.json
 "title": "…",                    // as in units.json (you may refine wording slightly)
 "short": "…",                    // ONE sentence (≤ 35 words) for the index page describing the unit
 "lead": "…",                     // 1–2 sentences under the page title
 "period": "1791–1799",           // time span label
 "main_ideas": ["…", "…", "…"],   // 3–5 short bullet phrases (topic list page)
 "sections": [                    // 4–6 sections
   {"id": "s1", "title": "…", "html": "…"}   // ids s1..s6 in order
 ],
 "mistakes": ["html", ...],       // 4–6 common misconceptions, each: the misconception + correction (1–3 sentences)
 "check": [{"q": "html", "a": "html"}, ...],  // EXACTLY 8 short check-yourself questions with short answers
 "workbook": {
   "A": [{"q": "html", "a": "html"}, ...],   // EXACTLY 10 – basic: knowledge & understanding
   "B": [ ... ],                             // EXACTLY 10 – practice: explain causes/results, compare, connect concept↔example, order events
   "C": [ ... ]                              // EXACTLY 10 – test level (school exam / higher-order thinking)
 },
 "terms": [                       // 6–14 terms that this unit DEFINES
   {"he": "נאורות", "en": "Enlightenment", "def": "1–2 sentences, grade-8 level",
    "extra": "optional: date / example / name; '' if none", "section": "s2", "area_tag": "רעיונות"}
 ]
}
area_tag is one of: "רעיונות" (ideas & concepts), "פוליטיקה ומשטר", "חברה וכלכלה", "תולדות ישראל", "אירועים ומסמכים", "אישים", "תרבות ואמנות".
Each term MUST appear in **bold** (<strong>term</strong>) in the html of the section given by "section",
where it is defined/explained (the validator checks the exact "he" string appears inside a <strong> in that section).
Include key PEOPLE (as "אישים", e.g. "מונטסקייה") and key events/documents as terms where central.

## HTML you may use inside "html" strings
Plain: <p>, <strong>, <em>, <ul>/<ol>/<li>, <h3> (sub-heading inside a section), <br> rarely.
Every paragraph of text must be wrapped in <p> (also if it starts with <strong>).
Components (classes defined by the site CSS):
- Key idea box:   <div class="key"><b>רעיון מרכזי</b><p>…</p></div>
- Timeline:       <ol class="timeline"><li><b>1789</b> <span>…event…</span></li>…</ol>
- Cause→result chain (renders as boxes with arrows): <div class="flow"><div>…</div><div>…</div><div>…</div></div>  (3–5 short steps)
- Historical source (short quotation, PUBLIC-DOMAIN documents only, your own Hebrew translation):
  <blockquote class="source"><p>«…»</p><cite>מתוך: הכרזת זכויות האדם והאזרח, 1789 (תרגום חופשי)</cite></blockquote>
- Example / "think about it" box: <div class="example"><span class="tag">דוגמה</span><p>…</p></div>  (tag may be: דוגמה / חשבו על זה / מקרה מבחן)
- Note box:       <div class="note"><strong>שימו לב:</strong> …</div>
- Table:          <div class="tablebox"><table><thead><tr><th>…</th></tr></thead><tbody><tr><td>…</td></tr></tbody></table></div>
- Compare two sides: <div class="compare"><div><h4>…</h4><p>…</p></div><div><h4>…</h4><p>…</p></div></div>
Each section should use at least one component; each unit should have at least one timeline, one table or compare,
and (where a fitting public-domain source exists) one or two short sources. Section html ≈ 150–450 words each.
Do NOT use: images, <script>, <style>, inline styles, markdown, the characters < or > as text (write "לפני"/"אחרי" or &lt; &gt;).
Links to other units are allowed: <a href="NN-slug-explanation.html">…</a> (use the slugs in units.json).

## Workbook guidance (history)
- A (basic): who/what/when, define a term in your words, match concept↔example, put 4–5 events in order,
  "complete the sentence", identify which statement is correct and explain why. Answer: full, 1–4 sentences.
- B (practice): explain a cause or a result, compare two things by 2 criteria, explain how an idea is expressed
  in an event/document, "why did … happen", short source with 1 question.
- C (test level): in the style of school tests in junior-high history — tasks with a short source
  (quoted in the question inside <blockquote class="source">) and 2–3 sub-questions (א, ב, ג);
  "express a position and support it with two arguments/evidence"; compare by criteria; evaluate significance;
  "in your opinion…" with a model answer that shows how to build an argument (claim → evidence → explanation).
  Include at least 4 source-based tasks in C. For opinion questions give a model answer AND note other legitimate positions.
- Every answer is a complete MODEL ANSWER (what a top student would write), not a hint.
  Use <p>, <ul>, and for multi-part answers <p><strong>א.</strong> …</p>.
- Check-yourself (8): quick questions, short answers (1–2 sentences).

## Accuracy & copyright
- Historical facts, names and dates must be correct. If you are unsure of a detail, leave it out rather than guess.
  Use common Hebrew spellings (רובספייר, נפוליאון, מונטסקייה, רוסו, לוק, ג׳פרסון, מנדלסון, הבעש״ט, הגר״א, הרצל, דרייפוס).
- Write original text. Quote only public-domain historical documents (≤ 3 sentences each), translated by you.
- Balanced and sensitive on Jewish history and religious streams: describe each stream's view fairly.
