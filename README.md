# Smartfox Pro 2 – Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
![Version](https://img.shields.io/badge/version-1.0.0-blue)

Inoffizielle Home Assistant Integration für den **Smartfox Pro 2 Energiemanager**.  
Die Integration liest die Daten über die lokale HTTP-Schnittstelle (`/values.xml`) aus — keine Cloud, keine externen Dienste.

---

## Unterstützte Geräte

| Gerät | Beschreibung |
|---|---|
| Smartfox Pro 2 | Energiemanager (Netzanschlusspunkt) |
| Smartfox Pro Charger (CC1) | Wallbox / E-Auto-Ladestation |

---

## Sensoren

### Smartfox Pro 2 (Netzanschlusspunkt) — 15 Sensoren

| Sensor | Einheit | Beschreibung |
|---|---|---|
| Netzleistung | W | Gesamtleistung am Netzanschluss (+ = Bezug, − = Einspeisung) |
| Netzleistung L1 / L2 / L3 | W | Leistung je Phase |
| Netzspannung L1 / L2 / L3 | V | Spannung je Phase |
| Netzstrom L1 / L2 / L3 | A | Strom je Phase |
| Netzbezug gesamt | kWh | Kumulativer Energiebezug (TOTAL_INCREASING) |
| Netzeinspeisung gesamt | kWh | Kumulative Einspeisung (TOTAL_INCREASING) |
| Netzbezug heute | kWh | Tageswert Energiebezug |
| Netzeinspeisung heute | kWh | Tageswert Einspeisung |
| Netzfrequenz | Hz | Netzfrequenz |

### Wallbox CC1 — 12 Sensoren

| Sensor | Einheit | Beschreibung |
|---|---|---|
| Ladeleistung | W | Aktuelle Ladeleistung |
| Ladeenergie gesamt | kWh | Kumulativer Gesamtzähler aller Ladevorgänge (persistent, Energy-Dashboard-kompatibel) |
| Ladeenergie heute | kWh | Ladeenergie des heutigen Tages |
| Letzte Ladesession | kWh | Energie der letzten Ladesession |
| Ladezyklen gesamt | – | Anzahl abgeschlossener Ladevorgänge |
| Status | – | Verfügbar / Lädt / Belegt / Offline |
| Regelstrom | A | Vom Energiemanager vorgegebener Ladestrom |
| Phasenstrom L1 / L2 / L3 | A | Gemessener Strom je Phase an der Wallbox |
| Temperatur | °C | Temperatur des Ladecontrollers |
| Stromlimit | % | Aktuelles Stromlimit in Prozent |

---

## Installation

### Option A – HACS (empfohlen)

1. HACS öffnen → **„Benutzerdefinierte Repositories"**
2. URL dieses Repositories einfügen, Kategorie **„Integration"** auswählen
3. Integration **„Smartfox Pro 2"** suchen und installieren
4. Home Assistant neu starten

### Option B – Manuell

1. ZIP herunterladen und entpacken
2. Den Ordner `smartfox_pro2` nach `config/custom_components/smartfox_pro2` kopieren
3. Home Assistant neu starten

---

## Einrichtung

1. Einstellungen → Geräte & Dienste → **Integration hinzufügen**
2. „Smartfox Pro 2" suchen
3. IP-Adresse des Smartfox eingeben (z. B. `192.168.178.143`)
4. Abfrageintervall wählen (Standard: 30 Sekunden, Minimum: 10 s empfohlen)

---

## Energy Dashboard

Den Sensor **„Ladeenergie gesamt"** (`sensor.wallbox_ladeenergie_gesamt`) direkt unter  
**Einstellungen → Energie → Individuelle Geräte** hinzufügen.

Dieser Sensor akkumuliert alle Ladevorgänge dauerhaft und übersteht auch HA-Neustarts.

---

## Voraussetzungen

- Home Assistant 2023.6 oder neuer
- Smartfox Pro 2 im lokalen Netzwerk erreichbar
- Kein Internetzugang des Smartfox notwendig

---

## Bekannte Einschränkungen

- Der Smartfox Pro 2 hat keinen direkten Zugriff auf Wechselrichter- oder Speicherdaten — diese Werte werden daher nicht ausgelesen
- Die `/values.xml`-Schnittstelle ist eine inoffizielle API und kann sich mit Firmware-Updates ändern

---

## Lizenz

Diese Integration steht unter einer **nicht-kommerziellen Lizenz**.

- Private und gemeinnützige Nutzung: ✅ erlaubt
- Veränderung und Weitergabe: ✅ erlaubt (unter gleichen Bedingungen)
- Kommerzielle Nutzung: ❌ nicht erlaubt

Siehe [LICENSE](LICENSE) für den vollständigen Lizenztext.
