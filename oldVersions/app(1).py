#!/bin/bash
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

    # ---------------- VARS ---------------- #

DATA_FILE = "sessions.json"
VERSION = '0.1'
VERSION_TYPE = 'beta'

    # ---------------- CLASSES ---------------- #

#ooo how classy XD
class SessionApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SessionLog " + VERSION + " "  + VERSION_TYPE)
        self.root.geometry("600x400")

        self.session_active = False
        self.session_start = None
        self.current_task = ""
        self.current_intent = ""

        self._load_data()
        self._build_ui()

    # ---------------- DATA ---------------- #

    def _load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                self.data = json.load(f)
        else:
            self.data = {}

    def _save_session(self, session):
        date_key = datetime.now().strftime("%Y-%m-%d")
        self.data.setdefault(date_key, []).append(session)
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=2)

    # ---------------- UI ---------------- #

    def _build_ui(self):
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True)

        self.main_tab = ttk.Frame(self.tabs)
        self.log_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.main_tab, text="Session")
        self.tabs.add(self.log_tab, text="Log")

        self._build_main_tab()
        self._build_log_tab()

    def _build_main_tab(self):
        frame = self.main_tab

        ttk.Label(frame, text="What are you working on?", font=("Arial", 12)).pack(pady=10)
        self.task_entry = ttk.Entry(frame, width=50)
        self.task_entry.pack()

        ttk.Label(frame, text="Intent (optional, one sentence)", font=("Arial", 10)).pack(pady=5)
        self.intent_entry = ttk.Entry(frame, width=50)
        self.intent_entry.pack()

        self.status_label = ttk.Label(frame, text="No active session", font=("Arial", 10))
        self.status_label.pack(pady=15)

        self.start_button = ttk.Button(frame, text="START SESSION", command=self.start_session)
        self.start_button.pack(pady=5)

        self.end_button = ttk.Button(frame, text="END SESSION", command=self.end_session, state="disabled")
        self.end_button.pack(pady=5)

    def _build_log_tab(self):
        frame = self.log_tab

        self.log_list = tk.Listbox(frame)
        self.log_list.pack(fill="both", expand=True, padx=10, pady=10)

        self.refresh_log()

    # ---------------- SESSION LOGIC ---------------- #

    def start_session(self):
        task = self.task_entry.get().strip()
        if not task:
            messagebox.showwarning("Missing task", "You need to actually be doing something.")
            return

        self.session_active = True
        self.session_start = datetime.now()
        self.current_task = task
        self.current_intent = self.intent_entry.get().strip()

        self.task_entry.config(state="disabled")
        self.intent_entry.config(state="disabled")
        self.start_button.config(state="disabled")
        self.end_button.config(state="normal")

        self._update_status()

    def end_session(self):
        if not self.session_active:
            return

        end_time = datetime.now()
        duration = int((end_time - self.session_start).total_seconds() / 60)

        outcome = messagebox.askquestion(
            "Session End",
            "Was the session finished?",
            icon="question"
        )

        reason = ""
        final_outcome = "finished"

        if outcome == "no":
            final_outcome = "interrupted"
            reason = self._ask_interrupt_reason()

        session = {
            "task": self.current_task,
            "intent": self.current_intent,
            "start": self.session_start.strftime("%H:%M"),
            "end": end_time.strftime("%H:%M"),
            "duration_min": duration,
            "outcome": final_outcome,
            "reason": reason
        }

        self._save_session(session)
        self._reset_session()
        self.refresh_log()

    def _ask_interrupt_reason(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Interruption Reason")
        dialog.geometry("300x200")

        choice = tk.StringVar(value="Distracted")

        options = [
            "Legitimate",
            "Distracted",
            "Avoidance",
            "Other"
        ]

        for opt in options:
            ttk.Radiobutton(dialog, text=opt, variable=choice, value=opt).pack(anchor="w", padx=20)

        extra = ttk.Entry(dialog)
        extra.pack(pady=5)

        def submit():
            dialog.destroy()

        ttk.Button(dialog, text="OK", command=submit).pack(pady=10)

        self.root.wait_window(dialog)

        if choice.get() == "Other":
            return extra.get().strip()
        return choice.get()

    def _reset_session(self):
        self.session_active = False
        self.session_start = None
        self.current_task = ""
        self.current_intent = ""

        self.task_entry.config(state="normal")
        self.intent_entry.config(state="normal")
        self.task_entry.delete(0, tk.END)
        self.intent_entry.delete(0, tk.END)

        self.start_button.config(state="normal")
        self.end_button.config(state="disabled")
        self.status_label.config(text="No active session")

    def _update_status(self):
        elapsed = int((datetime.now() - self.session_start).total_seconds() / 60)
        self.status_label.config(
            text=f"Working on: {self.current_task} | {elapsed} min elapsed"
        )
        if self.session_active:
            self.root.after(60000, self._update_status)
    def do_precaution(self):
        #dialog = tk.Toplevel(self.root)
        #dialog.title("Warning")
        #dialog.geometry("300x200")
        #old stuff#
        messagebox.showwarning( "Warning", "Warning: You are using a non-release version of SessionLog." ) 

    # ---------------- LOG ---------------- #

    def refresh_log(self):
        self.log_list.delete(0, tk.END)
        for date, sessions in sorted(self.data.items(), reverse=True):
            self.log_list.insert(tk.END, f"=== {date} ===")
            for s in sessions:
                line = f"{s['start']} ({s['duration_min']}m) - {s['task']} [{s['outcome']}]"
                self.log_list.insert(tk.END, line)

    def run(self):
        if VERSION_TYPE == 'beta' or VERSION_TYPE == 'alpha':
              self.do_precaution()
        self.root.mainloop()

if __name__ == "__main__":
    SessionApp().run()
