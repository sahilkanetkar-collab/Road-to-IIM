#!/usr/bin/env python3
"""
riim_audit.py — Road to IIM pre-delivery audit (Gate 1)
Usage: python3 riim_audit.py RoadToIIM_TestXX_OnlineTest.html [more files...]

Exit code 0 = all checks pass. Exit code 1 = failures found.
Rule: ZERO failures before delivery. Warnings must be reviewed and justified.

v2 — July 2026. Rebuilt after the Tests 13/14/15/16 placeholder-stem incident.
CHECK 1 (STEM INTEGRITY) is first and non-negotiable: it catches questions whose
stem is empty or is just the section label ("Vocabulary", "Idiom", ...), meaning
students would see options with no question — the exact failure students
photographed in Test 14 on 11-07-2026.
"""
import re, sys, subprocess, shutil
from collections import Counter

CURRENT_APPS_SCRIPT = "AKfycbx5Ojm_zp4LfsMeelx5e06KNjVH1wfsXdV0keS4407m4FO1HU4EpVb7GKj-ibAsxnspeA"
PAYLOAD_CORE = ["testName", "name", "pin", "batch", "score", "correct",
                "wrong", "skipped", "maxMarks", "timeTaken", "timestamp"]
LETTERS = "ABCD"

QRX = re.compile(r'\{section:"(.*?)",stem:"(.*?)",opts:\[(.*?)\],ans:(\d+),exp:"(.*?)"\}', re.S)

def split_opts(s):
    return re.findall(r'"((?:[^"\\]|\\.)*)"', s)

