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
        self.root.geometry("400x600")

        tk.Label(self.root, text="Custom Factory", font=("Segoe UI", 16, "bold")).pack(pady=20)

        btn_units = tk.Button(self.root, text="1. Einheiten erstellen", command=self.run_unit_creator, width=30, height=2, bg="#2196F3", fg="white", font=("Segoe UI", 10, "bold"))
        btn_units.pack(pady=10)

        btn_cards = tk.Button(self.root, text="2. Kommandokarten erstellen", command=self.run_card_creator, width=30, height=2, bg="#673AB7", fg="white", font=("Segoe UI", 10, "bold"))
        btn_cards.pack(pady=10)

        btn_upgrades = tk.Button(self.root, text="3. Ausrüstung erstellen", command=self.run_upgrade_creator, width=30, height=2, bg="#FF5722", fg="white", font=("Segoe UI", 10, "bold"))
        btn_upgrades.pack(pady=10)

        btn_battle = tk.Button(self.root, text="4. Schlachtkarten erstellen", command=self.run_battle_card_creator, width=30, height=2, bg="#607D8B", fg="white", font=("Segoe UI", 10, "bold"))
        btn_battle.pack(pady=10)

        btn_map = tk.Button(self.root, text="5. Schlachtfeld Planer", command=self.run_map_creator, width=30, height=2, bg="#795548", fg="white", font=("Segoe UI", 10, "bold"))
        btn_map.pack(pady=10)

        btn_print = tk.Button(self.root, text="6. Karten Layout & Druck", command=self.run_printer, width=30, height=2, bg="#009688", fg="white", font=("Segoe UI", 10, "bold"))
        btn_print.pack(pady=10)

    def run_unit_creator(self):
        self.launch(os.path.join("utilities", "CustomUnitCreator.py"))

    def run_card_creator(self):
        self.launch(os.path.join("utilities", "CustomCommandCardCreator.py"))

    def run_upgrade_creator(self):
        self.launch(os.path.join("utilities", "CustomUpgradeCreator.py"))

    def run_battle_card_creator(self):
        self.launch(os.path.join("utilities", "CustomBattleCardCreator.py"))

    def run_map_creator(self):
        self.launch(os.path.join("utilities", "BattlefieldMapCreator.py"))

    def run_printer(self):
        self.launch(os.path.join("utilities", "CardPrinter.py"))

    def launch(self, script_name):
        try:
            logging.info(f"CustomFactory launching: {script_name}")
            
            # Check if running as PyInstaller executable
            is_frozen = getattr(sys, 'frozen', False)
            has_meipass = hasattr(sys, '_MEIPASS')
            executable_name = sys.executable.lower()
            is_exe = executable_name.endswith('.exe') and 'python' not in executable_name
            
            logging.info(f"Debug: sys.frozen = {is_frozen}, has _MEIPASS = {has_meipass}, is_exe = {is_exe}")
            
            if is_frozen or has_meipass or is_exe:
                # Running as PyInstaller executable - use direct module import
                logging.info(f"Running as executable, using direct module import for {script_name}")
                self.run_module_directly(script_name)
            else:
                # Running as Python script
                if not os.path.exists(script_name):
                     logging.error(f"Script missing: {script_name}")
                     messagebox.showerror("Fehler", f"Datei nicht gefunden: {script_name}")
                     return

                cmd = [sys.executable, script_name]
                logging.info(f"Executing subprocess command: {cmd}")
                subprocess.Popen(cmd)

        except Exception as e:
            error_msg = f"Konnte {script_name} nicht starten: {str(e)}"
            logging.error(error_msg, exc_info=True)
            messagebox.showerror("Fehler", f"{error_msg}\n\nSiehe Log für Details.")

    def run_module_directly(self, script_name):
        """Run modules directly when running as executable"""
        try:
            # Normalize path for comparison
            script_name = script_name.replace('\\', '/')
            logging.info(f"Attempting direct module import for: {script_name}")
            
            if script_name == "utilities/CustomUnitCreator.py":
                logging.info("Importing CustomUnitCreator module")
                try:
                    from utilities.CustomUnitCreator import CustomUnitCreator
                    logging.info("CustomUnitCreator import successful")
                    new_window = tk.Toplevel(self.root)
                    new_window.withdraw()
                    app = CustomUnitCreator(new_window)
                    new_window.deiconify()
                    logging.info("CustomUnitCreator instance created successfully")
                except ImportError as ie:
                    logging.error(f"Failed to import CustomUnitCreator: {ie}", exc_info=True)
                    raise
                except Exception as ee:
                    logging.error(f"Failed to create CustomUnitCreator instance: {ee}", exc_info=True)
                    raise
            elif script_name == "utilities/CustomCommandCardCreator.py":
                logging.info("Importing CustomCommandCardCreator module")
                try:
                    from utilities.CustomCommandCardCreator import CustomCommandCardCreator
                    logging.info("CustomCommandCardCreator import successful")
                    new_window = tk.Toplevel(self.root)
                    new_window.withdraw()
                    app = CustomCommandCardCreator(new_window)
                    new_window.deiconify()
                    logging.info("CustomCommandCardCreator instance created successfully")
                except ImportError as ie:
                    logging.error(f"Failed to import CustomCommandCardCreator: {ie}", exc_info=True)
                    raise
                except Exception as ee:
                    logging.error(f"Failed to create CustomCommandCardCreator instance: {ee}", exc_info=True)
                    raise
            elif script_name == "utilities/CustomUpgradeCreator.py":
                logging.info("Importing CustomUpgradeCreator module")
                try:
                    from utilities.CustomUpgradeCreator import CustomUpgradeCreator
                    logging.info("CustomUpgradeCreator import successful")
                    new_window = tk.Toplevel(self.root)
                    new_window.withdraw()
                    app = CustomUpgradeCreator(new_window)
                    new_window.deiconify()
                    logging.info("CustomUpgradeCreator instance created successfully")
                except ImportError as ie:
                    logging.error(f"Failed to import CustomUpgradeCreator: {ie}", exc_info=True)
                    raise
                except Exception as ee:
                    logging.error(f"Failed to create CustomUpgradeCreator instance: {ee}", exc_info=True)
                    raise
            elif script_name == "utilities/CustomBattleCardCreator.py":
                logging.info("Importing CustomBattleCardCreator module")
                try:
                    from utilities.CustomBattleCardCreator import CustomBattleCardCreator
                    logging.info("CustomBattleCardCreator import successful")
                    new_window = tk.Toplevel(self.root)
                    new_window.withdraw()
                    app = CustomBattleCardCreator(new_window)
                    new_window.deiconify()
                    logging.info("CustomBattleCardCreator instance created successfully")
                except ImportError as ie:
                    logging.error(f"Failed to import CustomBattleCardCreator: {ie}", exc_info=True)
                    raise
                except Exception as ee:
                    logging.error(f"Failed to create CustomBattleCardCreator instance: {ee}", exc_info=True)
                    raise
            elif script_name == "utilities/BattlefieldMapCreator.py":
                logging.info("Importing BattlefieldMapCreator module")
                try:
                    from utilities.BattlefieldMapCreator import BattlefieldMapCreator
                    logging.info("BattlefieldMapCreator import successful")
                    new_window = tk.Toplevel(self.root)
                    new_window.withdraw()
                    app = BattlefieldMapCreator(new_window)
                    new_window.deiconify()
                    logging.info("BattlefieldMapCreator instance created successfully")
                except ImportError as ie:
                    logging.error(f"Failed to import BattlefieldMapCreator: {ie}", exc_info=True)
                    raise
                except Exception as ee:
                    logging.error(f"Failed to create BattlefieldMapCreator instance: {ee}", exc_info=True)
                    raise
            elif script_name == "utilities/CardPrinter.py":
                logging.info("Importing CardPrinter module")
                try:
                    from utilities.CardPrinter import CardPrinter
                    logging.info("CardPrinter import successful")
                    new_window = tk.Toplevel(self.root)
                    new_window.withdraw()
                    app = CardPrinter(new_window)
                    new_window.deiconify()
                    logging.info("CardPrinter instance created successfully")
                except ImportError as ie:
                    logging.error(f"Failed to import CardPrinter: {ie}", exc_info=True)
                    raise
                except Exception as ee:
                    logging.error(f"Failed to create CardPrinter instance: {ee}", exc_info=True)
                    raise
            else:
                logging.warning(f"Module {script_name} not configured for direct execution")
                messagebox.showwarning("Warnung", f"Modul {script_name} nicht für direkte Ausführung konfiguriert")
        except ImportError as e:
            error_msg = f"Import error for {script_name}: {str(e)}"
            logging.error(error_msg, exc_info=True)
            messagebox.showerror("Import Fehler", f"Modul konnte nicht importiert werden: {script_name}\n\nFehler: {str(e)}\n\nSiehe Log für Details.")
        except Exception as e:
            error_msg = f"Error running {script_name}: {str(e)}"
            logging.error(error_msg, exc_info=True)
            messagebox.showerror("Fehler", f"Fehler beim Starten von {script_name}:\n\n{str(e)}\n\nSiehe Log für Details.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CustomFactoryMenu(root)
    root.mainloop()
