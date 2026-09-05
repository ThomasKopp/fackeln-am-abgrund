# Fackeln am Abgrund

Zusätzliche statische Kopie der bestehenden [Wix-Website](https://tkopp37.wixsite.com/fackeln-am-abgrund), Stand 5. September 2026. Wix bleibt unverändert bestehen. Keine Umleitung, kein Domainwechsel und keine automatische Synchronisierung.

## Inhalt

- 19 vollständige, im Decap CMS bearbeitbare Beiträge: 14 Sessions und 5 Hintergrundbeiträge.
- Startseite, Datenschutzseite, unveränderte Blog-Slugs, Formatierung, Tabellen und Bildunterschriften.
- 34 archivierte Originalbilddateien sowie CMS-Uploads unter `assets/uploads/`. Bei einem fehlenden Bild bricht der normale Build ab.
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

Repository: `ThomasKopp/fackeln-am-abgrund`. Unter Settings → Pages → Source `GitHub Actions` wählen. Der Workflow `Pages` baut, prüft und veröffentlicht die Website nach jeder Änderung auf `main`. Das gilt auch für Änderungen, die Decap CMS speichert. Der Workflow kann zusätzlich manuell gestartet werden.

Die geplante Adresse ist `https://thomaskopp.github.io/fackeln-am-abgrund/`. Sie ist erst nach erfolgreichem Deployment verfügbar.

## Inhalte bearbeiten

Die browserbasierte Bearbeitungsoberfläche liegt unter `https://thomaskopp.github.io/fackeln-am-abgrund/admin/`. Die einmalige OAuth-Freischaltung ist in [DECAP-EINRICHTUNG.md](DECAP-EINRICHTUNG.md) beschrieben.

`content/posts/*.md` enthält die von Decap verwalteten Beiträge. Alle 19 Wix-Beiträge wurden mit Titeln, Texten, Listen, Tabellen, Bildern, Bildunterschriften, Datumsangaben und unveränderten Slugs in dieses Format übertragen. Die ursprünglichen Wix-Rich-Content-Dokumente bleiben als `content/posts/*.json` unverändert daneben erhalten und werden vom CMS nicht angezeigt. `validate.py` vergleicht bei jedem Build die übertragenen Texte, Bild- und Tabellenanzahlen mit diesen Originalen. `static/` enthält Gestaltung, Suche und CMS-Oberfläche; `content/privacy.html` die an den zusätzlichen Hoster angepasste Datenschutzseite.

Die GitHub-Kopie ist eine Momentaufnahme. Spätere Änderungen auf Wix erscheinen hier nicht automatisch. Neue Änderungen werden stattdessen über Decap CMS in GitHub gepflegt. Wix-Zugangsdaten sind weder enthalten noch für den Build erforderlich.

## Grenzen der Kopie

Wix-Editor, Mitgliederkonten, Buchungsverwaltung, Rechnungen, Likes und Kommentare sind keine statischen Website-Dateien. Sie wurden nicht übertragen. Installierte Wix-Apps sind im Bestandsbericht aufgeführt. Ein eigenständiger Login oder Buchungsdienst müsste separat angebunden werden. Derzeit bleibt Wix für die vorhandenen Diskussionen die verlinkte Anlaufstelle. Die Titelschrift wird mit einer lokalen Serifenschrift angenähert; die Gestaltung ist nachgebaut, kein identischer Wix-Editor-Export.

Inhalte und Bilder behalten ihre bestehenden Rechte; dieses Repository erteilt keine zusätzliche Nutzungslizenz.
