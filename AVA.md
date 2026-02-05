# User Story: AVA Desktop-App für SHK-Installateure

## Standalone GAEB-Tool für Handwerksbetriebe

---

## Story

**Als** SHK-Installateur (Wasser, Gas, Kanal)
**möchte ich** GAEB-Dateien öffnen, Angebote kalkulieren und Abrechnungen erstellen
**damit** ich Ausschreibungen von Kommunen und Generalunternehmern professionell bearbeiten kann, ohne teure AVA-Software kaufen zu müssen.

---

## Kontext

AVA (Ausschreibung, Vergabe, Abrechnung) ist der Standardprozess im Bauwesen. GAEB-Dateien sind der de-facto Standard für den Datenaustausch. Bestehende Software (ORCA AVA, California.pro) kostet €2.000–6.000/Lizenz und ist für Architekten/Planer gebaut — zu komplex und zu teuer für kleine Handwerksbetriebe.

**Zielgruppe:** Kleine SHK-Betriebe (2–10 Mitarbeiter) im DACH-Raum, die:
- Ausschreibungen von Kommunen/GUs als GAEB empfangen
- Angebote mit eigenen Preisen erstellen müssen
- Aufmaße auf der Baustelle erfassen
- Abrechnungen nach Projektabschluss erstellen
- Aktuell mit Excel und manuellen Templates arbeiten

**Branche:** Sanitär, Heizung, Klima (SHK) — StLB-Bau Bereiche 040–046

---

## Typischer Workflow

```
1. AUSSCHREIBUNG empfangen
   Kommune/GU sendet .x83 (LV mit Mengen, ohne Preise)

2. ANGEBOT kalkulieren
   → Positionen durchgehen
   → Material + Lohn + Zuschläge = Einheitspreis (EP)
   → Export als .x84

3. AUFTRAG erhalten
   → Vergabe-Datei (.x84) importieren
   → Projekt-Status auf "Auftrag" setzen

4. AUFMASS erfassen
   → Tatsächliche Mengen auf der Baustelle dokumentieren
   → Export als .x86

5. ABRECHNUNG erstellen
   → Aufmaß-Mengen × EP = Rechnungssumme
   → Export als .x89 oder PDF
```

---

## Akzeptanzkriterien

### 1. GAEB-Import (Must Have)

- [ ] **GAEB XML 3.x** (.x81, .x83, .x84, .x86, .x89) vollständig parsen
- [ ] **GAEB 2000** (.d81, .d83, .d84, .d86, .d89) parsen
- [ ] **GAEB 90** (.d81, .d83, .d84) parsen (Legacy-Support)
- [ ] Automatische Formaterkennung anhand Dateiinhalt (nicht nur Extension)
- [ ] Fehlertolerantes Parsing (reale Dateien weichen oft vom Schema ab)

### 2. Datenmodell (Must Have)

Einheitliches internes Modell unabhängig vom Quellformat:

```
Projekt
├── Metadaten (Auftraggeber, Datum, Vergabeart, Status)
├── Leistungsverzeichnis (LV)
│   ├── Lose
│   │   ├── Titel/Bereiche
│   │   │   ├── Positionen
│   │   │   │   ├── Ordnungszahl (OZ)
│   │   │   │   ├── Kurztext / Langtext
│   │   │   │   ├── Menge + Einheit
│   │   │   │   ├── Einheitspreis (EP)
│   │   │   │   ├── Gesamtpreis (GP = Menge × EP)
│   │   │   │   └── Positionsart (Normal, Eventual, Bedarfs, Alternativ)
├── Kalkulation (EP-Aufgliederung)
│   ├── Materialkosten
│   ├── Lohnkosten (Stunden × Stundensatz)
│   └── Zuschläge (Gemeinkosten, Gewinn, Wagnis)
├── Aufmaße (bei laufenden Projekten)
│   ├── Aufmaß-Blätter
│   │   ├── Position-Referenz
│   │   ├── Ist-Menge
│   │   └── Bemerkung
└── Projekthistorie (Statusänderungen)
```

### 3. Positionseditor (Must Have)

- [ ] Positionsliste als Tabelle (OZ, Text, Menge, Einheit, EP, GP)
- [ ] Positionen hinzufügen, bearbeiten, löschen
- [ ] Drag & Drop zum Umsortieren
- [ ] Suche/Filter über Positionen
- [ ] Summenzeilen pro Titel/Bereich/Los
- [ ] Gesamtsumme (Netto, MwSt, Brutto)

### 4. Preiskalkulation (Must Have)

- [ ] EP-Aufgliederung: Material + Lohn + Zuschläge
- [ ] Stundensätze pro Mitarbeiter/Qualifikation konfigurierbar
- [ ] Materialpreise aus Stammdaten übernehmen
- [ ] Zuschlagssätze (Gemeinkosten %, Gewinn %, Wagnis %)
- [ ] Nachlass-Berechnung

### 5. Stammdaten (Must Have)

