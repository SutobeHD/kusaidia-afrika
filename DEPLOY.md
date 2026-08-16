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

## Was wir über den Server wissen

Geprüft am 16. August 2026:

| | |
|---|---|
| **Hoster** | Contabo, Rechner `m2794.contabo.net` (IP 193.34.145.200) |
| **Verwaltung** | **cPanel** — <https://cpanel.kusaidia-afrika.de> ist erreichbar |
| **FTP** | Pure-FTPd mit TLS, **Port 21**, FTPS explizit. SFTP/Port 22 ist zu. |
| **Mail** | Exim auf Port 587, Webmail unter <https://webmail.kusaidia-afrika.de> |
| **Nameserver** | ns1–ns3.contabo.net, Domain zeigt bereits auf den richtigen Server |

Weil cPanel im Einsatz ist, heißt das Web-Verzeichnis mit hoher Wahrscheinlichkeit
**`public_html`** (nicht `httpdocs`, das wäre Plesk).

---

## Schritt 1 — FTP-Zugangsdaten holen

Am einfachsten direkt über cPanel, das Contabo-Kundenportal wird dafür nicht gebraucht:

1. <https://cpanel.kusaidia-afrika.de> aufrufen und anmelden
2. Bereich **„FTP-Konten"** öffnen
3. Dort steht der vollständige Benutzername und darunter der Pfad des Kontos.
   Über **„Passwort ändern"** kannst du ein neues vergeben, falls das alte fehlt.
4. Notiere dir:

| Variable | Wert für diesen Server |
|---|---|
| **FTP-Host** | `kusaidia-afrika.de` (antwortet nachweislich auf Port 21) |
| **FTP-Benutzername** | steht in cPanel unter „FTP-Konten", meist `name@kusaidia-afrika.de` |
| **FTP-Passwort** | in cPanel neu setzen, falls unbekannt |
| **Webspace-Pfad** | `./public_html/` (cPanel-Standard) |

> **Wichtig:** Diese Daten **NIEMALS in den Chat schreiben** oder ins Repo committen.
> Wir packen sie in GitHub Secrets — die sind verschlüsselt und nur GitHub Actions kann sie lesen.

Falls die cPanel-Anmeldung nicht klappt: Die Zugangsdaten dafür stehen in der
Einrichtungsmail von Contabo (im Postfach unter
<https://webmail.kusaidia-afrika.de> nachsehen) oder lassen sich über den
Contabo-Support zurücksetzen.

---

## Schritt 2 — Secrets in GitHub eintragen

1. Gehe zu deinem Repo: <https://github.com/SutobeHD/kusaidia-afrika>
2. Klicke auf **Settings** (oben rechts)
3. Linke Seitenleiste: **Secrets and variables → Actions**
4. Klick **„New repository secret"** und lege diese vier an:

| Name | Wert |
|---|---|
| `FTP_HOST` | `kusaidia-afrika.de` |
| `FTP_USERNAME` | dein FTP-Benutzername aus cPanel |
| `FTP_PASSWORD` | dein FTP-Passwort |
| `FTP_TARGET_DIR` | `./public_html/` |

Die Namen müssen **exakt** so geschrieben sein — der Workflow sucht wortwörtlich
nach `FTP_HOST`; bei `FTP_Host` findet er nichts.

Jeder Eintrag wird verschlüsselt gespeichert. Auch du als Repo-Besitzer kannst sie nach dem Speichern nicht mehr lesen — nur ersetzen. Dass das Repository öffentlich ist, spielt dabei keine Rolle: Secrets liegen nicht im Repository, sondern in dessen Einstellungen, und tauchen weder in Dateien noch im Verlauf auf.

---

## Schritt 2b — Das alte WordPress aus dem Weg räumen

**Vor dem ersten Deploy erledigen.** Unter `kusaidia-afrika.de` liegt noch eine
defekte WordPress-Installation (sie liefert derzeit Fehler 500). Solange deren
`index.php` und `.htaccess` im Web-Verzeichnis liegen, zeigt der Server weiter
WordPress an — die hochgeladene `index.html` bliebe unsichtbar.

1. In cPanel den **Dateimanager** öffnen und nach `public_html` wechseln
2. **Erst sichern:** In cPanel unter **„Backup"** eine Sicherung des
   Web-Verzeichnisses herunterladen. Falls WordPress eine Datenbank nutzt, auch
   diese exportieren (Bereich **phpMyAdmin**).
3. Danach den Inhalt von `public_html` leeren — insbesondere `index.php`,
   `.htaccess`, `wp-config.php` und die Ordner `wp-admin`, `wp-content`,
   `wp-includes`.

> Die Mail-Postfächer sind davon **nicht** betroffen, die liegen außerhalb von
> `public_html`. Webmail und die Adressen `@kusaidia-afrika.de` bleiben unverändert.

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
