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

UI = {
    "en": dict(
        site_title="JL Apps – Apps for iPhone, iPad & Mac by Julian Lau",
        site_description="Apps for iPhone, iPad and Mac by Julian Lau: HowlNight party games, Cardfox vocabulary flashcards, Code Editor, Python Editor, Texlet LaTeX editor, Markdown Editor, txt Editor, AdNumbers, Connect Insights and ETF Calculator.",
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
    ),
    "de": dict(
        site_title="JL Apps – Apps für iPhone, iPad & Mac von Julian Lau",
        site_description="Apps für iPhone, iPad und Mac von Julian Lau: HowlNight Partyspiele, Cardfox Vokabel-Karteikarten, Code Editor, Python Editor, Texlet LaTeX-Editor, Markdown Editor, txt Editor, AdNumbers, Connect Insights und ETF-Rechner.",
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
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src) and max_side(dst) == min(width, max_side(src)):
        return
    args = ["sips", "-Z", str(width), src, "--out", dst]
    if fmt == "jpeg":
        args = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(quality), "-Z", str(width), src, "--out", dst]
    subprocess.run(args, check=True, capture_output=True)


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
    return "<head>\n" + "\n".join(tags) + ("\n" + extra if extra else "") + "\n</head>"


def header(lang, alternate_path):
    t = UI[lang]
    home = path_for(lang)
    other = "de" if lang == "en" else "en"
    return f"""<header class="topbar">
  <a class="brand" href="{home}" aria-label="JL Apps"><img src="/assets/logo.svg" alt="" width="34" height="34"><span>JL Apps</span></a>
  <nav>
    <a href="{home}#apps">{t["apps"]}</a>
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
        groups += f'<section class="group"><h2>{label[lang]}</h2><div class="grid">{"".join(cards)}</div></section>\n'

    # YarnSpace on the left (where Cardfox was), HowlNight big in the middle, Owlvest on the right.
    shots = [external_shots["yarnspace"][lang], data["howlnight"]["shots"][lang][0], (data["etf-calculator"]["shots"][lang] or [None])[0]]
    showcase = "".join(f'<img src="{u}" alt="" loading="lazy" width="320" height="695">' for u in shots if u)
    items = [{"@type": "ListItem", "position": i + 1, "url": f"{SITE}{path_for(lang, app['slug'])}",
              "name": short_name(data[app["slug"]]["texts"][lang]["name"])} for i, app in enumerate(APPS)]
    ld = [
        {"@context": "https://schema.org", "@type": "Person", "name": "Julian Lau", "url": SITE + "/",
         "email": CONTACT_EMAIL, "address": {"@type": "PostalAddress", "addressCountry": "DE"}},
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
        "inLanguage": lang, "author": {"@type": "Person", "name": "Julian Lau", "url": SITE + "/"},
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR" if lang == "de" else "USD"},
    }
    extra = (f'<meta name="apple-itunes-app" content="app-id={app["id"]}">\n'
             f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')

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
    showcase_cards = "".join(
        f'<article class="feature shot"><h3>{e(f["title"])}</h3><div class="feature-body">{f["body"]}</div>'
        f'<div class="rise"><div class="device"><img src="{f["screen"]}" alt="{e(f["title"].title())}" loading="lazy" width="700" height="1521"></div></div></article>'
        for f in showcase)
    feature_rows = "".join(
        f'<article class="feature span-{f["span"]}"><h3>{e(f["title"])}</h3><div class="feature-body">{f["body"]}</div></article>'
        for f in pack_features([f for f in features if f not in showcase]))
    intro_html = "".join(f"<p>{e(p)}</p>" for p in intro if not p.startswith("•"))
    intro_bullets = [p for p in intro if p not in intro_html]

    shots = d["shots"][lang]
    # Not the first one again: it's the big one beside the title.
    gallery = "".join(
        f'<img src="{u}" alt="{e(short)} {t["screenshots"].lower()} {i}" loading="lazy" width="320" height="695">'
        for i, u in enumerate(shots[1:], start=2))
    # The first screenshot big in the hero, the next two fanned out behind it.
    hero_shots = "".join(f'<img class="{c}" src="{shots[i]}" alt="{e(short)}" width="320" height="695">'
                         for c, i in (("left", 1), ("middle", 0), ("right", 2))) if len(shots) >= 3 else (
        f'<img src="{shots[0]}" alt="{e(short)}" width="320" height="695">' if shots else "")
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
    urls = ["/", "/de/", "/imprint/", "/de/impressum/"]
    for app in APPS:
        urls += [path_for("en", app["slug"]), path_for("de", app["slug"])]
        if os.path.exists(os.path.join(ROOT, app["slug"], "privacy", "index.html")):
            urls.append(f"/{app['slug']}/privacy/")
    for extra in ("code-editor", "python-editor", "markdown-editor", "latex-editor", "txt-editor"):
        p = f"/{extra}/privacy/"
        if p not in urls and os.path.exists(os.path.join(ROOT, extra, "privacy", "index.html")):
            urls.append(p)
    entries = "".join(f"<url><loc>{SITE}{u}</loc><lastmod>{today}</lastmod></url>\n" for u in urls)
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
    external_icons = {item["slug"]: external_icon(item) for item in EXTERNAL}
    external_shots = {item["slug"]: external_shot(item) for item in EXTERNAL}
    for lang in LANGS:
        home(lang, data, external_icons, external_shots)
        for app in APPS:
            app_page(app, lang, data)
        imprint(lang)
    not_found(data)
    sitemap()
    print("built", len(APPS) * 2 + 4, "pages")


if __name__ == "__main__":
    main()