- [ ] Eigene Leistungstexte speichern und wiederverwenden
- [ ] Materialpreisliste pflegen (Artikel, Einheit, Preis, Lieferant)
- [ ] Stundensätze konfigurieren (Geselle, Meister, Azubi)
- [ ] Firmenstammdaten (Name, Adresse, Steuernummer, Bankverbindung)

### 6. Projektübersicht (Must Have)

- [ ] Liste aller Projekte mit Status-Anzeige
- [ ] Status: Ausschreibung → Angebot → Auftrag → In Arbeit → Abgerechnet
- [ ] Sortierung/Filter nach Status, Datum, Auftraggeber
- [ ] Projekt duplizieren (als Vorlage nutzen)

### 7. Excel-Import/Export (Should Have)

- [ ] Strukturierte LV-Tabellen einlesen (Spalten: OZ, Text, Menge, Einheit, EP, GP)
- [ ] Flexible Spaltenerkennung (Header-Mapping konfigurierbar)
- [ ] Export als Excel mit Formeln für Summen
- [ ] Kalkulationsfreundliches Format

### 8. GAEB-Datei neu anlegen (Must Have)

- [ ] Leere GAEB-Datei erstellen (Typ wählbar: Ausschreibung, Angebot, Aufmaß, Abrechnung)
- [ ] Projekt-Metadaten eingeben (Auftraggeber, Bauvorhaben, Datum)
- [ ] Positionen manuell hinzufügen (OZ, Text, Menge, Einheit, EP)
- [ ] Titel/Bereiche/Lose strukturieren
- [ ] Als GAEB XML 3.3 oder GAEB 2000 speichern
- [ ] Vorlage aus bestehendem Projekt erstellen (Positionen ohne Preise/Mengen)

### 9. GAEB-Dateien mergen (Should Have)

- [ ] Zwei oder mehr GAEB-Dateien zusammenführen
- [ ] Merge-Strategien:
  - Positionen ergänzen (OZ-Bereiche aus verschiedenen Dateien kombinieren)
  - Preise übernehmen (Preise aus Datei A auf Positionen von Datei B anwenden)
  - Mengen aktualisieren (Aufmaß-Mengen auf Angebotspositionen übertragen)
- [ ] Konflikterkennung bei gleichen OZ mit unterschiedlichen Daten
- [ ] Vorschau vor dem Merge (Diff-Ansicht: was wird hinzugefügt/geändert)
- [ ] Undo nach Merge

### 10. GAEB-Export (Must Have)

- [ ] Internes Modell → GAEB XML 3.2/3.3 (.x84 Angebot, .x86 Aufmaß, .x89 Abrechnung)
- [ ] Internes Modell → GAEB 2000 (für ältere Systeme)
- [ ] Schema-Validierung vor Export

### 11. PDF-Ausgabe (Should Have)

- [ ] Angebot als PDF mit Firmenbriefkopf
- [ ] Aufmaß-Blatt als PDF
- [ ] Rechnung als PDF
- [ ] Konfigurierbare Templates

### 12. Aufmaß-Erfassung (Should Have)

- [ ] Aufmaß-Blätter pro Position anlegen
- [ ] Ist-Mengen erfassen mit Kommentar
- [ ] Vergleich Soll/Ist-Mengen
- [ ] Automatische Übernahme in Abrechnung

---

## Technische Anforderungen

### Plattform: Electron + TypeScript

Gründe:
- Desktop-App, offline-fähig (Baustelle hat oft kein Internet)
- Cross-Platform (Windows primär, macOS sekundär)
- TypeScript für Typsicherheit bei komplexem Datenmodell
- Lokale Datenhaltung (SQLite oder JSON-Files)

### Architektur

```
ava-app/
├── src/
│   ├── main/                    # Electron Main Process
│   │   ├── main.ts
│   │   ├── ipc/                 # IPC Handler
│   │   └── storage/             # Persistenz (SQLite/JSON)
│   ├── renderer/                # UI
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── ProjectList.tsx  # Projektübersicht
│   │   │   ├── ProjectEditor.tsx # LV-Editor
│   │   │   ├── Calculation.tsx  # EP-Kalkulation
│   │   │   ├── Measurement.tsx  # Aufmaß
│   │   │   └── Settings.tsx     # Stammdaten
│   │   └── components/
│   │       ├── PositionTable.tsx # Positions-Tabelle
│   │       ├── PriceCalc.tsx    # Preis-Rechner
│   │       └── FileImport.tsx   # Datei-Import Dialog
│   ├── domain/                  # Business Logic
│   │   ├── model/               # Datenmodell (Projekt, Position, etc.)
│   │   ├── gaeb/                # GAEB Parser & Writer
│   │   │   ├── parser.ts        # Unified Parser Interface
│   │   │   ├── xml3/            # GAEB XML 3.x
│   │   │   ├── gaeb2000/        # GAEB 2000
│   │   │   ├── gaeb90/          # GAEB 90
│   │   │   ├── detect.ts        # Format-Erkennung
│   │   │   └── writer.ts        # GAEB Export
│   │   ├── excel/               # Excel Import/Export
│   │   └── calculation/         # Preiskalkulation
│   └── preload.ts
├── assets/                      # Icons, Templates
├── testdata/                    # GAEB Testdateien
│   ├── gaeb90/
│   ├── gaeb2000/
│   └── gaebxml/
├── package.json
├── tsconfig.json
└── electron-builder.yml
```

