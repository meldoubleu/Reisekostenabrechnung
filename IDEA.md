# MVP: Reisekostenabrechnung (Web)

## 🎯 Ziel
Ein erstes, minimales Web-MVP für Reisekostenabrechnung mit Python-Backend.  
Fokus auf:
- Zwei Rollen: Mitarbeiter & Controlling
- Reisen anlegen
- Belegerfassung per Upload (Foto/PDF) mit OCR + manueller Eingabe
- Kategorisierung von Spesen
- Export als PDF

---

## 👤 Rollen

### Mitarbeiter
- Reisen anlegen (Start, Ende, Ziel, Zweck)
- Belege hochladen (Foto/PDF)
- OCR-Ergebnisse prüfen & manuell ergänzen
- Spesen kategorisieren
- Reise einreichen

### Controlling
- Eingereichte Reisen prüfen
- Belege kontrollieren (Original + OCR)
- Kategorien & Beträge validieren
- Reise freigeben oder ablehnen
- Export als PDF erstellen

---

## 📂 Wichtige Einträge pro Reise

### Stammdaten Reise
- Startdatum + Uhrzeit
- Enddatum + Uhrzeit
- Zielort (Land/Stadt)
- Zweck der Reise
- Kostenstelle (optional im MVP)
- Status (Entwurf, Eingereicht, Genehmigt, Abgelehnt)

### Spesen-Belege
- Datei-Upload (JPG/PNG/PDF)
- OCR-Extraktion: 
  - Betrag
  - Währung
  - Datum
  - MwSt (falls vorhanden)
  - Händler/Anbieter
- Manuelle Eingabe/Korrektur möglich
- Kategorisierung verpflichtend

---

## 🗂️ Kategorien der Spesen (MVP)

- **Übernachtung** (Hotel, Airbnb, Pension)
- **Transport** (Bahn, Flug, Taxi, ÖPNV, Mietwagen)
- **Verpflegung** (Restaurant, Café, Snacks – NICHT Tagessätze)
- **Bewirtung** (mit Kunden/externen Gästen, inkl. Teilnehmerangaben)
- **Sonstiges** (Pauschalen, Parkgebühren, Maut, etc.)

---

## 🖥️ User Flow (vereinfacht)

### Mitarbeiter
1. Login  
2. „Neue Reise anlegen“ → Stammdaten eingeben  
3. Belege hochladen (Foto oder PDF)  
   - OCR liest Daten aus  
   - Mitarbeiter prüft & ergänzt manuell  
   - Kategorie wählen  
4. Reiseübersicht prüfen  
5. Reise einreichen  

### Controlling
1. Login  
2. Übersicht „Eingereichte Reisen“  
3. Reise öffnen  
   - Belege im Original + OCR-Daten sehen  
   - Kategorien prüfen  
4. Entscheidung: Genehmigen oder Ablehnen  
5. Export der Reise als PDF  

---

## 📑 Export (PDF-Abrechnung)
- Deckblatt: Reisedaten (Zeitraum, Ziel, Zweck, Mitarbeiter)  
- Zusammenfassung: Gesamtsumme je Kategorie + Gesamtbetrag  
- Detailansicht: Einzelne Belege mit OCR-Daten  
- Belegbilder im Anhang (optional verkleinert)  

---

## 🚀 MVP-Umfang
- Backend in Python (FastAPI)
- Datenbank: PostgreSQL
- Upload: lokale Speicherung im MVP, Pfad in DB
- OCR: Tesseract (lokal)
- Export: PDF via ReportLab
