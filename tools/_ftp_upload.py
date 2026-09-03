#!/usr/bin/env python3
"""Laedt die Website per FTPS auf den Webspace - Notweg, wenn GitHub Actions nicht kann.

Die Zugangsdaten stehen in einer Datei ausserhalb des Repos und werden von
diesem Skript nur gelesen, nie ausgegeben. Standardpfad: ~/.kusaidia-ftp

    host=kusaidia-afrika.de
    user=DER_BENUTZERNAME
    password=DAS_PASSWORT
    dir=public_html

Anlegen und absichern:

    touch ~/.kusaidia-ftp && chmod 600 ~/.kusaidia-ftp

Aufruf:

    python3 tools/_ftp_upload.py            # laedt hoch
    python3 tools/_ftp_upload.py --probe    # meldet sich nur an, laedt nichts
    python3 tools/_ftp_upload.py --dry-run  # zeigt, was hochgeladen wuerde

Zum Zertifikat: Contabo liefert auf Port 21 ein gueltiges Sectigo-Zertifikat,
das aber auf *.contabo.net lautet und nicht auf kusaidia-afrika.de. Die Kette
wird deshalb geprueft, der Namensabgleich abgeschaltet - sonst bricht jede
Verbindung ab.
"""

import argparse
import fnmatch
import os
import ssl
import sys
from ftplib import FTP_TLS, all_errors, error_perm
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Dieselben Ausschluesse wie in .github/workflows/deploy.yml
AUSSCHLUSS = [
    ".git", ".github", "tools", ".gitignore",
    "README.md", "DEPLOY.md", "build-handbuch.py",
    "_archive_*.html", "_cdx.json", "_content.md", "_extract.py",
    "*.swp", ".DS_Store",
]


def ausgeschlossen(rel: Path) -> bool:
    teile = rel.parts
    for muster in AUSSCHLUSS:
        if any(fnmatch.fnmatch(t, muster) for t in teile):
            return True
    return False


def dateien():
    for pfad in sorted(REPO.rglob("*")):
        if not pfad.is_file():
            continue
        rel = pfad.relative_to(REPO)
        if not ausgeschlossen(rel):
            yield rel


def zugang(pfad: Path) -> dict:
    if not pfad.exists():
        sys.exit(
            f"Zugangsdatei {pfad} fehlt.\n"
            "Anlegen mit: touch ~/.kusaidia-ftp && chmod 600 ~/.kusaidia-ftp\n"
            "Inhalt siehe Kopf dieses Skripts."
        )
    if pfad.stat().st_mode & 0o077:
        print(f"Warnung: {pfad} ist fuer andere lesbar. Besser: chmod 600 {pfad}")

    daten = {}
    for zeile in pfad.read_text(encoding="utf-8").splitlines():
        zeile = zeile.strip()
        if not zeile or zeile.startswith("#") or "=" not in zeile:
            continue
        schluessel, wert = zeile.split("=", 1)
        daten[schluessel.strip().lower()] = wert.strip()

    fehlend = [k for k in ("host", "user", "password") if not daten.get(k)]
    if fehlend:
        sys.exit(f"In {pfad} fehlt: {', '.join(fehlend)}")
    daten.setdefault("dir", "")
    return daten


def verbinden(daten: dict) -> FTP_TLS:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False  # Zertifikat lautet auf *.contabo.net
    ftp = FTP_TLS(context=ctx, timeout=60)
    ftp.connect(daten["host"], 21)
    ftp.auth()
    ftp.login(daten["user"], daten["password"])
    ftp.prot_p()
    ftp.set_pasv(True)
    return ftp


def sicherstellen(ftp: FTP_TLS, verzeichnis: str, bekannt: set) -> None:
    """Legt ein Verzeichnis an, falls noetig - Pfad fuer Pfad."""
    if not verzeichnis or verzeichnis in bekannt:
        return
    eltern = os.path.dirname(verzeichnis)
    sicherstellen(ftp, eltern, bekannt)
    try:
        ftp.mkd(verzeichnis)
    except error_perm as fehler:
        if not str(fehler).startswith("550"):  # 550 = gibt es schon
            raise
    bekannt.add(verzeichnis)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zugang", type=Path, default=Path.home() / ".kusaidia-ftp")
    p.add_argument("--probe", action="store_true", help="nur anmelden")
    p.add_argument("--dry-run", action="store_true", help="nichts hochladen")
    args = p.parse_args()

    liste = list(dateien())
    umfang = sum((REPO / f).stat().st_size for f in liste)
    print(f"{len(liste)} Dateien, {umfang / 1_048_576:.1f} MB")

    if args.dry_run:
        for rel in liste:
            print("  ", rel)
        return 0

    daten = zugang(args.zugang)
    print(f"Verbinde mit {daten['host']} …")   # nur der Host, nie Benutzer oder Passwort

    try:
        ftp = verbinden(daten)
    except all_errors as fehler:
        print(f"Anmeldung fehlgeschlagen: {fehler}")
        print("421 Home directory not available -> das Verzeichnis des Kontos "
              "fehlt auf dem Server, in cPanel unter 'FTP-Konten' richtigstellen.")
        return 1

    print("Angemeldet.")
    if daten["dir"]:
        ftp.cwd(daten["dir"])
    print(f"Zielverzeichnis: {ftp.pwd()}")

    if args.probe:
        ftp.quit()
        return 0

    bekannt: set = set()
    for nummer, rel in enumerate(liste, 1):
        ziel = rel.as_posix()
        sicherstellen(ftp, os.path.dirname(ziel), bekannt)
        with open(REPO / rel, "rb") as f:
            ftp.storbinary(f"STOR {ziel}", f)
        print(f"  [{nummer}/{len(liste)}] {ziel}")

    ftp.quit()
    print("Fertig.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
