# Bedienungsanleitung: Kolosseum 3D

Diese Anleitung beschreibt die Bedienung des 3D-Modells von Rom (`roma3d.html`): Navigation, Ansichten, Radfahrt, Nachtmodus, Screenshots und den Live-Ergometer-Modus.

---

## 1. Starten

**Online:** https://helmutqualtinger.github.io/roma/

**Lokal:** Die Datei `roma3d.html` im Browser öffnen. Ein Server oder Build-Schritt ist nicht nötig. Die Szene wird beim Start aufgebaut; bis dahin erscheint der Hinweis „Szene wird aufgebaut …“.

**Empfohlen:** Chrome, Edge, Safari oder Firefox mit aktivierter WebGL-Unterstützung. Auf schwächeren Geräten kann die Bildrate sinken. Das Programm passt dann die Auflösung automatisch an.

### Sprache

Die Oberfläche gibt es auf Deutsch, Englisch, Italienisch und Französisch. Umschalten über das Auswahlfeld rechts oben (🇩🇪 🇬🇧 🇮🇹 🇫🇷). Die Wahl wird gespeichert.

Beim ersten Aufruf richtet sich die Sprache nach dem Browser; ohne passende Sprache wird Deutsch verwendet. Über die Adresse lässt sich die Sprache direkt festlegen, z. B. `roma3d.html?lang=en`.

---

## 2. Navigation im Modell

| Aktion | Maus / Trackpad | Touch |
|---|---|---|
| Drehen (um den Mittelpunkt) | Linke Taste ziehen | Mit einem Finger ziehen |
| Verschieben | Rechte Taste ziehen | Mit zwei Fingern ziehen |
| Zoomen | Mausrad oder Trackpad-Geste | Zwei Finger zusammen- oder auseinanderziehen |
| Hinfliegen | Kurz auf einen Punkt klicken: Die Kamera fliegt dorthin und kommt mit jedem Klick näher (bis 80 m) | Kurz tippen |

- Die Kamera lässt sich bis unter die Horizontale drehen, um in den Himmel zu schauen (nachts sichtbar: Sterne und Mond).
- Der Zoom ist begrenzt: näher als 25 m oder weiter als 5 km geht es nicht.
- Während der Radfahrt ist die freie Navigation gesperrt; die Kamera folgt dem Fahrer.

---

## 3. Schaltflächen und Auswahl

| Element | Funktion |
|---|---|
| **Orte …** (Auswahlliste) | Die Kamera fliegt zu einer Ansicht: *Google-Earth-Ansicht*, *Kolosseum nah*, *Piazza Venezia*, *Konstantinsbogen*, *Draufsicht* oder zu einer beschrifteten Sehenswürdigkeit. Während einer Radfahrt nicht verfügbar. |
| **Rundflug** | Die Kamera kreist automatisch um die Szene. Erneut klicken beendet den Rundflug. |
| **Beschriftung** | Beschriftungen von Sehenswürdigkeiten ein- und ausblenden. |
| **Route** | Die Routenlinie auf dem Boden ein- und ausblenden. |
| **Nacht** | Nachtmodus ein- und ausschalten (siehe Abschnitt 6). |
| **Radfahrt ▶** | Radfahrt starten (siehe Abschnitt 4). |
| **Musik ♪** | Hintergrundmusik in Endlosschleife: startet und pausiert „Eye of the Tiger“ (`data/eyeOfTheToger.mp3`, nur lokal vorhanden). Fehlt die Datei, zum Beispiel auf GitHub Pages, wählst du eine eigene Audiodatei; der Browser merkt sie sich. Shift-Klick wählt eine andere Datei. |
| **Rad 🚴 / Laufen 🏃** | Wechselt zwischen Radfahrer und Läufer. Im Läufermodus laufen auch „Last Round“ und „Pacemaker“ als Läufer, und die Geschwindigkeit folgt einer Laufphysik: dieselbe Leistung ergibt etwa ein Drittel der Radgeschwindigkeit (180 W bei 79 kg ≈ 8 km/h in der Ebene). Im Läufermodus ist überall vom Lauf statt vom Rad die Rede (Knöpfe, Kamera, Anzeige der Schrittfrequenz), das Gewichtsfeld zeigt das Gewicht des Läufers. Die Wahl bleibt gespeichert. |
| **Kamera: hinter Rad / Drohne** | Kameramodus der Radfahrt wechseln. |
| **Tempo** (Regler) | Abspielgeschwindigkeit der Radfahrt im Demo-Modus, von 1 bis 10. |
| **Screenshot 4K** | Bild mit 3840 × 2160 Pixeln speichern. |
| **Screenshot 8K** | Bild mit 7680 × 4320 Pixeln speichern. Das braucht viel Speicher und dauert länger. |

