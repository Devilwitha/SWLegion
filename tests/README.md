# Unit Tests for SWLegion Project

This folder contains automated unit tests for the core utilities and logic of the SWLegion application.

## How to Run Tests

### Using Command Line
Open a terminal in the project root (`SWLegion/SWLegion`) and run:

```bash
python -m unittest discover tests
```

### In Visual Studio Code
1. Go to the "Testing" tab in the sidebar (beaker icon).
2. If not configured, click "Configure Python Tests".
3. Select `unittest` as the framework.
4. Select `tests` as the directory.
5. You can now run individual tests or all tests from the UI.

## Test Coverage
- **LegionData**: Tests initialization and translation logic.
- **LegionRules**: Verifies integrity of game rule constants.
- **LegionUtils**: Tests path resolution and file helpers.
- **MapRenderer**: Tests the map image generation logic.
