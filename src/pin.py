import logging
import platform
import pygame
from typing import Any, Dict

smbus2_module = None
if platform.system() != "Windows":
    import smbus2 as smbus2_module
else:
    # Mock classes for Windows development
    class _SMBusRuntime:
        def __init__(self, bus):
            print(f"Mock SMBus initialized on bus {bus}")

        def write_i2c_block_data(self, *args):
            print("Mock write called with", args)

        def read_i2c_block_data(self, address, register, length):
            return [0xFF, 0]  # Return dummy data

    class i2c_msg:
        @staticmethod
        def write(address, data):
            print(f"Mock i2c_msg.write called: address={address}, data={data}")
            return None


import time
from src.constants import (
    PIN_BENTER,
    PIN_BNEXT,
    PIN_RIGHT,
    PIN_H20,
    PIN_H25,
    PIN_H40,
    PIN_H50,
    PIN_H100,
    PIN_HBOTTLE,
    PIN_HSFROG,
    PIN_HLFROG,
)

I2C_BUS = 1  # I2C bus number (usually 1 on Raspberry Pi)
I2C_ADDRESS = 0x08  # I2C address of the ESP32 (or other I2C device)


class PIN:
    def __init__(self, screen, use_i2c=True):
        self.use_i2c = use_i2c
        self.bus: Any = None
        self.last_pin_time = {}  # Dictionary to track last detection time for each pin
        self.default_sensor_cooldown_ms = 500
        self.sensor_cooldown_overrides_ms = {
            4: 140,
        }
        self.button_cooldown_ms = 320
        self.pin_hole = set(
            PIN_H20
            + PIN_H25
            + PIN_H40
            + PIN_H50
            + PIN_H100
            + PIN_HBOTTLE
            + PIN_HSFROG
            + PIN_HLFROG
        )
        self.button_pin = {PIN_BNEXT, PIN_BENTER, PIN_RIGHT}
        self.menu_pins = {PIN_BENTER, PIN_RIGHT, PIN_BNEXT}
        self.game_pins = self.pin_hole | {PIN_BNEXT, PIN_BENTER, PIN_RIGHT}
        self.end_menu_pins = {PIN_BENTER, PIN_BNEXT}
        self.diagnostic_pins = self.pin_hole | self.button_pin
        self.diagnostic_groups = [
            {"name": "20", "pins": tuple(PIN_H20), "family": "side"},
            {"name": "25", "pins": tuple(PIN_H25), "family": "side"},
            {"name": "40", "pins": tuple(PIN_H40), "family": "side"},
            {"name": "50", "pins": tuple(PIN_H50), "family": "side"},
            {"name": "100", "pins": tuple(PIN_H100), "family": "side"},
            {"name": "BOUTEILLE", "pins": tuple(PIN_HBOTTLE), "family": "bonus"},
            {"name": "PETITE GRENOUILLE", "pins": tuple(PIN_HSFROG), "family": "frog"},
            {"name": "GRANDE GRENOUILLE", "pins": tuple(PIN_HLFROG), "family": "frog"},
            {"name": "NEXT", "pins": (PIN_BNEXT,), "family": "button"},
            {"name": "ENTER", "pins": (PIN_BENTER,), "family": "button"},
            {"name": "ACTION", "pins": (PIN_RIGHT,), "family": "button"},
        ]
        self.game_sensor_reference_pins = set(self.pin_hole)
        self.firmware_reference_pins = {
            4,
            5,
            13,
            14,
            15,
            16,
            17,
            18,
            23,
            25,
            26,
            27,
            32,
            33,
        }
        self.firmware_button_reference_pins = {0, 12, 19}
        self.schematic_reference_pins = {
            4,
            5,
            13,
            14,
            16,
            17,
            18,
            19,
            21,
            22,
            23,
            25,
            26,
            27,
            32,
            33,
        }
        self.pull_mode_reference = {
            "firmware": "Mixte: GPIO4 pulldown, autres GPIO capteurs pullup",
            "schematic": "PULLDOWN interne",
        }
        self.wiring_notes = [
            "Emetteur IR: anode longue, cathode courte.",
            "Recepteur IR: collecteur long, emetteur court.",
            "R1/R2: 100 Ohm en 3.3V d'apres le schema.",
            "Le schema recommande un pull-down interne sur les GPIO.",
            "20 A (GPIO4) utilise actuellement INPUT_PULLDOWN + RISING car ce capteur est different.",
            "Les autres capteurs valident actuellement les impulsions en INPUT_PULLUP + CHANGE.",
            "Les boutons firmware sont sur GPIO 19, 0 et 12 en INPUT_PULLUP.",
            "GPIO 21 et 22 restent reserves au bus I2C cote ESP32.",
        ]
        self.pin_labels = {}
        for group in self.diagnostic_groups:
            for index, pin in enumerate(group["pins"]):
                suffix = f" {index + 1}" if len(group["pins"]) > 1 else ""
                self.pin_labels[pin] = f"{group['name']}{suffix}"
        self.reset_diagnostics()

        if not self.use_i2c:
            logging.info("Keyboard/test mode enabled: skipping I2C initialization.")
            return

        self.bus = (
            smbus2_module.SMBus(I2C_BUS)
            if smbus2_module is not None
            else _SMBusRuntime(I2C_BUS)
        )  # Initialize the I2C bus
        logging.info("Initializing communication with the I2C slave...")

        self.display_waiting_popup(screen)
        bus = self.bus

        while True:
            try:
                # Attempt to read back a response
                raw_data = bus.read_i2c_block_data(I2C_ADDRESS, 0, 2)
                response = list(raw_data)

                if response:  # If a response is received, break the loop
                    logging.info(f"I2C slave connected. Received response: {response}")
                    break

            except Exception as e:
                logging.error(f"Failed to receive data: {e}")
                logging.info("Retrying in 1 second...")
                time.sleep(1)  # Wait before retrying

        logging.info("Communication with the I2C slave was successful.")
        self.clear_popup(screen)

    def display_waiting_popup(self, screen):
        font = pygame.font.Font(None, 36)
        text = font.render("Waiting for I2C connection...", True, (255, 255, 255))
        text_rect = text.get_rect(center=screen.get_rect().center)

        screen.fill((0, 0, 0))  # Fill the screen with black
        screen.blit(text, text_rect)
        pygame.display.flip()

    def clear_popup(self, screen):
        screen.fill((0, 0, 0))  # Clear the screen
        pygame.display.flip()

    def read_pin_states(self, game_action):
        bus = self.bus
        if not self.use_i2c or bus is None:
            return None
        try:
            # Request data from the ESP32, assuming 2 bytes are needed
            raw_data = bus.read_i2c_block_data(I2C_ADDRESS, 0, 2)
            # Parse the received data into pin states
            pin = self._parse_i2c_data(raw_data, game_action)

            return pin
        except Exception as e:
            logging.error(f"Failed to read from I2C bus: {e}")
            self.diagnostics_errors += 1
            self.diagnostics_last_packet = {
                "raw": [],
                "pin": None,
                "state": "ERROR",
                "timestamp": time.monotonic(),
                "source": "i2c",
            }
            return None

    def _parse_i2c_data(self, data, game_action):
        # Convert the raw I2C data into a dictionary of pin states
        pin_number = data[0]
        state = "LOW" if data[1] == 0 else "HIGH"
        self.diagnostics_packets += 1
        packet = {
            "raw": list(data),
            "pin": None if pin_number == 0xFF else int(pin_number),
            "state": state,
            "timestamp": time.monotonic(),
            "source": "i2c",
        }
        self._record_packet(packet)
        if pin_number == 0xFF:
            return None  # Neutral signal, nothing to process

        logging.debug(f"Pin {pin_number} state is {state}")

        if state == "HIGH":
            return self._get_next_pin(pin_number, game_action)
        return None

    def _get_allowed_pins(self, game_action):
        if game_action == "menu":
            return self.menu_pins
        if game_action == "game":
            return self.game_pins
        if game_action == "end_menu":
            return self.end_menu_pins
        if game_action == "sensor_analysis":
            return self.diagnostic_pins
        return set()

    def _get_next_pin(self, pin, game_action):
        pin = int(pin)
        current_time = time.monotonic() * 1000  # monotonic ms — no wall-clock jumps
        last_time = self.last_pin_time.get(pin, 0)

        cooldown = self._get_pin_cooldown_ms(pin)
        # Apply cooldown
        if current_time - last_time < cooldown:
            logging.debug(f"Pin {pin} ignored due to cooldown.")
            self._record_diagnostic_event(
                pin, game_action, accepted=False, reason="cooldown"
            )
            return None

        allowed_pins = self._get_allowed_pins(game_action)
        if pin not in allowed_pins:
            self._record_diagnostic_event(
                pin, game_action, accepted=False, reason="mode"
            )
            return None

        # Update last detection time for the pin
        self.last_pin_time[pin] = current_time
        self._record_diagnostic_event(pin, game_action, accepted=True)
        return pin

    def _get_pin_cooldown_ms(self, pin):
        if pin in self.pin_hole:
            return self.sensor_cooldown_overrides_ms.get(
                pin, self.default_sensor_cooldown_ms
            )
        return self.button_cooldown_ms

    def _record_diagnostic_event(self, pin, game_action, accepted, reason=None):
        now = time.monotonic()
        pin = int(pin)
        self.diagnostics_last_activity[pin] = now
        if accepted:
            previous_accept = self.diagnostics_last_accept.get(pin, 0.0)
            if previous_accept > 0:
                interval = now - previous_accept
                self.diagnostics_last_accept_interval[pin] = interval
                self.diagnostics_accept_interval_sum[pin] += interval
                self.diagnostics_accept_interval_count[pin] += 1
                current_min = self.diagnostics_accept_min_interval[pin]
                if current_min is None or interval < current_min:
                    self.diagnostics_accept_min_interval[pin] = interval
                if interval < 0.55:
                    self.diagnostics_burst_count[pin] += 1
            self.diagnostics_counts[pin] = self.diagnostics_counts.get(pin, 0) + 1
            self.diagnostics_last_accept[pin] = now
        else:
            self.diagnostics_suppressed[pin] = (
                self.diagnostics_suppressed.get(pin, 0) + 1
            )

        event = {
            "pin": pin,
            "label": self.pin_labels.get(pin, str(pin)),
            "accepted": accepted,
            "reason": reason or ("accepted" if accepted else "ignored"),
            "mode": game_action,
            "timestamp": now,
        }
        self.diagnostics_last_event = event
        self.diagnostics_history.insert(0, event)
        self.diagnostics_history = self.diagnostics_history[:18]

    def _record_packet(self, packet):
        self.diagnostics_last_bus_packet = packet
        self.diagnostics_last_bus_heartbeat = packet["timestamp"]
        if packet.get("pin") is None and packet.get("state") != "ERROR":
            self.diagnostics_idle_packet_count += 1
            return

        self.diagnostics_last_packet = packet
        self.diagnostics_packet_history.insert(0, packet)
        self.diagnostics_packet_history = self.diagnostics_packet_history[:24]

    def record_game_score_event(self, result):
        if not result:
            return
        event = {
            **result,
            "timestamp": time.monotonic(),
        }
        self.diagnostics_last_score_event = event
        self.diagnostics_score_history.insert(0, event)
        self.diagnostics_score_history = self.diagnostics_score_history[:12]

    def record_manual_pin(self, pin, game_action="sensor_analysis"):
        pin = int(pin)
        self.diagnostics_packets += 1
        self._record_packet(
            {
                "raw": [pin, 1],
                "pin": pin,
                "state": "HIGH",
                "timestamp": time.monotonic(),
                "source": "manual",
            }
        )
        self._record_diagnostic_event(pin, game_action, accepted=True)

    def reset_diagnostics(self):
        started = time.monotonic()
        self.diagnostics_started = started
        self.diagnostics_packets = 0
        self.diagnostics_errors = 0
        self.diagnostics_counts = {pin: 0 for pin in self.pin_labels}
        self.diagnostics_suppressed = {pin: 0 for pin in self.pin_labels}
        self.diagnostics_last_activity = {pin: 0.0 for pin in self.pin_labels}
        self.diagnostics_last_accept = {pin: 0.0 for pin in self.pin_labels}
        self.diagnostics_last_accept_interval: Dict[int, float | None] = {
            pin: None for pin in self.pin_labels
        }
        self.diagnostics_accept_interval_sum = {pin: 0.0 for pin in self.pin_labels}
        self.diagnostics_accept_interval_count = {pin: 0 for pin in self.pin_labels}
        self.diagnostics_accept_min_interval: Dict[int, float | None] = {
            pin: None for pin in self.pin_labels
        }
        self.diagnostics_burst_count = {pin: 0 for pin in self.pin_labels}
        self.diagnostics_idle_packet_count = 0
        self.diagnostics_history = []
        self.diagnostics_packet_history = []
        self.diagnostics_last_event = None
        self.diagnostics_score_history = []
        self.diagnostics_last_score_event = None
        self.diagnostics_last_packet = None
        self.diagnostics_last_bus_packet = {
            "raw": [0xFF, 0],
            "pin": None,
            "state": "IDLE",
            "timestamp": started,
            "source": "system",
        }
        self.diagnostics_last_bus_heartbeat = started

    def get_diagnostics_snapshot(self):
        now = time.monotonic()
        severity_rank = {"ok": 0, "watch": 1, "warning": 2, "error": 3}
        groups = []
        for group in self.diagnostic_groups:
            pins = tuple(int(pin) for pin in group["pins"])
            accepted = sum(self.diagnostics_counts.get(pin, 0) for pin in pins)
            suppressed = sum(self.diagnostics_suppressed.get(pin, 0) for pin in pins)
            accepted_by_pin = {pin: self.diagnostics_counts.get(pin, 0) for pin in pins}
            suppressed_by_pin = {
                pin: self.diagnostics_suppressed.get(pin, 0) for pin in pins
            }
            recent_ages = [
                now - self.diagnostics_last_activity.get(pin, 0.0)
                for pin in pins
                if self.diagnostics_last_activity.get(pin, 0.0) > 0
            ]
            accepted_ages = [
                now - self.diagnostics_last_accept.get(pin, 0.0)
                for pin in pins
                if self.diagnostics_last_accept.get(pin, 0.0) > 0
            ]
            interval_values: list[float] = []
            for pin in pins:
                interval = self.diagnostics_last_accept_interval.get(pin)
                if interval is not None:
                    interval_values.append(interval)
            burst_count = sum(self.diagnostics_burst_count.get(pin, 0) for pin in pins)
            active_pins = sum(1 for pin in pins if accepted_by_pin[pin] > 0)
            tested_pins = sum(
                1
                for pin in pins
                if accepted_by_pin[pin] > 0 or suppressed_by_pin[pin] > 0
            )
            health = "ok"
            issues = []
            fixes = []

            if accepted == 0 and suppressed > 0:
                health = "warning"
                issues.append("Signal vu mais bloque par cooldown.")
                fixes.append("Verifier rebond, parasite IR ou faisceau trop long.")

            if len(pins) == 2 and accepted >= 4:
                count_values = list(accepted_by_pin.values())
                if active_pins == 1:
                    health = "error"
                    issues.append("Une voie sur deux semble muette.")
                    fixes.append(
                        "Verifier alignement, polarite du recepteur et continuite sur la paire."
                    )
                elif min(count_values) > 0:
                    high_count = max(count_values)
                    low_count = min(count_values)
                    if high_count >= low_count * 3 and high_count - low_count >= 4:
                        if severity_rank[health] < severity_rank["warning"]:
                            health = "warning"
                        issues.append("La paire est fortement desequilibree.")
                        fixes.append(
                            "Verifier diode, resistance et positionnement du capteur le plus faible."
                        )

            if suppressed >= max(4, accepted * 2):
                if severity_rank[health] < severity_rank["warning"]:
                    health = "warning"
                issues.append("Trop de lectures ignorees par cooldown.")
                fixes.append(
                    "Chercher du bruit optique, une balle qui reste dans le faisceau ou une sensibilite excessive."
                )

            if burst_count >= 3:
                if severity_rank[health] < severity_rank["warning"]:
                    health = "warning"
                issues.append("Impulsions trop rapprochees detectees.")
                fixes.append(
                    "Verifier faux contact, oscillation electrique ou capteur trop expose."
                )

            if (
                accepted == 0
                and suppressed == 0
                and now - self.diagnostics_started > 12
                and sum(self.diagnostics_counts.values()) >= 8
            ):
                if severity_rank[health] < severity_rank["watch"]:
                    health = "watch"
                issues.append("Ce capteur n'a toujours pas ete teste.")
                fixes.append(
                    "Passer volontairement une balle devant ce capteur pour valider la chaine complete."
                )

            if not issues:
                fixes.append("RAS: comportement coherent sur les lectures actuelles.")

            groups.append(
                {
                    "name": group["name"],
                    "pins": pins,
                    "pin_labels": [self.pin_labels.get(pin, str(pin)) for pin in pins],
                    "family": group["family"],
                    "accepted": accepted,
                    "suppressed": suppressed,
                    "accepted_by_pin": accepted_by_pin,
                    "suppressed_by_pin": suppressed_by_pin,
                    "recent_age": min(recent_ages) if recent_ages else None,
                    "accepted_age": min(accepted_ages) if accepted_ages else None,
                    "tested_pins": tested_pins,
                    "active_pins": active_pins,
                    "min_interval": min(interval_values) if interval_values else None,
                    "burst_count": burst_count,
                    "health": health,
                    "issues": issues,
                    "fixes": fixes,
                }
            )

        history = []
        for event in self.diagnostics_history:
            history.append(
                {
                    **event,
                    "age": now - event["timestamp"],
                }
            )

        packet_history = []
        for packet in self.diagnostics_packet_history:
            packet_history.append(
                {
                    **packet,
                    "age": now - packet["timestamp"],
                }
            )

        score_history = []
        for event in self.diagnostics_score_history:
            score_history.append(
                {
                    **event,
                    "age": now - event["timestamp"],
                }
            )

        last_packet = None
        if self.diagnostics_last_packet is not None:
            last_packet = dict(self.diagnostics_last_packet)
            last_packet["age"] = now - last_packet["timestamp"]

        last_bus_packet = dict(self.diagnostics_last_bus_packet)
        last_bus_packet["age"] = now - last_bus_packet["timestamp"]
        bus_heartbeat_age = now - self.diagnostics_last_bus_heartbeat
        bus_alive = self.use_i2c and self.bus is not None and bus_heartbeat_age < 0.6

        last_event = None
        if self.diagnostics_last_event is not None:
            last_event = dict(self.diagnostics_last_event)
            last_event["age"] = now - self.diagnostics_last_event["timestamp"]

        last_score_event = None
        if self.diagnostics_last_score_event is not None:
            last_score_event = dict(self.diagnostics_last_score_event)
            last_score_event["age"] = (
                now - self.diagnostics_last_score_event["timestamp"]
            )

        alerts = []
        actions = []
        for group in groups:
            if group["health"] in {"error", "warning", "watch"}:
                alerts.append(
                    {
                        "severity": group["health"],
                        "title": group["name"],
                        "detail": group["issues"][0],
                        "fix": group["fixes"][0],
                    }
                )

        missing_in_firmware = sorted(
            self.game_sensor_reference_pins - self.firmware_reference_pins
        )
        extra_in_firmware = sorted(
            self.firmware_reference_pins - self.game_sensor_reference_pins
        )
        missing_in_schematic = sorted(
            self.game_sensor_reference_pins - self.schematic_reference_pins
        )
        extra_in_schematic = sorted(
            self.schematic_reference_pins - self.game_sensor_reference_pins
        )
        button_conflicts = sorted(self.button_pin & self.firmware_reference_pins)
        boot_strap_buttons = sorted(
            self.firmware_button_reference_pins & {0, 2, 12, 15}
        )

        if missing_in_firmware:
            alerts.insert(
                0,
                {
                    "severity": "error",
                    "title": "Firmware ESP32 incomplet",
                    "detail": f"Pins capteurs absents du firmware: {', '.join(map(str, missing_in_firmware))}",
                    "fix": "Ajouter ces GPIO dans inputPins du firmware ESP32.",
                },
            )
            actions.append(
                f"Mettre a jour inputPins dans l'ESP32 avec: {', '.join(map(str, missing_in_firmware))}."
            )

        if missing_in_schematic or extra_in_schematic:
            alerts.insert(
                0,
                {
                    "severity": "warning",
                    "title": "Schema / carte jeu divergents",
                    "detail": (
                        f"Schema manque {', '.join(map(str, missing_in_schematic)) or 'aucun'}"
                        f" | schema en plus {', '.join(map(str, extra_in_schematic)) or 'aucun'}"
                    ),
                    "fix": "Verifier si le schema est a jour par rapport au cablage reel et au mapping jeu/ESP32.",
                },
            )
            actions.append(
                "Comparer les GPIO du schema detecteur avec la carte jeu actuelle avant de changer du code."
            )

        if button_conflicts:
            alerts.insert(
                0,
                {
                    "severity": "warning",
                    "title": "Conflit bouton / entree firmware",
                    "detail": f"GPIO partages avec un bouton jeu: {', '.join(map(str, button_conflicts))}",
                    "fix": "Verifier qu'aucun bouton Raspberry ne partage une entree capteur ESP32.",
                },
            )

        if boot_strap_buttons:
            alerts.insert(
                0,
                {
                    "severity": "watch",
                    "title": "Boutons sur GPIO de boot",
                    "detail": f"Boutons branches sur GPIO de strapping: {', '.join(map(str, boot_strap_buttons))}",
                    "fix": "Garder ces boutons relaches au demarrage ou migrer ces boutons vers des GPIO non critiques.",
                },
            )
            actions.append(
                "Si des boots aleatoires apparaissent, deplacer les boutons de GPIO0/GPIO12 vers des GPIO non strap."
            )

        if (
            self.pull_mode_reference["firmware"]
            != self.pull_mode_reference["schematic"]
        ):
            alerts.insert(
                0,
                {
                    "severity": "warning",
                    "title": "Pull mode incoherent",
                    "detail": f"Firmware: {self.pull_mode_reference['firmware']} | schema: {self.pull_mode_reference['schematic']}",
                    "fix": "Verifier si le montage doit etre lu en pull-up ou pull-down puis harmoniser firmware/schema.",
                },
            )
            actions.append(
                "Comparer le mode d'entree declare dans le firmware avec la note de pull-down du schema."
            )

        if not actions:
            actions.append(
                "Tester chaque capteur une fois puis verifier que toutes les paires restent equilibrees."
            )
        if not alerts:
            alerts.append(
                {
                    "severity": "ok",
                    "title": "Alerte majeure absente",
                    "detail": "Aucune anomalie structurelle detectee pour le moment.",
                    "fix": "Continuer le test capteur par capteur pour valider toute la matrice.",
                }
            )

        return {
            "connected": self.use_i2c and self.bus is not None,
            "transport": (
                "I2C ACTIF"
                if bus_alive
                else (
                    "I2C RELENTI"
                    if self.use_i2c and self.bus is not None
                    else "MODE TEST"
                )
            ),
            "uptime": now - self.diagnostics_started,
            "packets": self.diagnostics_packets,
            "errors": self.diagnostics_errors,
            "idle_packets": self.diagnostics_idle_packet_count,
            "accepted_total": sum(self.diagnostics_counts.values()),
            "suppressed_total": sum(self.diagnostics_suppressed.values()),
            "groups": groups,
            "history": history,
            "packet_history": packet_history,
            "score_history": score_history,
            "last_packet": last_packet,
            "last_bus_packet": last_bus_packet,
            "bus_alive": bus_alive,
            "bus_heartbeat_age": bus_heartbeat_age,
            "last_event": last_event,
            "last_score_event": last_score_event,
            "use_i2c": self.use_i2c,
            "analysis": {
                "alerts": alerts[:10],
                "actions": actions[:6],
                "tested_groups": sum(
                    1
                    for group in groups
                    if group["accepted"] > 0 or group["suppressed"] > 0
                ),
                "healthy_groups": sum(1 for group in groups if group["health"] == "ok"),
            },
            "audit": {
                "missing_in_firmware": missing_in_firmware,
                "extra_in_firmware": extra_in_firmware,
                "missing_in_schematic": missing_in_schematic,
                "extra_in_schematic": extra_in_schematic,
                "button_conflicts": button_conflicts,
                "firmware_button_pins": sorted(self.firmware_button_reference_pins),
                "boot_strap_buttons": boot_strap_buttons,
                "pull_mode_firmware": self.pull_mode_reference["firmware"],
                "pull_mode_schematic": self.pull_mode_reference["schematic"],
                "wiring_notes": list(self.wiring_notes),
            },
        }
