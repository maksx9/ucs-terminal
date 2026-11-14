# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import queue
import time
from datetime import datetime
import json
import os
import sys
import ctypes


# Włączenie ostrości High-DPI na systemie Windows (brak rozmytych czcionek)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def resource_path(relative_path):
    """Zwraca poprawną ścieżkę do zasobów (działa ze źródeł oraz po spakowaniu PyInstallerem)."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "uart_config.json")


# ==================== NOWOCZESNE PALETY KOLORÓW (MOTYW JASNY I NOWOCZESNY INDYGO) ====================
THEMES = {
    "light": {
        "name": "light",
        "bg_app": "#f0f4f9",          # Świeże, miękkie tło w stylu Windows 11 / Fluent
        "bg_card": "#ffffff",         # Białe zaokrąglone karty
        "bg_subtle": "#f8fafc",       # Delikatne tło wierszy i kontenerów
        "bg_input": "#f1f5f9",        # Tło pól wpisywania
        "border": "#e2e8f0",          # Subtelne obramowanie kart
        "border_focus": "#6366f1",    # Indygo przy aktywności
        "fg_primary": "#0f172a",      # Głęboki grafit (główny tekst)
        "fg_secondary": "#64748b",    # Stonowany szary (etykiety i opisy)
        "accent": "#4f46e5",          # Nowoczesny Indygo (Primary)
        "accent_hover": "#4338ca",
        "accent_soft": "#eef2ff",     # Jasne tło pod akcenty
        "btn_neutral": "#f1f5f9",
        "btn_neutral_hover": "#e2e8f0",
        "btn_neutral_fg": "#1e293b",
        "success": "#10b981",         # Szmaragdowy zielony
        "success_hover": "#059669",
        "success_bg": "#ecfdf5",
        "success_fg": "#047857",
        "danger": "#ef4444",          # Koralowa czerwień
        "danger_hover": "#dc2626",
        "danger_bg": "#fef2f2",
        "danger_fg": "#b91c1c",
        "warning_bg": "#fffbeb",
        "warning_fg": "#b45309",
        "log_bg": "#f8fafc",
        "tx_color": "#4f46e5",        # Indygo dla wysłanych
        "rx_color": "#059669",        # Szmaragdowy dla odebranych
        "sys_color": "#64748b",
        "ts_color": "#94a3b8",
    },
    "dark": {
        "name": "dark",
        "bg_app": "#131620",          # Nowoczesny, miękki grafit-indygo (bez czerni retro)
        "bg_card": "#1c2030",         # Zaokrąglone karty
        "bg_subtle": "#23283b",       # Tło wierszy i sekcji wewnętrznych
        "bg_input": "#151824",        # Pola tekstowe
        "border": "#2b3248",          # Subtelny kontur
        "border_focus": "#6366f1",
        "fg_primary": "#f1f5f9",
        "fg_secondary": "#94a3b8",
        "accent": "#6366f1",          # Świeży Indygo-Fiolet
        "accent_hover": "#4f46e5",
        "accent_soft": "#262b44",
        "btn_neutral": "#262c40",
        "btn_neutral_hover": "#323a54",
        "btn_neutral_fg": "#e2e8f0",
        "success": "#10b981",
        "success_hover": "#059669",
        "success_bg": "#112e28",
        "success_fg": "#34d399",
        "danger": "#f43f5e",
        "danger_hover": "#e11d48",
        "danger_bg": "#311822",
        "danger_fg": "#fb7185",
        "warning_bg": "#332411",
        "warning_fg": "#fbbf24",
        "log_bg": "#151824",
        "tx_color": "#818cf8",        # Jasny indygo dla TX
        "rx_color": "#34d399",        # Miętowy dla RX
        "sys_color": "#94a3b8",
        "ts_color": "#64748b",
    }
}


# ==================== FUNKCJE RYSOWANIA ZAOKRĄGLEŃ NA CANVASIE ====================
def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=12, **kwargs):
    """Rysuje gładki zaokrąglony prostokąt na widgecie tk.Canvas."""
    r = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    points = [
        x1 + r, y1,
        x1 + r, y1,
        x2 - r, y1,
        x2 - r, y1,
        x2, y1,
        x2, y1 + r,
        x2, y1 + r,
        x2, y2 - r,
        x2, y2 - r,
        x2, y2,
        x2 - r, y2,
        x2 - r, y2,
        x1 + r, y2,
        x1 + r, y2,
        x1, y2,
        x1, y2 - r,
        x1, y2 - r,
        x1, y1 + r,
        x1, y1 + r,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class RoundedCard(tk.Canvas):
    """Nowoczesny kontener (karta) z zaokrąglonymi rogami i obramowaniem."""
    def __init__(self, parent, theme, radius=14, padding=14, **kwargs):
        super().__init__(parent, highlightthickness=0, bd=0, bg=theme["bg_app"], **kwargs)
        self.theme = theme
        self.radius = radius
        self.padding = padding
        self.inner = tk.Frame(self, bg=theme["bg_card"])
        self._win_id = self.create_window((padding, padding), window=self.inner, anchor="nw")
        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, event):
        self.delete("card_bg")
        w, h = max(event.width, 20), max(event.height, 20)
        p = self.padding
        draw_rounded_rect(
            self, 2, 2, w - 2, h - 2, radius=self.radius,
            fill=self.theme["bg_card"], outline=self.theme["border"], width=1.5, tags="card_bg"
        )
        self.tag_lower("card_bg")
        self.coords(self._win_id, p, p)
        self.itemconfigure(self._win_id, width=max(10, w - 2 * p), height=max(10, h - 2 * p))


class RoundedButton(tk.Canvas):
    """Zaokrąglony, nowoczesny przycisk z efektem hover i obsługą stanów."""
    def __init__(self, parent, text, command=None, kind="neutral", width=110, height=34, radius=9, theme=None, font=("Segoe UI Semibold", 9)):
        self.theme = theme or THEMES["light"]
        parent_bg = parent.cget("bg") if "bg" in parent.keys() else self.theme["bg_card"]
        super().__init__(parent, width=width, height=height, highlightthickness=0, bd=0, bg=parent_bg, cursor="hand2")
        self.text = text
        self.command = command
        self.kind = kind
        self.btn_w = width
        self.btn_h = height
        self.radius = radius
        self.font = font
        self._enabled = True
        self._hovered = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_click)
        self.bind("<Configure>", lambda e: self._redraw())
        self._redraw()

    def _colors(self):
        t = self.theme
        if not self._enabled:
            return t["btn_neutral"], t["fg_secondary"], t["border"]
        if self.kind == "accent":
            bg = t["accent_hover"] if self._hovered else t["accent"]
            return bg, "#ffffff", bg
        if self.kind == "success":
            bg = t["success_hover"] if self._hovered else t["success"]
            return bg, "#ffffff", bg
        if self.kind == "danger":
            bg = t["danger_hover"] if self._hovered else t["danger"]
            return bg, "#ffffff", bg
        if self.kind == "soft_danger":
            bg = t["danger"] if self._hovered else t["danger_bg"]
            fg = "#ffffff" if self._hovered else t["danger_fg"]
            return bg, fg, t["danger_bg"]
        if self.kind == "soft_accent":
            bg = t["accent"] if self._hovered else t["accent_soft"]
            fg = "#ffffff" if self._hovered else t["accent"]
            return bg, fg, t["accent_soft"]
        # neutral
        bg = t["btn_neutral_hover"] if self._hovered else t["btn_neutral"]
        return bg, t["btn_neutral_fg"], t["border"]

    def _redraw(self):
        self.delete("all")
        w = self.winfo_width() if self.winfo_width() > 5 else self.btn_w
        h = self.winfo_height() if self.winfo_height() > 5 else self.btn_h
        bg, fg, border = self._colors()
        draw_rounded_rect(self, 1, 1, w - 1, h - 1, radius=self.radius, fill=bg, outline=border, width=1)
        self.create_text(w / 2, h / 2, text=self.text, fill=fg, font=self.font)

    def _on_enter(self, _e):
        if self._enabled:
            self._hovered = True
            self._redraw()

    def _on_leave(self, _e):
        self._hovered = False
        self._redraw()

    def _on_click(self, _e):
        if self._enabled and self.command:
            self.command()

    def configure_btn(self, text=None, kind=None, enabled=None, theme=None, parent_bg=None):
        if text is not None:
            self.text = text
        if kind is not None:
            self.kind = kind
        if enabled is not None:
            self._enabled = enabled
            self.configure(cursor="hand2" if enabled else "arrow")
        if theme is not None:
            self.theme = theme
        if parent_bg is not None:
            self.configure(bg=parent_bg)
        self._redraw()


class ToggleSwitch(tk.Frame):
    """Nowoczesny przełącznik suwakowy (w stylu iOS / Fluent UI) z etykietą."""
    def __init__(self, parent, text, variable, command=None, theme=None):
        self.theme = theme or THEMES["light"]
        parent_bg = parent.cget("bg")
        super().__init__(parent, bg=parent_bg)
        self.variable = variable
        self.command = command

        self.canvas = tk.Canvas(self, width=38, height=22, highlightthickness=0, bd=0, bg=parent_bg, cursor="hand2")
        self.canvas.pack(side=tk.LEFT)

        self.label = tk.Label(self, text=text, bg=parent_bg, fg=self.theme["fg_primary"], font=("Segoe UI", 9), cursor="hand2")
        if text:
            self.label.pack(side=tk.LEFT, padx=(6, 0))

        self.canvas.bind("<ButtonRelease-1>", self._toggle)
        self.label.bind("<ButtonRelease-1>", self._toggle)
        self.variable.trace_add("write", lambda *_: self._redraw())
        self._redraw()

    def _toggle(self, _e=None):
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()

    def _redraw(self):
        self.canvas.delete("all")
        on = self.variable.get()
        t = self.theme
        track_color = t["accent"] if on else t["border"]
        draw_rounded_rect(self.canvas, 2, 3, 36, 19, radius=8, fill=track_color, outline=track_color)
        knob_x = 26 if on else 12
        self.canvas.create_oval(knob_x - 6, 5, knob_x + 6, 17, fill="#ffffff", outline="")

    def update_theme(self, theme, parent_bg):
        self.theme = theme
        self.configure(bg=parent_bg)
        self.canvas.configure(bg=parent_bg)
        self.label.configure(bg=parent_bg, fg=theme["fg_primary"])
        self._redraw()


class SegmentedControl(tk.Canvas):
    """Zaokrąglony przełącznik segmentowy (np. Uproszczony / Zaawansowany)."""
    def __init__(self, parent, options, variable, command=None, theme=None, width=230, height=32):
        self.theme = theme or THEMES["light"]
        parent_bg = parent.cget("bg")
        super().__init__(parent, width=width, height=height, highlightthickness=0, bd=0, bg=parent_bg, cursor="hand2")
        self.options = options  # lista krotek: [(value, label), ...]
        self.variable = variable
        self.command = command
        self.ctrl_w = width
        self.ctrl_h = height

        self.bind("<ButtonRelease-1>", self._on_click)
        self.variable.trace_add("write", lambda *_: self._redraw())
        self._redraw()

    def _on_click(self, event):
        seg_w = self.ctrl_w / len(self.options)
        idx = min(max(int(event.x // seg_w), 0), len(self.options) - 1)
        val = self.options[idx][0]
        if self.variable.get() != val:
            self.variable.set(val)
            if self.command:
                self.command()

    def _redraw(self):
        self.delete("all")
        t = self.theme
        w, h = self.ctrl_w, self.ctrl_h
        draw_rounded_rect(self, 1, 1, w - 1, h - 1, radius=9, fill=t["bg_input"], outline=t["border"], width=1)
        seg_w = (w - 6) / len(self.options)
        curr = self.variable.get()
        for i, (val, label) in enumerate(self.options):
            x1 = 3 + i * seg_w
            x2 = x1 + seg_w
            if val == curr:
                draw_rounded_rect(self, x1, 3, x2, h - 3, radius=7, fill=t["accent"], outline=t["accent"])
                fg = "#ffffff"
                fnt = ("Segoe UI Semibold", 9)
            else:
                fg = t["fg_secondary"]
                fnt = ("Segoe UI", 9)
            self.create_text((x1 + x2) / 2, h / 2, text=label, fill=fg, font=fnt)

    def update_theme(self, theme, parent_bg):
        self.theme = theme
        self.configure(bg=parent_bg)
        self._redraw()


# ==================== GŁÓWNA KLASA APLIKACJI ====================
class UARTTerminal:
    def __init__(self, root):
        self.root = root
        self.root.title("UCS Terminal 2.3 — Nowoczesny Terminal UART")
        self.root.geometry("1160x760")
        self.root.minsize(940, 620)

        # Ustawienie ikony okna
        ico_path = resource_path(os.path.join("assets", "UCS_Terminal.ico"))
        if os.path.exists(ico_path):
            try:
                self.root.iconbitmap(ico_path)
            except Exception:
                pass

        # Stan komunikacji
        self.ser = None
        self.read_thread = None
        self.running = False
        self.want_connected = False
        self.last_port = None
        self.last_baud = 115200
        self.send_thread = None
        self.sending = False

        # Kolejka zdarzeń GUI
        self.ui_queue = queue.Queue()

        # Zmienne stanu i trybu
        self.theme_mode = tk.StringVar(value="light")       # "light" (świeży nowoczesny) lub "dark" (indygo)
        self.ui_mode = tk.StringVar(value="simple")         # "simple" (Uproszczony) lub "advanced" (Zaawansowany)
        self.autoscroll = tk.BooleanVar(value=True)
        self.show_timestamps = tk.BooleanVar(value=True)
        self.hex_view = tk.BooleanVar(value=False)
        self.hex_send = tk.BooleanVar(value=False)
        self.auto_reconnect = tk.BooleanVar(value=True)
        self.dtr_var = tk.BooleanVar(value=False)
        self.rts_var = tk.BooleanVar(value=False)
        self.send_mode = tk.StringVar(value="once")
        self.line_ending = tk.StringVar(value="LF (\\n)")
        self.data_format = tk.StringVar(value="8N1")
        self.filter_var = tk.StringVar(value="")

        # Dane i statystyki
        self.cmd_entries = []
        self.log_lines = []
        self.tx_bytes = 0
        self.rx_bytes = 0
        self.manual_history = []
        self.history_idx = -1

        self.theme = THEMES[self.theme_mode.get()]
        self._setup_ttk_styles()
        self._build_ui()
        self._try_load_default_config()
        self._apply_ui_mode()

        self.root.after(25, self._process_ui_queue)

    # ==================== STYLIZACJA KOMPONENTÓW POMOCNICZYCH ====================
    def _setup_ttk_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self._refresh_ttk_styles()

    def _refresh_ttk_styles(self):
        t = self.theme
        self.root.configure(bg=t["bg_app"])
        self.style.configure(
            "Modern.TCombobox",
            fieldbackground=t["bg_input"],
            background=t["btn_neutral"],
            foreground=t["fg_primary"],
            arrowcolor=t["fg_secondary"],
            bordercolor=t["border"],
            lightcolor=t["bg_input"],
            darkcolor=t["bg_input"],
            padding=6
        )
        self.style.map(
            "Modern.TCombobox",
            fieldbackground=[("readonly", t["bg_input"])],
            selectbackground=[("readonly", t["bg_input"])],
            selectforeground=[("readonly", t["fg_primary"])],
            bordercolor=[("focus", t["accent"])]
        )
        self.root.option_add("*TCombobox*Listbox.background", t["bg_card"])
        self.root.option_add("*TCombobox*Listbox.foreground", t["fg_primary"])
        self.root.option_add("*TCombobox*Listbox.selectBackground", t["accent"])
        self.root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

        self.style.configure(
            "Vertical.TScrollbar",
            background=t["btn_neutral"],
            troughcolor=t["bg_subtle"],
            bordercolor=t["bg_subtle"],
            arrowcolor=t["fg_secondary"]
        )

    def _make_entry(self, parent, textvariable, width=18, font=("Segoe UI", 10), justify=tk.LEFT):
        """Tworzy nowoczesne pole tekstowe z delikatną ramką."""
        t = self.theme
        e = tk.Entry(
            parent, textvariable=textvariable, width=width, font=font, justify=justify,
            bg=t["bg_input"], fg=t["fg_primary"], insertbackground=t["fg_primary"],
            relief="flat", highlightthickness=1,
            highlightbackground=t["border"], highlightcolor=t["accent"], bd=5
        )
        return e

    # ==================== BUDOWANIE INTERFEJSU ====================
    def _build_ui(self):
        t = self.theme

        # ------------------------------------------------------------------
        # 1. NAGŁÓWEK APLIKACJI (TYTUŁ + PRZEŁĄCZNIK TRYBU + INSTRUKCJA)
        # ------------------------------------------------------------------
        self.header_frame = tk.Frame(self.root, bg=t["bg_app"])
        self.header_frame.pack(fill=tk.X, padx=18, pady=(14, 6))

        # Lewa strona nagłówka: Logo + Tytuł + Status Badge
        title_box = tk.Frame(self.header_frame, bg=t["bg_app"])
        title_box.pack(side=tk.LEFT)

        self.app_title_lbl = tk.Label(
            title_box, text="UCS Terminal", bg=t["bg_app"], fg=t["fg_primary"],
            font=("Segoe UI Semibold", 16)
        )
        self.app_title_lbl.pack(side=tk.LEFT, padx=(0, 12))

        self.status_badge = tk.Label(
            title_box, text="● Rozłączono", bg=t["danger_bg"], fg=t["danger_fg"],
            font=("Segoe UI Semibold", 9), padx=12, pady=4
        )
        self.status_badge.pack(side=tk.LEFT)

        # Prawa strona nagłówka: Instrukcja, Motyw Jasny/Ciemny, Tryb Uproszczony/Zaawansowany
        right_hdr = tk.Frame(self.header_frame, bg=t["bg_app"])
        right_hdr.pack(side=tk.RIGHT)

        self.help_btn = RoundedButton(
            right_hdr, text="📖 Instrukcja obsługi", command=self._show_manual_window,
            kind="soft_accent", width=152, height=32, theme=t
        )
        self.help_btn.pack(side=tk.RIGHT, padx=(10, 0))

        self.theme_btn = RoundedButton(
            right_hdr, text="🌙 Motyw" if self.theme_mode.get() == "light" else "☀️ Motyw",
            command=self._toggle_theme, kind="neutral", width=88, height=32, theme=t
        )
        self.theme_btn.pack(side=tk.RIGHT, padx=(10, 0))

        self.mode_seg = SegmentedControl(
            right_hdr,
            options=[("simple", "Uproszczony"), ("advanced", "Zaawansowany")],
            variable=self.ui_mode,
            command=self._apply_ui_mode,
            theme=t, width=230, height=32
        )
        self.mode_seg.pack(side=tk.RIGHT)

        self.mode_lbl = tk.Label(
            right_hdr, text="Widok:", bg=t["bg_app"], fg=t["fg_secondary"],
            font=("Segoe UI Semibold", 9)
        )
        self.mode_lbl.pack(side=tk.RIGHT, padx=(0, 8))

        # ------------------------------------------------------------------
        # 2. KARTA POŁĄCZENIA (ZAOKRĄGLONA)
        # ------------------------------------------------------------------
        self.conn_card = RoundedCard(self.root, theme=t, radius=14, padding=12, height=74)
        self.conn_card.pack(fill=tk.X, padx=16, pady=(4, 8))
        c_in = self.conn_card.inner

        # Sekcja podstawowa (zawsze widoczna)
        self.conn_basic_frame = tk.Frame(c_in, bg=t["bg_card"])
        self.conn_basic_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(self.conn_basic_frame, text="Port COM", bg=t["bg_card"], fg=t["fg_secondary"], font=("Segoe UI Semibold", 9)).pack(side=tk.LEFT, padx=(4, 6))
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(self.conn_basic_frame, textvariable=self.port_var, width=28, state="readonly", style="Modern.TCombobox", font=("Segoe UI", 9))
        self.port_combo.pack(side=tk.LEFT, padx=(0, 6))

        self.refresh_btn = RoundedButton(self.conn_basic_frame, text="⟳ Odśwież", command=self._refresh_ports, kind="neutral", width=88, height=32, theme=t)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 14))

        tk.Label(self.conn_basic_frame, text="Prędkość (Baud)", bg=t["bg_card"], fg=t["fg_secondary"], font=("Segoe UI Semibold", 9)).pack(side=tk.LEFT, padx=(0, 6))
        self.baud_var = tk.StringVar(value="115200")
        self.baud_combo = ttk.Combobox(
            self.conn_basic_frame, textvariable=self.baud_var,
            values=["4800", "9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"],
            width=10, style="Modern.TCombobox", font=("Segoe UI", 9)
        )
        self.baud_combo.pack(side=tk.LEFT, padx=(0, 14))

        # Sekcja zaawansowana połączenia (ukrywana w trybie Uproszczonym)
        self.conn_adv_frame = tk.Frame(c_in, bg=t["bg_card"])
        self.conn_adv_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(self.conn_adv_frame, text="Format", bg=t["bg_card"], fg=t["fg_secondary"], font=("Segoe UI Semibold", 9)).pack(side=tk.LEFT, padx=(0, 6))
        self.format_combo = ttk.Combobox(
            self.conn_adv_frame, textvariable=self.data_format,
            values=["8N1", "8E1", "8O1", "8N2", "7E1"],
            width=6, state="readonly", style="Modern.TCombobox", font=("Segoe UI", 9)
        )
        self.format_combo.pack(side=tk.LEFT, padx=(0, 14))

        self.dtr_switch = ToggleSwitch(self.conn_adv_frame, text="DTR", variable=self.dtr_var, command=self._update_modem_lines, theme=t)
        self.dtr_switch.pack(side=tk.LEFT, padx=(0, 10))

        self.rts_switch = ToggleSwitch(self.conn_adv_frame, text="RTS", variable=self.rts_var, command=self._update_modem_lines, theme=t)
        self.rts_switch.pack(side=tk.LEFT, padx=(0, 10))

        self.reconnect_switch = ToggleSwitch(self.conn_adv_frame, text="Auto-Reconnect", variable=self.auto_reconnect, theme=t)
        self.reconnect_switch.pack(side=tk.LEFT, padx=(0, 10))

        # Przycisk Połącz po prawej stronie karty
        self.connect_btn = RoundedButton(c_in, text="Połącz", command=self._toggle_connection, kind="accent", width=116, height=34, theme=t, font=("Segoe UI Semibold", 10))
        self.connect_btn.pack(side=tk.RIGHT, padx=(8, 4))

        self._refresh_ports()

        # ------------------------------------------------------------------
        # 3. GŁÓWNY OBSZAR ROBOCZY (DWIE ZAOKRĄGLONE KARTY OBOK SIEBIE)
        # ------------------------------------------------------------------
        self.workspace = tk.Frame(self.root, bg=t["bg_app"])
        self.workspace.pack(fill=tk.BOTH, expand=True, padx=16, pady=(2, 6))
        self.workspace.columnconfigure(0, weight=4, minsize=380)
        self.workspace.columnconfigure(1, weight=6, minsize=460)
        self.workspace.rowconfigure(0, weight=1)

        # === LEWA KARTA: LISTA KOMEND I AUTOMATYZACJA ===
        self.cmd_card = RoundedCard(self.workspace, theme=t, radius=14, padding=14)
        self.cmd_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left_in = self.cmd_card.inner

        # Nagłówek lewej karty
        left_hdr = tk.Frame(left_in, bg=t["bg_card"])
        left_hdr.pack(fill=tk.X, pady=(0, 8))
        tk.Label(left_hdr, text="Lista Komend i Sekwencje", bg=t["bg_card"], fg=t["fg_primary"], font=("Segoe UI Semibold", 11)).pack(side=tk.LEFT)
        tk.Label(left_hdr, text="Automatyczne lub pojedyncze wysyłanie", bg=t["bg_card"], fg=t["fg_secondary"], font=("Segoe UI", 8)).pack(side=tk.RIGHT)

        # Pasek nagłówków kolumn
        self.col_hdr = tk.Frame(left_in, bg=t["bg_subtle"], padx=8, pady=5)
        self.col_hdr.pack(fill=tk.X, pady=(0, 4))
        self.hdr_act_lbl = tk.Label(self.col_hdr, text="Akt.", bg=t["bg_subtle"], fg=t["fg_secondary"], font=("Segoe UI Semibold", 8), width=4, anchor="w")
        self.hdr_act_lbl.pack(side=tk.LEFT)
        self.hdr_tag_lbl = tk.Label(self.col_hdr, text="Etykieta", bg=t["bg_subtle"], fg=t["fg_secondary"], font=("Segoe UI Semibold", 8), width=11, anchor="w")
        self.hdr_tag_lbl.pack(side=tk.LEFT, padx=(4, 4))
        self.hdr_cmd_lbl = tk.Label(self.col_hdr, text="Treść komendy", bg=t["bg_subtle"], fg=t["fg_secondary"], font=("Segoe UI Semibold", 8), anchor="w")
        self.hdr_cmd_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))
        self.hdr_int_lbl = tk.Label(self.col_hdr, text="Odstęp (ms)", bg=t["bg_subtle"], fg=t["fg_secondary"], font=("Segoe UI Semibold", 8), width=10)
        self.hdr_int_lbl.pack(side=tk.LEFT, padx=(2, 4))
        self.hdr_btn_lbl = tk.Label(self.col_hdr, text="Akcja", bg=t["bg_subtle"], fg=t["fg_secondary"], font=("Segoe UI Semibold", 8), width=8)
        self.hdr_btn_lbl.pack(side=tk.RIGHT)

        # Przewijana lista wierszy
        list_wrap = tk.Frame(left_in, bg=t["bg_card"])
        list_wrap.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.cmd_canvas = tk.Canvas(list_wrap, bg=t["bg_card"], highlightthickness=0, bd=0)
        cmd_scroll = ttk.Scrollbar(list_wrap, orient=tk.VERTICAL, command=self.cmd_canvas.yview, style="Vertical.TScrollbar")
        self.cmd_rows_frame = tk.Frame(self.cmd_canvas, bg=t["bg_card"])

        self.cmd_rows_frame.bind(
            "<Configure>",
            lambda e: self.cmd_canvas.configure(scrollregion=self.cmd_canvas.bbox("all"))
        )
        self.cmd_canvas_window = self.cmd_canvas.create_window((0, 0), window=self.cmd_rows_frame, anchor="nw")
        self.cmd_canvas.bind(
            "<Configure>",
            lambda e: self.cmd_canvas.itemconfigure(self.cmd_canvas_window, width=e.width)
        )
        self.cmd_canvas.configure(yscrollcommand=cmd_scroll.set)

        self.cmd_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cmd_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Dolne narzędzia listy (Dodaj, Zapisz profil, Wczytaj profil)
        cmd_tools = tk.Frame(left_in, bg=t["bg_card"])
        cmd_tools.pack(fill=tk.X, pady=(0, 10))

        self.add_cmd_btn = RoundedButton(cmd_tools, text="＋ Dodaj komendę", command=self._add_command_row, kind="soft_accent", width=136, height=32, theme=t)
        self.add_cmd_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.save_cfg_btn = RoundedButton(cmd_tools, text="💾 Zapisz", command=self._save_config_dialog, kind="neutral", width=86, height=32, theme=t)
        self.save_cfg_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.load_cfg_btn = RoundedButton(cmd_tools, text="📂 Wczytaj", command=self._load_config_dialog, kind="neutral", width=92, height=32, theme=t)
        self.load_cfg_btn.pack(side=tk.LEFT)

        # Pasek uruchamiania sekwencji (Jednorazowo / Pętla + Start / Stop)
        seq_bar = tk.Frame(left_in, bg=t["bg_subtle"], padx=10, pady=8)
        seq_bar.pack(fill=tk.X)

        self.seq_mode_seg = SegmentedControl(
            seq_bar,
            options=[("once", "Jednorazowo"), ("loop", "W pętli")],
            variable=self.send_mode,
            theme=t, width=185, height=32
        )
        self.seq_mode_seg.pack(side=tk.LEFT)

        self.stop_btn = RoundedButton(seq_bar, text="■ Stop", command=self._stop_sending, kind="danger", width=80, height=32, theme=t)
        self.stop_btn.configure_btn(enabled=False)
        self.stop_btn.pack(side=tk.RIGHT)

        self.start_btn = RoundedButton(seq_bar, text="▶ Start", command=self._start_sending, kind="success", width=88, height=32, theme=t)
        self.start_btn.pack(side=tk.RIGHT, padx=(0, 6))

        self._add_command_row(label="Test AT", name="AT", interval="1000")

        # === PRAWA KARTA: MONITOR KOMUNIKACJI I WYSYŁANIE ===
        self.log_card = RoundedCard(self.workspace, theme=t, radius=14, padding=14)
        self.log_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right_in = self.log_card.inner

        # Nagłówek i pasek narzędzi monitora
        log_top = tk.Frame(right_in, bg=t["bg_card"])
        log_top.pack(fill=tk.X, pady=(0, 8))

        tk.Label(log_top, text="Monitor Komunikacji", bg=t["bg_card"], fg=t["fg_primary"], font=("Segoe UI Semibold", 11)).pack(side=tk.LEFT)

        # Przyciski eksportu i czyszczenia
        self.clear_btn = RoundedButton(log_top, text="Wyczyść", command=self._clear_log, kind="neutral", width=76, height=30, theme=t)
        self.clear_btn.pack(side=tk.RIGHT)
        self.csv_btn = RoundedButton(log_top, text="Eksport CSV", command=self._export_csv, kind="neutral", width=92, height=30, theme=t)
        self.csv_btn.pack(side=tk.RIGHT, padx=(0, 6))
        self.txt_btn = RoundedButton(log_top, text="Zapisz TXT", command=self._save_log, kind="neutral", width=86, height=30, theme=t)
        self.txt_btn.pack(side=tk.RIGHT, padx=(0, 6))

        # Drugi wiersz paska nad logiem (Przełączniki + Filtr w trybie zaawansowanym)
        self.log_opts_bar = tk.Frame(right_in, bg=t["bg_subtle"], padx=10, pady=6)
        self.log_opts_bar.pack(fill=tk.X, pady=(0, 8))

        self.autoscroll_sw = ToggleSwitch(self.log_opts_bar, text="Auto-przewijanie", variable=self.autoscroll, theme=t)
        self.autoscroll_sw.pack(side=tk.LEFT, padx=(0, 14))

        self.ts_sw = ToggleSwitch(self.log_opts_bar, text="Znacznik czasu", variable=self.show_timestamps, command=self._rerender_log, theme=t)
        self.ts_sw.pack(side=tk.LEFT, padx=(0, 14))

        # Zaawansowane opcje logu (Widok HEX + Filtr)
        self.log_adv_frame = tk.Frame(self.log_opts_bar, bg=t["bg_subtle"])
        self.log_adv_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.hex_view_sw = ToggleSwitch(self.log_adv_frame, text="Widok HEX", variable=self.hex_view, command=self._rerender_log, theme=t)
        self.hex_view_sw.pack(side=tk.LEFT, padx=(0, 14))

        self.filter_entry = self._make_entry(self.log_adv_frame, textvariable=self.filter_var, width=16, font=("Segoe UI", 9))
        self.filter_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        self.filter_lbl = tk.Label(self.log_adv_frame, text="Szukaj:", bg=t["bg_subtle"], fg=t["fg_secondary"], font=("Segoe UI Semibold", 8))
        self.filter_lbl.pack(side=tk.RIGHT, padx=(0, 6))
        self.filter_var.trace_add("write", lambda *_: self._rerender_log())

        # Okno rozmowy / logów (Nowoczesny czysty widok)
        term_wrap = tk.Frame(right_in, bg=t["bg_card"])
        term_wrap.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(
            term_wrap, wrap=tk.WORD, font=("Consolas", 10),
            state=tk.DISABLED, bg=t["log_bg"], fg=t["fg_primary"],
            insertbackground=t["fg_primary"], selectbackground=t["accent"],
            selectforeground="#ffffff", relief="flat", padx=14, pady=12,
            highlightthickness=1, highlightbackground=t["border"], spacing1=2, spacing3=2
        )
        log_scroll = ttk.Scrollbar(term_wrap, orient=tk.VERTICAL, command=self.log_text.yview, style="Vertical.TScrollbar")
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._configure_log_tags()

        # Dolny pasek ręcznego wysyłania komendy
        self.send_bar = tk.Frame(right_in, bg=t["bg_card"])
        self.send_bar.pack(fill=tk.X, pady=(10, 0))

        # Zaawansowane opcje wysyłania (Koniec linii + HEX)
        self.send_adv_frame = tk.Frame(self.send_bar, bg=t["bg_card"])
        self.send_adv_frame.pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(self.send_adv_frame, text="Koniec linii:", bg=t["bg_card"], fg=t["fg_secondary"], font=("Segoe UI Semibold", 8)).pack(side=tk.LEFT, padx=(0, 4))
        self.eol_combo = ttk.Combobox(
            self.send_adv_frame, textvariable=self.line_ending,
            values=["LF (\\n)", "CRLF (\\r\\n)", "CR (\\r)", "Brak"],
            width=9, state="readonly", style="Modern.TCombobox", font=("Segoe UI", 9)
        )
        self.eol_combo.pack(side=tk.LEFT, padx=(0, 10))

        self.hex_send_sw = ToggleSwitch(self.send_adv_frame, text="HEX", variable=self.hex_send, theme=t)
        self.hex_send_sw.pack(side=tk.LEFT)

        self.manual_cmd = tk.StringVar()
        self.manual_entry = self._make_entry(self.send_bar, textvariable=self.manual_cmd, font=("Consolas", 10))
        self.manual_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.manual_entry.bind("<Return>", lambda e: self._send_manual())
        self.manual_entry.bind("<Up>", self._history_up)
        self.manual_entry.bind("<Down>", self._history_down)

        self.send_btn = RoundedButton(self.send_bar, text="Wyślij ↵", command=self._send_manual, kind="accent", width=98, height=34, theme=t)
        self.send_btn.pack(side=tk.RIGHT)

        # ------------------------------------------------------------------
        # 4. DOLNY PASEK STANU (STATUS BAR)
        # ------------------------------------------------------------------
        self.footer = tk.Frame(self.root, bg=t["bg_app"])
        self.footer.pack(fill=tk.X, padx=20, pady=(2, 10))

        self.stats_label = tk.Label(
            self.footer, text="Wysłano (TX): 0 B   •   Odebrano (RX): 0 B   •   Wiadomości: 0",
            bg=t["bg_app"], fg=t["fg_secondary"], font=("Segoe UI", 8)
        )
        self.stats_label.pack(side=tk.LEFT)

        self.hint_label = tk.Label(
            self.footer,
            text="Wskazówka: Strzałki ↑/↓ przywołują poprzednie komendy. Kliknij „Instrukcja obsługi”, aby poznać wszystkie funkcje.",
            bg=t["bg_app"], fg=t["fg_secondary"], font=("Segoe UI", 8)
        )
        self.hint_label.pack(side=tk.RIGHT)

    def _configure_log_tags(self):
        t = self.theme
        self.log_text.tag_configure("ts", foreground=t["ts_color"], font=("Consolas", 9))
        self.log_text.tag_configure("TX", foreground=t["tx_color"], font=("Consolas", 10, "bold"))
        self.log_text.tag_configure("RX", foreground=t["rx_color"], font=("Consolas", 10))
        self.log_text.tag_configure("SYS", foreground=t["sys_color"], font=("Segoe UI", 9, "italic"))
        self.log_text.tag_configure("ERR", foreground=t["danger"], font=("Segoe UI Semibold", 9))

    # ==================== PRZEŁĄCZANIE TRYBU: UPROSZCZONY / ZAAWANSOWANY ====================
    def _apply_ui_mode(self):
        mode = self.ui_mode.get()
        is_adv = (mode == "advanced")

        if is_adv:
            self.conn_adv_frame.pack(side=tk.LEFT, fill=tk.Y)
            self.log_adv_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.send_adv_frame.pack(side=tk.LEFT, padx=(0, 8), before=self.manual_entry)
            self.hdr_tag_lbl.pack(side=tk.LEFT, padx=(4, 4), after=self.hdr_act_lbl)
        else:
            self.conn_adv_frame.pack_forget()
            self.log_adv_frame.pack_forget()
            self.send_adv_frame.pack_forget()
            self.hdr_tag_lbl.pack_forget()
            # W trybie uproszczonym wyłączamy widok/wysyłanie HEX, by nie mylić użytkownika
            self.hex_view.set(False)
            self.hex_send.set(False)
            self.filter_var.set("")

        # Ukryj lub pokaż pole Etykieta w każdym wierszu komendy
        for row in self.cmd_entries:
            if is_adv:
                row["lbl_entry"].pack(side=tk.LEFT, padx=3, after=row["cb"])
            else:
                row["lbl_entry"].pack_forget()

        self._rerender_log()

    # ==================== PRZEŁĄCZANIE MOTYWU: JASNY / CIEMNY ====================
    def _toggle_theme(self):
        new_mode = "dark" if self.theme_mode.get() == "light" else "light"
        self.theme_mode.set(new_mode)
        self.theme = THEMES[new_mode]
        # Przebudowa z zachowaniem stanu i logów
        saved_cfg = self._config_data()
        saved_logs = list(self.log_lines)
        for child in self.root.winfo_children():
            child.destroy()
        self.cmd_entries.clear()
        self._refresh_ttk_styles()
        self._build_ui()
        self._apply_config(saved_cfg)
        self._apply_ui_mode()
        self.log_lines = saved_logs
        self._rerender_log()
        self._update_stats_bar()
        if self.running:
            self._update_status_badge("connected", f"{self.last_port} @ {self.last_baud}")

    # ==================== OKNO INSTRUKCJI OBSŁUGI ====================
    def _show_manual_window(self):
        t = self.theme
        win = tk.Toplevel(self.root)
        win.title("Instrukcja obsługi — UCS Terminal")
        win.geometry("760x620")
        win.minsize(640, 480)
        win.configure(bg=t["bg_app"])
        win.transient(self.root)

        hdr = tk.Frame(win, bg=t["bg_app"])
        hdr.pack(fill=tk.X, padx=20, pady=(16, 8))
        tk.Label(hdr, text="📖 Instrukcja obsługi programu UCS Terminal", bg=t["bg_app"], fg=t["fg_primary"], font=("Segoe UI Semibold", 14)).pack(side=tk.LEFT)
        RoundedButton(hdr, text="Zamknij", command=win.destroy, kind="accent", width=90, height=30, theme=t).pack(side=tk.RIGHT)

        card = RoundedCard(win, theme=t, radius=14, padding=14)
        card.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 18))

        txt_wrap = tk.Frame(card.inner, bg=t["bg_card"])
        txt_wrap.pack(fill=tk.BOTH, expand=True)

        help_text = tk.Text(
            txt_wrap, wrap=tk.WORD, bg=t["bg_card"], fg=t["fg_primary"],
            font=("Segoe UI", 10), relief="flat", bd=0, padx=10, pady=6,
            spacing1=3, spacing3=5
        )
        scroll = ttk.Scrollbar(txt_wrap, orient=tk.VERTICAL, command=help_text.yview, style="Vertical.TScrollbar")
        help_text.configure(yscrollcommand=scroll.set)
        help_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        help_text.tag_configure("h1", font=("Segoe UI Semibold", 12), foreground=t["accent"], spacing1=10, spacing3=4)
        help_text.tag_configure("bold", font=("Segoe UI Semibold", 10), foreground=t["fg_primary"])
        help_text.tag_configure("body", font=("Segoe UI", 10), foreground=t["fg_primary"])
        help_text.tag_configure("muted", font=("Segoe UI", 9, "italic"), foreground=t["fg_secondary"])

        sections = [
            ("1. Tryb Uproszczony vs Zaawansowany", [
                ("Przełącznik w prawym górnym rogu: ", "Pozwala dostosować wygląd programu do Twoich potrzeb."),
                ("• Tryb Uproszczony: ", "Ukrywa zaawansowane parametry techniczne (Format ramki, linie DTR/RTS, tryb HEX, znaki końca linii, filtry). Idealny do szybkiego podłączenia się do portu i wysyłania komend tekstowych."),
                ("• Tryb Zaawansowany: ", "Odkrywa wszystkie funkcje inżynierskie przydatne przy debugowaniu mikrokontrolerów, modemów i protokołów binarnych."),
            ]),
            ("2. Połączenie z urządzeniem (Port szeregowy UART)", [
                ("• Port COM: ", "Wybierz z listy port przypisany do Twojego urządzenia (np. COM3 – USB Serial)."),
                ("• Odśwież: ", "Aktualizuje listę dostępnych portów po podłączeniu nowej przejściówki USB-UART."),
                ("• Prędkość (Baud): ", "Szybkość transmisji w bitach na sekundę (najczęściej 9600 lub 115200). Musi być taka sama jak w urządzeniu docelowym."),
                ("• Format [Zaawansowany]: ", "Określa liczbę bitów danych, parzystość i bity stopu (domyślnie 8N1: 8 bitów danych, brak parzystości, 1 bit stopu)."),
                ("• DTR i RTS [Zaawansowany]: ", "Ręczne sterowanie liniami sprzętowymi modemu (często używane do resetowania płytek Arduino/ESP32/STM32)."),
                ("• Auto-Reconnect [Zaawansowany]: ", "Gdy włączone, program po chwilowym rozłączeniu kabla USB sam spróbuje wznowić połączenie, gdy port znów pojawi się w systemie."),
            ]),
            ("3. Lista Komend i Sekwencje", [
                ("• Przełącznik Akt. (Aktywna): ", "Decyduje, czy dana komenda będzie brana pod uwagę podczas automatycznego wysyłania przyciskiem Start."),
                ("• Etykieta [Zaawansowany]: ", "Twoja własna, przyjazna nazwa komendy (np. „Restart”, „Pomiar napięcia”). Nie jest wysyłana do urządzenia."),
                ("• Treść komendy: ", "Komenda wysyłana przez port (np. AT+RST). Możesz też wpisać znaki specjalne \\r lub \\n."),
                ("• Odstęp (ms): ", "Czas oczekiwania w milisekundach po wysłaniu tej komendy przed przejściem do następnej (1000 ms = 1 sekunda)."),
                ("• Przycisk ▶ (w wierszu): ", "Natychmiast wysyła tylko tę jedną wybraną komendę, bez uruchamiania całej pętli."),
                ("• Przycisk ✕ (w wierszu): ", "Usuwa wybrany wiersz z listy."),
                ("• Tryb Jednorazowo / W pętli: ", "„Jednorazowo” wykonuje aktywne komendy z listy od góry do dołu jeden raz. „W pętli” powtarza całą sekwencję w kółko aż do kliknięcia Stop."),
                ("• Zapisz / Wczytaj: ", "Pozwala zapisać przygotowaną listę komend i ustawienia portu do pliku JSON i wczytać je ponownie w przyszłości."),
            ]),
            ("4. Monitor Komunikacji i Wysyłanie ręczne", [
                ("• Kolory wiadomości: ", "Komendy wysłane przez Ciebie oznaczane są jako „Wysłano >>” (kolor indygo), a odpowiedzi z urządzenia jako „Odebrano <<” (kolor zielony)."),
                ("• Auto-przewijanie: ", "Automatycznie przesuwa widok na sam dół po nadejściu nowej wiadomości."),
                ("• Znacznik czasu: ", "Pokazuje lub ukrywa dokładny czas zdarzenia z precyzją do milisekund [GG:MM:SS.mmm]."),
                ("• Widok HEX [Zaawansowany]: ", "Przełącza podgląd wiadomości z tekstu ASCII na postać szesnastkową (np. 41 54 0A) — niezastąpione przy protokołach binarnych."),
                ("• Szukaj [Zaawansowany]: ", "Filtruje widoczne wiadomości w czasie rzeczywistym — pokazuje tylko linie zawierające wpisane słowo."),
                ("• Koniec linii [Zaawansowany]: ", "Wybiera znak automatycznie dopisywany na końcu wysyłanej komendy: LF (\\n), CRLF (\\r\\n - wymagany przez wiele modemów AT), CR (\\r) lub Brak."),
                ("• Przełącznik HEX [Zaawansowany]: ", "Gdy włączony, wpisane komendy są interpretowane jako bajty szesnastkowe (np. wpisz „AA 01 FF” aby wysłać 3 bajty binarne)."),
                ("• Historia komend (Strzałki ↑ / ↓): ", "Kliknij w dolne pole wpisywania i użyj strzałek Góra/Dół na klawiaturze, aby szybko przywołać wcześniej wysłane komendy."),
                ("• Zapisz TXT / Eksport CSV: ", "Zapisuje całą historię rozmowy do pliku tekstowego lub arkusza kalkulacyjnego CSV (wraz z kolumną HEX)."),
            ]),
        ]

        for heading, items in sections:
            help_text.insert(tk.END, heading + "\n", "h1")
            for bold_part, desc_part in items:
                help_text.insert(tk.END, bold_part, "bold")
                help_text.insert(tk.END, desc_part + "\n", "body")
            help_text.insert(tk.END, "\n", "body")

        help_text.config(state=tk.DISABLED)

    # ==================== KOLEJKA ZDARZEŃ GUI (THREAD-SAFE) ====================
    def _process_ui_queue(self):
        try:
            while True:
                item = self.ui_queue.get_nowait()
                kind = item[0]
                if kind == "log":
                    _, text, direction, raw_bytes = item
                    self._append_log_OnMainThread(text, direction, raw_bytes)
                elif kind == "status":
                    _, state, message = item
                    self._update_status_badge(state, message)
                elif kind == "sending_done":
                    self.start_btn.configure_btn(enabled=True)
                    self.stop_btn.configure_btn(enabled=False)
        except queue.Empty:
            pass
        finally:
            self.root.after(25, self._process_ui_queue)

    def _enqueue_log(self, text, direction="SYS", raw_bytes=b""):
        self.ui_queue.put(("log", text, direction, raw_bytes))

    def _update_status_badge(self, state, message):
        t = self.theme
        if state == "connected":
            self.status_badge.config(text=f"● Połączono: {message}", bg=t["success_bg"], fg=t["success_fg"])
            self.connect_btn.configure_btn(text="Rozłącz", kind="danger")
        elif state == "reconnecting":
            self.status_badge.config(text=f"◌ Wznawianie ({self.last_port})...", bg=t["warning_bg"], fg=t["warning_fg"])
            self.connect_btn.configure_btn(text="Anuluj", kind="danger")
        else:
            self.status_badge.config(text="● Rozłączono", bg=t["danger_bg"], fg=t["danger_fg"])
            self.connect_btn.configure_btn(text="Połącz", kind="accent")

    # ==================== OBSŁUGA PORTU SZEREGOWEGO ====================
    def _refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [f"{p.device} — {p.description}" for p in ports]
        self.port_combo["values"] = port_list
        if port_list and not self.port_var.get():
            self.port_combo.current(0)

    def _get_selected_port(self):
        val = self.port_var.get()
        for sep in (" — ", " - "):
            if sep in val:
                return val.split(sep)[0].strip()
        return val.strip()

    def _parse_serial_format(self):
        fmt = self.data_format.get()
        bytesize = serial.SEVENBITS if fmt.startswith("7") else serial.EIGHTBITS
        parity_map = {"N": serial.PARITY_NONE, "E": serial.PARITY_EVEN, "O": serial.PARITY_ODD}
        parity = parity_map.get(fmt[1:2], serial.PARITY_NONE)
        stopbits = serial.STOPBITS_TWO if fmt.endswith("2") else serial.STOPBITS_ONE
        return bytesize, parity, stopbits

    def _get_eol_bytes(self):
        eol = self.line_ending.get()
        if "CRLF" in eol:
            return b"\r\n"
        if "LF" in eol:
            return b"\n"
        if "CR" in eol:
            return b"\r"
        return b""

    def _encode_payload(self, text, as_hex=False):
        if as_hex:
            cleaned = text.replace("0x", "").replace("0X", "").replace(",", " ").strip()
            return bytes.fromhex(cleaned)
        processed = text.replace("\\r", "\r").replace("\\n", "\n")
        payload = processed.encode("utf-8")
        eol = self._get_eol_bytes()
        if eol and not payload.endswith(eol):
            payload += eol
        return payload

    def _update_modem_lines(self):
        if self.ser and self.ser.is_open:
            try:
                self.ser.dtr = self.dtr_var.get()
                self.ser.rts = self.rts_var.get()
            except Exception as e:
                self._enqueue_log(f"Błąd ustawiania linii DTR/RTS: {e}", "ERR")

    def _toggle_connection(self):
        if self.running or self.want_connected:
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        port = self._get_selected_port()
        if not port:
            messagebox.showwarning("Brak portu", "Wybierz port szeregowy COM z listy.")
            return
        try:
            baud = int(self.baud_var.get())
        except ValueError:
            messagebox.showwarning("Błąd", "Nieprawidłowa wartość prędkości Baudrate.")
            return

        bytesize, parity, stopbits = self._parse_serial_format()
        try:
            self.ser = serial.Serial(
                port=port, baudrate=baud, bytesize=bytesize,
                parity=parity, stopbits=stopbits, timeout=0.05
            )
            self.ser.dtr = self.dtr_var.get()
            self.ser.rts = self.rts_var.get()
            self.running = True
            self.want_connected = True
            self.last_port = port
            self.last_baud = baud
            self._update_status_badge("connected", f"{port} @ {baud}")
            self._enqueue_log(f"Połączono z portem {port} ({baud} bps, format {self.data_format.get()})", "SYS")
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
        except serial.SerialException as e:
            messagebox.showerror("Błąd połączenia", str(e))

    def _disconnect(self):
        self.want_connected = False
        self._stop_sending()
        self.running = False
        if self.ser:
            try:
                if self.ser.is_open:
                    self.ser.close()
            except Exception:
                pass
        self.ser = None
        self._update_status_badge("disconnected", "")
        self._enqueue_log("Zakończono połączenie z portem szeregowym.", "SYS")

    def _read_loop(self):
        buf = bytearray()
        last_rx_time = time.time()

        while self.want_connected:
            if not self.ser or not self.ser.is_open:
                if not self.auto_reconnect.get():
                    break
                self.ui_queue.put(("status", "reconnecting", ""))
                try:
                    bytesize, parity, stopbits = self._parse_serial_format()
                    self.ser = serial.Serial(
                        port=self.last_port, baudrate=self.last_baud,
                        bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=0.05
                    )
                    self.running = True
                    self.ui_queue.put(("status", "connected", f"{self.last_port} @ {self.last_baud}"))
                    self._enqueue_log(f"Automatycznie wznowiono połączenie z {self.last_port}", "SYS")
                except Exception:
                    time.sleep(1.0)
                    continue

            try:
                waiting = self.ser.in_waiting
                if waiting > 0:
                    chunk = self.ser.read(waiting)
                    buf.extend(chunk)
                    last_rx_time = time.time()

                    while b"\n" in buf:
                        line_bytes, buf = buf.split(b"\n", 1)
                        line_bytes = line_bytes.rstrip(b"\r")
                        text = line_bytes.decode("utf-8", errors="replace")
                        self._enqueue_log(text, "RX", bytes(line_bytes) + b"\n")
                else:
                    if buf and (time.time() - last_rx_time) > 0.08:
                        raw = bytes(buf)
                        buf.clear()
                        text = raw.decode("utf-8", errors="replace").strip("\r\n")
                        self._enqueue_log(text, "RX", raw)
                    time.sleep(0.01)
            except (serial.SerialException, OSError) as e:
                self.running = False
                try:
                    self.ser.close()
                except Exception:
                    pass
                self._enqueue_log(f"Utracono połączenie z urządzeniem: {e}", "ERR")
                if not self.auto_reconnect.get():
                    self.want_connected = False
                    self.ui_queue.put(("status", "disconnected", ""))
                    break
                time.sleep(0.5)

    # ==================== OBSŁUGA LOGÓW ====================
    def _append_log_OnMainThread(self, text, direction="SYS", raw_bytes=b""):
        now = datetime.now()
        ts = now.strftime("%H:%M:%S.") + f"{now.microsecond // 1000:03d}"

        if not raw_bytes:
            raw_bytes = text.encode("utf-8", errors="replace")

        if direction == "TX":
            self.tx_bytes += len(raw_bytes)
        elif direction == "RX":
            self.rx_bytes += len(raw_bytes)

        hex_str = " ".join(f"{b:02X}" for b in raw_bytes)
        entry = {"ts": ts, "direction": direction, "text": text, "hex": hex_str}
        self.log_lines.append(entry)

        if self._matches_filter(entry):
            self._insert_log_entry(entry)

        self._update_stats_bar()

    def _matches_filter(self, entry):
        flt = self.filter_var.get().strip().lower()
        if not flt:
            return True
        return flt in entry["text"].lower() or flt in entry["hex"].lower() or flt in entry["direction"].lower()

    def _insert_log_entry(self, entry):
        self.log_text.config(state=tk.NORMAL)
        if self.show_timestamps.get():
            self.log_text.insert(tk.END, f"[{entry['ts']}]  ", "ts")

        direction = entry["direction"]
        content = entry["hex"] if (self.hex_view.get() and direction in ("RX", "TX")) else entry["text"]

        if direction == "TX":
            prefix = "Wysłano  >>  "
        elif direction == "RX":
            prefix = "Odebrano <<  "
        elif direction == "ERR":
            prefix = "Błąd     !   "
        else:
            prefix = "System   •   "

        self.log_text.insert(tk.END, f"{prefix}{content}\n", direction)

        if self.autoscroll.get():
            self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _rerender_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        for entry in self.log_lines:
            if self._matches_filter(entry):
                self._insert_log_entry(entry)
        self.log_text.config(state=tk.DISABLED)

    def _update_stats_bar(self):
        self.stats_label.config(
            text=f"Wysłano (TX): {self.tx_bytes} B   •   Odebrano (RX): {self.rx_bytes} B   •   Wiadomości: {len(self.log_lines)}"
        )

    def _clear_log(self):
        self.log_lines.clear()
        self.tx_bytes = 0
        self.rx_bytes = 0
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)
        self._update_stats_bar()

    def _save_log(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Plik tekstowy", "*.txt"), ("Wszystkie pliki", "*.*")],
            initialfile="uart_log.txt"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_text.get("1.0", tk.END))
            self._enqueue_log(f"Zapisano historię rozmowy do pliku: {path}", "SYS")

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Plik CSV", "*.csv"), ("Wszystkie pliki", "*.*")],
            initialfile="uart_log.csv"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write("timestamp,direction,message,hex\n")
                for e in self.log_lines:
                    escaped = e["text"].replace('"', '""')
                    f.write(f'"{e["ts"]}","{e["direction"]}","{escaped}","{e["hex"]}"\n')
            self._enqueue_log(f"Wyeksportowano dane do pliku CSV: {path}", "SYS")

    # ==================== WIERSZE KOMEND ====================
    def _add_command_row(self, label="", name="", interval="1000", enabled=True):
        t = self.theme
        row_data = {
            "enabled_var": tk.BooleanVar(value=enabled),
            "label_var": tk.StringVar(value=label),
            "name_var": tk.StringVar(value=name),
            "interval_var": tk.StringVar(value=str(interval)),
        }

        row_frame = tk.Frame(self.cmd_rows_frame, bg=t["bg_card"], pady=3)
        row_frame.pack(fill=tk.X, padx=2, pady=2)

        cb = ToggleSwitch(row_frame, text="", variable=row_data["enabled_var"], theme=t)
        cb.pack(side=tk.LEFT, padx=(2, 4))

        lbl_entry = self._make_entry(row_frame, textvariable=row_data["label_var"], width=10, font=("Segoe UI", 9))
        if self.ui_mode.get() == "advanced":
            lbl_entry.pack(side=tk.LEFT, padx=3)

        cmd_entry = self._make_entry(row_frame, textvariable=row_data["name_var"], width=18, font=("Consolas", 10))
        cmd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)

        int_entry = self._make_entry(row_frame, textvariable=row_data["interval_var"], width=7, font=("Segoe UI", 9), justify=tk.CENTER)
        int_entry.pack(side=tk.LEFT, padx=3)

        remove_btn = RoundedButton(
            row_frame, text="✕", kind="soft_danger", width=30, height=30, radius=7, theme=t,
            command=lambda rf=row_frame, rd=row_data: self._remove_command_row(rf, rd)
        )
        remove_btn.pack(side=tk.RIGHT, padx=(2, 2))

        send_one_btn = RoundedButton(
            row_frame, text="▶", kind="soft_accent", width=32, height=30, radius=7, theme=t,
            command=lambda rd=row_data: self._send_single_row(rd)
        )
        send_one_btn.pack(side=tk.RIGHT, padx=(3, 2))

        row_data["frame"] = row_frame
        row_data["cb"] = cb
        row_data["lbl_entry"] = lbl_entry
        self.cmd_entries.append(row_data)

    def _remove_command_row(self, row_frame, row_data):
        if row_data in self.cmd_entries:
            self.cmd_entries.remove(row_data)
        row_frame.destroy()

    def _send_single_row(self, row_data):
        if not self.running or not self.ser or not self.ser.is_open:
            messagebox.showwarning("Brak połączenia", "Najpierw połącz się z wybranym portem COM.")
            return
        cmd_text = row_data["name_var"].get().strip()
        if not cmd_text:
            return
        self._transmit_command(cmd_text, as_hex=self.hex_send.get())

    # ==================== WYSYŁANIE SEKWENCYJNE I RĘCZNE ====================
    def _transmit_command(self, cmd_text, as_hex=False):
        try:
            payload = self._encode_payload(cmd_text, as_hex=as_hex)
            self.ser.write(payload)
            self._enqueue_log(cmd_text, "TX", payload)
            return True
        except ValueError as e:
            self._enqueue_log(f"Nieprawidłowy ciąg HEX ('{cmd_text}'): {e}", "ERR")
            return False
        except Exception as e:
            self._enqueue_log(f"Błąd wysyłania danych: {e}", "ERR")
            return False

    def _start_sending(self):
        if not self.running or not self.ser or not self.ser.is_open:
            messagebox.showwarning("Brak połączenia", "Najpierw połącz się z wybranym portem COM.")
            return

        commands = []
        for cmd in self.cmd_entries:
            if not cmd["enabled_var"].get():
                continue
            name = cmd["name_var"].get().strip()
            if not name:
                continue
            try:
                interval = max(0.0, int(cmd["interval_var"].get()) / 1000.0)
            except (ValueError, TypeError):
                interval = 1.0
            commands.append((name, interval))

        if not commands:
            messagebox.showwarning("Brak komend", "Dodaj i włącz przynajmniej jedną niepustą komendę na liście.")
            return

        self.sending = True
        self.start_btn.configure_btn(enabled=False)
        self.stop_btn.configure_btn(enabled=True)
        mode = self.send_mode.get()
        as_hex = self.hex_send.get()
        self.send_thread = threading.Thread(target=self._send_loop, args=(commands, mode, as_hex), daemon=True)
        self.send_thread.start()

    def _stop_sending(self):
        self.sending = False
        self.start_btn.configure_btn(enabled=True)
        self.stop_btn.configure_btn(enabled=False)

    def _send_loop(self, commands, mode, as_hex):
        mode_pl = "jednorazowo" if mode == "once" else "w pętli"
        self._enqueue_log(f"Rozpoczęto wysyłanie sekwencji ({mode_pl}, komend: {len(commands)})", "SYS")
        while self.sending:
            for cmd_text, interval in commands:
                if not self.sending or not self.running:
                    break
                ok = self._transmit_command(cmd_text, as_hex=as_hex)
                if not ok:
                    self.sending = False
                    break
                if interval > 0:
                    elapsed = 0.0
                    while elapsed < interval and self.sending:
                        time.sleep(0.025)
                        elapsed += 0.025
            if mode == "once":
                break

        self.sending = False
        self._enqueue_log("Zakończono wykonywanie sekwencji.", "SYS")
        self.ui_queue.put(("sending_done",))

    def _send_manual(self):
        cmd = self.manual_cmd.get().strip()
        if not cmd:
            return
        if not self.running or not self.ser or not self.ser.is_open:
            messagebox.showwarning("Brak połączenia", "Najpierw połącz się z wybranym portem COM.")
            return

        if not self.manual_history or self.manual_history[-1] != cmd:
            self.manual_history.append(cmd)
        self.history_idx = len(self.manual_history)

        self._transmit_command(cmd, as_hex=self.hex_send.get())
        self.manual_cmd.set("")

    def _history_up(self, _event):
        if self.manual_history and self.history_idx > 0:
            self.history_idx -= 1
            self.manual_cmd.set(self.manual_history[self.history_idx])
            self.manual_entry.icursor(tk.END)

    def _history_down(self, _event):
        if not self.manual_history:
            return
        if self.history_idx < len(self.manual_history) - 1:
            self.history_idx += 1
            self.manual_cmd.set(self.manual_history[self.history_idx])
            self.manual_entry.icursor(tk.END)
        else:
            self.history_idx = len(self.manual_history)
            self.manual_cmd.set("")

    # ==================== KONFIGURACJA (JSON) ====================
    def _config_data(self):
        return {
            "ui_mode": self.ui_mode.get(),
            "theme_mode": self.theme_mode.get(),
            "port": self.port_var.get(),
            "baud": self.baud_var.get(),
            "format": self.data_format.get(),
            "line_ending": self.line_ending.get(),
            "mode": self.send_mode.get(),
            "auto_reconnect": self.auto_reconnect.get(),
            "commands": [
                {
                    "enabled": c["enabled_var"].get(),
                    "label": c["label_var"].get(),
                    "name": c["name_var"].get(),
                    "interval": c["interval_var"].get(),
                }
                for c in self.cmd_entries
            ],
        }

    def _apply_config(self, data):
        if data.get("ui_mode") in ("simple", "advanced"):
            self.ui_mode.set(data["ui_mode"])
        if data.get("port"):
            self.port_var.set(data["port"])
        if data.get("baud") or data.get("baudrate"):
            self.baud_var.set(str(data.get("baud") or data.get("baudrate")))
        if data.get("format"):
            self.data_format.set(data["format"])
        if data.get("line_ending"):
            self.line_ending.set(data["line_ending"])
        if data.get("mode"):
            self.send_mode.set(data["mode"])
        if "auto_reconnect" in data:
            self.auto_reconnect.set(bool(data["auto_reconnect"]))

        for cmd in self.cmd_entries[:]:
            cmd["frame"].destroy()
        self.cmd_entries.clear()

        for c in data.get("commands", []):
            cmd_str = c.get("name", c.get("cmd", ""))
            lbl_str = c.get("label", "")
            int_str = str(c.get("interval", "1000"))
            enabled = c.get("enabled", True)
            self._add_command_row(label=lbl_str, name=cmd_str, interval=int_str, enabled=enabled)

        if not self.cmd_entries:
            self._add_command_row(label="Test AT", name="AT", interval="1000")

        self._apply_ui_mode()

    def _save_config_dialog(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Konfiguracja JSON", "*.json"), ("Wszystkie pliki", "*.*")],
            initialfile="uart_config.json"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self._config_data(), f, indent=2, ensure_ascii=False)
                self._enqueue_log(f"Zapisano profil ustawień: {path}", "SYS")
            except Exception as e:
                messagebox.showerror("Błąd zapisu", str(e))

    def _load_config_dialog(self):
        path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("Konfiguracja JSON", "*.json"), ("Wszystkie pliki", "*.*")]
        )
        if path:
            self._load_config_from(path)

    def _load_config_from(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("theme_mode") in ("light", "dark") and data["theme_mode"] != self.theme_mode.get():
                self._toggle_theme()
            self._apply_config(data)
            self._enqueue_log(f"Wczytano profil ustawień: {path}", "SYS")
        except Exception as e:
            messagebox.showerror("Błąd odczytu", str(e))

    def _try_load_default_config(self):
        if os.path.exists(DEFAULT_CONFIG):
            self._load_config_from(DEFAULT_CONFIG)


def main():
    root = tk.Tk()
    app = UARTTerminal(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app._disconnect(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
