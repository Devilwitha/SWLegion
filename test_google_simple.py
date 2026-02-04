
import sys
import os

print(f"Exec: {sys.executable}")
print(f"Path: {sys.path}")

try:
    import google
    print(f"Google imported: {google.__path__}")
except ImportError as e:
    print(f"Google import failed: {e}")

try:
    from google import genai
    print(f"Genai imported from: {genai.__file__}")
except ImportError as e:
    print(f"Genai import failed: {e}")

try:
    import google.generativeai
    print("Old GenerativeAI imported")
except ImportError as e:
    print(f"Old GenerativeAI import failed: {e}")
