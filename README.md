# Kusaidia Afrika – Helfen in Afrika e.V.

Statische Website des gemeinnützigen Vereins Kusaidia Afrika. Neuaufbau der ursprünglichen Seite kusaidia-afrika.de auf Basis der im Webarchiv gesicherten Inhalte.

## Struktur

```
.
├── index.html                Startseite
├── ueber-uns.html            Vereinsgeschichte & Vorstand
├── projekte.html             Projektübersicht
├── projekte/                 Projektdetailseiten
│   ├── laborantenkolleg-bashanet.html
│   ├── clinical-medicine.html
│   ├── sanu-tec.html
│   ├── madunga-girls-school.html
│   └── student-support.html
├── partner.html              Partner in Tansania
├── aktuelles.html            News
├── unterstuetzen.html        Spenden & Mitgliedschaft
├── ihre-spende-kommt-an.html Transparenz
├── kontakt.html              Kontakt
├── impressum.html
├── datenschutz.html
├── css/style.css             Styles (Vanilla CSS)
├── js/main.js                Mini-JS (Nav, Slideshow, Reveal, Copy)
└── assets/images/            Bilder
```

## Lokal ansehen

Datei `index.html` im Browser öffnen – fertig. Es ist kein Build-Schritt nötig.

Für korrekte Pfade beim lokalen Entwickeln am besten einen Mini-Server starten:

```bash
# Python (vorinstalliert auf macOS/Linux, oft auch Windows)
python -m http.server 8000
# dann: http://localhost:8000
```

## Deployment

- **GitHub Pages**: Repo-Settings → Pages → Branch `main`, Folder `/ (root)`.
- **Netlify Drop**: Ordner auf [app.netlify.com/drop](https://app.netlify.com/drop) ziehen.

## Bearbeiten

Inhalt steckt direkt im HTML. Bilder kommen in `assets/images/`. Style-Variablen (Farben, Spacing, Typo) sind oben in `css/style.css` als CSS Custom Properties definiert.

## Lizenz / Rechte

Texte und Fotos: © Kusaidia Afrika – Helfen in Afrika e.V.
Code: zur freien Nutzung durch den Verein.
