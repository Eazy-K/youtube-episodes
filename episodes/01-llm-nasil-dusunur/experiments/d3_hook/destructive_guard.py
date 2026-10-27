"""Claude Code PreToolUse hook: deny destructive Bash commands. Stdlib only."""
import json
import re
import sys

PATTERNS = [("rm -rf", r"rm\s+-rf"), ("rm -r", r"rm\s+-r\s"), ("rm -fr", r"rm\s+-fr"),
            ("git worktree remove", r"git\s+worktree\s+remove"),
            ("git reset --hard", r"git\s+reset\s+--hard"),
            ("git clean -f", r"git\s+clean\s+-\w*f"),
            ("git push --force", r"git\s+push\s+.*(--force|\s-f\b)"),
            ("git branch -D", r"git\s+branch\s+-D"),
            ("del /s", r"del\s+/s"), ("rd /s", r"rd\s+/s"),
            ("Remove-Item -Recurse", r"Remove-Item\s.*-Recurse")]


def check(command):
    """Return the label of the first matching pattern, or None."""
    return next((name for name, rx in PATTERNS if re.search(rx, command, re.IGNORECASE)), None)


def decide(event):
    if event.get("tool_name") != "Bash":
        return None
    label = check(event.get("tool_input", {}).get("command", ""))
    if not label:
        return None
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
            "permissionDecisionReason": f"destructive-guard: '{label}' engellendi. "
            "Silme ve geri alınamaz git işlemleri için kullanıcıdan onay al."}}


def self_test():
    bad = ["rm -rf output", "git reset --hard HEAD~1", "git push origin main --force",
           "git worktree remove ../x", "Remove-Item -Recurse out"]
    good = ["ls -la", "git status", "python main.py", "git worktree list"]
    for c in bad:
        print("PASS" if check(c) else "FAIL", "engellenmeli:", c)
    for c in good:
        print("PASS" if not check(c) else "FAIL", "geçmeli:", c)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--self-test" in sys.argv:
        self_test()
    else:
        try:
            event = json.load(sys.stdin)
        except ValueError:
            sys.exit(0)
        out = decide(event) if isinstance(event, dict) else None
        if out:
            print(json.dumps(out, ensure_ascii=False))
