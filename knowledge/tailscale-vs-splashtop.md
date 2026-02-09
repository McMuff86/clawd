# Tailscale vs. Splashtop – Warum wechseln?

## Zusammenfassung

Splashtop ist ein Screen-Sharing-Tool, das über Drittserver läuft. Tailscale ist ein modernes Mesh-VPN, das direkte Peer-to-Peer-Verbindungen zwischen Geräten aufbaut. Tailscale ist sicherer, schneller, flexibler und günstiger.

---

## 1. Sicherheit & Datenschutz

| Aspekt | Splashtop | Tailscale |
|--------|-----------|-----------|
| **Datenfluss** | Über Splashtop Cloud-Server (USA) | Direkt zwischen Geräten (P2P) |
| **Verschlüsselung** | TLS – Splashtop *könnte* theoretisch mitlesen | WireGuard E2E – niemand ausser den Endgeräten kann mitlesen |
| **VPN-Protokoll** | Proprietär, Closed Source | WireGuard – Open Source, von Kryptographie-Experten auditiert |
| **Client-Software** | Closed Source | Open Source (Code einsehbar auf GitHub) |
| **Serverstandort** | USA (Splashtop Inc., San Jose, CA) | Kein Server im Datenpfad – nur Handshake-Vermittlung |
| **DSGVO** | Problematisch – Daten verlassen die EU/CH | Unbedenklich – Daten bleiben zwischen den Geräten |
| **Selbst-Hosting** | Nicht möglich | Möglich via Headscale (eigener Coordination Server) |

### Kernargument Sicherheit
> Bei Splashtop wird der gesamte Bildschirminhalt – inklusive sensibler Geschäftsdaten, Passwörter, Kundendaten – über Server eines US-Unternehmens geleitet. Bei Tailscale verlassen die Daten nie den direkten Weg zwischen den zwei Geräten. Kein Drittanbieter hat Zugriff, auch Tailscale selbst nicht.

---

## 2. Technologie

| Aspekt | Splashtop | Tailscale |
|--------|-----------|-----------|
| **Prinzip** | Bildschirm-Streaming über Cloud | Echtes VPN-Netzwerk (Mesh) |
| **Protokoll** | Proprietär | WireGuard (State-of-the-Art, im Linux-Kernel integriert) |
| **Verbindungsart** | Client → Cloud → Client | Client ↔ Client (direkt) |
| **Latenz** | Abhängig von Splashtop-Servern | Minimal – direkter Weg, oft <10ms im gleichen Netz |
| **NAT/Firewall** | Funktioniert durch NAT Traversal | Funktioniert durch NAT Traversal (STUN/DERP) |
| **Relay-Fallback** | Immer über Cloud | Nur wenn P2P nicht möglich – auch dann verschlüsselt |

### Was bedeutet "Mesh-VPN"?
Jedes Gerät im Tailscale-Netzwerk kann direkt mit jedem anderen kommunizieren – ohne zentralen Server dazwischen. Das ist fundamental anders als Splashtop, wo alles über die Cloud geroutet wird.

---

## 3. Funktionsumfang

| Funktion | Splashtop | Tailscale |
|----------|-----------|-----------|
| **Remote Desktop** | Ja (Screen-Streaming) | Ja (via natives RDP – besser!) |
| **Dateifreigabe** | Eingeschränkt (Dateitransfer-Tool) | Voller Netzwerkzugriff (SMB, FTP, etc.) |
| **Drucker** | Umständlich | Nativ erreichbar über Netzwerk |
| **SSH-Zugriff** | Nein | Ja |
| **Mehrere Services** | Nur Bildschirm | Alles – Web-Apps, Datenbanken, APIs, NAS, etc. |
| **Clipboard Sync** | Ja | Ja (über RDP) |
| **Multi-Monitor** | Ja | Ja (über RDP) |
| **Mobilzugriff** | Ja (eigene App) | Ja (iOS/Android App + beliebiger RDP-Client) |
| **Subnet Routing** | Nein | Ja – Zugriff auf ganze Subnetze möglich |

