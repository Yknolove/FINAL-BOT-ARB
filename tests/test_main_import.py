import pytest
import importlib
import os
import sys

# Skip the test entirely if aiogram is not available
pytest.importorskip("aiogram")


def test_import_main(monkeypatch):
    monkeypatch.setenv('BOT_TOKEN', 'test-token')
    monkeypatch.setenv('WEBHOOK_URL', 'https://example.com/webhook')
    monkeypatch.setenv('PORT', '1234')

    # Attempt to import main module
    try:
        import main
        importlib.reload(main)
    except Exception as e:
        pytest.fail(f"Failed to import main.py: {e}")

    assert main.BOT_TOKEN == 'test-token'
    assert main.WEBHOOK_URL == 'https://example.com/webhook'
    assert main.PORT == 1234
