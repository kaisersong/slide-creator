#!/usr/bin/env python3
"""
Audit style reference files for CSS class consistency.

Checks that every CSS class defined in Typography/Components sections
is also listed in Signature Elements Required CSS Classes.

Usage:
    python3 tests/audit_style_consistency.py          # Check all styles
    python3 tests/audit_style_consistency.py neon-cyber  # Check one style
"""
import re, os, sys

REFS_DIR = os.path.join(os.path.dirname(__file__), '..', 'references')

GENERIC = {
    'slide', 'reveal', 'visible', 'grid', 'body', 'html', 'card', 'container',
    'content-box', 'slide-content', 'slide-image', 'progress-bar', 'nav-dots',
    'edit-hotzone', 'edit-toggle', 'notes-panel', 'notes-body', 'notes-textarea',
    'notes-panel-header', 'notes-panel-label', 'notes-drag-hint',
    'notes-collapse-btn', 'slide-credit', 'presenting', 'presenting-black',
    'p-on', 'title-slide', 'show', 'active', 'collapsed',
}

def audit_file(fpath):
    name = os.path.basename(fpath).replace('.md', '')
    content = open(fpath).read()

    sig_start = content.find('## Signature Elements')
    if sig_start == -1:
        return name, [], True  # skip files without signature section

    pre_sig = content[:sig_start]

    # Extract CSS class selectors from pre-signature sections
    pre_classes = set()
    for match in re.finditer(r'\.([a-z][a-z0-9_-]*)\s*[\{:,]', pre_sig):
        cls = match.group(1)
        if len(cls) > 2 and cls not in GENERIC:
            pre_classes.add(cls)

    # Extract class names from Signature Elements Required CSS Classes
    sig_section = content[sig_start:]
    req_match = re.search(r'### Required CSS Classes\n(.*?)(?=\n###|\n---|\Z)', sig_section, re.DOTALL)
    if not req_match:
        return name, sorted(pre_classes), False

    req_text = req_match.group(1)
    sig_classes = set()
    for match in re.finditer(r'\.([a-z][a-z0-9_-]*)', req_text):
        cls = match.group(1)
        if len(cls) > 2:
            sig_classes.add(cls)

    missing = sorted(pre_classes - sig_classes)
    return name, missing, len(missing) == 0

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None

    if target:
        fpath = os.path.join(REFS_DIR, f'{target}.md')
        if not os.path.exists(fpath):
            print(f"File not found: {fpath}")
            sys.exit(1)
        files = [fpath]
    else:
        files = sorted([
            f for f in os.listdir(REFS_DIR)
            if f.endswith('.md') and 'Signature Elements' in open(os.path.join(REFS_DIR, f)).read()
        ])
        files = [os.path.join(REFS_DIR, f) for f in files]

    total_issues = 0
    for fpath in files:
        name, missing, ok = audit_file(fpath)
        if ok:
            print(f"  OK  {name}")
        else:
            total_issues += len(missing)
            print(f"  MISS  {name} — {len(missing)} classes not in Signature Required CSS:")
            for c in missing:
                print(f"    .{c}")

    print(f"\n{'All checks passed!' if total_issues == 0 else f'{total_issues} missing class references across {len(files)} files.'}")
    sys.exit(0 if total_issues == 0 else 1)

if __name__ == '__main__':
    main()