### Kernargument Funktionsumfang
> Splashtop kann nur Bildschirme spiegeln. Tailscale gibt volles Netzwerk – als wäre man direkt vor Ort. Remote Desktop, Dateifreigaben, Drucker, interne Web-Apps, Datenbanken – alles erreichbar.

---

## 4. Kosten

| Plan | Splashtop | Tailscale |
|------|-----------|-----------|
| **Einzelnutzer** | ~60 CHF/Jahr (Business Solo) | **Kostenlos** (bis 100 Geräte, 3 User) |
| **Team (5 User)** | ~250-500 CHF/Jahr | **Kostenlos** oder ab ~60 CHF/Jahr (Starter) |
| **Enterprise** | Auf Anfrage | Ab ~60 CHF/User/Jahr |

### Kernargument Kosten
> Tailscale ist für kleine Teams kostenlos und bietet dabei mehr Funktionalität und bessere Sicherheit als die bezahlte Splashtop-Lösung.

---

## 5. Performance

| Aspekt | Splashtop | Tailscale + RDP |
|--------|-----------|-----------------|
| **Bildqualität** | Komprimiertes Video-Streaming | Natives RDP – schärfer, effizienter |
| **Latenz** | ~30-80ms (über Cloud) | ~5-20ms (P2P, oft gleicher ISP) |
| **Bandbreite** | Hoch (Video-Stream) | Niedrig (RDP sendet nur Änderungen) |
| **CPU-Last** | Hoch (Encoding/Decoding) | Niedrig |
| **Flüssigkeit** | Gut, aber spürbare Verzögerung | Fühlt sich an wie lokal |

### Kernargument Performance
> RDP über Tailscale ist schneller und ressourcenschonender als Splashtop, weil kein Video-Stream über Drittserver läuft. Die Verbindung ist direkt – als wäre man am gleichen Schreibtisch.

---

## 6. Vertrauenswürdigkeit & Transparenz

### Splashtop
- Closed Source, proprietär
- US-Unternehmen, US-Recht (CLOUD Act – US-Behörden können Zugriff auf Daten verlangen)
- Keine Möglichkeit zu verifizieren was die Software tatsächlich tut
- Vertrauen basiert rein auf Marketing-Versprechen

### Tailscale
- **Open Source** – Code auf GitHub einsehbar: github.com/tailscale/tailscale
- Basiert auf **WireGuard** – ebenfalls Open Source, von Kryptographie-Experten weltweit geprüft
- WireGuard ist so vertrauenswürdig, dass es **in den Linux-Kernel aufgenommen** wurde (seit 2020)
- Option zur vollständigen Selbst-Hosting (Headscale)
- Regelmässige Security Audits

### Kernargument Transparenz
> Bei Splashtop muss man dem Unternehmen blind vertrauen. Bei Tailscale/WireGuard kann jeder den Quellcode lesen und prüfen. Das ist der Unterschied zwischen "Trust us" und "Verify it yourself".

---

## 7. Compliance & Regulierung

Für Schweizer Unternehmen besonders relevant:

- **DSG (CH):** Personendaten über US-Server = problematisch ohne adequate Schutzgarantien
- **DSGVO (EU):** Falls EU-Kundendaten auf dem Bildschirm sichtbar sind → Datentransfer in die USA
- **CLOUD Act:** US-Behörden können bei US-Firmen Herausgabe von Daten erzwingen
- **Revisionssicherheit:** Bei Tailscale bleiben Daten lokal – kein Drittland-Transfer

### Kernargument Compliance
> Mit Splashtop werden potenziell Geschäfts- und Kundendaten über US-Server geleitet. Mit Tailscale gibt es keinen Drittland-Transfer – die Daten bleiben zwischen den Endgeräten. Das vereinfacht die Compliance-Situation erheblich.

---

## 8. Setup & Migration

