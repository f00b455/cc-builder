# Todo-Liste REST API

## User Story

**Als** Anwendungsentwickler
**möchte ich** eine REST API für eine Todo-Liste mit vollständigen CRUD-Operationen
**um** Todo-Einträge programmatisch verwalten zu können und als Backend für Frontend-Anwendungen zu dienen.

## Beschreibung

Die API soll es ermöglichen, Todo-Einträge zu erstellen, zu lesen, zu aktualisieren und zu löschen. Jeder Todo-Eintrag besteht aus:
- **ID**: Eindeutige Identifikation (automatisch generiert)
- **Title**: Titel des Todos (Pflichtfeld)
- **Description**: Detaillierte Beschreibung (optional)
- **Status**: completed (true/false, Standard: false)
- **Created At**: Erstellungszeitpunkt (automatisch)
- **Updated At**: Zeitpunkt der letzten Änderung (automatisch)

## Akzeptanzkriterien

### CRUD Operationen
- [ ] **POST /todos** - Neuen Todo erstellen
  - Pflichtfeld: title (nicht leer)
  - Optional: description, completed
  - Status Code: 201 Created
  - Response: Erstelltes Todo mit generierter ID

- [ ] **GET /todos** - Alle Todos abrufen
  - Unterstützt Query-Parameter für Filterung (z.B. ?completed=true)
  - Status Code: 200 OK
  - Response: Array aller Todos

- [ ] **GET /todos/{id}** - Einzelnes Todo abrufen
  - Status Code: 200 OK bei Erfolg
  - Status Code: 404 Not Found wenn ID nicht existiert

- [ ] **PUT /todos/{id}** - Todo vollständig aktualisieren
  - Alle Felder können geändert werden (außer ID, timestamps)
  - Status Code: 200 OK bei Erfolg
  - Status Code: 404 Not Found wenn ID nicht existiert

- [ ] **PATCH /todos/{id}** - Todo teilweise aktualisieren
  - Nur übergebene Felder werden geändert
  - Status Code: 200 OK bei Erfolg
  - Status Code: 404 Not Found wenn ID nicht existiert

- [ ] **DELETE /todos/{id}** - Todo löschen
  - Status Code: 204 No Content bei Erfolg
  - Status Code: 404 Not Found wenn ID nicht existiert

### Validierung
- [ ] Title darf nicht leer sein (min. 1 Zeichen)
- [ ] Title darf nicht länger als 200 Zeichen sein
- [ ] Description darf maximal 2000 Zeichen haben
- [ ] Ungültige JSON-Requests werden mit 400 Bad Request abgelehnt
- [ ] Ungültige IDs im URL-Pfad werden korrekt behandelt

### Fehlerbehandlung
- [ ] Konsistente Fehler-Response-Struktur (error, message, status)
- [ ] 400 Bad Request bei Validierungsfehlern
- [ ] 404 Not Found bei nicht existierenden Ressourcen
- [ ] 405 Method Not Allowed bei nicht unterstützten HTTP-Methoden
- [ ] 500 Internal Server Error bei unerwarteten Fehlern

### API Design
- [ ] RESTful URL-Struktur (/todos, /todos/{id})
- [ ] Korrekte HTTP-Methoden (GET, POST, PUT, PATCH, DELETE)
- [ ] Korrekte Content-Type Header (application/json)
- [ ] ISO 8601 Format für Timestamps

## Technische Notizen

### Security
- Eingabe-Validierung gegen XSS und Injection-Angriffe
- Request-Size-Limiting (max. Payload-Größe)
- Rate-Limiting erwägen für Production

### Performance
- Effiziente Datenbankabfragen
- Pagination für GET /todos bei vielen Einträgen
- Caching-Header setzen

### Datenbank
- Auto-Increment ID oder UUID verwenden
- Indexierung auf ID-Feld
- Timestamps automatisch setzen/aktualisieren

### Testing
- Unit Tests für Business Logic
- Integration Tests für API-Endpoints
- BDD Tests mit Gherkin-Szenarien
- Edge Cases und Error Cases abdecken

### Logging
- Alle API-Requests loggen (Method, Path, Status)
- Fehler mit Stack Traces loggen
- Keine sensitiven Daten in Logs

## Out of Scope (für spätere Iterationen)
- Authentifizierung / Authorization
- Multi-User Support (User-spezifische Todos)
- Tags oder Kategorien
- Due Dates / Prioritäten
- Todo-Listen-Gruppen
- Volltextsuche
