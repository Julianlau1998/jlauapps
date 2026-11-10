#!/usr/bin/env python3
"""Builds the app pages of jlauapps.com from the App Store texts and screenshots.

    python3 _tools/build.py

Writes (English at the root, German under /de/):
  /index.html, /de/index.html            all apps and the contact form
  /<app>/index.html, /de/<app>/index.html  one page per app
  /imprint/, /de/impressum/, /404.html, /sitemap.xml, /robots.txt
  /assets/apps/<app>/                     icon and screenshots, resized for the web
The privacy pages (/<app>/privacy/) are left exactly as they are: App Store Connect and the
apps link to them.
"""
import datetime
import html
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from apps import APPS, ETF_TEXTS, EXTERNAL, GROUPS  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = "https://jlauapps.com"
ICONS = "/tmp/site-icons"  # 1024 px icons, collected beforehand (App Store artwork or the projects)
LANGS = ("en", "de")
SHOTS_PER_APP = 6
CONTACT_EMAIL = "jlauapps@gmail.com"
DEVELOPER_URL = "https://apps.apple.com/developer/julian-lau/id1603050262"
SAME_AS = [DEVELOPER_URL, "https://github.com/Julianlau1998", "https://yarnspace.app/"]
GUIDES_PUBLISHED = "2026-11-09"

# FAQ per app and the guide articles, written from the store texts and the apps' code.
CONTENT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "content")
with open(os.path.join(CONTENT, "faq.json")) as f:
    FAQ = json.load(f)
with open(os.path.join(CONTENT, "guides.json")) as f:
    GUIDES = json.load(f)

# Apps that aren't in the App Store yet: their page is hand-written (and left alone by this script),
# but guides can already belong to them. Their guides point to that page instead of the store.
# Once an app is out, it moves to APPS in apps.py and leaves this list.
UPCOMING = [
    dict(slug="rankpilot", accent="#5b59fa", icon="/assets/apps/rankpilot/icon.png", group="money",
         genre={"en": "SEO", "de": "SEO"}, texts={
        "en": dict(name="Rankpilot: SEO Check", subtitle="Website score & Search Console",
                   promo="Check your website’s SEO in under a minute: a score from 0 to 100, concrete fixes and your Google Search Console numbers – right on your iPhone."),
        "de": dict(name="Rankpilot: SEO-Check", subtitle="Website-Score & Search Console",
                   promo="Prüfe die SEO deiner Website in unter einer Minute: ein Score von 0 bis 100, konkrete Tipps und deine Zahlen aus der Google Search Console – direkt auf dem iPhone."),
    }),
]

UI = {
    "en": dict(
        site_title="JL Apps – Apps for iPhone, iPad & Mac by Julian Lau",
        site_description="Apps for iPhone, iPad and Mac by Julian Lau: HowlNight party games, Cardfox vocabulary flashcards, Code Editor, Python Editor, Texlet LaTeX editor, Markdown Editor, txt Editor, AdNumbers, Connect Insights, Netora salary calculator and Owlvest.",
        hero_kicker="Independent apps from Germany",
        hero_title="Apps that just work.",
        hero_text="Fast, focused apps for iPhone, iPad and Mac – for playing, learning, writing, coding and your money. No accounts, no clutter.",
        see_apps="See all apps", contact="Contact", apps="Apps",
        download="Download on the App Store", free="Free · In-app purchases",
        more_apps="More apps", privacy="Privacy Policy", imprint="Imprint",
        visit_site="Visit website", learn_more="Learn more",
        contact_title="Get in touch",
        contact_text="Questions, ideas or a problem with one of my apps? Write me – I read every message.",
        email_label="Your email", message_label="Your message", send="Send message",
        sent="Thanks! Your message is on its way – I'll get back to you soon.",
        features="Features", screenshots="Screenshots", made_by="Made by Julian Lau",
        on="for", lang_switch="Deutsch", platforms_join=", ",
        not_found_title="Page not found", not_found_text="This page doesn't exist (anymore). Here are my apps instead.",
        back_home="Back to all apps",
        facts="iPhone, iPad, Mac & Apple Watch",
        free_short="Free", get_app="Get {name}",
        faq="Frequently asked questions", guides="Guides", guides_path="guides",
        guides_title="Guides – game rules, SEO, LaTeX, Python, ETF taxes | JL Apps",
        guides_description="Free guides: party game rules, vocabulary learning, coding on iPad, LaTeX and Markdown, ETF taxes, website SEO, AdMob and App Store metrics.",
        guides_text="Rules, explanations and worked examples – free to read, with the app that does it for you.",
        guides_for="Guides for {name}", all_guides="All guides", read_guide="Read guide", more_guides="More guides",
        guide_app="The app for this", screenshot="screenshot",
        guide_label="Guide", try_in="Do it with {name}", get_short="Get", free_store="Free on the App Store",
        coming_soon="Coming soon to the App Store",
    ),
    "de": dict(
        site_title="JL Apps – Apps für iPhone, iPad & Mac von Julian Lau",
        site_description="Apps für iPhone, iPad und Mac von Julian Lau: HowlNight Partyspiele, Cardfox Vokabel-Karteikarten, Code Editor, Python Editor, Texlet LaTeX-Editor, Markdown Editor, txt Editor, AdNumbers, Connect Insights, Netora Brutto-Netto-Rechner und Owlvest.",
        hero_kicker="Unabhängige Apps aus Deutschland",
        hero_title="Apps, die einfach funktionieren.",
        hero_text="Schnelle, durchdachte Apps für iPhone, iPad und Mac – zum Spielen, Lernen, Schreiben, Programmieren und für dein Geld. Ohne Konto, ohne Ballast.",
        see_apps="Alle Apps ansehen", contact="Kontakt", apps="Apps",
        download="Laden im App Store", free="Gratis · In-App-Käufe",
        more_apps="Weitere Apps", privacy="Datenschutz", imprint="Impressum",
        visit_site="Zur Website", learn_more="Mehr erfahren",
        contact_title="Kontakt",
        contact_text="Fragen, Ideen oder ein Problem mit einer meiner Apps? Schreib mir – ich lese jede Nachricht.",
        email_label="Deine E-Mail-Adresse", message_label="Deine Nachricht", send="Nachricht senden",
        sent="Danke! Deine Nachricht ist unterwegs – ich melde mich bald.",
        features="Funktionen", screenshots="Screenshots", made_by="Entwickelt von Julian Lau",
        on="für", lang_switch="English", platforms_join=", ",
        not_found_title="Seite nicht gefunden", not_found_text="Diese Seite gibt es nicht (mehr). Hier sind stattdessen meine Apps.",
        back_home="Zu allen Apps",
        facts="iPhone, iPad, Mac & Apple Watch",
        free_short="Gratis", get_app="{name} laden",
        faq="Häufige Fragen", guides="Ratgeber", guides_path="ratgeber",
        guides_title="Ratgeber – Spielregeln, SEO, LaTeX, Python, ETF | JL Apps",
        guides_description="Kostenlose Ratgeber: Partyspiel-Regeln, Vokabeln lernen, Programmieren auf dem iPad, LaTeX und Markdown, ETF-Steuern, Website-SEO, AdMob, App Store.",
        guides_text="Regeln, Erklärungen und Rechenbeispiele – kostenlos zum Nachlesen, mit der passenden App dazu.",
        guides_for="Ratgeber zu {name}", all_guides="Alle Ratgeber", read_guide="Zum Ratgeber", more_guides="Weitere Ratgeber",
        guide_app="Die passende App", screenshot="Screenshot",
        guide_label="Ratgeber", try_in="Mit {name} geht's einfacher", get_short="Laden", free_store="Gratis im App Store",
        coming_soon="Bald im App Store",
    ),
}

