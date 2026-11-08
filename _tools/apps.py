"""The apps shown on jlauapps.com: App Store data, colors, screenshots and where their texts live.

Texts come from the "App Store Texte.md" files in ~/Documents/StoreScreenshots <App>, so the website
says the same as the App Store. Apps without such a file carry their texts here.
"""
import os

DOCS = os.path.expanduser("~/Documents")

# Order on the home page; `group` decides the section.
APPS = [
    dict(slug="howlnight", id=6829856365, accent="#8b5cf6", group="play",
         texts=f"{DOCS}/StoreScreenshots HowlNight/App Store Texte.md",
         shots=f"{DOCS}/StoreScreenshots HowlNight/iPhone 6.9",
         category="GameApplication", genre={"en": "Party game", "de": "Partyspiel"}),
    dict(slug="cardfox", id=6826939608, accent="#f97316", group="play",
         texts=f"{DOCS}/StoreScreenshots Cardfox/App Store Texte.md",
         shots=f"{DOCS}/StoreScreenshots Cardfox/iPhone 6.9",
         category="EducationalApplication", genre={"en": "Learning", "de": "Lernen"}),
    dict(slug="code-editor", id=6448794019, accent="#fb6b3c", group="create",
         texts=f"{DOCS}/StoreScreenshots Code Editor/App Store Texte.md",
         shots=f"{DOCS}/StoreScreenshots Code Editor/iPhone 6.9",
         category="DeveloperApplication", genre={"en": "Developer tools", "de": "Entwicklung"}),
    dict(slug="python-editor", id=6450125642, accent="#4f8cff", group="create",
         texts=f"{DOCS}/StoreScreenshots Python Editor/App Store Texte.md",
         shots=f"{DOCS}/StoreScreenshots Python Editor/iPhone 6.9",
         category="DeveloperApplication", genre={"en": "Developer tools", "de": "Entwicklung"}),
    dict(slug="latex-editor", id=1621591035, accent="#f43f6b", group="create",
         texts=f"{DOCS}/StoreScreenshots LaTeX Editor/App Store Texte.md",
         shots=f"{DOCS}/StoreScreenshots LaTeX Editor/iPhone 6.9",
         category="EducationalApplication", genre={"en": "Math & science", "de": "Mathe & Wissenschaft"}),
    dict(slug="markdown-editor", id=1617814051, accent="#6d7cff", group="create",
         texts=f"{DOCS}/StoreScreenshots Markdown Editor/App Store Texte.md",
         shots=f"{DOCS}/StoreScreenshots Markdown Editor/iPhone 6.9",
         category="ProductivityApplication", genre={"en": "Writing", "de": "Schreiben"}),
    dict(slug="txt-editor", id=6447488397, accent="#14b8a6", group="create",
         texts=f"{DOCS}/StoreScreenshots txt Editor/App Store Texte.md",
         shots=f"{DOCS}/StoreScreenshots txt Editor/iPhone 6.9",
         category="ProductivityApplication", genre={"en": "Notes", "de": "Notizen"}),
    dict(slug="adnumbers", id=6826622598, accent="#f5a524", group="money",
         texts=f"{DOCS}/StoreScreenshots AdNumbers/App Store Texte.md",
         shots=f"{DOCS}/StoreScreenshots AdNumbers/iPhone 6.9",
         category="BusinessApplication", genre={"en": "Business", "de": "Business"}),
    dict(slug="connect-insights", id=6830901660, accent="#4f7cff", group="money",
         texts=f"{DOCS}/StoreScreenshots Connect Insights/App Store Texte.md",
         shots=f"{DOCS}/StoreScreenshots Connect Insights/iPhone 6.9",
         category="DeveloperApplication", genre={"en": "Developer tools", "de": "Entwicklung"}),
    dict(slug="etf-calculator", id=6443639781, accent="#22c55e", group="money",
         texts=f"{DOCS}/StoreScreenshots ETF Calculator/App Store Texte.md",
         shots=f"{DOCS}/StoreScreenshots ETF Calculator/iPhone 6.9",
         category="FinanceApplication", genre={"en": "Finance", "de": "Finanzen"}),
]

# Has its own website; the home page links there instead of a duplicate page.
EXTERNAL = [
    dict(slug="yarnspace", url="https://yarnspace.app/", accent="#c06bff", group="play",
         name={"en": "YarnSpace", "de": "YarnSpace"},
         subtitle={"en": "Knitting & crochet companion", "de": "Begleiter fürs Stricken & Häkeln"},
         blurb={"en": "Row counters for every project, your yarn stash with label scanning, Ravelry patterns, yarn substitutes and handy calculators.",
                "de": "Reihenzähler für jedes Projekt, dein Wollvorrat mit Etiketten-Scan, Ravelry-Anleitungen, Garn-Alternativen und praktische Rechner."}),
]

