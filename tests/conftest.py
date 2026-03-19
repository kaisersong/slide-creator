def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests that invoke a headless browser (deselect with -m 'not slow')"
    )