BOILERPLATE = re.compile(
    r"(Die Zahlung erfolgt|Payment is charged|Nutzungsbedingungen:|Terms of Use:|Datenschutz:|Privacy Policy:|"
    r"Datenschutzerklärung:|EULA|verlängern sich automatisch|renew automatically)", re.I)


# ---------------------------------------------------------------- texts

def store_texts(path):
    """Name, subtitle, promo, keywords and description per language from an App Store Texte.md."""
    source = open(path).read()
    result = {}
    sections = re.split(r"\n## ", "\n" + source)
    for section in sections:
        head = section.split("\n", 1)[0].lower()
        lang = "de" if head.startswith("deutsch") else "en" if head.startswith(("englisch", "english")) else None
        if not lang or lang in result:
            continue
        result[lang] = dict(
            name=field(section, ("Name",)),
            subtitle=field(section, ("Untertitel", "Subtitle")),
            promo=field(section, ("Werbetext", "Promotional Text")),
            keywords=field(section, ("Schlüsselwörter", "Keywords")),
            description=field(section, ("Beschreibung", "Description")),
        )
    return result


def field(section, labels):
    for label in labels:
        # "### Label (n/30 Zeichen)" followed by a fenced block …
        m = re.search(r"### " + re.escape(label) + r"\b[^\n]*\n+```[a-z]*\n(.*?)```", section, re.S)
        if m:
            return m.group(1).strip()
        # … or "**Label (30):** value" / "**Label (4000):**\n\nvalue" up to the next bold label.
        m = re.search(r"\*\*" + re.escape(label) + r"\b[^*]*\*\*[ \t]*(.*?)(?=\n\*\*[A-ZÄÖÜ][^*\n]*\*\*|\n---|\Z)", section, re.S)
        if m:
            return m.group(1).strip()
    return ""


def parse_description(text):
    """Intro paragraphs and sections (UPPERCASE heading, paragraphs, bullets) of a store description."""
    intro, sections, current = [], [], None
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = [line.rstrip() for line in block.strip().split("\n") if line.strip()]
        if not lines or BOILERPLATE.search(lines[0]):
            continue
        first = lines[0]
        letters = re.sub(r"[^A-Za-zÄÖÜäöüß]", "", first)
        if letters and letters.upper() == letters and len(first) < 60 and not first.startswith("•"):
            current = dict(title=first, items=[], text=[], blocks=[])
            sections.append(current)
            lines = lines[1:]
        for line in lines:
            if BOILERPLATE.search(line):
                continue
            target = current if current else None
            if line.startswith(("•", "-", "–")):
                item = line.lstrip("•-– ").strip()
                (target["items"] if target else intro).append(item)
                if target:
                    target["blocks"].append(("li", item))
            elif target:
                target["text"].append(line)
                target["blocks"].append(("p", line))
            else:
                intro.append(line)
    return intro, sections


def nice_title(title, lang):
    """UPPERCASE store headings → readable headings (keeps brand words)."""
    words = title.split()
    keep = {"AI", "KI", "PRO", "LIVE", "PDF", "PNG", "HTML", "CSS", "JS", "CSV", "ETF", "FSRS", "API", "IOS", "IPAD", "MAC"}
    out = []
    for i, word in enumerate(words):
        bare = re.sub(r"[^A-Za-zÄÖÜ]", "", word.upper())
        if bare in keep:
            out.append(word.upper().replace("IPAD", "iPad").replace("IOS", "iOS").replace("MAC", "Mac"))
        elif i == 0 or lang == "de":
            out.append(word.capitalize())
        else:
            out.append(word.lower() if word.lower() in {"and", "or", "the", "a", "of", "for", "to", "in", "on", "with", "at", "your"} else word.capitalize())
    text = " ".join(out)
    for brand in ("Cardfox", "HowlNight", "AdNumbers", "Texlet", "Python", "Jupyter", "Markdown", "LaTeX", "AdMob", "AdSense", "Apple Watch", "Apple Intelligence", "Siri", "iCloud"):
        text = re.sub(re.escape(brand), brand, text, flags=re.I)
    return text


def app_texts(app):
    if app["texts"] is None:
        return ETF_TEXTS
    return store_texts(app["texts"])


def platforms(description, lang):
    items = ["iPhone", "iPad"]
    if re.search(r"\bMac\b", description):
        items.append("Mac")
    if "Apple Watch" in description:
        items.append("Apple Watch")
    return items


# ---------------------------------------------------------------- images

def max_side(path):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", path], capture_output=True, text=True).stdout
    return max([int(n) for n in re.findall(r"pixel(?:Width|Height): (\d+)", out)] or [0])


# Screenshots are shown up to ~340 pt wide, so they need ~700 px for Retina screens (640 px tall was blurry).
SHOT_SIZE = 1400


def resize(src, dst, width, fmt="jpeg", quality=82):
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src) and max_side(dst) == min(width, max_side(src)) \
            and (fmt != "jpeg" or os.path.exists(dst[:-4] + ".webp")):
        return
    args = ["sips", "-Z", str(width), src, "--out", dst]
    if fmt == "jpeg":
        args = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(quality), "-Z", str(width), src, "--out", dst]
    subprocess.run(args, check=True, capture_output=True)
    if fmt == "jpeg":
        # A WebP copy for browsers that take it (about a third smaller).
        subprocess.run(["cwebp", "-quiet", "-q", "80", dst, "-o", dst[:-4] + ".webp"], check=True, capture_output=True)


def app_images(app):
    """Icon and up to SHOTS_PER_APP screenshots per language, as web-sized files. Returns their URLs."""
    slug = app["slug"]
    folder = os.path.join(ROOT, "assets", "apps", slug)
    resize(os.path.join(ICONS, f"{slug}.png"), os.path.join(folder, "icon.png"), 256, fmt="png")
    resize(os.path.join(ICONS, f"{slug}.png"), os.path.join(folder, "icon-512.png"), 512, fmt="png")
    shots = {}
    if not os.path.isdir(app["shots"]):
        # Source screenshots moved or deleted: keep the web-sized copies from an earlier build.
        built = sorted(os.listdir(folder))
        for lang in LANGS:
            own = [n for n in built if n.startswith(f"{lang}-") and n.endswith(".jpg")]
            own = own or [n for n in built if n.startswith("en-") and n.endswith(".jpg")]
            shots[lang] = [f"/assets/apps/{slug}/{n}" for n in own[:SHOTS_PER_APP]]
        return f"/assets/apps/{slug}/icon.png", shots
    names = sorted(os.listdir(app["shots"]))
    for lang in LANGS:
        own = [n for n in names if n.startswith(f"{lang}-") and n.endswith(".png")]
        if not own:  # only English screenshots (ETF Calculator) or unprefixed names
            own = [n for n in names if n.startswith("en-") and n.endswith(".png")] or [n for n in names if n.endswith(".png")]
        urls = []
        for index, name in enumerate(own[:SHOTS_PER_APP], start=1):
            target_lang = lang if name.startswith(f"{lang}-") else "en"
            target = os.path.join(folder, f"{target_lang}-{index}.jpg")
            resize(os.path.join(app["shots"], name), target, SHOT_SIZE)
            urls.append(f"/assets/apps/{slug}/{target_lang}-{index}.jpg")
        shots[lang] = urls
    return f"/assets/apps/{slug}/icon.png", shots


