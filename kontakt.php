<?php
/**
 * Verarbeitung des Kontaktformulars.
 *
 * Schickt die Anfrage an den Verein und eine Eingangsbestätigung an die
 * absendende Person. Läuft nur auf dem Contabo-Webspace (PHP), nicht auf
 * GitHub Pages.
 *
 * Sicherheitsgrundsätze:
 *  - Der Empfänger ist fest verdrahtet und stammt nie aus der Eingabe.
 *  - In Mail-Headern landet ausschließlich geprüfter Inhalt; Zeilenumbrüche
 *    werden vorher entfernt (Schutz vor Header-Injection).
 *  - Alle Felder sind längenbegrenzt, die Ausgabe wird maskiert.
 *  - Honeypot-Feld und IP-Ratenbegrenzung gegen automatisierte Einsendungen.
 */

declare(strict_types=1);

// ---------------------------------------------------------------- Konfiguration

/** Empfänger im Verein – bewusst hier hinterlegt, nie aus dem Formular. */
const EMPFAENGER = 'kontakt@kusaidia-afrika.de';

/** Absender aller ausgehenden Mails. Muss zur Domain gehören, sonst
 *  scheitert die SPF-Prüfung und die Mail landet im Spam. */
const ABSENDER = 'kontakt@kusaidia-afrika.de';

/** Höchstens so viele Einsendungen je IP innerhalb des Zeitfensters. */
const LIMIT_ANZAHL  = 3;
const LIMIT_FENSTER = 900; // Sekunden (15 Minuten)

/** Längengrenzen, damit niemand riesige Datenmengen einschleust. */
const MAX_NAME    = 100;
const MAX_BETREFF = 150;
const MAX_TEXT    = 5000;

// ---------------------------------------------------------------- Hilfsfunktionen

/**
 * Entfernt alles, was eine neue Header-Zeile beginnen könnte.
 * Ohne diesen Schritt könnte jemand über ein Eingabefeld zusätzliche
 * Empfänger oder Header in die Mail schmuggeln.
 */
function kopfzeilen_saeubern(string $wert): string
{
    return trim(str_replace(["\r", "\n", "\0", '%0a', '%0d'], '', $wert));
}

/** Kodiert einen Betreff regelkonform, damit Umlaute nicht zerfallen. */
function betreff_kodieren(string $betreff): string
{
    return '=?UTF-8?B?' . base64_encode($betreff) . '?=';
}

/** Kürzt auf eine Höchstlänge, ohne Mehrbyte-Zeichen zu zerschneiden. */
function kuerzen(string $wert, int $max): string
{
    return function_exists('mb_substr')
        ? mb_substr($wert, 0, $max, 'UTF-8')
        : substr($wert, 0, $max);
}

/**
 * Einfache Ratenbegrenzung je IP-Adresse über eine Datei im temporären
 * Verzeichnis. Gibt false zurück, wenn das Kontingent erschöpft ist.
 */
function kontingent_frei(): bool
{
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unbekannt';
    $datei = sys_get_temp_dir() . '/kusaidia-kontakt-' . sha1($ip) . '.txt';

    $jetzt = time();
    $zeiten = [];
    if (is_readable($datei)) {
        $inhalt = (string) file_get_contents($datei);
        foreach (explode(',', $inhalt) as $eintrag) {
            $zeitpunkt = (int) $eintrag;
            if ($zeitpunkt > $jetzt - LIMIT_FENSTER) {
                $zeiten[] = $zeitpunkt;
            }
        }
    }

    if (count($zeiten) >= LIMIT_ANZAHL) {
        return false;
    }

    $zeiten[] = $jetzt;
    @file_put_contents($datei, implode(',', $zeiten), LOCK_EX);
    return true;
}

/** Gibt eine Rückmeldeseite im Seitendesign aus und beendet das Skript. */
function seite_ausgeben(string $titel, string $text, bool $erfolg = true): void
{
    $t = htmlspecialchars($titel, ENT_QUOTES, 'UTF-8');
    $b = htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
    http_response_code($erfolg ? 200 : 400);
    echo <<<HTML
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{$t} – Kusaidia Afrika</title>
  <meta name="robots" content="noindex" />
  <link rel="stylesheet" href="css/style.css">
  <link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
</head>
<body>
<main id="main">
  <header class="page-head">
    <div class="page-head__inner">
      <span class="eyebrow">Kontakt</span>
      <h1>{$t}</h1>
      <p class="page-head__lead">{$b}</p>
    </div>
  </header>
  <section class="section">
    <div class="container container--narrow">
      <p><a class="btn btn--primary" href="index.html">Zur Startseite</a></p>
    </div>
  </section>
</main>
</body>
</html>
HTML;
    exit;
}

// ---------------------------------------------------------------- Ablauf

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Location: kontakt.html');
    exit;
}