### Aufwand
1. Tailscale auf beiden Rechnern installieren (2 Minuten pro Gerät)
2. Mit Account anmelden
3. RDP auf dem Zielrechner aktivieren (Windows Pro/Enterprise: schon eingebaut)
4. Verbinden via `mstsc` auf die Tailscale-IP
5. Fertig

### Rückfallplan
Splashtop kann parallel installiert bleiben. Kein Risiko bei der Migration.

---

## 9. Mitarbeiter-Privatsphäre & Überwachung

### Das Problem mit Splashtop
Splashtop bietet einen **unbeaufsichtigten Zugriffsmodus** (Unattended Access). Das bedeutet:
- Der IT-Admin kann sich **jederzeit** auf jeden Rechner schalten – ohne Passwort, ohne Freigabe
- Der Mitarbeiter muss **nichts bestätigen** und merkt es je nach Konfiguration **nicht**
- Der Admin sieht den **laufenden Bildschirm** in Echtzeit: offene Dokumente, E-Mails, Passwort-Eingaben, private Nachrichten
- Es gibt **kein Log** das der Mitarbeiter einsehen kann

### Tailscale + RDP: Kein heimliches Zuschauen möglich
- Tailscale hat **keine Bildschirm-Funktion** – es ist ein Netzwerktunnel, kein Fernwartungstool
- Für Remote Desktop (RDP) braucht man das **Windows-Passwort** des Nutzers
- Bei RDP-Verbindung wird der aktive Nutzer **sofort ausgeloggt** (Sperrbildschirm) – heimliches Zuschauen ist technisch unmöglich
- Der Nutzer **merkt immer** wenn jemand zugreift

### Rechtliche Lage in der Schweiz

**Heimliche Bildschirmüberwachung ist illegal:**

- **OR Art. 328b:** Arbeitgeber darf nur Personendaten bearbeiten, die für das Arbeitsverhältnis erforderlich sind
- **ArGV 3, Art. 26:** Überwachungssysteme, die das Verhalten der Arbeitnehmer am Arbeitsplatz überwachen, dürfen nicht eingesetzt werden
- **DSG (Datenschutzgesetz):** Verdeckte Überwachung von Mitarbeitern ist grundsätzlich unzulässig
- **ZGB Art. 28:** Schutz der Persönlichkeit – widerrechtliche Verletzung kann eingeklagt werden

**Voraussetzungen für jede Form von Überwachung:**
1. Mitarbeiter muss **vorher informiert** werden
2. Es muss einen **sachlichen Grund** geben
3. Muss im Arbeitsvertrag oder Reglement **festgehalten** sein
4. Muss **verhältnismässig** sein

**Konsequenzen bei Verstössen:**
- Zivilrechtliche Klagen (Persönlichkeitsverletzung)
- Bussen durch den EDÖB (Eidgenössischer Datenschutzbeauftragter)
- Arbeitsrechtliche Konsequenzen

### Kernargument Privatsphäre
> Splashtop ermöglicht standardmässig den unbeaufsichtigten Zugriff auf Mitarbeiter-Bildschirme – ohne deren Wissen oder Zustimmung. Das ist in der Schweiz rechtlich problematisch (ArGV 3 Art. 26, DSG, OR Art. 328b). Tailscale bietet diese Möglichkeit technisch gar nicht. Der Wechsel eliminiert ein rechtliches Risiko und schützt die Privatsphäre der Mitarbeiter.

---

## Fazit

| Kriterium | Gewinner |
|-----------|----------|
| Sicherheit | **Tailscale** ✅ |
| Datenschutz | **Tailscale** ✅ |
| Performance | **Tailscale** ✅ |
| Funktionsumfang | **Tailscale** ✅ |
| Kosten | **Tailscale** ✅ |
| Transparenz | **Tailscale** ✅ |
| Compliance | **Tailscale** ✅ |
| Einfachheit | Unentschieden |

Tailscale ist in **jeder relevanten Kategorie** überlegen. Der einzige Grund Splashtop zu behalten wäre, wenn die IT-Abteilung die Installation von Software auf Firmenrechnern blockiert.

---

*Erstellt: 1. Februar 2026*
