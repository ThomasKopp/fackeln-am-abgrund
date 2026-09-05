# Bestandsaufnahme und Abweichungen

Stand: 05.09.2026. Ziel ist eine zusätzliche Kopie, kein Umzug der bestehenden Adresse.

## Verifizierte Quelle

Wix-Konto tkopp37, veröffentlichte Website „Fackeln Am Abgrund“: https://tkopp37.wixsite.com/fackeln-am-abgrund. Velo deaktiviert. Die öffentliche Startseite enthält den Titel, das Fackellogo, Sessions, Hintergrund und einen Datenschutzlink. Die Blog-API meldet 19 von insgesamt 19 veröffentlichten Beiträgen. Davon sind 14 Session-Berichte und 5 Hintergrundbeiträge. Alle wurden als vollständige Rich-Content-Dokumente gesichert. Entwürfe und Mitgliederdaten sind nicht Teil dieser Kopie.

34 eindeutige Originalbilder werden benötigt. In den Beiträgen sind 31 Bildblöcke, 19 Bildunterschrift-Blöcke, 2 Tabellen, 100 Überschriften und 589 Textblöcke enthalten. Die erzeugte Website umfasst 23 HTML-Dateien: Startseite, 19 Beiträge, Datenschutzseite, Fehlerseite und Decap-CMS-Oberfläche.

## Funktionen

| Wix-Funktion | Kopie / Status |
|---|---|
| Blog und Beitragslisten | Statische HTML-Seiten, lokale Suche, alle veröffentlichten Beiträge |
| Bilder und Vergrößerung | Eigene Bilddateien; Klick öffnet das Originalbild |
| Kommentare, Likes | Kein Konto-/Kommentarimport; Link zur bestehenden Diskussion auf Wix |
| Members Area | Installiert; kein eigenständiger Mitgliederbereich auf der Kopie |
| Bookings | Installiert; auf der geprüften öffentlichen Startseite keine Buchungsoberfläche sichtbar; kein Buchungs- oder Kundendatenimport |
| Invoices | Installiert; Verwaltungsfunktion bleibt bei Wix |
| Instagram Feed | Installiert; auf der geprüften Startseite kein sichtbarer Feed; nicht eingebettet |
| Promote SEO | Installiert; Titel, Beschreibungen und Canonical-Links werden als HTML ausgegeben |
| Wix-Editor, Layout und Schrift | Responsives Layout nachgebaut; Titelschrift mit Systemschrift angenähert |
| Inhalte bearbeiten | Decap CMS unter `/admin/`; alle 19 Beiträge in Markdown migriert; Wix-JSON unverändert daneben erhalten |
| Datenschutzseite | Kontakt- und Betroffenenrechtstexte übernommen; Hostingabschnitt auf GitHub angepasst; fehlerhafter Link zum NRW-Formular durch die bereits im Originaltext genannte BW-Adresse ersetzt |

Die installierten Apps beweisen nicht, dass alle Funktionen öffentlich genutzt werden. Geschützte Bereiche und Verwaltungsdaten wurden nicht untersucht oder dupliziert. Ein zukünftiger eigenständiger Kommentarbereich könnte über GitHub Discussions angebunden werden; Buchungen oder ein Login benötigen einen zusätzlichen Dienst. In der jetzigen Kopie wird dafür kein neuer Dienst eingerichtet.

## Erhaltung des Originals

Alle Wix-Zugriffe waren lesend. Keine Veröffentlichung, Bearbeitung, Umleitung, DNS-Änderung, Löschung oder Vertragsänderung auf Wix. Bestehende Links bleiben erreichbar. Interne Beitragslinks innerhalb der GitHub-Kopie verweisen auf die entsprechenden kopierten Seiten. Canonical-Links verweisen weiterhin auf Wix als Hauptquelle.

## Prüfung und Bereitstellung

Lokal sind HTML-Erstellung und Abgleich aller 589 Textblöcke, der Tabellen/Bilderanzahl sowie interner Links erfolgreich. Die 19 Wix-JSON-Dateien bleiben als Rückfallebene unverändert neben den Markdown-Dateien erhalten. Der direkte lokale Netzwerkzugriff ist durch Windows-Socketfehler 10106/11003 gestört; deshalb wurde die neue Fassung lokal ohne die bereits im GitHub-Repository vorhandenen 34 Bilder gebaut. Der normale GitHub-Build verwendet diese archivierten Bilder, bricht bei fehlenden Bildern ab und prüft alle internen Medienpfade. Jede Änderung auf `main`, einschließlich CMS-Änderungen, wird nach erfolgreicher Prüfung automatisch über GitHub Pages veröffentlicht.

Die übernommene Datenschutzgrundlage ist kein vollständig neu erstelltes oder juristisch geprüftes Dokument. Die lokale Vorschau konnte wegen des Netzwerkfehlers nicht im Browser getestet werden; eine visuelle Prüfung der erzeugten Website steht vor ihrer Veröffentlichung noch aus.

Quellen: [Wix-Original](https://tkopp37.wixsite.com/fackeln-am-abgrund), Wix-Kontokontext und Blog-API vom 05.09.2026, [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages), [GitHub Pages Workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