def audit(path):
    fails, warns = [], []
    try:
        txt = open(path, encoding="utf-8").read()
    except Exception as e:
        return [f"cannot read file: {e}"], []

    qs = QRX.findall(txt)
    if not qs:
        return [f"no questions parsed — QUESTIONS array missing or format changed"], []

    # ---------- CHECK 1: STEM INTEGRITY (the Test 13/14/15/16 bug) ----------
    for i, (sec, stem, opts_s, ans, exp) in enumerate(qs, 1):
        clean = stem.strip()
        if clean == "":
            fails.append(f"Q{i} [{sec}] CHECK1: EMPTY STEM — question shows only options")
        elif clean.lower() == sec.strip().lower():
            fails.append(f"Q{i} [{sec}] CHECK1: PLACEHOLDER STEM — stem is just the section label")
        elif len(clean) < 12:
            warns.append(f"Q{i} [{sec}] CHECK1: suspiciously short stem: '{clean}'")
        # Sentence Completion: stem must contain blanks matching option word-count
        if sec == "Sentence Completion":
            nb = clean.count("______")
            if nb == 0:
                fails.append(f"Q{i} [{sec}] CHECK1: SC stem has no blanks")
            else:
                for oi, o in enumerate(split_opts(opts_s)):
                    words = [w.strip() for w in o.split(";")]
                    if len(words) > 1 and len(words) != nb:
                        fails.append(f"Q{i} [{sec}] CHECK1: {nb} blanks but option "
                                     f"{LETTERS[oi]} supplies {len(words)} words")
        # Vocabulary/Idiom: stem must reference the target (quoted word/idiom) or carry a blank
        if sec in ("Vocabulary", "Idiom"):
            if "'" not in clean and "______" not in clean and "<u>" not in clean:
                warns.append(f"Q{i} [{sec}] CHECK1: stem names no quoted target word/idiom and has no blank")

    # ---------- CHECK 2: counts & option hygiene ----------
    if len(qs) != 45:
        fails.append(f"CHECK2: question count = {len(qs)}, expected 45")
    for i, (sec, stem, opts_s, ans, exp) in enumerate(qs, 1):
        opts = split_opts(opts_s)
        ans = int(ans)
        if len(opts) != 4:
            fails.append(f"Q{i} CHECK2: {len(opts)} options (need 4)")
        if any(not o.strip() for o in opts):
            fails.append(f"Q{i} CHECK2: empty option text")
        low = [o.strip().lower() for o in opts]
        if len(set(low)) != len(low):
            fails.append(f"Q{i} CHECK2: duplicate option text")
        if ans >= len(opts):
            fails.append(f"Q{i} CHECK2: ans index {ans} out of range")

    # ---------- CHECK 3: answer key vs explanation ----------
    for i, (sec, stem, opts_s, ans, exp) in enumerate(qs, 1):
        m = re.search(r'Correct Answer:\s*([A-D])', exp)
        if not m:
            warns.append(f"Q{i} CHECK3: explanation lacks 'Correct Answer: X'")
        elif LETTERS.index(m.group(1)) != int(ans):
            fails.append(f"Q{i} CHECK3: explanation says {m.group(1)}, key says {LETTERS[int(ans)]}")

    # ---------- CHECK 4: answer distribution ----------
    seq = [LETTERS[int(q[3])] for q in qs]
    dist = Counter(seq)
    for L in LETTERS:
        if dist.get(L, 0) < 7 or dist.get(L, 0) > 17:
            warns.append(f"CHECK4: unbalanced distribution — {L} appears {dist.get(L,0)} times")
    run = 1
    for i in range(1, len(seq)):
        run = run + 1 if seq[i] == seq[i-1] else 1
        if run == 4:
            fails.append(f"CHECK4: run of 4+ consecutive '{seq[i]}' answers ending Q{i+1}")

    # ---------- CHECK 5: payload fields ----------
    for f in PAYLOAD_CORE:
        if not re.search(rf'\b{f}\s*:', txt):
            fails.append(f"CHECK5: payload field '{f}' not found")

    # ---------- CHECK 6: Apps Script URL ----------
    urls = set(re.findall(r'script\.google\.com/macros/s/([A-Za-z0-9_-]+)', txt))
    if not urls:
        fails.append("CHECK6: no Apps Script URL found")
    else:
        for u in urls:
            if u != CURRENT_APPS_SCRIPT:
                fails.append(f"CHECK6: STALE Apps Script URL ...{u[-16:]} (update CURRENT_APPS_SCRIPT in this script if the deployment legitimately changed)")

    # ---------- CHECK 7: JS syntax (node --check) ----------
    if shutil.which("node"):
        for j, s in enumerate(re.findall(r'<script>(.*?)</script>', txt, re.S)):
            import tempfile, os
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as tf:
                tf.write(s); p = tf.name
            r = subprocess.run(["node", "--check", p], capture_output=True, text=True)
            os.unlink(p)
            if r.returncode != 0:
                fails.append(f"CHECK7: JS syntax error in script block {j}: "
                             f"{r.stderr.strip().splitlines()[-1][:120]}")
    else:
        warns.append("CHECK7: node not available — JS syntax not verified")

    # ---------- CHECK 8: standard features ----------
    if "downloadPDF" not in txt and "jspdf" not in txt.lower():
        warns.append("CHECK8: no PDF download button (mandatory for tests built after June 2026; legacy tests exempt)")
    if not re.search(r'\b(1800|30\s*\*\s*60|TIMER_DURATION\s*=\s*30)\b', txt):
        warns.append("CHECK8: 30-minute timer constant not detected — verify timer manually")

    return fails, warns


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    any_fail = False
    for path in sys.argv[1:]:
        fails, warns = audit(path)
        print(f"\n===== {path} =====")
        for f in fails: print(f"  FAIL  {f}")
        for w in warns: print(f"  warn  {w}")
        if not fails and not warns:
            print("  ALL CHECKS PASS — zero failures, zero warnings")
        elif not fails:
            print(f"  0 failures, {len(warns)} warning(s) — review before delivery")
        else:
            any_fail = True
            print(f"  {len(fails)} FAILURE(S) — DO NOT DELIVER")
    sys.exit(1 if any_fail else 0)
