#!/usr/bin/env python3
"""Export agent transcript to markdown by conversation rounds."""
import ast
import json
import re
from pathlib import Path

TRANSCRIPT = Path(
    r"C:\Users\cenhuiying\.cursor\projects\D-NOTE-PERSONAL\agent-transcripts"
    r"\5e12d300-1f90-4409-b098-1f5da9ca345d\5e12d300-1f90-4409-b098-1f5da9ca345d.jsonl"
)
OUTPUT = Path(
    r"D:\NOTE\PERSONAL\openspec\changes\pixel-rpg-personal-site\conversation-log.md"
)


def parse_message(raw):
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            return ast.literal_eval(raw)
        except (SyntaxError, ValueError):
            return {"content": [{"type": "text", "text": raw}]}
    return {"content": []}


def text_blocks(msg_dict):
    blocks = []
    for part in msg_dict.get("content", []):
        if part.get("type") == "text":
            t = part.get("text", "")
            if t and t.strip() not in ("[REDACTED]",):
                blocks.append(t)
    return blocks


def extract_user_fields(text):
    ts = re.search(r"<timestamp>(.*?)</timestamp>", text, re.S)
    uq = re.search(r"<user_query>(.*?)</user_query>", text, re.S)
    timestamp = ts.group(1).strip() if ts else None
    if uq:
        query = uq.group(1).strip()
    else:
        # fallback: strip known wrappers, keep body
        query = text
        for pat in (
            r"<manually_attached_skills>.*?</manually_attached_skills>",
            r"<agent_skills>.*?</agent_skills>",
            r"<user_info>.*?</user_info>",
            r"<git_status>.*?</git_status>",
            r"<agent_transcripts>.*?</agent_transcripts>",
            r"<timestamp>.*?</timestamp>",
        ):
            query = re.sub(pat, "", query, flags=re.S)
        query = query.strip()
    return timestamp, query


def assistant_visible_text(text):
    """Drop tool XML noise; keep prose."""
    t = text.strip()
    if not t:
        return None
    if t == "[REDACTED]":
        return "*(工具调用步骤在 transcript 中已脱敏)*"
    t = t.replace("[REDACTED]", "*(工具调用步骤在 transcript 中已脱敏)*")
    return t.strip() or None


def dedupe_assistant_parts(parts):
    out = []
    for p in parts:
        if out and p == out[-1]:
            continue
        out.append(p)
    # collapse repeated redaction markers
    collapsed = []
    for p in out:
        if collapsed and p.startswith("*(") and collapsed[-1].startswith("*("):
            continue
        collapsed.append(p)
    return collapsed


def main():
    lines = TRANSCRIPT.read_text(encoding="utf-8").splitlines()
    rounds = []
    pending_user = None
    pending_assistant = []
    round_no = 0

    def flush_round():
        nonlocal round_no, pending_user, pending_assistant
        if pending_user is None:
            pending_assistant = []
            return
        if not pending_assistant:
            return
        round_no += 1
        rounds.append(
            {
                "round": round_no,
                "timestamp": pending_user["timestamp"],
                "user": pending_user["content"],
                "assistant": "\n\n".join(dedupe_assistant_parts(pending_assistant)),
            }
        )
        pending_user = None
        pending_assistant = []

    for line in lines:
        if not line.strip():
            continue
        obj = json.loads(line)
        role = obj.get("role")
        msg = parse_message(obj.get("message", {}))

        if role == "user":
            flush_round()
            for block in text_blocks(msg):
                ts, query = extract_user_fields(block)
                if not query:
                    continue
                pending_user = {"timestamp": ts, "content": query}

        elif role == "assistant":
            for block in text_blocks(msg):
                cleaned = assistant_visible_text(block)
                if cleaned and pending_user is not None:
                    pending_assistant.append(cleaned)

    flush_round()

    # Build markdown
    out = [
        "# Pixel RPG Personal Site — 对话记录",
        "",
        "> 按轮次归档；用户消息含 `<timestamp>` 的以该时间为准，其余轮次时间见 transcript 顺序。",
        "> 来源：`agent-transcripts/5e12d300-1f90-4409-b098-1f5da9ca345d.jsonl`",
        "> 助手消息中 `*(工具调用步骤在 transcript 中已脱敏)*` 表示原 transcript 对工具调用内容做了 REDACTED。",
        "",
        "**导出脚本：** `scripts/export-conversation.py`（可重复运行以从 transcript 刷新）",
        "",
        f"**总轮次：** {len(rounds)}",
        "",
        "---",
        "",
    ]

    for r in rounds:
        out.append(f"## 第 {r['round']} 轮")
        out.append("")
        if r["timestamp"]:
            out.append(f"**时间：** {r['timestamp']}")
            out.append("")
        out.append("### 用户")
        out.append("")
        out.append(r["user"])
        out.append("")
        out.append("### 助手")
        out.append("")
        out.append(r["assistant"])
        out.append("")
        out.append("---")
        out.append("")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {len(rounds)} rounds -> {OUTPUT}")


if __name__ == "__main__":
    main()
