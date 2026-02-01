import logging
import os
import sys

def setup_logging(log_file="legion_app.log"):
    """
    Configures the logging module to write to a file and stdout.
    """
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File Handler
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logging.info("Logging initialized.")

def get_gemini_key(key_file="gemini_key.txt"):
    """
    Retrieves the Gemini API Key from the specified file.
    If the file does not exist, it creates it with a placeholder.
    Returns the key string if valid, or None if missing/placeholder.
    """
    placeholder = "BITTE_HIER_API_KEY_EINFUEGEN"

    if not os.path.exists(key_file):
        try:
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
