# Fackeln am Abgrund

Zusätzliche statische Kopie der bestehenden [Wix-Website](https://tkopp37.wixsite.com/fackeln-am-abgrund), Stand 5. September 2026. Wix bleibt unverändert bestehen. Keine Umleitung, kein Domainwechsel und keine automatische Synchronisierung.

## Inhalt

- 19 vollständige veröffentlichte Beiträge: 14 Sessions und 5 Hintergrundbeiträge.
- Startseite, Datenschutzseite, unveränderte Blog-Slugs, Formatierung, Tabellen und Bildunterschriften.
- 34 Originalbilddateien im Download-Manifest; der Build lädt sie einmalig nach `assets/` und kopiert sie in das Deployment. Bei einem fehlenden Bild bricht der normale Build ab.
- Responsive Schwarz-Weiß-Gestaltung, lokale Beitragssuche, vergrößerbare Bilder und Druckansicht.
- Links zu Kommentaren führen zum jeweiligen Wix-Original. Canonical-Links behalten Wix als Hauptquelle bei.

## Lokal bauen

Python 3.12 oder neuer, keine zusätzlichen Pakete erforderlich:

```sh
python build.py
python validate.py
python -m http.server 8000 --directory .
```

Für eine lokale Vorschau stattdessen mit `python build.py --base /site` bauen und `python validate.py --base /site` prüfen; anschließend `http://localhost:8000/site/` öffnen.

`--offline` erzeugt HTML auch ohne heruntergeladene Bilder. Das ist nur zur Strukturprüfung vorgesehen; ein solches Ergebnis darf nicht veröffentlicht werden. `python validate.py --allow-missing-media` dokumentiert die fehlenden Dateien ausdrücklich.

## GitHub Pages

Repository: `ThomasKopp/fackeln-am-abgrund`. Unter Settings → Pages → Source `GitHub Actions` wählen. Der Workflow `Pages` baut und prüft die Website. Die Veröffentlichung wird manuell über Actions → Pages → Run workflow mit aktivierter Option `publish` ausgelöst. Normale Pushes prüfen nur und erzeugen ein herunterladbares Website-Artefakt.

Die geplante Adresse ist `https://thomaskopp.github.io/fackeln-am-abgrund/`. Sie ist erst nach erfolgreichem Deployment verfügbar.

## Inhalte bearbeiten

`content/posts/*.json` enthält die gesicherten Wix-Rich-Content-Dokumente. `build.py` übersetzt sämtliche im Export vorkommenden Blocktypen. Eine neue unbekannte Struktur führt zu einem Fehler statt zu stillschweigendem Inhaltsverlust. Texte können in den `textData.text`-Feldern bearbeitet werden. `static/` enthält Gestaltung und Suche; `content/privacy.html` die an den zusätzlichen Hoster angepasste Datenschutzseite.

Die GitHub-Kopie ist eine Momentaufnahme. Spätere Änderungen auf Wix erscheinen hier erst nach einem erneuten Export. Wix-Zugangsdaten sind weder enthalten noch für den Build erforderlich. Bereits heruntergeladene `assets/` können ins Repository aufgenommen werden, um auch künftige Builds vom Wix-Bildserver unabhängig zu machen.

## Grenzen der Kopie

Wix-Editor, Mitgliederkonten, Buchungsverwaltung, Rechnungen, Likes und Kommentare sind keine statischen Website-Dateien. Sie wurden nicht übertragen. Installierte Wix-Apps sind im Bestandsbericht aufgeführt. Ein eigenständiger Login oder Buchungsdienst müsste separat angebunden werden. Derzeit bleibt Wix für die vorhandenen Diskussionen die verlinkte Anlaufstelle. Die Titelschrift wird mit einer lokalen Serifenschrift angenähert; die Gestaltung ist nachgebaut, kein identischer Wix-Editor-Export.

Inhalte und Bilder behalten ihre bestehenden Rechte; dieses Repository erteilt keine zusätzliche Nutzungslizenz.
