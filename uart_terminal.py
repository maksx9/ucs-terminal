# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import time
import json
import os

DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uart_config.json")

class UARTTerminal:
    def __init__(self, root):
        self.root = root
        self.root.title("UCS Terminal (UART Command Sender)")
        self.root.geometry("900x720")
        self.root.minsize(800, 600)

        self.ser = None
        self.read_thread = None
        self.running = False
        self.send_thread = None
        self.sending = False
        self.autoscroll = tk.BooleanVar(value=True)
        self.send_mode = tk.StringVar(value="once")
        self.cmd_entries = []
        self.log_lines = []

        self._build_ui()
        self._try_load_default_config()


    def _build_ui(self):
        # === CONNECTION ===
        conn_frame = ttk.LabelFrame(self.root, text="Connection", padding=10)
        conn_frame.pack(fill=tk.X, padx=10, pady=(10, 5))

        ttk.Label(conn_frame, text="Port:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(conn_frame, textvariable=self.port_var, width=30, state="readonly")
        self.port_combo.grid(row=0, column=1, padx=(0, 5))
        ttk.Button(conn_frame, text="Refresh", command=self._refresh_ports, width=10).grid(row=0, column=2, padx=(0, 15))

        ttk.Label(conn_frame, text="Baud:").grid(row=0, column=3, sticky=tk.W, padx=(0, 5))
        self.baud_var = tk.StringVar(value="115200")
        self.baud_combo = ttk.Combobox(conn_frame, textvariable=self.baud_var,
                                       values=["9600","19200","38400","57600","115200","230400","460800","921600"],
                                       width=12)
        self.baud_combo.grid(row=0, column=4, padx=(0, 15))

        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self._toggle_connection, width=12)
        self.connect_btn.grid(row=0, column=5, padx=(0, 10))
        self.status_label = ttk.Label(conn_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=0, column=6, padx=(10, 0))

        self._refresh_ports()

        # === COMMANDS ===
        cmd_outer = ttk.LabelFrame(self.root, text="Commands", padding=10)
        cmd_outer.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(cmd_outer, text="Command", font=("",9,"bold")).grid(row=0, column=0, padx=5, sticky=tk.W)
        ttk.Label(cmd_outer, text="Interval (ms)", font=("",9,"bold")).grid(row=0, column=1, padx=5)

        self.cmd_rows_frame = ttk.Frame(cmd_outer)
        self.cmd_rows_frame.grid(row=1, column=0, columnspan=3, sticky=tk.W)

        btn_row = ttk.Frame(cmd_outer)
        btn_row.grid(row=2, column=0, columnspan=3, pady=(10,0), sticky=tk.W)
        ttk.Button(btn_row, text="+ Add command", command=self._add_command_row).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(btn_row, text="Save config", command=self._save_config_dialog).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(btn_row, text="Load config", command=self._load_config_dialog).pack(side=tk.LEFT)

        ctrl_frame = ttk.Frame(cmd_outer)
        ctrl_frame.grid(row=3, column=0, columnspan=3, pady=(15,0), sticky=tk.W)

        ttk.Label(ctrl_frame, text="Mode:").pack(side=tk.LEFT, padx=(0,5))
        ttk.Radiobutton(ctrl_frame, text="Once", variable=self.send_mode, value="once").pack(side=tk.LEFT, padx=(0,10))
        ttk.Radiobutton(ctrl_frame, text="Loop", variable=self.send_mode, value="loop").pack(side=tk.LEFT, padx=(0,20))

        self.start_btn = ttk.Button(ctrl_frame, text="Start", command=self._start_sending, width=10)
        self.start_btn.pack(side=tk.LEFT, padx=(0,5))
        self.stop_btn = ttk.Button(ctrl_frame, text="Stop", command=self._stop_sending, width=10, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        self._add_command_row()

        # === LOG ===
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        toolbar = ttk.Frame(log_frame)
        toolbar.pack(fill=tk.X, pady=(0,5))
        ttk.Button(toolbar, text="Clear", command=self._clear_log).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(toolbar, text="Save log", command=self._save_log).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(toolbar, text="Export CSV", command=self._export_csv).pack(side=tk.LEFT, padx=(0,5))
        ttk.Checkbutton(toolbar, text="Auto-scroll", variable=self.autoscroll).pack(side=tk.LEFT, padx=(10,0))

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, font=("Courier",10),
                                                  state=tk.DISABLED, bg="#1e1e1e", fg="#00ff00",
                                                  insertbackground="#00ff00")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        send_frame = ttk.Frame(log_frame)
        send_frame.pack(fill=tk.X, pady=(5,0))
        self.manual_cmd = tk.StringVar()
        manual_entry = ttk.Entry(send_frame, textvariable=self.manual_cmd, font=("Courier",10))
        manual_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        manual_entry.bind("<Return>", lambda e: self._send_manual())
        ttk.Button(send_frame, text="Send", command=self._send_manual).pack(side=tk.RIGHT)

    # ==================== SERIAL ====================
    def _refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        port_list = [f"{p.device} - {p.description}" for p in ports]
        self.port_combo["values"] = port_list
        if port_list:
            self.port_combo.current(0)

    def _get_selected_port(self):
        val = self.port_var.get()
        if " - " in val:
            return val.split(" - ")[0]
        return val.strip()

    def _toggle_connection(self):
        if self.running:
            self._disconnect()
        else:
            self._connect()

    def _connect(self):
        port = self._get_selected_port()
        if not port:
            messagebox.showwarning("Error", "Select a port")
            return
        try:
            baud = int(self.baud_var.get())
        except ValueError:
            messagebox.showwarning("Error", "Invalid baud rate")
            return
        try:
            self.ser = serial.Serial(port, baud, timeout=0.1)
            time.sleep(0.2)
            self.running = True
            self.status_label.config(text=f"Connected: {port} @ {baud}", foreground="green")
            self.connect_btn.config(text="Disconnect")
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
        except serial.SerialException as e:
            messagebox.showerror("Connection error", str(e))

    def _disconnect(self):
        self._stop_sending()
        self.running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.ser = None
        self.status_label.config(text="Disconnected", foreground="red")
        self.connect_btn.config(text="Connect")

    def _read_loop(self):
        buf = ""
        while self.running and self.ser and self.ser.is_open:
            try:
                if self.ser.in_waiting:
                    data = self.ser.read(self.ser.in_waiting).decode(errors="ignore")
                    buf += data
                    while "\n" in buf:
                        line, buf = buf.split("\n", 1)
                        line = line.strip()
                        if line:
                            self._append_log(line)
                else:
                    time.sleep(0.01)
            except Exception:
                break

    # ==================== LOG ====================
    def _append_log(self, text):
        ts = time.strftime("%H:%M:%S")
        self.log_lines.append((ts, text))
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] {text}\n")
        if self.autoscroll.get():
            self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        self.log_lines.clear()
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _save_log(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text","*.txt"),("All","*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_text.get("1.0", tk.END))

    def _export_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV","*.csv"),("All","*.*")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write("timestamp,message\n")
                for ts, msg in self.log_lines:
                    escaped = msg.replace('"', '""')
                    f.write(f'"{ts}","{escaped}"\n')

    # ==================== COMMAND ROWS ====================
    def _add_command_row(self, name="", interval="1000"):
        row = len(self.cmd_entries)
        name_var = tk.StringVar(value=name)
        interval_var = tk.StringVar(value=interval)

        entry = ttk.Entry(self.cmd_rows_frame, textvariable=name_var, width=40)
        entry.grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)

        interval_entry = ttk.Entry(self.cmd_rows_frame, textvariable=interval_var, width=12)
        interval_entry.grid(row=row, column=1, padx=5, pady=2)

        remove_btn = ttk.Button(self.cmd_rows_frame, text="X", width=3,
                                command=lambda r=row: self._remove_command_row(r))
        remove_btn.grid(row=row, column=2, padx=5, pady=2)

        self.cmd_entries.append({
            "name_var": name_var,
            "interval_var": interval_var,
            "entry": entry,
            "interval_entry": interval_entry,
            "remove_btn": remove_btn,
            "row": row
        })

    def _remove_command_row(self, row):
        for i, cmd in enumerate(self.cmd_entries):
            if cmd["row"] == row:
                cmd["entry"].destroy()
                cmd["interval_entry"].destroy()
                cmd["remove_btn"].destroy()
                self.cmd_entries.pop(i)
                for j, c in enumerate(self.cmd_entries):
                    c["row"] = j
                    c["entry"].grid(row=j, column=0)
                    c["interval_entry"].grid(row=j, column=1)
                    c["remove_btn"].grid(row=j, column=2)
                break

    # ==================== START / STOP ====================
    def _start_sending(self):
        if not self.running or not self.ser or not self.ser.is_open:
            messagebox.showwarning("Error", "Connect to a port first")
            return
        commands = []
        for cmd in self.cmd_entries:
            name = cmd["name_var"].get().strip()
            if not name:
                continue
            try:
                interval = int(cmd["interval_var"].get()) / 1000.0
            except (ValueError, TypeError):
                interval = 1.0
            commands.append((name, interval))
        if not commands:
            messagebox.showwarning("Error", "Add at least one command")
            return
        self.sending = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        mode = self.send_mode.get()
        self.send_thread = threading.Thread(target=self._send_loop, args=(commands, mode), daemon=True)
        self.send_thread.start()

    def _stop_sending(self):
        self.sending = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def _send_loop(self, commands, mode):
        self._append_log(f"--- Start sending (mode: {mode}, commands: {len(commands)}) ---")
        while self.sending:
            for cmd_text, interval in commands:
                if not self.sending:
                    break
                try:
                    self.ser.write((cmd_text + "\n").encode())
                    self._append_log(f">> {cmd_text}")
                except Exception as e:
                    self._append_log(f"ERROR: {e}")
                    self.sending = False
                    break
                if interval > 0:
                    elapsed = 0.0
                    while elapsed < interval and self.sending:
                        time.sleep(0.05)
                        elapsed += 0.05
            if mode == "once":
                break
        self._append_log("--- Stopped ---")
        self.root.after(0, lambda: (self.start_btn.config(state=tk.NORMAL),
                                     self.stop_btn.config(state=tk.DISABLED)))

    # ==================== MANUAL SEND ====================
    def _send_manual(self):
        cmd = self.manual_cmd.get().strip()
        if cmd and self.ser and self.ser.is_open:
            try:
                self.ser.write((cmd + "\n").encode())
                self._append_log(f">> {cmd}")
            except Exception as e:
                self._append_log(f"ERROR: {e}")
            self.manual_cmd.set("")

    # ==================== CONFIG ====================
    def _config_data(self):
        return {
            "port": self.port_var.get(),
            "baud": self.baud_var.get(),
            "mode": self.send_mode.get(),
            "commands": [
                {"name": c["name_var"].get(), "interval": c["interval_var"].get()}
                for c in self.cmd_entries
            ]
        }

    def _apply_config(self, data):
        if data.get("port"):
            self.port_var.set(data["port"])
        if data.get("baud"):
            self.baud_var.set(data["baud"])
        if data.get("mode"):
            self.send_mode.set(data["mode"])

        # clear existing rows
        for cmd in self.cmd_entries[:]:
            cmd["entry"].destroy()
            cmd["interval_entry"].destroy()
            cmd["remove_btn"].destroy()
        self.cmd_entries.clear()

        for c in data.get("commands", []):
            self._add_command_row(name=c.get("name", ""), interval=c.get("interval", "1000"))
        if not self.cmd_entries:
            self._add_command_row()

    def _save_config_dialog(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON config","*.json"),("All","*.*")],
            initialfile="uart_config.json"
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(self._config_data(), f, indent=2, ensure_ascii=False)
                self._append_log(f"Config saved: {path}")
            except Exception as e:
                messagebox.showerror("Save error", str(e))

    def _load_config_dialog(self):
        path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON config","*.json"),("All","*.*")]
        )
        if path:
            self._load_config_from(path)

    def _load_config_from(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._apply_config(data)
            self._append_log(f"Config loaded: {path}")
        except Exception as e:
            messagebox.showerror("Load error", str(e))

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