def external_icon(item):
    slug = item["slug"]
    resize(os.path.join(ICONS, f"{slug}.png"), os.path.join(ROOT, "assets", "apps", slug, "icon.png"), 256, fmt="png")
    return f"/assets/apps/{slug}/icon.png"


def external_shot(item):
    """An app with its own website: one screenshot per language for the home page."""
    urls = {}
    for lang in LANGS:
        src = item.get("shot", "").format(lang=lang)
        target = os.path.join(ROOT, "assets", "apps", item["slug"], f"{lang}-1.jpg")
        if src and os.path.exists(src):
            resize(src, target, SHOT_SIZE)
        urls[lang] = f"/assets/apps/{item['slug']}/{lang}-1.jpg" if os.path.exists(target) else None
    return urls


# ---------------------------------------------------------------- page parts

def e(text):
    return html.escape(text, quote=True)


def picture(url, attrs):
    """An <img> with its WebP twin as <source>, when there is one (CSS treats <picture> as transparent)."""
    img = f'<img src="{url}" {attrs}>'
    if url.endswith(".jpg") and os.path.exists(os.path.join(ROOT, url.lstrip("/")[:-4] + ".webp")):
        return f'<picture><source srcset="{url[:-4]}.webp" type="image/webp">{img}</picture>'
    return img


def faq_ld(items):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": x["q"], "acceptedAnswer": {"@type": "Answer", "text": x["a"]}} for x in items]}


def faq_section(items, title):
    if not items:
        return ""
    entries = "".join(f'<details><summary>{e(x["q"])}</summary><p>{e(x["a"])}</p></details>' for x in items)
    return f'<section class="faq"><h2>{e(title)}</h2><div class="faq-list">{entries}</div></section>'


def guide_path(lang, slug=""):
    return path_for(lang, UI[lang]["guides_path"]) + (f"{slug}/" if slug else "")


def guide_app(guide):
    """The app a guide belongs to: one in the App Store or an upcoming one."""
    return next(a for a in APPS + UPCOMING if a["slug"] == guide["app"])


def large_icon(app):
    """The 512 px icon when there is one (upcoming apps only have their page's 256 px icon)."""
    url = f"/assets/apps/{app['slug']}/icon-512.png"
    return url if os.path.exists(os.path.join(ROOT, url.lstrip("/"))) else app.get("icon", url)


GUIDE_LINK = re.compile(r"\[([^\]]+)\]\(((?:/guides/|/de/ratgeber/)[a-z0-9-]+/)\)")


def guide_card(guide, lang, data):
    g = guide[lang]
    app = guide_app(guide)
    return f"""<a class="guide-card" href="{guide_path(lang, guide["slug"][lang])}" style="--accent:{app["accent"]}">
  <span class="genre"><img src="{data[app["slug"]]["icon"]}" alt="" width="22" height="22" loading="lazy">{e(short_name(data[app["slug"]]["texts"][lang]["name"]))}</span>
  <h3>{e(g["h1"])}</h3>
  <p>{e(g["description"])}</p>
  <span class="more-link">{UI[lang]["read_guide"]} →</span>
</a>"""


def path_for(lang, slug=""):
    base = "/" if lang == "en" else "/de/"
    return base + (f"{slug}/" if slug else "")


