# pyright: reportAttributeAccessIssue=false
import math
import time

import pygame

from src.constants import BLACK, CHROME_COLORS, WHITE, YELLOW


class UIMenuMixin:
    MENU_CACHE_FPS = 8

    def freeze_menu_cache_value(self, value):
        if isinstance(value, dict):
            return tuple(
                (key, self.freeze_menu_cache_value(item))
                for key, item in sorted(value.items())
            )
        if isinstance(value, (list, tuple)):
            return tuple(self.freeze_menu_cache_value(item) for item in value)
        return value

    def get_menu_frame_cache_key(self, menu, mode):
        options_signature = tuple(
            self.freeze_menu_cache_value(option) for option in menu.options
        )
        return (
            mode,
            int(time.monotonic() * self.MENU_CACHE_FPS),
            menu.selected_option,
            options_signature,
        )

    def draw_menu(self, menu):
        cache_key = self.get_menu_frame_cache_key(menu, "menu")
        cached_surface = self._menu_frame_cache.get(cache_key)
        if cached_surface is not None:
            self.display.screen.blit(cached_surface, (0, 0))
            pygame.display.update()
            return

        phase = time.monotonic()
        selected_option = menu.options[menu.selected_option]
        subtitle = f"{selected_option['name']} : {selected_option['value']}"
        self.display.screen.blit(self.display.resources["menu_background"], (0, 0))
        self.draw_vertical_gradient((6, 18, 36), (10, 56, 94), alpha=132)
        self.draw_spotlight_canopy(phase, intensity=1.0, tint=(255, 224, 168))
        self.draw_stage_floor(phase, horizon_ratio=0.74, tint=(120, 214, 255), alpha=24)
        self.draw_ambient_backdrop(phase)
        self.draw_screen_frame(phase)
        self.draw_scene_badges(
            "EDITION PRESTIGE",
            f"OPTION {menu.selected_option + 1:02d}/{len(menu.options):02d}",
            phase,
        )
        self.draw_title_panel("BOLIRANA", subtitle, phase)
        self._draw_option_grid(
            menu.options, menu.selected_option, show_value=True, phase=phase
        )
        footer_prompt = (
            "NEXT pour naviguer  |  RIGHT pour changer  |  ENTER pour analyser"
            if menu.is_sensor_analysis_selected()
            else "NEXT pour naviguer  |  RIGHT pour changer  |  ENTER pour lancer"
        )
        self.draw_footer_prompt(
            footer_prompt,
            phase,
        )
        self._menu_frame_cache = {cache_key: self.display.screen.copy()}
        pygame.display.update()

    def draw_sensor_analysis(self, snapshot, page_index=0):
        phase = time.monotonic()
        page_labels = [
            "PAGE 1/4  OVERVIEW",
            "PAGE 2/4  TIMELINE",
            "PAGE 3/4  RAW I2C",
            "PAGE 4/4  AUDIT & FIX",
        ]
        mode_label = page_labels[page_index % len(page_labels)]
        subtitle = (
            "ESP32 en direct"
            if snapshot["bus_alive"]
            else "Mode test ou bus I2C inactif"
        )
        self.display.screen.blit(self.display.resources["menu_background"], (0, 0))
        self.draw_vertical_gradient((6, 14, 30), (8, 74, 86), alpha=150)
        self.draw_spotlight_canopy(phase, intensity=0.96, tint=(122, 244, 220))
        self.draw_stage_floor(phase, horizon_ratio=0.75, tint=(110, 232, 214), alpha=24)
        self.draw_ambient_backdrop(phase)
        self.draw_screen_frame(
            phase,
            accent_color=(118, 242, 214),
            secondary_color=(255, 214, 112),
        )
        self.draw_scene_badges("LAB CAPTEURS", mode_label, phase)
        self.draw_title_panel("ANALYSE ESP32", subtitle, phase)
        self._draw_sensor_metrics(snapshot, phase)
        if page_index == 0:
            self._draw_sensor_overview(snapshot, phase)
        elif page_index == 1:
            self._draw_sensor_timeline(snapshot, phase)
        elif page_index == 2:
            self._draw_sensor_raw_i2c(snapshot, phase)
        else:
            self._draw_sensor_audit(snapshot, phase)
        self.draw_footer_prompt(
            "NEXT change de page  |  RIGHT reset analyse  |  ENTER retour menu",
            phase,
        )
        pygame.display.update()

    def _draw_sensor_metrics(self, snapshot, phase):
        badges = [
            (snapshot["transport"], (44, 210, 188, 218), BLACK),
            (f"LECTURES {snapshot['packets']}", (6, 24, 52, 214), YELLOW),
            (f"VALIDES {snapshot['accepted_total']}", (255, 214, 82, 224), BLACK),
            (f"BLOQUEES {snapshot['suppressed_total']}", (194, 86, 62, 224), WHITE),
            (f"ERREURS {snapshot['errors']}", (96, 28, 34, 222), WHITE),
            (
                f"TESTES {snapshot['analysis']['tested_groups']}/{len(snapshot['groups'])}",
                (24, 86, 164, 220),
                WHITE,
            ),
        ]

        x = 52
        y = 178
        gap = 14
        for label, fill, text_color in badges:
            width = max(126, min(220, self.display.font_small.size(label)[0] + 34))
            rect = pygame.Rect(x, y, width, 30)
            self.draw_badge(label, rect, fill, text_color=text_color)
            x += width + gap

    def _draw_sensor_overview(self, snapshot, phase):
        grid_rect = pygame.Rect(44, 226, 604, 474)
        detail_rect = pygame.Rect(672, 226, 308, 474)
        self._draw_data_panel(grid_rect, phase, "CARTE DES DETECTIONS")
        self._draw_data_panel(detail_rect, phase, "TELEMETRIE")

        columns = 2
        card_width = 270
        card_height = 72
        gap_x = 18
        gap_y = 16
        start_x = grid_rect.x + 18
        start_y = grid_rect.y + 54

        family_colors = {
            "side": (54, 148, 238),
            "bonus": (255, 214, 82),
            "frog": (102, 220, 126),
            "button": (255, 132, 132),
        }

        for index, group in enumerate(snapshot["groups"]):
            x = start_x + (index % columns) * (card_width + gap_x)
            y = start_y + (index // columns) * (card_height + gap_y)
            card_rect = pygame.Rect(x, y, card_width, card_height)
            is_live = group["recent_age"] is not None and group["recent_age"] < 1.2
            accent = family_colors.get(group["family"], (120, 214, 255))
            fill = (*accent, 216 if is_live else 170)
            glow_alpha = 96 if is_live else 46
            health_text, health_fill, health_text_color = self._get_sensor_health_badge(
                group["health"], is_live
            )

            self.draw_panel_shadow(
                card_rect,
                alpha=78 if is_live else 54,
                inflate=12,
                offset=(0, 8),
                border_radius=18,
            )
            card_surface = pygame.Surface(card_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                card_surface,
                (10, 26, 48, 210),
                card_surface.get_rect(),
                border_radius=18,
            )
            pygame.draw.rect(
                card_surface,
                (*accent, 28 + glow_alpha),
                (0, 0, card_rect.width, 18),
                border_radius=18,
            )
            pygame.draw.rect(
                card_surface,
                (255, 255, 255, 16),
                (8, 8, card_rect.width - 16, 16),
                border_radius=10,
            )
            self.display.screen.blit(card_surface, card_rect.topleft)
            self.draw_chrome_rect(card_rect, CHROME_COLORS, 18, 3)
            self.draw_badge(
                group["name"],
                pygame.Rect(card_rect.left + 12, card_rect.top + 10, 126, 22),
                fill,
                text_color=BLACK if group["family"] != "button" else WHITE,
            )
            self.draw_badge(
                health_text,
                pygame.Rect(card_rect.right - 84, card_rect.top + 10, 72, 22),
                health_fill,
                text_color=health_text_color,
            )
            pins_text = " / ".join(str(pin) for pin in group["pins"])
            self.draw_text_with_shadow(
                f"Pins {pins_text}",
                self.display.font_tiny,
                WHITE,
                BLACK,
                (card_rect.left + 16, card_rect.top + 36),
            )
            self.draw_text_with_shadow(
                f"Detectes {group['accepted']}",
                self.display.font_small,
                WHITE,
                BLACK,
                (card_rect.left + 16, card_rect.bottom - 18),
            )
            self.draw_text_with_shadow(
                (group["issues"][0] if group["issues"] else "RAS")[:28],
                self.display.font_tiny,
                YELLOW,
                BLACK,
                (card_rect.right - 98, card_rect.bottom - 18),
                center=True,
            )

        info_x = detail_rect.x + 18
        info_y = detail_rect.y + 62
        self._draw_snapshot_line(
            "Session", f"{snapshot['uptime']:.1f}s", info_x, info_y
        )
        self._draw_snapshot_line(
            "Dernier paquet",
            self._format_packet_text(snapshot["last_packet"]),
            info_x,
            info_y + 42,
        )
        last_event = snapshot["last_event"]
        self._draw_snapshot_line(
            "Dernier event",
            self._format_event_text(last_event),
            info_x,
            info_y + 84,
        )
        self._draw_snapshot_line(
            "Etat bus",
            (
                "Heartbeat actif"
                if snapshot["bus_alive"]
                else "I2C absent, ralenti ou test mode"
            ),
            info_x,
            info_y + 126,
        )

        hint_rect = pygame.Rect(detail_rect.x + 16, detail_rect.bottom - 138, 276, 104)
        hint_surface = pygame.Surface(hint_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            hint_surface, (8, 22, 42, 208), hint_surface.get_rect(), border_radius=18
        )
        pygame.draw.rect(
            hint_surface,
            (255, 255, 255, 16),
            (8, 8, hint_rect.width - 16, 22),
            border_radius=12,
        )
        self.display.screen.blit(hint_surface, hint_rect.topleft)
        self.draw_chrome_rect(hint_rect, CHROME_COLORS, 18, 2)
        self.draw_badge(
            "MODE D'EMPLOI",
            pygame.Rect(hint_rect.x + 12, hint_rect.y - 10, 132, 22),
            (255, 214, 82, 224),
            text_color=BLACK,
        )
        instructions = [
            "Declenche chaque capteur et observe son etat.",
            "NEXT ouvre timeline, raw I2C puis audit/fix.",
            "RIGHT remet les compteurs a zero.",
            "ENTER revient au menu principal.",
        ]
        for index, line in enumerate(instructions):
            self.draw_text_with_shadow(
                line,
                self.display.font_tiny,
                WHITE,
                BLACK,
                (hint_rect.x + 14, hint_rect.y + 20 + index * 18),
            )

    def _draw_sensor_timeline(self, snapshot, phase):
        history_rect = pygame.Rect(44, 226, 572, 474)
        stats_rect = pygame.Rect(636, 226, 344, 474)
        self._draw_data_panel(history_rect, phase, "FLUX DES DETECTIONS")
        self._draw_data_panel(stats_rect, phase, "TOP DES CAPTEURS")

        rows = snapshot["history"][:12]
        start_y = history_rect.y + 56
        for index, event in enumerate(rows):
            row_rect = pygame.Rect(
                history_rect.x + 14, start_y + index * 32, history_rect.width - 28, 26
            )
            fill = (28, 112, 84, 214) if event["accepted"] else (118, 44, 44, 214)
            row_surface = pygame.Surface(row_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                row_surface, (8, 22, 42, 202), row_surface.get_rect(), border_radius=12
            )
            pygame.draw.rect(
                row_surface,
                (*fill[:3], 40),
                (0, 0, row_rect.width, 26),
                border_radius=12,
            )
            self.display.screen.blit(row_surface, row_rect.topleft)
            self.draw_chrome_rect(row_rect, CHROME_COLORS, 12, 2)
            badge_text = "OK" if event["accepted"] else event["reason"].upper()
            self.draw_badge(
                badge_text,
                pygame.Rect(row_rect.x + 10, row_rect.y + 2, 72, 22),
                fill,
                text_color=BLACK if event["accepted"] else WHITE,
            )
            event_text = f"{event['label']}  |  pin {event['pin']}  |  {event['mode']}"
            self.draw_text_with_shadow(
                event_text,
                self.display.font_tiny,
                WHITE,
                BLACK,
                (row_rect.x + 94, row_rect.y + 13),
            )
            self.draw_text_with_shadow(
                f"-{event['age']:.2f}s",
                self.display.font_tiny,
                YELLOW,
                BLACK,
                (row_rect.right - 46, row_rect.y + 13),
                center=True,
            )

        if not rows:
            self.draw_text_with_shadow(
                "Aucune detection pour le moment.",
                self.display.font_small,
                WHITE,
                BLACK,
                history_rect.center,
                center=True,
            )

        ranking = sorted(
            snapshot["groups"],
            key=lambda group: (group["accepted"], -group["suppressed"]),
            reverse=True,
        )
        stats_y = stats_rect.y + 56
        for index, group in enumerate(ranking[:8]):
            bar_rect = pygame.Rect(
                stats_rect.x + 16, stats_y + index * 48, stats_rect.width - 32, 36
            )
            bar_surface = pygame.Surface(bar_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                bar_surface, (10, 26, 48, 210), bar_surface.get_rect(), border_radius=14
            )
            self.display.screen.blit(bar_surface, bar_rect.topleft)
            self.draw_chrome_rect(bar_rect, CHROME_COLORS, 14, 2)
            score_width = 0
            if snapshot["accepted_total"] > 0:
                score_width = int(
                    (bar_rect.width - 96)
                    * (group["accepted"] / snapshot["accepted_total"])
                )
            if score_width > 0:
                pygame.draw.rect(
                    self.display.screen,
                    (118, 242, 214, 74),
                    (bar_rect.x + 2, bar_rect.y + 2, score_width, bar_rect.height - 4),
                    border_radius=12,
                )
            self.draw_badge(
                f"#{index + 1}",
                pygame.Rect(bar_rect.x + 8, bar_rect.y + 7, 42, 22),
                (255, 214, 82, 224),
                text_color=BLACK,
            )
            self.draw_text_with_shadow(
                group["name"],
                self.display.font_tiny,
                WHITE,
                BLACK,
                (bar_rect.x + 62, bar_rect.y + 18),
            )
            self.draw_text_with_shadow(
                f"{group['accepted']} ok / {group['suppressed']} cooldown",
                self.display.font_tiny,
                YELLOW,
                BLACK,
                (bar_rect.right - 90, bar_rect.y + 18),
                center=True,
            )

        packet_rect = pygame.Rect(
            stats_rect.x + 16, stats_rect.bottom - 132, stats_rect.width - 32, 102
        )
        packet_surface = pygame.Surface(packet_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            packet_surface,
            (8, 22, 42, 208),
            packet_surface.get_rect(),
            border_radius=16,
        )
        self.display.screen.blit(packet_surface, packet_rect.topleft)
        self.draw_chrome_rect(packet_rect, CHROME_COLORS, 16, 2)
        self.draw_badge(
            "SCORE JEU",
            pygame.Rect(packet_rect.x + 12, packet_rect.y - 10, 132, 22),
            (118, 242, 214, 220),
            text_color=BLACK,
        )
        score_lines = self._format_score_history_lines(snapshot["score_history"])
        for index, line in enumerate(score_lines):
            self.draw_text_with_shadow(
                line,
                self.display.font_tiny,
                WHITE,
                BLACK,
                (packet_rect.x + 14, packet_rect.y + 20 + index * 22),
            )

    def _draw_sensor_raw_i2c(self, snapshot, phase):
        stream_rect = pygame.Rect(44, 226, 572, 474)
        detail_rect = pygame.Rect(636, 226, 344, 474)
        self._draw_data_panel(stream_rect, phase, "TRAME BRUTE I2C")
        self._draw_data_panel(detail_rect, phase, "ETAT DU BUS")

        rows = snapshot["packet_history"][:11]
        start_y = stream_rect.y + 56
        for index, packet in enumerate(rows):
            row_rect = pygame.Rect(
                stream_rect.x + 14, start_y + index * 32, stream_rect.width - 28, 26
            )
            fill = (
                (44, 210, 188, 214)
                if packet.get("state") == "HIGH"
                else (160, 76, 58, 214)
            )
            row_surface = pygame.Surface(row_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                row_surface, (8, 22, 42, 202), row_surface.get_rect(), border_radius=12
            )
            pygame.draw.rect(
                row_surface,
                (*fill[:3], 38),
                (0, 0, row_rect.width, 26),
                border_radius=12,
            )
            self.display.screen.blit(row_surface, row_rect.topleft)
            self.draw_chrome_rect(row_rect, CHROME_COLORS, 12, 2)
            badge_text = (
                "ERR" if packet.get("state") == "ERROR" else packet.get("state", "UNK")
            )
            self.draw_badge(
                badge_text,
                pygame.Rect(row_rect.x + 10, row_rect.y + 2, 72, 22),
                fill,
                text_color=BLACK if badge_text == "HIGH" else WHITE,
            )
            raw_text = f"raw {packet.get('raw', [])}"
            if packet.get("pin") is not None:
                raw_text += f"  |  pin {packet['pin']}"
            self.draw_text_with_shadow(
                raw_text,
                self.display.font_tiny,
                WHITE,
                BLACK,
                (row_rect.x + 94, row_rect.y + 13),
            )
            self.draw_text_with_shadow(
                f"-{packet.get('age', 0.0):.2f}s",
                self.display.font_tiny,
                YELLOW,
                BLACK,
                (row_rect.right - 46, row_rect.y + 13),
                center=True,
            )

        if not rows:
            self.draw_text_with_shadow(
                (
                    "Bus actif, aucun message capteur pour le moment."
                    if snapshot["bus_alive"]
                    else "Aucune trame capteur recue pour le moment."
                ),
                self.display.font_small,
                WHITE,
                BLACK,
                stream_rect.center,
                center=True,
            )

        detail_x = detail_rect.x + 18
        detail_y = detail_rect.y + 62
        last_packet = snapshot["last_packet"]
        last_bus_packet = snapshot["last_bus_packet"]
        event_reads = len(snapshot["packet_history"])
        self._draw_snapshot_line(
            "Etat bus",
            "Actif" if snapshot["bus_alive"] else "Silencieux / timeout",
            detail_x,
            detail_y,
        )
        self._draw_snapshot_line(
            "Dernier heartbeat",
            f"{snapshot['bus_heartbeat_age']:.2f}s",
            detail_x,
            detail_y + 62,
        )
        self._draw_snapshot_line(
            "Dernier capteur",
            self._format_packet_text(last_packet),
            detail_x,
            detail_y + 124,
        )
        self._draw_snapshot_line(
            "Dernier score jeu",
            self._format_score_event_text(snapshot["last_score_event"]),
            detail_x,
            detail_y + 186,
        )
        self._draw_snapshot_line(
            "Flux recent",
            f"{event_reads} messages capteur  |  {snapshot['idle_packets']} heartbeats",
            detail_x,
            detail_y + 248,
        )
        self._draw_snapshot_line(
            "Derniere lecture bus",
            str(last_bus_packet.get("raw", [])),
            detail_x,
            detail_y + 310,
        )

        hint_rect = pygame.Rect(detail_rect.x + 16, detail_rect.bottom - 126, 312, 92)
        hint_surface = pygame.Surface(hint_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            hint_surface, (8, 22, 42, 208), hint_surface.get_rect(), border_radius=18
        )
        self.display.screen.blit(hint_surface, hint_rect.topleft)
        self.draw_chrome_rect(hint_rect, CHROME_COLORS, 18, 2)
        self.draw_badge(
            "AIDE RAW I2C",
            pygame.Rect(hint_rect.x + 12, hint_rect.y - 10, 132, 22),
            (118, 242, 214, 220),
            text_color=BLACK,
        )

    def _format_score_history_lines(self, score_history):
        if not score_history:
            return [
                "Aucun score jeu recu.",
                "Declenche un capteur sur cette page.",
                "Le verdict du jeu apparait ici.",
            ]
        lines = []
        for event in score_history[:3]:
            lines.append(self._format_score_event_text(event))
        return lines

    def _format_score_event_text(self, event):
        if event is None:
            return "Aucun verdict score pour le moment"
        if event.get("status") == "scored":
            label = event.get("label") or f"pin {event.get('pin', '?')}"
            return f"OK {label}  |  +{event.get('points', 0)}  |  {event.get('player', '-')}"
        reason = event.get("reason") or event.get("status") or "inconnu"
        label = event.get("label") or f"pin {event.get('pin', '?')}"
        return f"{reason.upper()}  |  {label}  |  {event.get('player', '-')}"

    def _draw_sensor_audit(self, snapshot, phase):
        alerts_rect = pygame.Rect(44, 226, 470, 474)
        audit_rect = pygame.Rect(536, 226, 444, 474)
        self._draw_data_panel(alerts_rect, phase, "ALERTES & ACTIONS")
        self._draw_data_panel(audit_rect, phase, "AUDIT CABLAGE / FIRMWARE")

        alert_y = alerts_rect.y + 54
        for index, alert in enumerate(snapshot["analysis"]["alerts"][:6]):
            row_rect = pygame.Rect(
                alerts_rect.x + 14,
                alert_y + index * 64,
                alerts_rect.width - 28,
                54,
            )
            fill = self._get_alert_fill(alert["severity"])
            row_surface = pygame.Surface(row_rect.size, pygame.SRCALPHA)
            pygame.draw.rect(
                row_surface,
                (8, 22, 42, 208),
                row_surface.get_rect(),
                border_radius=16,
            )
            pygame.draw.rect(
                row_surface,
                (*fill[:3], 34),
                (0, 0, row_rect.width, 54),
                border_radius=16,
            )
            self.display.screen.blit(row_surface, row_rect.topleft)
            self.draw_chrome_rect(row_rect, CHROME_COLORS, 16, 2)
            self.draw_badge(
                alert["severity"].upper(),
                pygame.Rect(row_rect.x + 10, row_rect.y + 8, 82, 22),
                fill,
                text_color=BLACK if alert["severity"] in {"ok", "watch"} else WHITE,
            )
            self.draw_text_with_shadow(
                alert["title"],
                self.display.font_small,
                WHITE,
                BLACK,
                (row_rect.x + 106, row_rect.y + 16),
            )
            self.draw_text_with_shadow(
                alert["detail"],
                self.display.font_tiny,
                YELLOW,
                BLACK,
                (row_rect.x + 14, row_rect.y + 36),
            )

        action_rect = pygame.Rect(
            alerts_rect.x + 14,
            alerts_rect.bottom - 136,
            alerts_rect.width - 28,
            112,
        )
        action_surface = pygame.Surface(action_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            action_surface,
            (8, 22, 42, 212),
            action_surface.get_rect(),
            border_radius=18,
        )
        self.display.screen.blit(action_surface, action_rect.topleft)
        self.draw_chrome_rect(action_rect, CHROME_COLORS, 18, 2)
        self.draw_badge(
            "PLAN DE TEST",
            pygame.Rect(action_rect.x + 12, action_rect.y - 10, 126, 22),
            (255, 214, 82, 224),
            text_color=BLACK,
        )
        for index, action in enumerate(snapshot["analysis"]["actions"][:4]):
            self.draw_text_with_shadow(
                f"{index + 1}. {action}",
                self.display.font_tiny,
                WHITE,
                BLACK,
                (action_rect.x + 14, action_rect.y + 18 + index * 22),
            )

        audit = snapshot["audit"]
        audit_lines = [
            (
                "Pins capteurs absents du firmware",
                self._format_pin_list(audit["missing_in_firmware"]),
            ),
            (
                "Pins firmware hors carte jeu",
                self._format_pin_list(audit["extra_in_firmware"]),
            ),
            (
                "Pins capteurs hors schema",
                self._format_pin_list(audit["missing_in_schematic"]),
            ),
            (
                "Pins schema non utilises",
                self._format_pin_list(audit["extra_in_schematic"]),
            ),
            (
                "Collision bouton / firmware",
                self._format_pin_list(audit["button_conflicts"]),
            ),
        ]
        base_y = audit_rect.y + 54
        for index, (label, value) in enumerate(audit_lines):
            self.draw_text_with_shadow(
                label,
                self.display.font_tiny,
                YELLOW,
                BLACK,
                (audit_rect.x + 16, base_y + index * 56),
            )
            self.draw_text_with_shadow(
                value,
                self.display.font_small,
                WHITE,
                BLACK,
                (audit_rect.x + 16, base_y + 18 + index * 56),
            )

        notes_rect = pygame.Rect(
            audit_rect.x + 12,
            audit_rect.bottom - 146,
            audit_rect.width - 24,
            122,
        )
        notes_surface = pygame.Surface(notes_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            notes_surface,
            (8, 22, 42, 208),
            notes_surface.get_rect(),
            border_radius=18,
        )
        self.display.screen.blit(notes_surface, notes_rect.topleft)
        self.draw_chrome_rect(notes_rect, CHROME_COLORS, 18, 2)
        self.draw_badge(
            "RAPPELS SCHEMA",
            pygame.Rect(notes_rect.x + 12, notes_rect.y - 10, 136, 22),
            (118, 242, 214, 220),
            text_color=BLACK,
        )

    def _draw_data_panel(self, rect, phase, label):
        panel_rect = pygame.Rect(rect)
        self.draw_panel_shadow(
            panel_rect, alpha=104, inflate=22, offset=(0, 12), border_radius=28
        )
        panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            panel_surface, (10, 24, 54, 214), panel_surface.get_rect(), border_radius=28
        )
        pygame.draw.rect(
            panel_surface,
            (255, 255, 255, 14),
            (12, 12, panel_rect.width - 24, 28),
            border_radius=18,
        )
        self.display.screen.blit(panel_surface, panel_rect.topleft)
        self.draw_panel_grid(
            panel_rect.inflate(-18, -18), phase, (118, 242, 214), 12, 58
        )
        self.draw_halftone_dots(
            panel_rect.inflate(-24, -20),
            color=(255, 255, 255),
            alpha=9,
            spacing=22,
            radius=2,
            drift=phase * 5,
        )
        self.draw_chrome_rect(panel_rect, CHROME_COLORS, 26, 4)
        self.draw_badge(
            label,
            pygame.Rect(panel_rect.x + 16, panel_rect.y - 10, 168, 22),
            (255, 214, 82, 224),
            text_color=BLACK,
        )

    def _get_sensor_health_badge(self, health, is_live):
        if health == "error":
            return ("FAIL", (154, 48, 48, 224), WHITE)
        if health == "warning":
            return ("WARN", (196, 116, 48, 224), WHITE)
        if health == "watch":
            return ("CHECK", (76, 128, 210, 224), WHITE)
        if is_live:
            return ("LIVE", (90, 236, 168, 220), BLACK)
        return ("OK", (24, 112, 84, 220), WHITE)

    def _get_alert_fill(self, severity):
        if severity == "error":
            return (154, 48, 48, 224)
        if severity == "warning":
            return (196, 116, 48, 224)
        if severity == "watch":
            return (76, 128, 210, 224)
        return (90, 236, 168, 220)

    def _format_pin_list(self, pins):
        if not pins:
            return "aucun"
        return ", ".join(str(pin) for pin in pins)

    def _draw_snapshot_line(self, label, value, x, y):
        self.draw_text_with_shadow(label, self.display.font_tiny, YELLOW, BLACK, (x, y))
        self.draw_text_with_shadow(
            value, self.display.font_small, WHITE, BLACK, (x, y + 18)
        )

    def _format_packet_text(self, packet):
        if packet is None:
            return "Aucun paquet recu"
        if packet.get("state") == "ERROR":
            return "Erreur de lecture I2C"
        raw = packet.get("raw", [])
        pin = packet.get("pin")
        if pin is None:
            return f"Raw {raw}  |  neutre"
        return f"Raw {raw}  |  pin {pin} {packet.get('state', 'IDLE')}"

    def _format_event_text(self, event):
        if event is None:
            return "Aucun evennement recu"
        outcome = "OK" if event["accepted"] else event["reason"].upper()
        return f"{event['label']}  |  {outcome}  |  -{event['age']:.2f}s"

    def draw_end_menu(self, menu):
        cache_key = self.get_menu_frame_cache_key(menu, "end_menu")
        cached_surface = self._menu_frame_cache.get(cache_key)
        if cached_surface is not None:
            self.display.screen.blit(cached_surface, (0, 0))
            pygame.display.update()
            return

        phase = time.monotonic()
        title = "PAUSE" if "Continuer" in menu.options else "FIN DE PARTIE"
        subtitle = "Choisis la suite du show"
        self.display.screen.blit(self.display.resources["menu_background"], (0, 0))
        self.draw_vertical_gradient((8, 16, 30), (46, 14, 28), alpha=144)
        self.draw_spotlight_canopy(phase, intensity=0.88, tint=(255, 204, 150))
        self.draw_stage_floor(phase, horizon_ratio=0.75, tint=(255, 196, 110), alpha=26)
        self.draw_ambient_backdrop(phase)
        self.draw_screen_frame(
            phase,
            accent_color=(255, 196, 110),
            secondary_color=(255, 120, 120),
        )
        self.draw_scene_badges("ARENA CONTROL", f"{len(menu.options)} CHOIX", phase)
        self.draw_title_panel(title, subtitle, phase)
        self._draw_option_grid(
            menu.options, menu.selected_option, show_value=False, phase=phase
        )
        self.draw_footer_prompt("NEXT pour naviguer  |  ENTER pour valider", phase)
        self._menu_frame_cache = {cache_key: self.display.screen.copy()}
        pygame.display.update()

    def _draw_option_grid(self, options, selected_option, show_value, phase=None):
        phase = time.monotonic() if phase is None else phase
        box_width, box_height, margin_x, margin_y = 408, 112, 24, 24
        border_radius, border_width = 18, 5

        num_rows = (len(options) + 1) // 2
        total_height = num_rows * box_height + (num_rows - 1) * margin_y
        start_x = (self.display.screen.get_width() - (2 * box_width + margin_x)) // 2
        start_y = (self.display.screen.get_height() - total_height) // 2 + 26

        for index, option in enumerate(options):
            x = start_x + (index % 2) * (box_width + margin_x)
            y = start_y + (index // 2) * (box_height + margin_y)
            is_selected = index == selected_option
            lift = int((8 + math.sin(phase * 5.5) * 4) if is_selected else 0)
            card_rect = pygame.Rect(x, y - lift, box_width, box_height)
            base_color = (26, 118, 194, 224) if is_selected else (10, 32, 66, 194)
            inner_color = (92, 214, 255, 92) if is_selected else (255, 255, 255, 18)

            self.draw_panel_shadow(
                card_rect,
                alpha=110 if is_selected else 72,
                inflate=18,
                offset=(0, 12),
                border_radius=22,
            )

            if is_selected:
                burst_surface = pygame.Surface(
                    (card_rect.width + 80, card_rect.height + 80), pygame.SRCALPHA
                )
                burst_center = burst_surface.get_rect().center
                for ray_index in range(10):
                    angle = ray_index * math.tau / 10 + phase * 0.3
                    inner = 26
                    outer = 74
                    pygame.draw.polygon(
                        burst_surface,
                        (255, 220, 126, 34),
                        [
                            (
                                burst_center[0] + math.cos(angle - 0.12) * inner,
                                burst_center[1] + math.sin(angle - 0.12) * inner,
                            ),
                            (
                                burst_center[0] + math.cos(angle) * outer,
                                burst_center[1] + math.sin(angle) * outer,
                            ),
                            (
                                burst_center[0] + math.cos(angle + 0.12) * inner,
                                burst_center[1] + math.sin(angle + 0.12) * inner,
                            ),
                        ],
                    )
                self.display.screen.blit(
                    burst_surface,
                    burst_surface.get_rect(center=card_rect.center),
                )

            self.draw_chrome_rect(
                card_rect,
                CHROME_COLORS,
                border_radius,
                border_width,
            )

            rect_surface = pygame.Surface(
                (box_width - 2 * border_width, box_height - 2 * border_width),
                pygame.SRCALPHA,
            )
            rect_surface = rect_surface.convert_alpha()
            pygame.draw.rect(
                rect_surface,
                base_color,
                rect_surface.get_rect(),
                border_radius=border_radius - border_width,
            )
            pygame.draw.rect(
                rect_surface,
                inner_color,
                (8, 8, rect_surface.get_width() - 16, rect_surface.get_height() // 2),
                border_radius=border_radius - border_width,
            )
            pygame.draw.rect(
                rect_surface,
                (255, 255, 255, 22 if is_selected else 10),
                rect_surface.get_rect(),
                width=2,
                border_radius=border_radius - border_width,
            )
            self.display.screen.blit(
                rect_surface,
                (card_rect.x + border_width, card_rect.y + border_width),
            )
            self.draw_halftone_dots(
                card_rect.inflate(-26, -20),
                color=(255, 255, 255),
                alpha=12 if is_selected else 8,
                spacing=22,
                radius=2,
                drift=phase * 4,
            )
            self.draw_arcade_screws(card_rect, inset=12, radius=3)
            index_rect = pygame.Rect(card_rect.right - 54, card_rect.top + 10, 40, 20)
            self.draw_badge(
                f"{index + 1:02d}",
                index_rect,
                (255, 255, 255, 22 if is_selected else 14),
                text_color=WHITE,
                border_color=(255, 255, 255, 32),
            )

            if is_selected:
                self.draw_marquee_lights(card_rect, phase, (255, 226, 126), count=16)
                chip_rect = pygame.Rect(card_rect.left + 14, card_rect.top - 14, 74, 22)
                chip_surface = pygame.Surface(chip_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    chip_surface,
                    (255, 214, 82, 220),
                    chip_surface.get_rect(),
                    border_radius=12,
                )
                self.display.screen.blit(chip_surface, chip_rect.topleft)
                self.draw_text_with_shadow(
                    "SELECT",
                    self.display.font_verysmall,
                    BLACK,
                    WHITE,
                    chip_rect.center,
                    shadow_offset=(1, 1),
                    center=True,
                )
                pygame.draw.polygon(
                    self.display.screen,
                    (255, 222, 126),
                    [
                        (card_rect.left - 14, card_rect.centery),
                        (card_rect.left - 2, card_rect.centery - 10),
                        (card_rect.left - 2, card_rect.centery + 10),
                    ],
                )
                pygame.draw.polygon(
                    self.display.screen,
                    (255, 222, 126),
                    [
                        (card_rect.right + 14, card_rect.centery),
                        (card_rect.right + 2, card_rect.centery - 10),
                        (card_rect.right + 2, card_rect.centery + 10),
                    ],
                )

            if show_value:
                name_text = self.display.font_medium.render(option["name"], True, WHITE)
                name_text_rect = name_text.get_rect(
                    center=(
                        card_rect.x + box_width // 2,
                        card_rect.y + 34,
                    )
                )
                pygame.draw.line(
                    self.display.screen,
                    (255, 255, 255, 46),
                    (card_rect.left + 24, card_rect.top + 52),
                    (card_rect.right - 24, card_rect.top + 52),
                    1,
                )
                value_rect = pygame.Rect(
                    card_rect.left + 98, card_rect.bottom - 36, 206, 26
                )
                self.draw_badge(
                    str(option["value"]),
                    value_rect,
                    (6, 20, 42, 198),
                    text_color=YELLOW,
                    border_color=(255, 220, 126, 90),
                    font=self.display.font_small,
                )
                hint_rect = pygame.Rect(
                    card_rect.left + 20, card_rect.bottom - 34, 66, 22
                )
                self.draw_badge(
                    "FUN",
                    hint_rect,
                    (255, 214, 82, 214) if is_selected else (8, 24, 44, 188),
                    text_color=BLACK if is_selected else WHITE,
                    border_color=(255, 255, 255, 70),
                )
                self.display.screen.blit(name_text, name_text_rect)
            else:
                name_text = self.display.font_medium.render(str(option), True, WHITE)
                name_text_rect = name_text.get_rect(
                    center=(card_rect.x + box_width // 2, card_rect.y + box_height // 2)
                )
                self.display.screen.blit(name_text, name_text_rect)
                if is_selected:
                    action_rect = pygame.Rect(
                        card_rect.left + 20, card_rect.bottom - 34, 88, 22
                    )
                    self.draw_badge(
                        "GO!",
                        action_rect,
                        (255, 214, 82, 220),
                        text_color=BLACK,
                        border_color=(255, 255, 255, 70),
                    )

    def play_intro(self):
        sound = self.display.resources.get("intro_sound")
        if sound:
            sound.play()