GROUPS = {
    "play": {"en": "Play & learn", "de": "Spielen & lernen"},
    "create": {"en": "Write & code", "de": "Schreiben & programmieren"},
    "money": {"en": "Money & business", "de": "Geld & Business"},
}

# Texts for the ETF Calculator, which has no store text file yet.
ETF_TEXTS = {
    "en": dict(
        name="ETF Calculator: Savings Plan",
        subtitle="Plan, grow and track your ETFs",
        promo="See how your ETF savings plan grows, reach your goal, plan your payout and track your real portfolio – all calculated on your device.",
        keywords="etf,savings plan,compound interest,investment,portfolio,stocks,retirement,fire,withdrawal,dividends",
        description="""Plan your ETF savings with clarity. ETF Calculator shows how your money grows with compound interest, how long it takes to reach your goal and how long your savings last when you start paying yourself out. Everything is calculated on your device – no account needed.

SEE YOUR MONEY GROW
• Initial investment, monthly savings, yearly return and duration
• Final value with invested amount and returns, as a chart and a yearly table
• A range from many simulated market paths, so you know what's realistic
• Purchasing power: see your result in today's money

REACH YOUR GOAL
Enter the amount you want to reach and see how much you need to save each month – or how many years it takes.

PLAN YOUR PAYOUT
Find out how long your savings last with monthly withdrawals, or how much you can withdraw so they last for life.

COMPARE STRATEGIES
Save scenarios and put them side by side: more per month, a higher return, a few years longer.

TRACK YOUR REAL PORTFOLIO
• Record your positions, deposits and distributions
• Import a CSV file from your broker
• Automatic prices for ETFs with an ISIN
• See your allocation at a glance

GERMAN TAXES BUILT IN
The German Vorabpauschale is calculated with the current base rate from the Deutsche Bundesbank.

ALWAYS WITH YOU
Widgets for the Home Screen, Siri and Shortcuts, and iCloud sync between your devices."""),
    "de": dict(
        name="ETF-Rechner: Sparplan & Depot",
        subtitle="ETFs planen, wachsen, verfolgen",
        promo="Sieh, wie dein ETF-Sparplan wächst, erreiche dein Ziel, plane deine Entnahme und verfolge dein echtes Depot – alles auf deinem Gerät berechnet.",
        keywords="etf,sparplan,zinseszins,geldanlage,depot,aktien,rente,altersvorsorge,entnahme,vorabpauschale",
        description="""Plane deinen ETF-Sparplan mit klarem Blick. Der ETF-Rechner zeigt, wie dein Geld mit Zinseszins wächst, wie lange du bis zu deinem Ziel brauchst und wie lange dein Vermögen reicht, wenn du dir später etwas auszahlst. Alles wird auf deinem Gerät berechnet – ganz ohne Konto.

SIEH DEIN GELD WACHSEN
• Startkapital, monatliche Sparrate, jährliche Rendite und Laufzeit
• Endkapital mit Einzahlungen und Erträgen, als Diagramm und Jahrestabelle
• Eine Spanne aus vielen simulierten Marktverläufen, damit du weißt, was realistisch ist
• Kaufkraft: dein Ergebnis in heutigem Geld

ERREICHE DEIN ZIEL
Gib den Betrag ein, den du erreichen willst, und sieh, wie viel du monatlich sparen musst – oder wie viele Jahre es dauert.

PLANE DEINE ENTNAHME
Finde heraus, wie lange dein Vermögen bei monatlichen Entnahmen reicht – oder wie viel du entnehmen kannst, damit es ein Leben lang hält.

STRATEGIEN VERGLEICHEN
Speichere Szenarien und vergleiche sie nebeneinander: mehr pro Monat, höhere Rendite, ein paar Jahre länger.

DEIN ECHTES DEPOT
• Positionen, Einzahlungen und Ausschüttungen erfassen
• CSV-Datei deines Brokers importieren
• Automatische Kurse für ETFs mit ISIN
• Deine Aufteilung auf einen Blick

DEUTSCHE STEUERN EINGEBAUT
Die Vorabpauschale wird mit dem aktuellen Basiszins der Deutschen Bundesbank berechnet.

IMMER DABEI
Widgets für den Home-Bildschirm, Siri und Kurzbefehle sowie iCloud-Sync zwischen deinen Geräten."""),
}
