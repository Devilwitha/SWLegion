import tkinter as tk
from tkinter import messagebox
import os
import sys
import subprocess
import logging
import LegionUtils

class MainMenu:
    def __init__(self, root):
        LegionUtils.setup_logging()
        self.root = root
        self.root.title("Star Wars Legion: All-in-One Tool")
        self.root.geometry("400x400")

        tk.Label(self.root, text="Star Wars Legion Zentrale", font=("Segoe UI", 16, "bold")).pack(pady=20)

        btn_army = tk.Button(self.root, text="Armee Builder", command=self.run_army_builder, width=30, height=2, bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"))
        btn_army.pack(pady=10)

        btn_mission = tk.Button(self.root, text="Mission Generator", command=self.run_mission_builder, width=30, height=2, bg="#FF9800", fg="white", font=("Segoe UI", 10, "bold"))
        btn_mission.pack(pady=10)

        btn_game = tk.Button(self.root, text="Spiel-Begleiter (Game Companion)", command=self.run_game_companion, width=30, height=2, bg="#4CAF50", fg="white", font=("Segoe UI", 10, "bold"))
        btn_game.pack(pady=10)

        tk.Label(self.root, text="Wähle ein Modul um zu starten.", font=("Segoe UI", 10)).pack(pady=20)

    def run_army_builder(self):
        self.launch_script("ArmeeBuilder.py")

    def run_mission_builder(self):
        self.launch_script("MissionBuilder.py")

    def run_game_companion(self):
        self.launch_script("GameCompanion.py")

    def launch_script(self, script_name):
        try:
            # Prüfen ob Datei existiert
            if not os.path.exists(script_name):
                 logging.error(f"Script missing: {script_name}")
                 messagebox.showerror("Fehler", f"Datei nicht gefunden: {script_name}")
                 return

            # subprocess.Popen erlaubt paralleles Ausführen ohne die GUI einzufrieren
            logging.info(f"Launching submodule: {script_name}")
            cmd = [sys.executable, script_name]
            subprocess.Popen(cmd)

        except Exception as e:
            logging.error(f"Failed to launch {script_name}: {e}")
            messagebox.showerror("Fehler", f"Konnte {script_name} nicht starten:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainMenu(root)
    root.mainloop()