def head(lang, title, description, canonical_path, alternates, extra="", image=None, keywords=""):
    tags = [
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        f"<title>{e(title)}</title>",
        f'<meta name="description" content="{e(description)}">',
    ]
    if keywords:
        tags.append(f'<meta name="keywords" content="{e(keywords)}">')
    tags += [
        f'<link rel="canonical" href="{SITE}{canonical_path}">',
        *[f'<link rel="alternate" hreflang="{code}" href="{SITE}{href}">' for code, href in alternates],
        '<meta name="theme-color" content="#0b0a16">',
        '<meta name="color-scheme" content="dark">',
        '<link rel="icon" type="image/png" href="/favicon.png">',
        '<link rel="icon" type="image/svg+xml" href="/assets/logo.svg">',
        '<link rel="apple-touch-icon" href="/apple-touch-icon.png">',
        '<link rel="stylesheet" href="/assets/site.css">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(description)}">',
        f'<meta property="og:url" content="{SITE}{canonical_path}">',
        f'<meta property="og:locale" content="{"de_DE" if lang == "de" else "en_US"}">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if image:
        tags.append(f'<meta property="og:image" content="{SITE}{image}">')
        if image.startswith("/assets/og/"):
            tags += ['<meta property="og:image:width" content="1200">', '<meta property="og:image:height" content="630">']
    return "<head>\n" + "\n".join(tags) + ("\n" + extra if extra else "") + "\n</head>"


def header(lang, alternate_path):
    t = UI[lang]
    home = path_for(lang)
    other = "de" if lang == "en" else "en"
    return f"""<header class="topbar">
  <a class="brand" href="{home}" aria-label="JL Apps"><img src="/assets/logo.svg" alt="" width="34" height="34"><span>JL Apps</span></a>
  <nav>
    <a href="{home}#apps">{t["apps"]}</a>
    <a href="{guide_path(lang)}">{t["guides"]}</a>
    <a href="{home}#contact">{t["contact"]}</a>
    <a class="lang" href="{alternate_path}" hreflang="{other}" lang="{other}">{t["lang_switch"]}</a>
  </nav>
</header>"""


def footer(lang, privacy_path=None):
    t = UI[lang]
    year = datetime.date.today().year
    imprint = "/imprint/" if lang == "en" else "/de/impressum/"
    privacy = f'<a href="{privacy_path}">{t["privacy"]}</a>' if privacy_path else ""
    return f"""<footer class="footer">
  <div><img src="/assets/logo.svg" alt="" width="28" height="28"><span>© {year} Julian Lau</span></div>
  <nav>{privacy}<a href="{path_for(lang)}#contact">{t["contact"]}</a><a href="{imprint}">{t["imprint"]}</a><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></nav>
</footer>"""


def store_url(app, lang):
    return f"https://apps.apple.com/{'de' if lang == 'de' else 'us'}/app/id{app['id']}"


def app_card(app, lang, data):
    texts = data["texts"][lang]
    blurb = texts["promo"] or first_sentence(texts["description"])
    return f"""<a class="app-card" href="{path_for(lang, app["slug"])}" style="--accent:{app["accent"]}">
  <img class="app-icon" src="{data["icon"]}" alt="{e(short_name(texts["name"]))} app icon" width="88" height="88" loading="lazy">
  <div>
    <span class="genre">{e(app["genre"][lang])}</span>
    <h3>{e(short_name(texts["name"]))}</h3>
    <p class="subtitle">{e(texts["subtitle"])}</p>
    <p class="blurb">{e(blurb)}</p>
    <span class="more-link">{UI[lang]["learn_more"]} →</span>
  </div>
</a>"""


def external_card(item, lang, icon):
    return f"""<a class="app-card" href="{item["url"]}" style="--accent:{item["accent"]}">
  <img class="app-icon" src="{icon}" alt="{e(item["name"][lang])} app icon" width="88" height="88" loading="lazy">
  <div>
    <span class="genre">{"Craft" if lang == "en" else "Handarbeit"} · yarnspace.app ↗</span>
    <h3>{e(item["name"][lang])}</h3>
    <p class="subtitle">{e(item["subtitle"][lang])}</p>
    <p class="blurb">{e(item["blurb"][lang])}</p>
    <span class="more-link">{UI[lang]["visit_site"]} ↗</span>
  </div>
</a>"""


def upcoming_card(app, lang):
    """Card for an app that isn't in the App Store yet; links to its own page."""
    texts = app["texts"][lang]
    soon = "Coming soon" if lang == "en" else "Bald verfügbar"
    return f"""<a class="app-card" href="{path_for(lang, app["slug"])}" style="--accent:{app["accent"]}">
  <img class="app-icon" src="{app["icon"]}" alt="{e(short_name(texts["name"]))} app icon" width="88" height="88" loading="lazy">
  <div>
    <span class="genre">{e(app["genre"][lang])} · {soon}</span>
    <h3>{e(short_name(texts["name"]))}</h3>
    <p class="subtitle">{e(texts["subtitle"])}</p>
    <p class="blurb">{e(texts["promo"])}</p>
    <span class="more-link">{UI[lang]["learn_more"]} →</span>
  </div>
</a>"""


def short_name(name):
    """"Cardfox: Vocabulary Cards" → "Cardfox"; names without a colon stay."""
    for sep in (":", " - ", " – "):
        if sep in name:
            return name.split(sep)[0].strip()
    return name


def first_sentence(text):
    m = re.match(r"(.+?[.!?])(\s|$)", text.strip().replace("\n", " "))
    return m.group(1) if m else text[:160]


def contact_form(lang):
    t = UI[lang]
    next_url = f"{SITE}{path_for(lang)}?sent=1#contact"
    return f"""<section class="contact" id="contact">
  <div class="contact-text">
    <h2>{t["contact_title"]}</h2>
    <p>{t["contact_text"]}</p>
    <p class="mail"><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
    <p class="sent" hidden>{t["sent"]}</p>
  </div>
  <form action="https://formsubmit.co/{CONTACT_EMAIL}" method="POST">
    <input type="hidden" name="_captcha" value="false">
    <input type="hidden" name="_next" value="{next_url}">
    <input type="hidden" name="_subject" value="JL Apps – {"new message" if lang == "en" else "neue Nachricht"}">
    <input type="text" name="_honey" class="honey" tabindex="-1" autocomplete="off" aria-hidden="true">
    <label>{t["email_label"]}<input type="email" name="email" required autocomplete="email"></label>
    <label>{t["message_label"]}<textarea name="Email Text" rows="6" required></textarea></label>
    <button type="submit" class="button">{t["send"]}</button>
  </form>
</section>
<script>if (location.search.includes("sent=1")) document.querySelector(".sent").hidden = false;</script>"""


def write(path, content):
    full = os.path.join(ROOT, path.lstrip("/"), "index.html") if not path.endswith(".html") else os.path.join(ROOT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    # Unchanged pages keep their file date, which the sitemap reports as the last change.
    if os.path.exists(full) and open(full).read() == content:
        return
    with open(full, "w") as f:
        f.write(content)


# Gallery arrows scroll by one screenshot; the edges fade only where there's more to see,
# and the arrows hide when everything fits.
GALLERY_JS = """(() => {
  const section = document.querySelector(".gallery-section"), strip = section && section.querySelector(".gallery");
  if (!strip) return;
  const update = () => {
    const max = strip.scrollWidth - strip.clientWidth;
    section.classList.toggle("scrollable", max > 4);
    section.classList.toggle("at-start", strip.scrollLeft < 4);
    section.classList.toggle("at-end", strip.scrollLeft > max - 4);
  };
  const step = dir => {
    const img = strip.querySelector("img");
    strip.scrollBy({ left: dir * (img ? img.offsetWidth + 22 : 300), behavior: "smooth" });
  };
  section.querySelector(".prev").onclick = () => step(-1);
  section.querySelector(".next").onclick = () => step(1);
  strip.addEventListener("scroll", update, { passive: true });
  addEventListener("resize", update);
  addEventListener("load", update);
  update();
})();"""


def page(lang, head_html, body, accent="#8b5cf6", body_class=""):
    return f"""<!doctype html>
<html lang="{lang}">
{head_html}
<body class="{body_class}" style="--accent:{accent}">
{body}
</body>
</html>
"""


# ---------------------------------------------------------------- pages

def home(lang, data, external_icons, external_shots):
    t = UI[lang]
    groups = ""
    for key, label in GROUPS.items():
        cards = [app_card(app, lang, data[app["slug"]]) for app in APPS if app["group"] == key]
        cards += [external_card(item, lang, external_icons[item["slug"]]) for item in EXTERNAL if item["group"] == key]
        cards += [upcoming_card(app, lang) for app in UPCOMING if app.get("group") == key]
        groups += f'<section class="group"><h2>{label[lang]}</h2><div class="grid">{"".join(cards)}</div></section>\n'

    # YarnSpace on the left (where Cardfox was), HowlNight big in the middle, Owlvest on the right.
    shots = [external_shots["yarnspace"][lang], data["howlnight"]["shots"][lang][0], (data["etf-calculator"]["shots"][lang] or [None])[0]]
    showcase = "".join(f'<img src="{u}" alt="" loading="lazy" width="320" height="695">' for u in shots if u)
    items = [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}{path_for(lang, app['slug'])}",
              "name": short_name(data[app["slug"]]["texts"][lang]["name"])} for i, app in enumerate(APPS)]
    ld = [
        {"@context": "https://schema.org", "@type": "Person", "name": "Julian Lau", "url": SITE + "/",
         "email": CONTACT_EMAIL, "address": {"@type": "PostalAddress", "addressCountry": "DE"}, "sameAs": SAME_AS},
        {"@context": "https://schema.org", "@type": "ItemList", "name": t["apps"], "itemListElement": items},
    ]
    extra = "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    alternates = [("en", "/"), ("de", "/de/"), ("x-default", "/")]
    body = f"""{header(lang, path_for("de" if lang == "en" else "en"))}
<main>
  <section class="hero home-hero">
    <div class="hero-text">
      <p class="kicker">{t["hero_kicker"]}</p>
      <h1>{t["hero_title"]}</h1>
      <p class="lead">{t["hero_text"]}</p>
      <div class="actions"><a class="button" href="#apps">{t["see_apps"]}</a><a class="button ghost" href="#contact">{t["contact"]}</a></div>
      <p class="facts">{t["facts"]}</p>
    </div>
    <div class="showcase" aria-hidden="true">{showcase}</div>
  </section>
  <div id="apps" class="apps">{groups}</div>
  <section class="guides-block home-guides"><h2>{t["guides"]}</h2><div class="guide-grid">{"".join(guide_card(g, lang, data) for g in home_guides())}</div>
    <p><a class="text-link" href="{guide_path(lang)}">{t["all_guides"]} →</a></p></section>
  {contact_form(lang)}
</main>
{footer(lang)}"""
    write(path_for(lang), page(lang, head(lang, t["site_title"], t["site_description"], path_for(lang), alternates,
                                          extra=extra, image=data["howlnight"]["shots"][lang][0]), body, body_class="home"))


