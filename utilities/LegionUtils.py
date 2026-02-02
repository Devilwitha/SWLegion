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

def setup_logging(log_file="legion_app.log"):
    """
    Configures the logging module to write to a file and stdout.
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels including DEBUG

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File Handler - capture all messages including errors
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

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