### Direktaufruf von Ansichten

Über die Adresse öffnet sich eine Ansicht direkt:

| Adresse | Ansicht |
|---|---|
| `roma3d.html#ge` | Google-Earth-Ansicht (Standard) |
| `roma3d.html#close` | Kolosseum nah |
| `roma3d.html#venezia` | Piazza Venezia |
| `roma3d.html#arco` | Konstantinsbogen |
| `roma3d.html#top` | Draufsicht |

### Weitere Adressoptionen

| Option | Wirkung |
|---|---|
| `?night` | Startet im Nachtmodus. |
| `?lang=de\|en\|it\|fr` | Setzt die Sprache. |
| `#ride` | Startet direkt die Radfahrt. |
| `?t=<Sekunden>#ride` | Startet die Radfahrt und spult die angegebene Zeit vor, z. B. `?t=60#ride`. |
| `?drone` | Startet die Radfahrt mit der Drohnenkamera. |
| `?live` | Startet direkt im Live-Ergometer-Modus (siehe Abschnitt 5). |
| `?info` | Schreibt Angaben zur Grafiklast (Draw Calls, Dreiecke) in die Browser-Konsole. |

---

## 4. Radfahrt

Die Radfahrt (6,1 km) führt von der Piazza Venezia über den Circo Massimo, um das Kolosseum herum, die Via Cavour hinauf zum Bahnhof Termini und über die Piazza della Repubblica und die Via Nazionale zurück. Die Route ist als Neonlinie am Boden markiert. Die Fahrt geht Runde um Runde weiter, bis sie gestoppt wird.

### Starten und Stoppen

- **Radfahrt ▶** klicken, um zu starten. Die Schaltfläche zeigt dann **Radfahrt ❚❚**.
- Erneut klicken, um die Fahrt anzuhalten. Die Schaltfläche zeigt wieder **Radfahrt ▶**, und ein weiterer Klick setzt die Fahrt fort.
- Beim Stoppen kehrt die Kamera zur Übersichtsansicht zurück und die freie Navigation ist wieder aktiv.

### Anzeigen während der Fahrt

Oben rechts erscheinen diese Werte und ein Höhenprofil der Strecke:

- **Steigung** in Prozent
- **Geschwindigkeit** in km/h
- **Leistung** in Watt
- **Höhe** in Metern über dem Meer
- **Last Round:** Zeitabstand zum roten Geist, der ab der zweiten Runde die vorige Runde nachfährt
- **Pacemaker:** Zeitabstand zum blauen Pacemaker, der mit der Leistung aus dem Feld **Pacemaker** fährt

Die Laufschrift unten zeigt Runde, Position in der Runde und die Zeit der letzten Runde.

Der gelbe Punkt im Höhenprofil zeigt die aktuelle Position auf der Strecke.

### Kamera

- **Kamera: hinter Rad**: Die Kamera folgt dem Fahrer dicht von hinten. Ein Löwe läuft etwa 3,5 bis 4,5 m hinter dem Fahrer mit.
- **Kamera: Drohne**: Die Drohne kreist um Fahrer und Löwen; eine Umrundung dauert 36 Sekunden.

Der Wechsel zwischen beiden Modi ist fließend.

### Demo-Modus

Ohne angeschlossenen Ergometer fährt ein simulierter Fahrer die Strecke. Die Geschwindigkeit legt der Regler **Tempo** fest. Dieser Modus ist die Standardfahrt.

---

## 5. Live-Ergometer (optional)

Der Live-Modus misst die echte Trittleistung an einem angeschlossenen Ergometer und steuert dessen Widerstand nach der Steigung der Strecke.

### Voraussetzungen

Der Live-Modus funktioniert nur, wenn der Ergometer-Server die Seite ausliefert. Im Projektordner `~/Ergometer` starten:

```
uv run ergometer.py --panel --site ~/roma
```

Danach im Browser öffnen:

```
http://127.0.0.1:8050/site/roma3d.html
```

Auf GitHub Pages, einem anderen Webserver oder direkt über `file://` läuft die Seite im Demo-Modus, ohne Fehlermeldung.

