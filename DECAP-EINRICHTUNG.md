# Decap CMS einmalig freischalten

Die CMS-Dateien liegen unter `static/admin/` und werden als
`https://thomaskopp.github.io/fackeln-am-abgrund/admin/` veröffentlicht. Decap
schreibt veröffentlichte Änderungen direkt als Commit in den Branch `main`.
Der Pages-Workflow baut und veröffentlicht daraufhin automatisch.

GitHub Pages kann den geheimen Schlüssel einer GitHub-OAuth-Anwendung nicht
selbst sicher speichern. Für den kleinen serverseitigen Teil der Anmeldung wird
deshalb Netlifys OAuth-Dienst verwendet. Die Website bleibt auf GitHub Pages;
Netlify wird nur für die Anmeldung benötigt.

## 1. Netlify-Projekt anlegen

1. Bei Netlify anmelden und **Add new project → Import an existing project**
   wählen.
2. GitHub verbinden und `ThomasKopp/fackeln-am-abgrund` auswählen.
3. Den Projektnamen auf `fackeln-am-abgrund-cms` setzen. Die zugehörige Adresse
   muss `https://fackeln-am-abgrund-cms.netlify.app` lauten.
4. Falls dieser Name bereits vergeben ist, einen anderen Namen wählen und danach
   in `static/admin/config.yml` den Wert `site_domain` auf die tatsächlich
   angezeigte Netlify-Domain ändern.
5. Ein Netlify-Deployment ist für GitHub Pages nicht nötig. Falls Netlify einen
   Build verlangt, `python3 build.py` als Build-Befehl und `site` als
   Veröffentlichungsordner verwenden.

## 2. GitHub-OAuth-Anwendung anlegen

1. GitHub öffnen: **Profilbild → Settings → Developer settings → OAuth Apps →
   New OAuth App**.
2. Diese Werte eintragen:

   - Application name: `Fackeln am Abgrund CMS`
   - Homepage URL: `https://thomaskopp.github.io/fackeln-am-abgrund/`
   - Authorization callback URL: `https://api.netlify.com/auth/done`

3. **Register application** wählen.
4. **Generate a new client secret** wählen und Client ID sowie Client Secret für
   den nächsten Schritt bereithalten. Das Secret niemals in GitHub oder in eine
   Datei dieses Repositorys eintragen.

## 3. OAuth in Netlify hinterlegen

1. Im Netlify-Projekt **Project configuration → Access & security → OAuth →
   Authentication providers** öffnen.
2. **Install provider** bei GitHub wählen.
3. Client ID und Client Secret aus GitHub eintragen und speichern.

Danach `https://thomaskopp.github.io/fackeln-am-abgrund/admin/` öffnen und
**Login with GitHub** wählen. Der angemeldete GitHub-Nutzer benötigt
Schreibzugriff auf `ThomasKopp/fackeln-am-abgrund`.

## Verwendung

- **Beiträge** zeigt alle 19 übernommenen Wix-Beiträge.
- **New Beitrag** legt einen neuen Beitrag an.
- Das URL-Kürzel bestehender Beiträge sollte unverändert bleiben, damit ihre
  bisherigen URLs erhalten bleiben.
- Bilder können im Beitragseditor ausgewählt oder hochgeladen werden. Neue
  Dateien landen unter `assets/uploads/`.
- Mit **Auf Website anzeigen** kann ein Beitrag verborgen werden, ohne ihn zu
  löschen.
- **Publish** speichert in GitHub. Der Pages-Workflow veröffentlicht die Änderung
  anschließend automatisch.

Die ursprünglichen Wix-Rich-Content-Dateien bleiben unverändert als
`content/posts/*.json` neben den Markdown-Dateien erhalten. Sie dienen als
vollständige Rückfallebene und werden nicht vom CMS bearbeitet.
