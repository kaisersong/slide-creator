#!/usr/bin/env python3
"""
Audit style reference files for CSS class consistency.

Checks that every CSS class defined in Typography/Components sections
is also listed in Signature Elements Required CSS Classes or Allowed Components.

Usage:
    python3 tests/audit_style_consistency.py
    python3 tests/audit_style_consistency.py neon-cyber
    python3 tests/audit_style_consistency.py --fix
    python3 tests/audit_style_consistency.py neon-cyber --fix
"""
from __future__ import annotations

import argparse
import os
import re
import sys

REFS_DIR = os.path.join(os.path.dirname(__file__), '..', 'references')

GENERIC = {
    'slide', 'reveal', 'visible', 'grid', 'body', 'html', 'card', 'container',
    'content-box', 'slide-content', 'slide-image', 'progress-bar', 'nav-dots',
    'edit-hotzone', 'edit-toggle', 'notes-panel', 'notes-body', 'notes-textarea',
    'notes-panel-header', 'notes-panel-label', 'notes-drag-hint',
    'notes-collapse-btn', 'slide-credit', 'presenting', 'presenting-black',
    'p-on', 'title-slide', 'show', 'active', 'collapsed',
}

def _extract_pre_signature_classes(content: str) -> set[str]:
    sig_start = content.find('## Signature Elements')
    if sig_start == -1:
        return set()

    pre_sig = content[:sig_start]
    pre_classes = set()
    for match in re.finditer(r'\.([a-z][a-z0-9_-]*)\s*[\{:,]', pre_sig):
        cls = match.group(1)
        if len(cls) > 2 and cls not in GENERIC:
            pre_classes.add(cls)
    return pre_classes


def _extract_signature_classes(content: str) -> set[str]:
    sig_start = content.find('## Signature Elements')
    if sig_start == -1:
        return set()

    sig_section = content[sig_start:]
    sig_classes = set()
    for section_name in ['Required CSS Classes', 'Allowed Components']:
        pattern = rf'### {section_name}\n(.*?)(?=\n###|\n---|\Z)'
        section_match = re.search(pattern, sig_section, re.DOTALL)
        if section_match:
            section_text = section_match.group(1)
            for match in re.finditer(r'\.([a-z][a-z0-9_-]*)', section_text):
                cls = match.group(1)
                if len(cls) > 2:
                    sig_classes.add(cls)
    return sig_classes


def find_missing_classes(content: str) -> list[str]:
    return sorted(_extract_pre_signature_classes(content) - _extract_signature_classes(content))


def _render_audit_coverage_lines(classes: list[str], chunk_size: int = 8) -> str:
    lines = []
    for index in range(0, len(classes), chunk_size):
        chunk = classes[index:index + chunk_size]
        label = 'Audit coverage' if index == 0 else 'Audit coverage cont.'
        chunk_text = ' '.join(f'.{cls}' for cls in chunk)
        lines.append(f'- {label}: {chunk_text}\n')
    return ''.join(lines)


def apply_fix_to_content(content: str) -> str:
    missing = find_missing_classes(content)
    if not missing:
        return content

    sig_start = content.find('## Signature Elements')
    if sig_start == -1:
        return content

    audit_lines = _render_audit_coverage_lines(missing)
    sig_section = content[sig_start:]

    allowed_pattern = re.compile(r'(### Allowed Components\n)(.*?)(?=\n###|\n---|\Z)', re.DOTALL)
    allowed_match = allowed_pattern.search(sig_section)
    if allowed_match:
        body = allowed_match.group(2)
        body = re.sub(r'(?m)^- Audit coverage(?: cont\.)?: .*(?:\n|$)', '', body)
        body = body.rstrip('\n')
        if body:
            body += '\n'
        replacement = allowed_match.group(1) + body + audit_lines.rstrip('\n')
        new_sig_section = (
            sig_section[:allowed_match.start()]
            + replacement
            + sig_section[allowed_match.end():]
        )
        return content[:sig_start] + new_sig_section

    insert_markers = ['\n### Background Rule', '\n### Signature Checklist', '\n---']
    insert_at = None
    for marker in insert_markers:
        idx = sig_section.find(marker)
        if idx != -1:
            insert_at = idx
            break
    if insert_at is None:
        insert_at = len(sig_section)

    new_section = f'\n### Allowed Components\n{audit_lines}'
    new_sig_section = sig_section[:insert_at] + new_section + sig_section[insert_at:]
    return content[:sig_start] + new_sig_section


def audit_file(fpath):
    name = os.path.basename(fpath).replace('.md', '')
    content = open(fpath).read()

    sig_start = content.find('## Signature Elements')
    if sig_start == -1:
        return name, [], True  # skip files without signature section

    missing = find_missing_classes(content)
    return name, missing, len(missing) == 0


def fix_file(fpath: str) -> tuple[str, list[str], bool, bool]:
    name = os.path.basename(fpath).replace('.md', '')
    with open(fpath, encoding='utf-8') as fh:
        original = fh.read()

    missing_before = find_missing_classes(original)
    if not missing_before:
        return name, [], True, False

    fixed = apply_fix_to_content(original)
    changed = fixed != original
    if changed:
        with open(fpath, 'w', encoding='utf-8') as fh:
            fh.write(fixed)

    missing_after = find_missing_classes(fixed)
    return name, missing_after, len(missing_after) == 0, changed


def _collect_files(target: str | None) -> list[str]:
    if target:
        fpath = os.path.join(REFS_DIR, f'{target}.md')
        if not os.path.exists(fpath):
            raise FileNotFoundError(fpath)
        return [fpath]

    files = sorted([
        f for f in os.listdir(REFS_DIR)
        if f.endswith('.md') and 'Signature Elements' in open(os.path.join(REFS_DIR, f)).read()
    ])
    return [os.path.join(REFS_DIR, f) for f in files]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('target', nargs='?')
    parser.add_argument('--fix', action='store_true', help='Auto-add missing classes to Allowed Components')
    args = parser.parse_args()

    try:
        files = _collect_files(args.target)
    except FileNotFoundError as exc:
        print(f"File not found: {exc}")
        sys.exit(1)

    if args.fix:
        fixed_count = 0
        for fpath in files:
            _, _, _, changed = fix_file(fpath)
            if changed:
                fixed_count += 1
        if fixed_count:
            print(f"Auto-fixed {fixed_count} file(s). Re-running audit.\n")

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