### Bedienung

1. **Live-Ergometer** klicken. Der Modus startet einen Lauf auf dem Server, damit die Fahrt protokolliert wird.
2. Das **Gewicht** (Standard 88 kg) eintragen. Es wird gespeichert und fließt in die Physik der Fahrt ein.
3. Das Rennen beginnt mit dem ersten Tritt. Vorher wartet der Fahrer an der Startlinie.
4. Der Widerstand des Ergometers passt sich der Steigung der nächsten 100 m an. Die Anzeige **Widerstand** zeigt die aktuelle Stufe (7 bis 15).
5. **Pause ❚❚** oder die Leertaste (außerhalb von Eingabefeldern) hält das Rennen an und setzt den Widerstand auf die niedrigste Stufe.
6. **Speichern ⤓** lädt die Fahrt seit dem Rennstart als CSV-Datei (`roma-ride-<Startzeit>.csv`) herunter. Die Datei enthält pro Sekunde Zeit, Runde, Strecke, Tempo, Leistung, Trittfrequenz, Widerstand, Puls, Steigung, Höhe, Position sowie die Abstände zu den Vergleichsfahrern.

### Vergleichsfahrer

- **Geist (rot):** Ab der zweiten Runde fährt die vorherige Runde des Fahrers als durchscheinende rote Figur nebenher. **Last Round** zeigt den Zeitunterschied. Auch die normale Radfahrt fährt Runde um Runde, der Geist erscheint dort ebenfalls ab der zweiten Runde.
- **Pacemaker (blau):** Eine Figur fährt mit konstanter Leistung, die im Feld **Pacemaker** (Standard 150 W) eingestellt wird, auch in der normalen Radfahrt. Die Anzeige **Pacemaker** zeigt den Zeitunterschied in beide Richtungen. Zu jeder neuen Runde wird der Pacemaker wieder auf die Position des Fahrers gesetzt.

### Zusatzanzeigen im Live-Modus

- **Trittfrequenz** in U/min
- **Runde**: aktuelle Runde und Rundenzeit

### Wenn der Ergometer fehlt

Ist kein Ergometer verbunden, nach 30 Sekunden ohne Messwerte oder bei abgebrochener Verbindung wechselt die Anzeige in den Demo-Modus. Der erste Tritt mit Messwert schaltet automatisch wieder auf Live.

---

## 6. Nachtmodus

**Nacht** schaltet Himmel, Licht und Beleuchtung um:

- Sternenhimmel mit Mond
- beleuchtete Fenster und Schaufenster; einzelne Fenster gehen nach und nach an und aus
- Straßenlaternen mit Lichtkegeln
- angestrahltes Kolosseum, Vittoriano, Pantheon und Trevi-Brunnen

Die Radfahrt funktioniert im Nachtmodus wie am Tag. Ein Scheinwerfer an der Kamera leuchtet dabei den Radfahrer und den Löwen an.

---

## 7. Screenshots

- **Screenshot 4K** und **Screenshot 8K** rendern die aktuelle Ansicht in hoher Auflösung und laden sie als Bilddatei herunter.
- Für eine gute Aufnahme vorher die gewünschte Ansicht, Beschriftung und Tageszeit einstellen.

---

## 8. Tipps und Fehlerbehebung

| Problem | Abhilfe |
|---|---|
| Die Szene bleibt bei „Szene wird aufgebaut …“ hängen | Seite neu laden. Der Browser braucht WebGL; ein Test ist unter https://get.webgl.org möglich. |
| Die Bildrate ist niedrig | Die Ansicht „Kolosseum nah“ oder den Nachtmodus ausschalten. Die Auflösung passt sich automatisch an. |
| Die Radfahrt startet nicht oder hängt | Die Fahrt mit **Radfahrt** stoppen und neu starten. |
| Der Live-Modus läuft als Demo | Prüfen, ob der Ergometer-Server läuft und die Seite über `http://127.0.0.1:8050/site/roma3d.html` geöffnet wurde. |
| Die Schrift ist nicht in der richtigen Sprache | Im Auswahlfeld die Sprache wechseln oder `?lang=` in der Adresse setzen. |

---

## 9. Quellen

Kartendaten © [OpenStreetMap](https://www.openstreetmap.org/copyright)-Mitwirkende, ODbL. Three.js r0.165 wird von jsDelivr geladen.
