import logging
import os
import sys

def get_data_path(relative_path):
    """
    Returns the correct path for data files, considering PyInstaller executable vs script mode.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # Running as PyInstaller executable - use _internal path
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        # Running as Python script - use relative path
        return relative_path

def get_writable_path(folder_name):
    """
    Returns a writable directory path for user data, avoiding Program Files restrictions.
    
    Args:
        folder_name (str): Name of the folder (e.g., 'Armeen', 'Missions', 'maps')
    
    Returns:
        str: Full path to a writable directory
    """
    try:
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable - use AppData
            app_data = os.environ.get('APPDATA')
            if app_data:
                base_dir = os.path.join(app_data, 'Star Wars Legion Tool Suite')
                user_dir = os.path.join(base_dir, folder_name)
                os.makedirs(user_dir, exist_ok=True)
                return user_dir
            else:
                # Fallback to user's Documents
                user_docs = os.path.join(os.path.expanduser('~'), 'Documents', 'Star Wars Legion')
                user_dir = os.path.join(user_docs, folder_name)
                os.makedirs(user_dir, exist_ok=True)
                return user_dir
        else:
            # Running as Python script - use current directory
            user_dir = os.path.join(os.getcwd(), folder_name)
            os.makedirs(user_dir, exist_ok=True)
            return user_dir
            
    except Exception as e:
        # Final fallback to user's home directory
        logging.warning(f"Could not create preferred directory for {folder_name}, using fallback: {e}")
        fallback_dir = os.path.join(os.path.expanduser('~'), 'SW_Legion_Data', folder_name)
        os.makedirs(fallback_dir, exist_ok=True)
        return fallback_dir

def setup_logging(log_file="legion_app.log"):
    """
    Configures the logging module to write to a file and stdout.
    Uses a writable directory for the log file (AppData or application directory).
    """
    # Determine a writable location for the log file
    try:
        if getattr(sys, 'frozen', False):
            # Running as PyInstaller executable
            # Try AppData directory first
            app_data = os.environ.get('APPDATA')
            if app_data:
                log_dir = os.path.join(app_data, 'Star Wars Legion Tool Suite')
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, log_file)
            else:
                # Fallback to temp directory
                log_file = os.path.join(os.path.expanduser('~'), log_file)
        else:
            # Running as Python script - use current directory
            log_file = os.path.join(os.getcwd(), log_file)
            
        # Test if we can write to the log file location
        test_path = os.path.dirname(log_file) if os.path.dirname(log_file) else '.'
        if not os.access(test_path, os.W_OK):
            # Fallback to user's home directory
            log_file = os.path.join(os.path.expanduser('~'), os.path.basename(log_file))
            
    except Exception as e:
        # Final fallback to a basic filename in user's home
        log_file = os.path.join(os.path.expanduser('~'), "legion_app.log")
        print(f"Warning: Could not determine log file location, using fallback: {log_file}")

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels including DEBUG

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File Handler - capture all messages including errors
    try:
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        print(f"Logging to: {log_file}")
    except (PermissionError, OSError) as e:
        print(f"Warning: Could not create log file at {log_file}: {e}")
        # Continue without file logging if we can't write to any location

    # Console Handler - only show INFO and above on console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Capture unhandled exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    sys.excepthook = handle_exception

    logging.info("Enhanced logging initialized with exception capture.")

def get_gemini_key(key_file="gemini_key.txt"):
    """
    Retrieves the Gemini API Key from the specified file.
    If the file does not exist, it creates it with a placeholder.
    Returns the key string if valid, or None if missing/placeholder.
    """
    placeholder = "BITTE_HIER_API_KEY_EINFUEGEN"

    if not os.path.exists(key_file):
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, "w", encoding="utf-8") as f:
                f.write(placeholder)
            logging.warning(f"API Key file '{key_file}' not found. Created placeholder file.")
            return None
        except Exception as e:
            logging.error(f"Failed to create key file '{key_file}': {e}")
            return None

    try:
        with open(key_file, "r", encoding="utf-8") as f:
            content = f.read().strip()

        if not content:
            logging.warning(f"API Key file '{key_file}' is empty.")
            return None

        if content == placeholder:
            logging.warning(f"API Key file '{key_file}' contains placeholder text.")
            return None

        logging.info("API Key successfully loaded.")
        return content

    except Exception as e:
        logging.error(f"Failed to read key file '{key_file}': {e}")
        return None