def feature_screen(app, lang, index):
    """The plain app screen (without the store caption) shown with a feature, from the app's raw
    captures; None when there's none for this feature in this language."""
    name = app.get("feature_screens", {}).get(index)
    src = os.path.join(os.path.dirname(app["shots"]), "raw", f"{lang}-iphone-{name}.png")
    if not name or not os.path.exists(src):
        return None
    resize(src, os.path.join(ROOT, "assets", "apps", app["slug"], f"screen-{lang}-{name}.jpg"), 1520)
    return f"/assets/apps/{app['slug']}/screen-{lang}-{name}.jpg"


def pack_features(features, columns=3):
    """Lays the tiles out in rows of three columns, in the store's order, without holes: a long tile
    takes two columns, and when a row would end with a free column, the longest tile in it grows
    into it (a long tile that doesn't fit any more starts the next row)."""
    rows, row = [], []
    for feature in features:
        if sum(f["span"] for f in row) + feature["span"] > columns:
            rows.append(row)
            row = []
        row.append(feature)
    if row:
        rows.append(row)
    for row in rows:
        free = columns - sum(f["span"] for f in row)
        if free:
            max(row, key=lambda f: f["weight"] / f["span"])["span"] += free
    return [f for row in rows for f in row]


def app_page(app, lang, data):
    t = UI[lang]
    d = data[app["slug"]]
    texts = d["texts"][lang]
    name = texts["name"]
    short = short_name(name)
    intro, sections = parse_description(texts["description"])
    plats = platforms(texts["description"], lang)
    # Name and subtitle, like in the App Store – short enough for search results (~60 characters).
    title = f"{name} – {texts['subtitle']}"
    description = texts["promo"] or first_sentence(texts["description"])
    description = description if len(description) <= 160 else description[:157].rsplit(" ", 1)[0] + "…"
    privacy = f"/{app['slug']}/privacy/"
    other = "de" if lang == "en" else "en"
    alternates = [("en", path_for("en", app["slug"])), ("de", path_for("de", app["slug"])), ("x-default", path_for("en", app["slug"]))]

    ld = {
        "@context": "https://schema.org", "@type": "SoftwareApplication", "name": short,
        "alternateName": name, "description": description, "applicationCategory": app["category"],
        "operatingSystem": ", ".join({"iPhone": "iOS", "iPad": "iPadOS", "Mac": "macOS", "Apple Watch": "watchOS"}[p] for p in plats),
        "url": f"{SITE}{path_for(lang, app['slug'])}", "downloadUrl": store_url(app, lang),
        "image": f"{SITE}/assets/apps/{app['slug']}/icon-512.png", "screenshot": [f"{SITE}{u}" for u in d["shots"][lang]],
        "inLanguage": lang, "author": {"@type": "Person", "name": "Julian Lau", "url": SITE + "/", "sameAs": SAME_AS},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR" if lang == "de" else "USD"},
    }
    faq = FAQ.get(app["slug"], {}).get(lang, [])
    extra = (f'<meta name="apple-itunes-app" content="app-id={app["id"]}">\n'
             f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>'
             + (f'\n<script type="application/ld+json">{json.dumps(faq_ld(faq), ensure_ascii=False)}</script>' if faq else ""))
    guides = [g for g in GUIDES if g["app"] == app["slug"]]
    guide_cards = "".join(guide_card(g, lang, data) for g in guides)

    # Tiles read row by row in the store's order (in columns they read top to bottom and looked
    # random; as a plain list without tiles they looked bare); tiles with many points are twice
    # as wide, so a row's tiles stay about as tall. The Pro section as an offer
    # card of its own below, its text in the store's order with the perks as a checklist (the
    # download follows right after it, in the closing card).
    features, pro_card = [], ""
    for index, section in enumerate(sections):
        is_pro = re.search(r"\bPRO\b|PREMIUM|PLUS\b", section["title"]) is not None
        body, bullets, foot = "", [], ""
        for kind, value in section["blocks"] + [("end", "")]:
            if kind == "li":
                bullets.append(value)
                continue
            if bullets:
                body += f'<ul class="{"checks" if is_pro else ""}">' + "".join(f"<li>{e(b)}</li>" for b in bullets) + "</ul>"
                bullets = []
            if kind == "p":
                # In the Pro card the text after the checklist (plans, trial) goes into the footer strip.
                if is_pro and "<ul" in body:
                    foot += f"<p>{e(value)}</p>"
                else:
                    body += f"<p>{e(value)}</p>"
        if is_pro:
            # With a checklist: intro on the left, the perks in a dark panel on the right.
            pro_head = f'<div class="pro-head"><span class="pro-badge">PRO</span><h3>{e(section["title"])}</h3></div>'
            lists = "".join(re.findall(r"<ul.*?</ul>", body, re.S))
            if lists:
                pro_intro = re.sub(r"<ul.*?</ul>", "", body, flags=re.S)
                inner = f'<div class="pro-main">{pro_head}{pro_intro}</div><div class="pro-perks">{lists}</div>'
            else:
                inner = pro_head + body
            pro_card += (f'<article class="pro-card{" split" if lists else ""}">{inner}'
                         f'{f"<div class=pro-foot>{foot}</div>" if foot else ""}</article>')
        else:
            # Rough height of the tile's text: characters plus a line's worth per bullet point.
            weight = sum(len(x) for x in section["text"]) + 70 * len(section["items"])
            features.append(dict(title=section["title"], body=body, weight=weight, span=2 if weight > 320 else 1,
                                 screen=feature_screen(app, lang, index)))
    # Features with an app screen first, two cards per row, the screen rising out of the card's
    # bottom edge (an even number of them, so no row is half empty); the rest as tiles below.
    showcase = [f for f in features if f["screen"]]
    showcase = showcase[:len(showcase) // 2 * 2]
    showcase_cards = ""
    for f in showcase:
        screen = picture(f["screen"], f'alt="{e(short)} – {e(f["title"].title())}" loading="lazy" width="700" height="1521"')
        showcase_cards += (f'<article class="feature shot"><h3>{e(f["title"])}</h3><div class="feature-body">{f["body"]}</div>'
                           f'<div class="rise"><div class="device">{screen}</div></div></article>')
    feature_rows = "".join(
        f'<article class="feature span-{f["span"]}"><h3>{e(f["title"])}</h3><div class="feature-body">{f["body"]}</div></article>'
        for f in pack_features([f for f in features if f not in showcase]))
    intro_html = "".join(f"<p>{e(p)}</p>" for p in intro if not p.startswith("•"))
    intro_bullets = [p for p in intro if p not in intro_html]

    shots = d["shots"][lang]
    # Not the first one again: it's the big one beside the title.
    gallery = "".join(
        picture(u, f'alt="{e(name)} – {t["screenshot"]} {i}" loading="lazy" width="320" height="695"')
        for i, u in enumerate(shots[1:], start=2))
    # The first screenshot big in the hero, the next two fanned out behind it.
    hero_shots = "".join(picture(shots[i], f'class="{c}" alt="{e(name)} – {t["screenshot"]} {i + 1}" width="320" height="695"')
                         for c, i in (("left", 1), ("middle", 0), ("right", 2))) if len(shots) >= 3 else (
        picture(shots[0], f'alt="{e(name)}" width="320" height="695"') if shots else "")
    chips = "".join(f'<span class="chip">{e(p)}</span>' for p in plats) + f'<span class="chip">{t["free_short"]}</span>'
    others = "".join(app_card(a, lang, data[a["slug"]]) for a in APPS if a["slug"] != app["slug"])

    body = f"""{header(lang, path_for(other, app["slug"]))}
<main>
  <section class="hero app-hero">
    <div class="hero-text">
      <img class="hero-icon" src="{d["icon"]}" alt="{e(short)} app icon" width="112" height="112">
      <p class="kicker">{e(app["genre"][lang])}</p>
      <h1>{e(name)}</h1>
      <p class="lead strong">{e(texts["subtitle"])}</p>
      {intro_html}
      <div class="actions">
        <a class="store-badge" href="{store_url(app, lang)}" rel="noopener">{store_badge(lang, t["download"])}</a>
      </div>
      <div class="chips" aria-label="{t["on"]}">{chips}</div>
    </div>
    <div class="phone{" fan" if len(shots) >= 3 else ""}">{hero_shots}</div>
  </section>

  <section class="gallery-section at-start" aria-label="{t["screenshots"]}">
    <div class="gallery-arrows"><button type="button" class="prev" aria-label="‹">‹</button><button type="button" class="next" aria-label="›">›</button></div>
    <div class="gallery">{gallery}</div>
  </section>
  <script>{GALLERY_JS}</script>

  <section class="features">
    <h2>{t["features"]}</h2>
    {f'<div class="feature-showcase">{showcase_cards}</div>' if showcase_cards else ""}
    <div class="feature-grid">{feature_rows}</div>
    {pro_card}
  </section>

  {faq_section(faq, t["faq"])}
  {f'<section class="guides-block"><h2>{e(t["guides_for"].format(name=short))}</h2><div class="guide-grid">{guide_cards}</div></section>' if guide_cards else ""}

  <section class="cta">
    <img src="{d["icon"]}" alt="" width="72" height="72" loading="lazy">
    <h2>{e(t["get_app"].format(name=short))}</h2>
    <p>{e(texts["promo"] or texts["subtitle"])}</p>
    <a class="store-badge" href="{store_url(app, lang)}" rel="noopener">{store_badge(lang, t["download"])}</a>
    <p class="fine">{t["free"]}</p>
  </section>

  <section class="group more"><h2>{t["more_apps"]}</h2><div class="grid">{others}</div></section>
</main>
{footer(lang, privacy)}"""
    write(path_for(lang, app["slug"]),
          page(lang, head(lang, title, description, path_for(lang, app["slug"]), alternates, extra=extra,
                          image=shots[0] if shots else None, keywords=texts["keywords"]),
               body, accent=app["accent"], body_class="app"))


def store_badge(lang, label):
    """Apple's official "Download on the App Store" badge in the page's language (same artwork as yarnspace.app)."""
    file = "badge-de-de.svg" if lang == "de" else "badge-en-us.svg"
    return f'<img src="/assets/badges/{file}" width="162" height="54" alt="{label}">'


def cell(text):
    """A table cell; one wrapped in backticks is shown as code (LaTeX/Markdown syntax in the cheat sheets)."""
    if len(text) > 1 and text.startswith("`") and text.endswith("`"):
        return f"<code>{e(text[1:-1])}</code>"
    return e(text)


def home_guides(count=6):
    """The first guide of each app, in the apps' order, for the home page."""
    firsts = [next(g for g in GUIDES if g["app"] == app["slug"]) for app in APPS + UPCOMING if any(g["app"] == app["slug"] for g in GUIDES)]
    return firsts[:count]


SNAP = os.path.expanduser("~/Documents/StoreScreenshots HowlNight/tools/snap")  # WKWebView → PNG, 2× scale


def guide_screen(guide, lang, app):
    """The app screen for a guide's share image: the one named in the guide's slug, else the app's first."""
    screens = list(app.get("feature_screens", {}).values())
    named = [n for n in screens if n.split("-")[0] in guide["slug"]["en"]] + screens
    for name in named:
        url = f"/assets/apps/{app['slug']}/screen-{lang}-{name}.jpg"
        if os.path.exists(os.path.join(ROOT, url.lstrip("/"))):
            return url
    return None


def og_image(guide, lang, data):
    """A 1200 × 630 share image: the title on the left, the app screen in a phone frame on the right
    (title only for apps without a screen). Rendered once and again only when its content changes."""
    app = guide_app(guide)
    # "Markdown Editor and Reader" is too long for the label line.
    short = re.split(r" and | und ", short_name(data[app["slug"]]["texts"][lang]["name"]))[0]
    screen = guide_screen(guide, lang, app)
    url = f"/assets/og/{lang}-{guide['slug'][lang]}.jpg"
    target = os.path.join(ROOT, url.lstrip("/"))
    if not os.path.exists(SNAP):
        return url if os.path.exists(target) else large_icon(app)
    local = lambda u: "file://" + os.path.join(ROOT, u.lstrip("/"))
    accent = app["accent"]
    phone = (f'<div class="phone"><img src="{local(screen)}"></div>' if screen else "")
    doc = f"""<!doctype html><html><head><meta charset="utf-8"><style>
body {{ margin: 0; width: 600px; height: 315px; overflow: hidden; color: #f4f2ff; font-family: -apple-system, "SF Pro Display", sans-serif;
  background: radial-gradient(420px 260px at 85% -10%, color-mix(in srgb, {accent} 55%, transparent), transparent 70%),
              radial-gradient(300px 200px at 0% 100%, rgba(91,70,220,.25), transparent 70%), #0b0a16; }}
.text {{ padding: 40px 0 0 40px; width: {350 if screen else 520}px; }}
.k {{ display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 14px; letter-spacing: .06em; text-transform: uppercase;
  color: color-mix(in srgb, {accent} 55%, white); }}
.k img {{ width: 34px; height: 34px; border-radius: 9px; }}
h1 {{ margin: 16px 0 0; font-size: {34 if screen else 40}px; line-height: 1.08; letter-spacing: -.02em; font-weight: 800; text-wrap: balance; }}
.f {{ position: absolute; left: 40px; bottom: 28px; display: flex; align-items: center; gap: 8px; font-size: 14px; color: #b7b2d6; font-weight: 600; }}
.f img {{ width: 22px; height: 22px; }}
.phone {{ position: absolute; right: 40px; top: 34px; width: 170px; padding: 6px 6px 0; border-radius: 30px 30px 0 0;
  background: linear-gradient(160deg, #3a3550, #16141f); box-shadow: 0 20px 60px rgba(0,0,0,.6); }}
.phone img {{ width: 100%; display: block; border-radius: 24px 24px 0 0; }}
</style></head><body>
<div class="text"><div class="k"><img src="{local(data[app["slug"]]["icon"])}">{e(short)} · {UI[lang]["guide_label"]}</div><h1>{e(guide[lang]["h1"])}</h1></div>
<div class="f"><img src="{local("/assets/logo.svg")}">jlauapps.com</div>{phone}
</body></html>"""
    stamp = target + ".src"
    if os.path.exists(target) and os.path.exists(stamp) and open(stamp).read() == doc:
        return url
    os.makedirs(os.path.dirname(target), exist_ok=True)
    tmp_html, tmp_png = f"/tmp/jl-og-{lang}-{guide['slug'][lang]}.html", f"/tmp/jl-og-{lang}-{guide['slug'][lang]}.png"
    with open(tmp_html, "w") as f:
        f.write(doc)
    subprocess.run([SNAP, tmp_html, "600", "315", tmp_png], check=True, capture_output=True)
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", tmp_png, "--out", target], check=True, capture_output=True)
    os.remove(tmp_html)
    os.remove(tmp_png)
    with open(stamp, "w") as f:
        f.write(doc)
    return url


def guide_page(guide, lang, data):
    t = UI[lang]
    g = guide[lang]
    other = "de" if lang == "en" else "en"
    app = guide_app(guide)
    upcoming = app in UPCOMING
    d = data[app["slug"]]
    texts = d["texts"][lang]
    short = short_name(texts["name"])
    path = guide_path(lang, guide["slug"][lang])
    alternates = [("en", guide_path("en", guide["slug"]["en"])), ("de", guide_path("de", guide["slug"]["de"])),
                  ("x-default", guide_path("en", guide["slug"]["en"]))]

    app_url = path_for(lang, app["slug"])
    linked = False

    def text(value):
        """Escaped text; the first mention of the app in the article links to its page."""
        nonlocal linked
        out = e(value)
        if not linked:
            # "Markdown Editor and Reader" is written as "Markdown Editor" in the articles.
            for mention in (short, re.split(r" and | und ", short)[0]):
                if e(mention) in out:
                    out = out.replace(e(mention), f'<a class="app-mention" href="{app_url}">{e(mention)}</a>', 1)
                    linked = True
                    break
        # [label](/guides/<slug>/) links to another guide.
        return GUIDE_LINK.sub(r'<a href="\2">\1</a>', out)

    intro = "".join(f"<p>{text(p)}</p>" for p in g["intro"].split("\n\n") if p.strip())
    # Not in the store yet: the button leads to the app's own page instead.
    badge = (f'<a class="button" href="{app_url}">{t["coming_soon"]}</a>' if upcoming else
             f'<a class="store-badge" href="{store_url(app, lang)}" rel="noopener">{store_badge(lang, t["download"])}</a>')
    # Right below the intro: the app, so readers see it before the long part.
    top_card = f"""<div class="guide-app-inline">
      <img src="{d["icon"]}" alt="{e(short)} app icon" width="56" height="56">
      <div><p class="kicker">{t["guide_app"]}</p><a class="name" href="{app_url}">{e(texts["name"])}</a><p>{e(texts["subtitle"])}</p></div>
      {badge}
    </div>"""
    # Halfway through: a slim reminder.
    middle_strip = (f'<a class="guide-strip" href="{app_url}"><img src="{d["icon"]}" alt="" width="32" height="32" loading="lazy">'
                    f'<span>{e(t["try_in"].format(name=short))}</span><b>{t["learn_more"]} →</b></a>')

    sections = ""
    for index, section in enumerate(g["sections"]):
        if index == len(g["sections"]) // 2:
            sections += middle_strip
        body = "".join(f"<p>{text(p)}</p>" for p in section.get("paragraphs", []))
        if section.get("code"):
            body += f'<pre><code>{e(section["code"])}</code></pre>'
        if section.get("list"):
            body += "<ul>" + "".join(f"<li>{text(x)}</li>" for x in section["list"]) + "</ul>"
        if section.get("table"):
            table = section["table"]
            body += ('<div class="table-wrap"><table><thead><tr>' + "".join(f"<th>{e(h)}</th>" for h in table["head"])
                     + "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{cell(c)}</td>" for c in row) + "</tr>" for row in table["rows"])
                     + "</tbody></table></div>")
        sections += f'<section><h2>{e(section["h2"])}</h2>{body}</section>'
    # Same app first, then others, four in all.
    # A guide can name its closest ones ("related": English slugs) to come first.
    related = [x for slug in guide.get("related", []) for x in GUIDES if x["slug"]["en"] == slug]
    related += [x for x in GUIDES if x is not guide and x["app"] == guide["app"] and x not in related]
    related += [x for x in GUIDES if x is not guide and x["app"] != guide["app"]][:4 - len(related)] if len(related) < 4 else []
    others = "".join(guide_card(x, lang, data) for x in related[:4])

    ld = [
        {"@context": "https://schema.org", "@type": "Article", "headline": g["h1"], "description": g["description"],
         "inLanguage": lang, "datePublished": GUIDES_PUBLISHED, "dateModified": guide.get("modified", GUIDES_PUBLISHED),
         "mainEntityOfPage": f"{SITE}{path}", "image": f"{SITE}{large_icon(app)}",
         "author": {"@type": "Person", "name": "Julian Lau", "url": SITE + "/", "sameAs": SAME_AS},
         "publisher": {"@type": "Person", "name": "Julian Lau", "url": SITE + "/"},
         "about": {"@type": "SoftwareApplication", "name": short, "url": f"{SITE}{path_for(lang, app['slug'])}"}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "JL Apps", "item": f"{SITE}{path_for(lang)}"},
            {"@type": "ListItem", "position": 2, "name": t["guides"], "item": f"{SITE}{guide_path(lang)}"},
            {"@type": "ListItem", "position": 3, "name": g["h1"], "item": f"{SITE}{path}"}]},
    ]
    if g.get("faq"):
        ld.append(faq_ld(g["faq"]))
    extra = ("" if upcoming else f'<meta name="apple-itunes-app" content="app-id={app["id"]}">\n') \
        + "\n".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    bar_url, bar_note, bar_action = ((app_url, t["coming_soon"], t["learn_more"]) if upcoming
                                     else (store_url(app, lang), t["free_store"], t["get_short"]))

    body = f"""{header(lang, alternates[1 if lang == "en" else 0][1])}
<main class="guide">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{path_for(lang)}">JL Apps</a> › <a href="{guide_path(lang)}">{t["guides"]}</a></nav>
  <div class="guide-layout">
  <article>
    <p class="kicker">{e(t["guides_for"].format(name=short))}</p>
    <h1>{e(g["h1"])}</h1>
    <div class="guide-intro">{intro}</div>
    {top_card}
    {sections}
    <aside class="guide-app">
      <img src="{d["icon"]}" alt="{e(short)} app icon" width="72" height="72" loading="lazy">
      <div>
        <p class="kicker">{t["guide_app"]}</p>
        <h2><a href="{app_url}">{e(texts["name"])}</a></h2>
        <p>{e(texts["promo"] or texts["subtitle"])}</p>
        {badge}
        <a class="text-link" href="{app_url}">{t["learn_more"]} →</a>
      </div>
    </aside>
    {faq_section(g.get("faq", []), t["faq"])}
  </article>
  <aside class="guide-side" aria-label="{e(short)}">
    <img src="{d["icon"]}" alt="" width="64" height="64">
    <a class="name" href="{app_url}">{e(short)}</a>
    <p>{e(texts["subtitle"])}</p>
    {badge}
    <span class="fine">{t["free"] if upcoming else t["free_store"]}</span>
  </aside>
  </div>
  <section class="guides-block"><h2>{t["more_guides"]}</h2><div class="guide-grid">{others}</div></section>
</main>
<a class="guide-bar" href="{bar_url}"{"" if upcoming else ' rel="noopener"'}>
  <img src="{d["icon"]}" alt="" width="40" height="40"><span><b>{e(short)}</b><small>{bar_note}</small></span><em>{bar_action}</em>
</a>
{footer(lang)}"""
    write(path, page(lang, head(lang, g["title"], g["description"], path, alternates, extra=extra,
                                image=og_image(guide, lang, data)),
                     body, accent=app["accent"], body_class="guide-page"))


