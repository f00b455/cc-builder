# Expression Parser Microservice

## Aufgabe

Implementiere eine REST-API die mathematische Ausdrücke auswertet.

## API

```
POST /calculate
Content-Type: application/json

{"expression": "2 + 3 * (4 - 1)"}
```

Response:
```json
{"result": 11}
```

## Anforderungen

### Operatoren
- Addition: `+`
- Subtraktion: `-`
- Multiplikation: `*`
- Division: `/`
- Korrekte Operator-Präzedenz (`*` und `/` vor `+` und `-`)

### Klammern
- Beliebig verschachtelte Klammern: `((1 + 2) * (3 + 4))`

### Fehlerbehandlung
- **400 Bad Request** bei Syntaxfehler
- **400 Bad Request** bei Division durch 0

### Einschränkungen
- **Keine `eval()` oder Script-Engines** - selbst parsen!
- Nur Integer-Arithmetik (keine Dezimalzahlen nötig)

## Beispiele

| Expression | Result |
|------------|--------|
| `1 + 2` | `3` |
| `2 * 3 + 4` | `10` |
| `2 + 3 * 4` | `14` |
| `(2 + 3) * 4` | `20` |
| `10 / 2` | `5` |
| `((1 + 2) * 3)` | `9` |

## Qualitätskriterien

- Kompiliert: `./gradlew build`
- Tests grün mit Coverage ≥80%
- Clean Code: keine God-Classes, kleine Methoden
- Edge Cases: leerer String, nur Zahl, Division/0
