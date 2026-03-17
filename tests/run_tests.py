#!/usr/bin/env python3
"""
slide-creator test runner.

Usage:
    python tests/run_tests.py                     # run all demo regression tests
    python tests/run_tests.py -v                  # verbose
    python tests/run_tests.py --validate FILE     # validate a specific HTML file
    python tests/run_tests.py --validate FILE --strict  # + edit mode / data-notes checks

Requires: pip install pytest beautifulsoup4
"""

import subprocess
import sys
import argparse
from pathlib import Path

TESTS_DIR = Path(__file__).parent


def check_deps():
    missing = []
    for pkg in ["pytest", "bs4"]:
        try:
            __import__(pkg)
        except ImportError:
            name = {"bs4": "beautifulsoup4"}.get(pkg, pkg)
            missing.append(name)
    if missing:
        print(f"Missing test dependencies. Install with:")
        print(f"  pip install {' '.join(missing)}")
        sys.exit(1)


def run_pytest(verbose: bool) -> int:
    args = [sys.executable, "-m", "pytest", "--tb=short",
            str(TESTS_DIR / "test_demo_quality.py")]
    if verbose:
        args.append("-v")
    return subprocess.run(args).returncode


def run_validate(html_path: str, strict: bool) -> int:
    # Import and run validate directly
    sys.path.insert(0, str(TESTS_DIR))
    from validate import validate
    ok = validate(html_path, strict=strict)
    return 0 if ok else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--validate", metavar="FILE",
                        help="Validate a specific HTML file instead of running demo tests")
    parser.add_argument("--strict", action="store_true",
                        help="With --validate: also check edit mode, keyboard nav, data-notes")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose pytest output")
    args = parser.parse_args()

    check_deps()

    if args.validate:
        sys.exit(run_validate(args.validate, args.strict))
    else:
        sys.exit(run_pytest(args.verbose))


if __name__ == "__main__":
    main()