def guides_index(lang, data):
    t = UI[lang]
    other = "de" if lang == "en" else "en"
    path = guide_path(lang)
    alternates = [("en", guide_path("en")), ("de", guide_path("de")), ("x-default", guide_path("en"))]
    groups = ""
    for app in APPS + UPCOMING:
        own = [g for g in GUIDES if g["app"] == app["slug"]]
        if own:
            name = short_name(data[app["slug"]]["texts"][lang]["name"])
            groups += (f'<section class="guides-block" style="--accent:{app["accent"]}"><h2>{e(t["guides_for"].format(name=name))}</h2>'
                       f'<div class="guide-grid">{"".join(guide_card(g, lang, data) for g in own)}</div></section>')
    body = f"""{header(lang, guide_path(other))}
<main>
  <section class="legal guides-head"><h1>{t["guides"]}</h1><p class="lead">{t["guides_text"]}</p></section>
  {groups}
</main>
{footer(lang)}"""
    write(path, page(lang, head(lang, t["guides_title"], t["guides_description"], path, alternates), body, body_class="guides-index"))


def imprint(lang):
    t = UI[lang]
    title = "Imprint" if lang == "en" else "Impressum"
    path = "/imprint/" if lang == "en" else "/de/impressum/"
    other = "/de/impressum/" if lang == "en" else "/imprint/"
    responsible = "Responsible for the content" if lang == "en" else "Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV"
    info = "Information according to § 5 DDG" if lang == "en" else "Angaben gemäß § 5 DDG"
    body = f"""{header(lang, other)}
<main class="legal">
  <h1>{title}</h1>
  <h2>{info}</h2>
  <p>Julian Lau<br>Weidengarten 1<br>53129 Bonn<br>{"Germany" if lang == "en" else "Deutschland"}</p>
  <h2>{t["contact"]}</h2>
  <p>E-Mail: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
  <h2>{responsible}</h2>
  <p>Julian Lau, {"address as above" if lang == "en" else "Anschrift wie oben"}</p>
</main>
{footer(lang)}"""
    alternates = [("en", "/imprint/"), ("de", "/de/impressum/"), ("x-default", "/imprint/")]
    write(path, page(lang, head(lang, f"{title} – JL Apps", title, path, alternates), body, body_class="legal-page"))


