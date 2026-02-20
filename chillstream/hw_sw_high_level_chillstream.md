### ChillStream — High-Level System Design

**Date:** 2026-02-20 | **Author:** | **Status:** Draft

#### What It Is

A plumbed-in countertop water dispenser that uses a phase-change thermal battery to deliver instant cold water during peak demand. Firmware manages thermal cycling, capacity estimation, and compressor control. A cloud platform provides fleet management, predictive maintenance, and OTA updates for facility operators managing multiple units across sites.

#### Block Diagram

```
                                    ┌──────────────────────────────────────────────────┐
                                    │              ChillStream Unit                     │
                                    │                                                  │
  Mains Water ──────→ ┌────────┐   │   ┌──────────────┐         ┌──────────────┐      │
  (3/8" BSP)          │ Filter │───┼──→│  Cold Path    │         │  Hot Path    │      │
                      └────────┘   │   │  Tank + PCM   │         │  Tank +      │      │
                                   │   │  Plate HX     │         │  Heater      │      │
                                   │   └──────┬───────┘         └──────┬───────┘      │
                                   │          │                        │               │
                                   │          ▼                        ▼               │
                                   │   ┌─────────────┐         ┌─────────────┐        │
                                   │   │  Cold Tap   │         │  Hot Tap    │        │
                                   │   └─────────────┘         └─────────────┘        │
                                   │                                                  │
                                   │   ┌──────────────┐    ┌───────────────────┐      │
                                   │   │ Refrigeration │    │  ESP32-S3 + FW    │      │
                                   │   │ Compressor   │←───│  Sensors, Display  │      │
                                   │   │ Condenser    │    │  Buttons, Valves   │      │
                                   │   └──────────────┘    └────────┬──────────┘      │
                                   │                                │                  │
                                   └────────────────────────────────┼──────────────────┘
                                                                    │ WiFi
                                                                    ▼
                                                        ┌──────────────────────┐
                                                        │   ChillStream Cloud  │
                                                        │   Fleet Dashboard    │
                                                        │   Telemetry + OTA    │
                                                        └──────────────────────┘
```

#### Subsystems

| Subsystem | Purpose | Domain |
|-----------|---------|--------|
| Cold assembly (tank + PCM plate HX + cover) | Store cold energy in PCM thermal battery, chill water on demand through submerged HX plates | HW |
| Refrigeration loop | Freeze PCM during idle via compressor/condenser/capillary cycle (R600a) | HW |
| Hot water system | Heat 1.5L tank to 85-95°C for instant hot water | HW |
| Filter module | Twist-lock cartridge with NFC tag for water filtration and lifecycle tracking | HW |
| ESP32-S3 firmware | Thermal PID control, capacity estimation, dispense management, display UI, WiFi/MQTT, OTA | FW |
| Cloud platform | Fleet dashboard, telemetry storage, alerts, predictive maintenance, OTA deployment | Cloud |

#### Key Interfaces

| From → To | What Crosses | Protocol / Medium |
|-----------|-------------|-------------------|
| Sensors (6x NTC, flow, current) → ESP32 | Temperature, flow rate, compressor current | ADC + GPIO pulse |
| ESP32 → Compressor, heater, valves | On/off control signals | GPIO → relay/SSR/MOSFET |
| ESP32 → Display + buttons | UI frames, press events | SPI + GPIO |
| ESP32 ↔ Cloud | Telemetry (60s), events, config, FW images | WiFi → MQTT + HTTPS, TLS 1.2/1.3 |
| Filter cartridge → ESP32 | Cartridge ID, install date | NFC (via reader on PCB) |

#### Constraints

| Constraint | Value | Why It Matters |
|-----------|-------|----------------|
| Peak demand | 50 consecutive pours at 4-6°C | Defines PCM mass and HX plate count — the core sizing decision |
| BOM cost | $250-390 (5L), $300-445 (10L) | Rules out inverter compressor and expensive connectivity (cellular) in V1 |
| Certifications | NSF/ANSI 42/53, UL 399, FCC, CE | Food-contact materials, refrigerant charge limits, and RF compliance constrain material and component choices |
| Noise | <45 dB(A) at 1m | Must be office-acceptable — constrains compressor selection and enclosure design |
| Form factor | Countertop (~30×40×45 cm) | Limits tank volume, condenser size, and thermal insulation thickness |

#### Three Hardest Problems

1. **PCM encapsulation durability:** Bonding food-safe PCM capsules to stainless steel HX plate surfaces that survive 10,000+ freeze-thaw cycles while submerged in drinking water — no established commercial process exists for this exact application.

2. **Cover manifold design:** Routing mains water in, chilled water out, and refrigerant lines through a single removable cover with a reliable seal — this is the most mechanically complex component and the only custom part.

3. **Accurate capacity estimation in firmware:** Predicting remaining cold water capacity from 2 PCM temperature sensors, pour history, and thermal modeling — the user-facing "capacity gauge" is the product's key differentiator and must be trustworthy.

#### Open Calls

| Decision | Options | Deadline |
|----------|---------|----------|
| PCM material selection | Salt hydrate vs. paraffin vs. glycol eutectic | Before thermal prototype (M3) |
| External ADC for temperature precision | ESP32 internal ADC (with calibration) vs. external 16-bit ADC ($1-2 add) | Before EVT (M9) |
| Cloud platform | AWS IoT Core vs. Azure IoT Hub | Before firmware network stack development (M4) |
