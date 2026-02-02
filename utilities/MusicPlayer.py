import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import pygame
import os
import json
import random
import sys
from pathlib import Path
from datetime import datetime

# Import Settings Manager
try:
    from .MusicSettingsManager import MusicSettingsManager
except ImportError:
    try:
        from utilities.MusicSettingsManager import MusicSettingsManager
    except ImportError:
        from MusicSettingsManager import MusicSettingsManager

class MusicPlayer:
    def __init__(self, root, start_with_playlist=None):
        self.root = root
        self.start_with_playlist = start_with_playlist
        self.root.title("SW Legion: Musikplayer")
        self.root.geometry("800x600")
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Music state
        self.current_playlist = []
        self.current_track_index = 0
        self.current_track = None
        self.is_playing = False
        self.is_paused = False
        self.current_position = 0
        
        # Initialize playlists dictionary
        self.playlists = {}
        
        # Settings Manager
        self.music_settings = MusicSettingsManager()
        self.settings = self.music_settings.load_settings()
        
        # Directories - finde das Projekt-Hauptverzeichnis oder EXE-Verzeichnis
        if getattr(sys, 'frozen', False):
            # Läuft als PyInstaller EXE
            base_path = sys._MEIPASS  # PyInstaller temp directory mit entpackten Dateien
            exe_dir = os.path.dirname(sys.executable)  # Verzeichnis der EXE für beschreibbare Dateien
            
            # Musik aus _MEIPASS (read-only), Playlists neben EXE (beschreibbar)
            self.music_dir = os.path.join(base_path, "musik")
            self.playlist_dir = os.path.join(exe_dir, "playlist")
            
            print(f"EXE-Modus: base_path={base_path}, exe_dir={exe_dir}")
        else:
            # Läuft als Python Script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_dir = os.path.dirname(current_dir)  # Gehe ein Verzeichnis hoch von utilities
            self.music_dir = os.path.join(project_dir, "musik")
            self.playlist_dir = os.path.join(project_dir, "playlist")
            print(f"Script-Modus: project_dir={project_dir}")
        
        print(f"Musik-Verzeichnis: {self.music_dir}")
        print(f"Playlist-Verzeichnis: {self.playlist_dir}")
        
        # Ensure directories exist
        os.makedirs(self.music_dir, exist_ok=True)
        os.makedirs(self.playlist_dir, exist_ok=True)
        
        # Wenn EXE-Modus, kopiere Beispielmusik und Playlists beim ersten Start
        if getattr(sys, 'frozen', False):
            self.copy_initial_files()
        
        self.setup_ui()
        self.load_music_files()
        self.load_playlists()
        
        # Auto-start with specified playlist if requested
        if self.start_with_playlist:
            self.load_playlist(self.start_with_playlist, auto_start=True)
        
    def copy_initial_files(self):
        """Kopiert initiale Dateien aus _MEIPASS zu beschreibbaren Verzeichnissen"""
        try:
            exe_dir = os.path.dirname(sys.executable)
            user_music_dir = os.path.join(exe_dir, "musik")
            
            # Stelle sicher dass user musik verzeichnis existiert
            os.makedirs(user_music_dir, exist_ok=True)
            
            # Kopiere Musik-Dateien aus _MEIPASS wenn user-Verzeichnis leer ist
            base_music_dir = os.path.join(sys._MEIPASS, "musik")
            if os.path.exists(base_music_dir) and len(os.listdir(user_music_dir)) <= 1:  # Nur README.md
                import shutil
                for file_name in os.listdir(base_music_dir):
                    if file_name.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                        src = os.path.join(base_music_dir, file_name)
                        dst = os.path.join(user_music_dir, file_name)
                        if not os.path.exists(dst):  # Überschreibe nicht vorhandene Dateien
                            shutil.copy2(src, dst)
                            print(f"MP3 kopiert: {file_name}")
            
            # Kopiere playlist-Beispiele wenn noch keine existieren
            base_playlist_dir = os.path.join(sys._MEIPASS, "playlist")
            if os.path.exists(base_playlist_dir) and not os.listdir(self.playlist_dir):
                import shutil
                for file_name in os.listdir(base_playlist_dir):
                    if file_name.endswith('.json'):
                        src = os.path.join(base_playlist_dir, file_name)
                        dst = os.path.join(self.playlist_dir, file_name)
                        shutil.copy2(src, dst)
                        print(f"Playlist kopiert: {file_name}")
                        
            # Aktualisiere musik_dir für Benutzer-Dateien
            self.music_dir = user_music_dir
            print(f"Benutzer-Musik-Verzeichnis: {self.music_dir}")
            
        except Exception as e:
            print(f"Fehler beim Kopieren initialer Dateien: {e}")
        
    def setup_ui(self):
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🎵 SW Legion Musikplayer", 
                              font=("Arial", 16, "bold"), fg="#2196F3")
        title_label.pack(pady=10)
        
        # Current track info
        self.track_info_frame = tk.LabelFrame(main_frame, text="🎶 Aktuelle Wiedergabe", 
                                             font=("Arial", 12, "bold"))
        self.track_info_frame.pack(fill="x", pady=5)
        
        self.current_track_label = tk.Label(self.track_info_frame, 
                                           text="Keine Musik ausgewählt", 
                                           font=("Arial", 11), wraplength=700)
        self.current_track_label.pack(pady=10)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.track_info_frame, 
                                           variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        
        # Control buttons
        control_frame = tk.Frame(main_frame)
        control_frame.pack(pady=10)
        
        self.btn_previous = tk.Button(control_frame, text="⏮️ Zurück", 
                                     font=("Arial", 12), command=self.previous_track,
                                     bg="#FFC107", width=10)
        self.btn_previous.pack(side="left", padx=5)
        
        self.btn_play_pause = tk.Button(control_frame, text="▶️ Play", 
                                       font=("Arial", 12), command=self.toggle_play_pause,
                                       bg="#4CAF50", width=10)
        self.btn_play_pause.pack(side="left", padx=5)
        
        self.btn_stop = tk.Button(control_frame, text="⏹️ Stop", 
                                 font=("Arial", 12), command=self.stop_music,
                                 bg="#f44336", width=10)
        self.btn_stop.pack(side="left", padx=5)
        
        self.btn_next = tk.Button(control_frame, text="⏭️ Weiter", 
                                 font=("Arial", 12), command=self.next_track,
                                 bg="#FFC107", width=10)
        self.btn_next.pack(side="left", padx=5)
        
        # Shuffle and Repeat
        options_frame = tk.Frame(main_frame)
        options_frame.pack(pady=5)
        
        self.shuffle_var = tk.BooleanVar()
        self.shuffle_check = tk.Checkbutton(options_frame, text="🔀 Zufällig", 
                                           variable=self.shuffle_var,
                                           font=("Arial", 10))
        self.shuffle_check.pack(side="left", padx=10)
        
        self.repeat_var = tk.BooleanVar()
        self.repeat_check = tk.Checkbutton(options_frame, text="🔁 Wiederholen", 
                                          variable=self.repeat_var,
                                          font=("Arial", 10))
        self.repeat_check.pack(side="left", padx=10)
        
        # Volume control
        volume_frame = tk.Frame(main_frame)
        volume_frame.pack(fill="x", pady=5)
        
        tk.Label(volume_frame, text="🔊 Lautstärke:", font=("Arial", 10)).pack(side="left")
        
        self.volume_var = tk.DoubleVar(value=70)
        self.volume_scale = tk.Scale(volume_frame, from_=0, to=100, 
                                    variable=self.volume_var, orient="horizontal",
                                    command=self.set_volume)
        self.volume_scale.pack(side="left", fill="x", expand=True, padx=10)
        
        # Main content area
        content_frame = tk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True, pady=10)
        
        # Left side - Music Library
        left_frame = tk.LabelFrame(content_frame, text="🎵 Musik Bibliothek", 
                                  font=("Arial", 11, "bold"))
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Music list
        music_list_frame = tk.Frame(left_frame)
        music_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.music_listbox = tk.Listbox(music_list_frame, font=("Arial", 9))
        music_scrollbar = ttk.Scrollbar(music_list_frame, orient="vertical")
        self.music_listbox.config(yscrollcommand=music_scrollbar.set)
        music_scrollbar.config(command=self.music_listbox.yview)
        
        self.music_listbox.pack(side="left", fill="both", expand=True)
        music_scrollbar.pack(side="right", fill="y")
        
        self.music_listbox.bind("<Double-Button-1>", self.on_music_double_click)
        
        # Music buttons
        music_btn_frame = tk.Frame(left_frame)
        music_btn_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Button(music_btn_frame, text="📁 Musik hinzufügen", 
                 command=self.add_music_file, bg="#2196F3", fg="white").pack(fill="x", pady=2)
        tk.Button(music_btn_frame, text="🔄 Aktualisieren", 
                 command=self.load_music_files, bg="#FF9800", fg="white").pack(fill="x", pady=2)
        
        # Right side - Playlists
        right_frame = tk.LabelFrame(content_frame, text="📂 Playlisten", 
                                   font=("Arial", 11, "bold"))
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Playlist list
        playlist_list_frame = tk.Frame(right_frame)
        playlist_list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.playlist_listbox = tk.Listbox(playlist_list_frame, font=("Arial", 9))
        playlist_scrollbar = ttk.Scrollbar(playlist_list_frame, orient="vertical")
        self.playlist_listbox.config(yscrollcommand=playlist_scrollbar.set)
        playlist_scrollbar.config(command=self.playlist_listbox.yview)
        
        self.playlist_listbox.pack(side="left", fill="both", expand=True)
        playlist_scrollbar.pack(side="right", fill="y")
        
        self.playlist_listbox.bind("<Double-Button-1>", self.on_playlist_double_click)
        
        # Playlist buttons
        playlist_btn_frame = tk.Frame(right_frame)
        playlist_btn_frame.pack(fill="x", padx=5, pady=5)
        
        tk.Button(playlist_btn_frame, text="➕ Neue Playlist", 
                 command=self.create_new_playlist, bg="#4CAF50", fg="white").pack(fill="x", pady=2)
        tk.Button(playlist_btn_frame, text="✏️ Playlist bearbeiten", 
                 command=self.edit_playlist, bg="#FF9800", fg="white").pack(fill="x", pady=2)
        tk.Button(playlist_btn_frame, text="🗑️ Playlist löschen", 
                 command=self.delete_playlist, bg="#f44336", fg="white").pack(fill="x", pady=2)
        
        # Set initial volume
        saved_volume = self.settings.get('volume', 70)
        self.volume_var.set(saved_volume)
        self.set_volume(saved_volume)
        
        # Restore shuffle and repeat settings
        self.shuffle_var.set(self.settings.get('shuffle', False))
        self.repeat_var.set(self.settings.get('repeat', False))
        
        # Load last playlist if available
        last_playlist = self.settings.get('current_playlist')
        if last_playlist and last_playlist in self.playlists:
            self.current_playlist = self.playlists[last_playlist].get('tracks', [])
            self.current_track_index = self.settings.get('current_song_index', 0)
            if self.current_track_index >= len(self.current_playlist):
                self.current_track_index = 0
        
        # Start update timer only once
        if not hasattr(self, '_timer_started'):
            self._timer_started = True
            self.update_progress()
        
    def load_music_files(self):
        """Lädt alle Musik-Dateien aus dem musik-Ordner"""
        self.music_listbox.delete(0, tk.END)
        self.music_files = []
        
        if not os.path.exists(self.music_dir):
            return
            
        supported_formats = ['.mp3', '.wav', '.ogg', '.m4a']
        
        for file_name in os.listdir(self.music_dir):
            file_path = os.path.join(self.music_dir, file_name)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file_name)
                if ext.lower() in supported_formats:
                    self.music_files.append(file_path)
                    self.music_listbox.insert(tk.END, file_name)
                    
    def load_playlists(self):
        """Lädt alle Playlisten"""
        self.playlist_listbox.delete(0, tk.END)
        self.playlists = {}
        
        if not os.path.exists(self.playlist_dir):
            return
        
        playlist_files = [f for f in os.listdir(self.playlist_dir) if f.endswith('.json')]
            
        for file_name in playlist_files:
            playlist_path = os.path.join(self.playlist_dir, file_name)
            try:
                with open(playlist_path, 'r', encoding='utf-8') as f:
                    playlist_data = json.load(f)
                    playlist_name = playlist_data.get('name', file_name[:-5])
                    self.playlists[playlist_name] = playlist_data
                    self.playlist_listbox.insert(tk.END, playlist_name)
            except Exception as e:
                print(f"Fehler beim Laden der Playlist {file_name}: {e}")
                    
    def add_music_file(self):
        """Fügt eine Musik-Datei hinzu"""
        files = filedialog.askopenfilenames(
            title="Musik-Dateien auswählen",
            filetypes=[
                ("Audio Dateien", "*.mp3 *.wav *.ogg *.m4a"),
                ("MP3 Dateien", "*.mp3"),
                ("WAV Dateien", "*.wav"),
                ("OGG Dateien", "*.ogg"),
                ("M4A Dateien", "*.m4a"),
                ("Alle Dateien", "*.*")
            ]
        )
        
        if files:
            for file_path in files:
                file_name = os.path.basename(file_path)
                destination = os.path.join(self.music_dir, file_name)
                
                try:
                    # Kopiere Datei in musik-Ordner
                    import shutil
                    shutil.copy2(file_path, destination)
                    print(f"Musik-Datei hinzugefügt: {file_name}")
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Kopieren von {file_name}: {e}")
            
            # Aktualisiere Liste
            self.load_music_files()
            messagebox.showinfo("Erfolg", f"{len(files)} Musik-Datei(en) hinzugefügt!")
            
    def on_music_double_click(self, event):
        """Spielt ausgewählte Musik ab"""
        selection = self.music_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.music_files):
                self.play_single_track(self.music_files[index])
                
    def on_playlist_double_click(self, event):
        """Lädt und spielt ausgewählte Playlist ab"""
        selection = self.playlist_listbox.curselection()
        if selection:
            index = selection[0]
            playlist_names = list(self.playlists.keys())
            if index < len(playlist_names):
                playlist_name = playlist_names[index]
                self.load_playlist(playlist_name)
                
    def play_single_track(self, track_path):
        """Spielt einen einzelnen Track ab"""
        self.current_playlist = [track_path]
        self.current_track_index = 0
        self.play_current_track()
        
    def load_playlist(self, playlist_name, auto_start=False):
        """Lädt eine Playlist und startet optional die Wiedergabe"""
        if playlist_name in self.playlists:
            playlist_data = self.playlists[playlist_name]
            tracks = playlist_data.get('tracks', [])
            
            # Filtere existierende Tracks
            valid_tracks = []
            for track in tracks:
                if os.path.exists(track):
                    valid_tracks.append(track)
                    
            if valid_tracks:
                self.current_playlist = valid_tracks
                self.current_track_index = 0
                
                # Save current playlist and song to settings
                self.music_settings.update_setting('current_playlist', playlist_name)
                self.music_settings.update_setting('current_song_index', 0)
                
                if auto_start:
                    self.play_current_track()
                
                if not auto_start:  # Only show message box if not auto-started
                    messagebox.showinfo("Playlist geladen", 
                                       f"Playlist '{playlist_name}' geladen: {len(valid_tracks)} Tracks")
                return True
            else:
                if not auto_start:
                    messagebox.showwarning("Warnung", 
                                           "Keine gültigen Tracks in der Playlist gefunden!")
                return False
        return False
        
    def play_current_track(self):
        """Spielt den aktuellen Track ab"""
        if not self.current_playlist or self.current_track_index >= len(self.current_playlist):
            return
            
        track_path = self.current_playlist[self.current_track_index]
        
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True
            self.is_paused = False
            self.current_track = track_path
            
            # Update UI
            track_name = os.path.basename(track_path)
            self.current_track_label.config(text=f"🎵 {track_name}")
            self.btn_play_pause.config(text="⏸️ Pause")
            
        except Exception as e:
            messagebox.showerror("Wiedergabe Fehler", f"Fehler beim Abspielen: {e}")
            
    def toggle_play_pause(self):
        """Pausiert oder setzt die Wiedergabe fort"""
        if self.is_playing:
            if self.is_paused:
                pygame.mixer.music.unpause()
                self.is_paused = False
                self.btn_play_pause.config(text="⏸️ Pause")
            else:
                pygame.mixer.music.pause()
                self.is_paused = True
                self.btn_play_pause.config(text="▶️ Play")
        else:
            # Start new playback if stopped
            if self.current_playlist:
                self.play_current_track()
                
    def stop_music(self):
        """Stoppt die Wiedergabe"""
        pygame.mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.current_track = None
        self.current_track_label.config(text="Wiedergabe gestoppt")
        self.btn_play_pause.config(text="▶️ Play")
        self.progress_var.set(0)
        
    def next_track(self):
        """Springt zum nächsten Track"""
        if not self.current_playlist:
            return
            
        if self.shuffle_var.get():
            self.current_track_index = random.randint(0, len(self.current_playlist) - 1)
        else:
            self.current_track_index += 1
            if self.current_track_index >= len(self.current_playlist):
                if self.repeat_var.get():
                    self.current_track_index = 0
                else:
                    self.stop_music()
                    return
                    
        # Save current song index to settings
        self.music_settings.update_setting('current_song_index', self.current_track_index)
        self.play_current_track()
        
    def previous_track(self):
        """Springt zum vorherigen Track"""
        if not self.current_playlist:
            return
            
        if self.shuffle_var.get():
            self.current_track_index = random.randint(0, len(self.current_playlist) - 1)
        else:
            self.current_track_index -= 1
            if self.current_track_index < 0:
                if self.repeat_var.get():
                    self.current_track_index = len(self.current_playlist) - 1
                else:
                    self.current_track_index = 0
                    
        # Save current song index to settings
        self.music_settings.update_setting('current_song_index', self.current_track_index)
        self.play_current_track()
        
    def set_volume(self, value):
        """Setzt die Lautstärke"""
        volume = float(value) / 100
        pygame.mixer.music.set_volume(volume)
        # Save volume to settings
        self.music_settings.update_setting('volume', int(value))
        
    def update_progress(self):
        """Aktualisiert die Progress Bar"""
        # Check if music has ended
        if self.is_playing and not pygame.mixer.music.get_busy() and not self.is_paused:
            # Track has ended, play next
            self.next_track()
            
        # Schedule next update
        self.root.after(1000, self.update_progress)
        
    def create_new_playlist(self):
        """Erstellt eine neue Playlist"""
        name = simpledialog.askstring("Neue Playlist", "Playlist-Name:")
        if name:
            self.edit_playlist_dialog(name)
            
    def edit_playlist(self):
        """Bearbeitet eine existierende Playlist"""
        selection = self.playlist_listbox.curselection()
        if selection:
            index = selection[0]
            playlist_names = list(self.playlists.keys())
            if index < len(playlist_names):
                playlist_name = playlist_names[index]
                self.edit_playlist_dialog(playlist_name)
        else:
            messagebox.showwarning("Auswahl erforderlich", "Bitte wähle eine Playlist aus!")
            
    def edit_playlist_dialog(self, playlist_name):
        """Dialog zum Bearbeiten einer Playlist"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Playlist bearbeiten: {playlist_name}")
        dialog.geometry("600x500")
        dialog.grab_set()
        
        # Current tracks in playlist
        current_tracks = []
        if playlist_name in self.playlists:
            current_tracks = self.playlists[playlist_name].get('tracks', [])
            
        # Layout
        left_frame = tk.LabelFrame(dialog, text="Verfügbare Musik")
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        middle_frame = tk.Frame(dialog)
        middle_frame.pack(side="left", padx=5, pady=5)
        
        right_frame = tk.LabelFrame(dialog, text="Playlist Tracks")
        right_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Available music list
        available_listbox = tk.Listbox(left_frame)
        available_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Populate available music
        for music_file in self.music_files:
            available_listbox.insert(tk.END, os.path.basename(music_file))
            
        # Control buttons in middle
        tk.Button(middle_frame, text="➡", command=lambda: move_to_playlist(available_listbox, playlist_listbox),
                 width=3, height=2).pack(pady=5)
        tk.Button(middle_frame, text="⬅", command=lambda: remove_from_playlist(playlist_listbox),
                 width=3, height=2).pack(pady=5)
        tk.Button(middle_frame, text="⬆", command=lambda: move_up_in_playlist(playlist_listbox),
                 width=3, height=2).pack(pady=5)
        tk.Button(middle_frame, text="⬇", command=lambda: move_down_in_playlist(playlist_listbox),
                 width=3, height=2).pack(pady=5)
        
        # Playlist tracks list
        playlist_listbox = tk.Listbox(right_frame)
        playlist_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        available_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        for music_file in self.music_files:
            available_listbox.insert(tk.END, os.path.basename(music_file))
            
        # Control buttons
        tk.Button(middle_frame, text="→", 
                 command=lambda: self.move_to_playlist(available_listbox, playlist_listbox)).pack(pady=5)
        tk.Button(middle_frame, text="←", 
                 command=lambda: self.remove_from_playlist(playlist_listbox)).pack(pady=5)
        tk.Button(middle_frame, text="↑", 
                 command=lambda: self.move_up_in_playlist(playlist_listbox)).pack(pady=5)
        tk.Button(middle_frame, text="↓", 
                 command=lambda: self.move_down_in_playlist(playlist_listbox)).pack(pady=5)
        
        # Playlist tracks list
        playlist_listbox = tk.Listbox(right_frame)
        playlist_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Load current tracks
        playlist_tracks = []
        for track_path in current_tracks:
            playlist_tracks.append(track_path)
            playlist_listbox.insert(tk.END, os.path.basename(track_path))
            
        # Buttons
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        def save_playlist():
            tracks = playlist_tracks[:]
            current_time = str(datetime.now())
            playlist_data = {
                'name': playlist_name,
                'tracks': tracks,
                'created': current_time if playlist_name not in self.playlists else self.playlists[playlist_name].get('created', current_time),
                'modified': current_time
            }
            
            # Save to file
            playlist_file = os.path.join(self.playlist_dir, f"{playlist_name}.json")
            try:
                with open(playlist_file, 'w', encoding='utf-8') as f:
                    json.dump(playlist_data, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("Gespeichert", f"Playlist '{playlist_name}' gespeichert!")
                self.load_playlists()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
                
        def move_to_playlist(from_list, to_list):
            selection = from_list.curselection()
            if selection:
                index = selection[0]
                if from_list == available_listbox and index < len(self.music_files):
                    track_path = self.music_files[index]
                    track_name = os.path.basename(track_path)
                    
                    playlist_tracks.append(track_path)
                    to_list.insert(tk.END, track_name)
                    
        def remove_from_playlist(from_list):
            selection = from_list.curselection()
            if selection:
                index = selection[0]
                if index < len(playlist_tracks):
                    del playlist_tracks[index]
                    from_list.delete(index)
                    
        def move_up_in_playlist(listbox):
            selection = listbox.curselection()
            if selection and selection[0] > 0:
                index = selection[0]
                # Swap in data
                playlist_tracks[index], playlist_tracks[index-1] = playlist_tracks[index-1], playlist_tracks[index]
                # Refresh listbox
                listbox.delete(0, tk.END)
                for track_path in playlist_tracks:
                    listbox.insert(tk.END, os.path.basename(track_path))
                listbox.select_set(index-1)
                
        def move_down_in_playlist(listbox):
            selection = listbox.curselection()
            if selection and selection[0] < len(playlist_tracks) - 1:
                index = selection[0]
                # Swap in data
                playlist_tracks[index], playlist_tracks[index+1] = playlist_tracks[index+1], playlist_tracks[index]
                # Refresh listbox
                listbox.delete(0, tk.END)
                for track_path in playlist_tracks:
                    listbox.insert(tk.END, os.path.basename(track_path))
                listbox.select_set(index+1)
        
        # Connect functions to local scope
        self.move_to_playlist = move_to_playlist
        self.remove_from_playlist = remove_from_playlist
        self.move_up_in_playlist = move_up_in_playlist
        self.move_down_in_playlist = move_down_in_playlist
        
        tk.Button(btn_frame, text="💾 Speichern", command=save_playlist, 
                 bg="#4CAF50", fg="white").pack(side="left", padx=5)
        tk.Button(btn_frame, text="❌ Abbrechen", command=dialog.destroy, 
                 bg="#f44336", fg="white").pack(side="left", padx=5)
                 
    def delete_playlist(self):
        """Löscht eine Playlist"""
        selection = self.playlist_listbox.curselection()
        if selection:
            index = selection[0]
            playlist_names = list(self.playlists.keys())
            if index < len(playlist_names):
                playlist_name = playlist_names[index]
                
                if messagebox.askyesno("Löschen bestätigen", 
                                      f"Playlist '{playlist_name}' wirklich löschen?"):
                    playlist_file = os.path.join(self.playlist_dir, f"{playlist_name}.json")
                    try:
                        os.remove(playlist_file)
                        self.load_playlists()
                        messagebox.showinfo("Gelöscht", f"Playlist '{playlist_name}' gelöscht!")
                    except Exception as e:
                        messagebox.showerror("Fehler", f"Fehler beim Löschen: {e}")
        else:
            messagebox.showwarning("Auswahl erforderlich", "Bitte wähle eine Playlist aus!")

    @staticmethod
    def launch_with_playlist(playlist_name):
        """Startet den Musikplayer mit einer bestimmten Playlist"""
        import threading
        
        def run_player():
            root = tk.Tk()
            app = MusicPlayer(root, start_with_playlist=playlist_name)
            root.mainloop()
            
        # Run in separate thread to avoid blocking
        thread = threading.Thread(target=run_player, daemon=True)
        thread.start()
        return thread

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()