def not_found(data):
    t = UI["en"]
    cards = "".join(app_card(app, "en", data[app["slug"]]) for app in APPS)
    body = f"""{header("en", "/de/")}
<main>
  <section class="legal"><h1>{t["not_found_title"]}</h1><p>{t["not_found_text"]}</p>
  <p><a class="button" href="/">{t["back_home"]}</a></p></section>
  <section class="group"><div class="grid">{cards}</div></section>
</main>
{footer("en")}"""
    with open(os.path.join(ROOT, "404.html"), "w") as f:
        f.write(page("en", head("en", f"{t['not_found_title']} – JL Apps", t["not_found_text"], "/404.html", []).replace(
            '<link rel="canonical"', '<meta name="robots" content="noindex">\n<link rel="canonical"'), body))


def sitemap():
    today = datetime.date.today().isoformat()
    urls = ["/", "/de/", "/imprint/", "/de/impressum/", guide_path("en"), guide_path("de")]
    for guide in GUIDES:
        urls += [guide_path("en", guide["slug"]["en"]), guide_path("de", guide["slug"]["de"])]
    for app in APPS:
        urls += [path_for("en", app["slug"]), path_for("de", app["slug"])]
        if os.path.exists(os.path.join(ROOT, app["slug"], "privacy", "index.html")):
            urls.append(f"/{app['slug']}/privacy/")
    for app in UPCOMING:  # their hand-written pages
        for p in (path_for("en", app["slug"]), path_for("de", app["slug"]), f"/{app['slug']}/privacy/"):
            if os.path.exists(os.path.join(ROOT, p.strip("/"), "index.html")):
                urls.append(p)
    for extra in ("code-editor", "python-editor", "markdown-editor", "latex-editor", "txt-editor", "netora"):
        p = f"/{extra}/privacy/"
        if p not in urls and os.path.exists(os.path.join(ROOT, extra, "privacy", "index.html")):
            urls.append(p)
    def lastmod(url):
        page_file = os.path.join(ROOT, url.strip("/"), "index.html")
        if not os.path.exists(page_file):
            return today
        return datetime.date.fromtimestamp(os.path.getmtime(page_file)).isoformat()
    entries = "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{lastmod(u)}</lastmod></url>\n" for u in urls)
    with open(os.path.join(ROOT, "sitemap.xml"), "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}</urlset>\n')
    with open(os.path.join(ROOT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nDisallow: /_tools/\n\nSitemap: {SITE}/sitemap.xml\n")


def main():
    data = {}
    for app in APPS:
        texts = app_texts(app)
        missing = [lang for lang in LANGS if lang not in texts or not texts[lang]["name"]]
        if missing:
            raise SystemExit(f"{app['slug']}: no texts for {missing}")
        icon, shots = app_images(app)
        data[app["slug"]] = dict(texts=texts, icon=icon, shots=shots)
    for app in UPCOMING:
        data[app["slug"]] = dict(texts=app["texts"], icon=app["icon"], shots={lang: [] for lang in LANGS})
    external_icons = {item["slug"]: external_icon(item) for item in EXTERNAL}
    external_shots = {item["slug"]: external_shot(item) for item in EXTERNAL}
    for lang in LANGS:
        home(lang, data, external_icons, external_shots)
        for app in APPS:
            app_page(app, lang, data)
        imprint(lang)
        guides_index(lang, data)
        for guide in GUIDES:
            guide_page(guide, lang, data)
    not_found(data)
    sitemap()
    print("built", len(APPS) * 2 + 6 + len(GUIDES) * 2, "pages")


if __name__ == "__main__":
    main()
