# Slot Simulator

Ein Python-Projekt zum schrittweisen Nachbau eines slot-inspirierten Spiels mit Fokus auf:

- nachvollziehbare Spielmechanik
- saubere Trennung von Logik und Darstellung
- mathematisch kontrollierbare Auszahlungsquote
- einfache Erweiterbarkeit für Bonus-Features, Freispiele und unterschiedliche Symbole

## Ziel

Dieses Projekt soll kein echter Casino-Automat sein, sondern eine eigene Simulation, die sich an realen Slot-Prinzipien orientiert.

Geplant sind unter anderem:

- Walzen mit Symbolen
- Gewinnlinien
- Paytable
- Wild- und Scatter-Symbole
- Freispiele / Bonus-Features
- Simulation vieler Spins zur Auswertung von RTP und Trefferquote
- später optional eine grafische Oberfläche mit Pygame

## Projektstatus

Aktuell befindet sich das Projekt im Aufbau.

## Voraussetzungen

- Python 3.12+ empfohlen
- Windows
- VS Code

## Einrichtung

### 1. Repository klonen
```bash
git clone <DEIN-REPO-URL>
cd <DEIN-REPO-NAME>
```

### 2. Virtuelle Umgebung erstellen
```bash
python -m venv .venv
```

### 3. Virtuelle Umgebung aktivieren
```bash
.venv\Scripts\activate
```

### 4. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

## Projektidee

Der Aufbau soll Schritt für Schritt erfolgen:
1. Grundstruktur des Projekts
2. Symbol- und Reel-Modell
3. Zufälliger Spin
4. Auswertung von Gewinnen
5. Guthaben / Einsatz
6. Freispiele und Bonuslogik
7. Simulation vieler Spins
8. optionale grafische Oberfläche

## Geplante Struktur
```txt
slot-simulator/
│
├── .gitignore
├── README.md
├── requirements.txt
└── src/
    └── main.py
```

## Start
Sobald eine erste lauffähige Version existiert, kann sie etwa so gestartet werden:
```txt
python src/main.py
```

## Hinweise
Dieses Projekt dient Lern- und Simulationszwecken.