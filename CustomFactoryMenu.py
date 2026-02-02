import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess
import logging

class CustomFactoryMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Custom Factory")
        self.root.geometry("400x450")

        tk.Label(self.root, text="Custom Factory", font=("Segoe UI", 16, "bold")).pack(pady=20)

        btn_units = tk.Button(self.root, text="1. Einheiten erstellen", command=self.run_unit_creator, width=30, height=2, bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"))
        btn_units.pack(pady=10)

        btn_cards = tk.Button(self.root, text="2. Kommandokarten erstellen", command=self.run_card_creator, width=30, height=2, bg="#673AB7", fg="white", font=("Segoe UI", 10, "bold"))
        btn_cards.pack(pady=10)

        btn_upgrades = tk.Button(self.root, text="3. Ausrüstung erstellen", command=self.run_upgrade_creator, width=30, height=2, bg="#FF5722", fg="white", font=("Segoe UI", 10, "bold"))
        btn_upgrades.pack(pady=10)

        btn_print = tk.Button(self.root, text="4. Karten Layout & Druck", command=self.run_printer, width=30, height=2, bg="#009688", fg="white", font=("Segoe UI", 10, "bold"))
        btn_print.pack(pady=10)

    def run_unit_creator(self):
        self.launch("CustomUnitCreator.py")

    def run_card_creator(self):
        self.launch("CustomCommandCardCreator.py")

    def run_upgrade_creator(self):
        self.launch("CustomUpgradeCreator.py")

    def run_printer(self):
        self.launch("CardPrinter.py")

    def launch(self, script_name):
        try:
            if not os.path.exists(script_name):
                 messagebox.showerror("Fehler", f"Datei nicht gefunden: {script_name}")
                 return

            cmd = [sys.executable, script_name]
            subprocess.Popen(cmd)

        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte {script_name} nicht starten:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomFactoryMenu(root)
    root.mainloop()