### Dependencies

- `fast-xml-parser` — XML Parsing (schnell, fehlertolerant)
- `exceljs` — Excel Read/Write
- `better-sqlite3` — Lokale Datenbank
- `pdfmake` oder `puppeteer` — PDF-Erzeugung
- `react` + `react-dom` — UI
- `ag-grid-react` oder `tanstack-table` — Tabellen-Komponente

### Schema-Quellen

- GAEB XML Schema: Reverse Engineering aus Beispieldateien + [Dangl-Dokumentation](https://www.dangl-it.com/articles/the-gaeb-data-formats-in-detail/)
- Beispieldateien: [GitHub Gist (Georg Dangl)](https://gist.github.com/GeorgDangl/29c8069c6fffac955f07d2c012249819)
- Kostenloser Viewer zum Vergleich: [WebGAEB](https://www.web-gaeb.de)

---

## Nicht-funktionale Anforderungen

| Anforderung             | Zielwert                                       |
| ----------------------- | ---------------------------------------------- |
| Parsing-Geschwindigkeit | < 200ms für typische LV-Datei (500 Positionen) |
| Speicher                | < 200MB RAM im Betrieb                         |
| Fehlertoleranz          | Graceful Degradation bei Schema-Abweichungen   |
| Testabdeckung           | > 80% für Parser + Kalkulations-Code           |
| Offline                 | 100% offline-fähig, keine Cloud-Abhängigkeit   |
| Startup                 | < 3s bis zur Projektliste                      |
| Plattform               | Windows 10+ (primär), macOS 12+ (sekundär)     |

---

## Beispiel-Workflow: Angebot auf Ausschreibung

```typescript
// 1. GAEB-Datei öffnen (Ausschreibung von der Kommune)
const project = await gaeb.parse(fs.readFileSync('ausschreibung.x83'));
// → Projekt mit 120 Positionen, keine Preise

// 2. Positionen anzeigen
project.positions.forEach(pos => {
  console.log(`${pos.oz} | ${pos.shortText} | ${pos.quantity} ${pos.unit} | EP: ---`);
});

// 3. Preise kalkulieren
const pos = project.positions[0]; // "Kupferrohr 22mm verlegen"
pos.calculation = {
  material: 12.50,    // €/m Kupferrohr
  labor: 0.15 * 48,   // 0.15h × 48€/h Stundensatz
  surcharge: 0.18,     // 18% Zuschlag (GK + Gewinn)
};
pos.unitPrice = (pos.calculation.material + pos.calculation.labor) * (1 + pos.calculation.surcharge);

// 4. Als Angebot exportieren
await gaeb.write(project, 'angebot.x84', { format: 'xml3.3' });

// 5. Als PDF drucken
await pdf.generate(project, 'angebot.pdf', { template: 'offer', letterhead: true });
```

---

## Risiken & Mitigations

| Risiko                                  | Impact | Mitigation                                                       |
| --------------------------------------- | ------ | ---------------------------------------------------------------- |
| GAEB-Schema nicht frei verfügbar        | Hoch   | Reverse Engineering aus Beispieldateien, Dangl-Doku als Referenz |
| Viele fehlerhafte Dateien "in the wild" | Mittel | Fehlertolerantes Parsing, Logging von Abweichungen               |
| Komplexität von GAEB 90 (Festformat)    | Mittel | Fokus auf XML 3.x, GAEB 90 nur Read-Support                     |
| Excel-Formate variieren stark           | Mittel | Konfigurierbares Spalten-Mapping                                 |
| Electron-App-Größe                      | Niedrig | Tree-Shaking, keine unnötigen Dependencies                      |

---

## Offene Fragen

1. **Lizenzierung:** Open Source (MIT) oder proprietär?
2. **ÖNorm-Support:** Österreichisches Format A 2063 — relevant für DACH?
3. **StLB-Bau Texte:** Dürfen wir die Standardtexte einbetten oder nur referenzieren?
4. **Nachträge:** Soll die erste Version Nachtrags-Management unterstützen?
5. **Multi-User:** Braucht der Betrieb Zugriff von mehreren Rechnern?

---

## Referenzen

- [GAEB Formate im Detail (Dangl IT)](https://www.dangl-it.com/articles/the-gaeb-data-formats-in-detail/)
- [GAEB e.V.](https://www.gaeb.de/)
- [Beispieldateien (GitHub Gist)](https://gist.github.com/GeorgDangl/29c8069c6fffac955f07d2c012249819)
- [WebGAEB Viewer (kostenlos)](https://www.web-gaeb.de)
- [gaeb4linux (Open Source)](https://github.com/klaus4772/gaeb4linux)