// Honeypot: Das Feld ist für Menschen unsichtbar. Ist es ausgefüllt, war es
// ein Bot. Wir melden trotzdem Erfolg, damit er nichts dazulernt.
if (trim((string) ($_POST['website'] ?? '')) !== '') {
    seite_ausgeben('Vielen Dank', 'Ihre Nachricht wurde übermittelt.');
}

$name    = kuerzen(trim((string) ($_POST['name'] ?? '')), MAX_NAME);
$email   = kopfzeilen_saeubern((string) ($_POST['email'] ?? ''));
$betreff = kuerzen(kopfzeilen_saeubern((string) ($_POST['subject'] ?? '')), MAX_BETREFF);
$text    = kuerzen(trim((string) ($_POST['message'] ?? '')), MAX_TEXT);

if ($name === '' || $text === '') {
    seite_ausgeben('Angaben unvollständig',
        'Bitte füllen Sie Name und Nachricht aus und senden Sie das Formular erneut.', false);
}

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    seite_ausgeben('E-Mail-Adresse prüfen',
        'Die angegebene E-Mail-Adresse ist nicht gültig. Bitte korrigieren Sie sie und senden Sie erneut.', false);
}

// Der Name geht in keinen Header ein, aber Zeilenumbrüche haben auch im
// Fließtext nichts zu suchen.
$name = kopfzeilen_saeubern($name);

if ($betreff === '') {
    $betreff = 'Anfrage über die Website';
}

if (!kontingent_frei()) {
    seite_ausgeben('Bitte etwas später erneut',
        'Von diesem Anschluss wurden gerade mehrere Nachrichten gesendet. '
        . 'Bitte versuchen Sie es in einer Viertelstunde noch einmal oder schreiben Sie direkt an '
        . EMPFAENGER . '.', false);
}

// --- Mail an den Verein -------------------------------------------------

$anVerein = "Name:    {$name}\n"
          . "E-Mail:  {$email}\n"
          . "Betreff: {$betreff}\n"
          . "\n"
          . "Nachricht:\n{$text}\n";

$headerVerein = [
    'From: Kusaidia Afrika Website <' . ABSENDER . '>',
    'Reply-To: ' . $email,   // geprüft, enthält keine Zeilenumbrüche
    'Content-Type: text/plain; charset=UTF-8',
    'MIME-Version: 1.0',
    'X-Mailer: Kusaidia Kontaktformular',
];

$gesendet = @mail(
    EMPFAENGER,
    betreff_kodieren('Kontaktformular: ' . $betreff),
    $anVerein,
    implode("\r\n", $headerVerein)
);

if (!$gesendet) {
    seite_ausgeben('Senden fehlgeschlagen',
        'Ihre Nachricht konnte technisch nicht zugestellt werden. '
        . 'Bitte schreiben Sie uns direkt an ' . EMPFAENGER . '.', false);
}

// --- Eingangsbestätigung an die absendende Person ------------------------

$anAbsender = "Guten Tag {$name},\n\n"
            . "vielen Dank für Ihre Nachricht an Kusaidia Afrika – Helfen in Afrika – e.V.\n"
            . "Wir haben sie erhalten und melden uns in der Regel innerhalb weniger Tage.\n\n"
            . "Ihre Nachricht im Wortlaut:\n"
            . str_repeat('-', 40) . "\n"
            . "Betreff: {$betreff}\n\n"
            . "{$text}\n"
            . str_repeat('-', 40) . "\n\n"
            . "Diese Bestätigung wurde automatisch erzeugt – bitte antworten Sie nicht darauf.\n"
            . "Sie erreichen uns unter " . EMPFAENGER . ".\n\n"
            . "Kusaidia Afrika – Helfen in Afrika – e.V.\n";

$headerAbsender = [
    'From: Kusaidia Afrika <' . ABSENDER . '>',
    'Content-Type: text/plain; charset=UTF-8',
    'MIME-Version: 1.0',
    'Auto-Submitted: auto-replied',
    'X-Mailer: Kusaidia Kontaktformular',
];

// Schlägt die Bestätigung fehl, ist die Anfrage trotzdem angekommen –
// das melden wir der Person unten offen.
$bestaetigt = @mail(
    $email,
    betreff_kodieren('Ihre Nachricht an Kusaidia Afrika'),
    $anAbsender,
    implode("\r\n", $headerAbsender)
);

seite_ausgeben(
    'Vielen Dank',
    $bestaetigt
        ? 'Ihre Nachricht ist bei uns eingegangen. Eine Bestätigung haben wir an ' . $email . ' geschickt.'
        : 'Ihre Nachricht ist bei uns eingegangen. Die Bestätigungsmail konnte nicht zugestellt werden – '
          . 'wir melden uns dennoch bei Ihnen.'
);
