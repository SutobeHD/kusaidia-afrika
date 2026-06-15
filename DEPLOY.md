# Deployment-Anleitung — Kusaidia Afrika auf Contabo

Du brauchst diese Anleitung nur **einmal**. Danach läuft alles automatisch: Du machst `git push`, und 30–60 Sekunden später ist die neue Version auf kusaidia-afrika.de.

---

## Übersicht

```
   Du machst eine Änderung
            ↓
   git commit && git push
            ↓
   GitHub Actions startet automatisch
            ↓
   FTPS-Upload zu Contabo
            ↓
   kusaidia-afrika.de zeigt neue Version
```

---

## Schritt 1 — FTP-Zugangsdaten bei Contabo finden

1. Logge dich ins **Contabo-Kundenportal** ein: <https://my.contabo.com>
2. Gehe zu **Webhosting → Verwalten** (oder ähnlich)
3. Suche den Bereich **„FTP-Zugang"** oder **„FTP-Accounts"**
4. Notiere dir:

| Variable | Wert |
|---|---|
| **FTP-Host** | typisch `ftp.kusaidia-afrika.de` oder `vmd12345.contaboserver.net` |
| **FTP-Benutzername** | typisch `kusaidia-afrika.de` oder ein Kürzel |
| **FTP-Passwort** | das hast du beim Anlegen vergeben (ggf. neu setzen lassen) |
| **Webspace-Pfad** | typisch `/httpdocs/` oder `/public_html/` oder `./` |

> **Wichtig:** Diese Daten **NIEMALS in den Chat schreiben** oder ins Repo committen.
> Wir packen sie in GitHub Secrets — die sind verschlüsselt und nur GitHub Actions kann sie lesen.

---

## Schritt 2 — Secrets in GitHub eintragen

1. Gehe zu deinem Repo: <https://github.com/SutobeHD/kusaidia-afrika>
2. Klicke auf **Settings** (oben rechts)
3. Linke Seitenleiste: **Secrets and variables → Actions**
4. Klick **„New repository secret"** und lege diese vier an:

| Name | Wert |
|---|---|
| `FTP_HOST` | dein Contabo-FTP-Host |
| `FTP_USERNAME` | dein FTP-Benutzername |
| `FTP_PASSWORD` | dein FTP-Passwort |
| `FTP_TARGET_DIR` | Webspace-Pfad, z.B. `./httpdocs/` |

Jeder Eintrag wird verschlüsselt gespeichert. Auch du als Repo-Besitzer kannst sie nach dem Speichern nicht mehr lesen — nur ersetzen.

---

## Schritt 3 — Den ersten Deploy auslösen

**Option A: Manuell triggern**

1. Im Repo → Tab **Actions**
2. Links: **„Deploy to Contabo"** auswählen
3. Rechts: **„Run workflow"** → grüner Knopf

**Option B: Mit einem Push**

```bash
git commit --allow-empty -m "Trigger first deploy"
git push
```

Im Tab **Actions** siehst du dann live, was passiert. Beim ersten Mal dauert es ein paar Minuten (alle Dateien werden hochgeladen). Bei späteren Deploys nur Sekunden — nur die geänderten Dateien gehen rüber.

---

## Schritt 4 — Domain auf Contabo zeigen lassen

Wenn `kusaidia-afrika.de` bei Contabo registriert ist (oder Contabo nur die Verwaltung macht):

- **Bei Contabo registriert:** sollte automatisch funktionieren, sobald die Dateien im Webspace liegen.
- **Bei einem anderen Anbieter:** dort die DNS-Einträge so setzen, dass `kusaidia-afrika.de` auf die Contabo-Server zeigt. Contabo zeigt dir die nötigen Werte im Kundenportal.

DNS-Änderungen brauchen meist 30 Minuten bis 24 Stunden, bis sie überall ankommen.

---

## Schritt 5 — GitHub Pages abschalten (optional)

Sobald `kusaidia-afrika.de` auf Contabo läuft, kannst du die GitHub-Pages-URL abschalten:

1. Repo → **Settings → Pages**
2. **Source**: auf „None" setzen

Die URL `sutobehd.github.io/kusaidia-afrika/` wird damit inaktiv. Der Code im Repo bleibt bestehen — nur das öffentliche Hosting wird beendet.

---

## Wenn etwas schiefgeht

**„Login incorrect" im Actions-Log:**
→ FTP-Daten in den Secrets prüfen. Tippfehler? Anführungszeichen?

**„Connection refused":**
→ Stimmt der FTP-Host? Manche Contabo-Webspaces nutzen einen anderen Port (z.B. 22 für SFTP).
→ Im Workflow `protocol: ftps` und `port: 21` ggf. zu `sftp` / `22` ändern.

**Die Seite wirkt kaputt nach Deploy:**
→ Im Actions-Log nachschauen, welche Dateien hochgeladen wurden.
→ Mit dem Backup von GitHub Pages vergleichen: <https://sutobehd.github.io/kusaidia-afrika/>

**Komplettreset:**
Falls der State-Tracker durcheinander ist, kannst du im Workflow `state-name` löschen oder umbenennen → beim nächsten Deploy werden alle Dateien neu hochgeladen.

---

## Was bleibt bei Contabo, was läuft über GitHub?

| Was | Wo |
|---|---|
| **Quellcode** (HTML, CSS, JS) | GitHub Repo |
| **Bilder, Schriften** | GitHub Repo *und* gespiegelt auf Contabo |
| **Website-Auslieferung** | Contabo Webspace |
| **E-Mail (`@kusaidia-afrika.de`)** | Contabo Mail-Server |
| **Domain `kusaidia-afrika.de`** | Contabo DNS |
| **Backup / History** | GitHub (komplette Git-Historie aller Commits) |

Du arbeitest also weiter wie bisher mit GitHub — Contabo ist nur der „Schaufenster"-Server für die Welt.
