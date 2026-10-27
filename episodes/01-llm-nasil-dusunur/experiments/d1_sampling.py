"""D1: same prompt 3x, default sampling. temperature/top_p were removed in API 2026-10-21 (400 error), so no temperature=0 run."""
import os
import sys

MODEL = "claude-sonnet-5-5"
FUNC = '''def count_words_per_line(path):
    counts = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            counts.append(len(line.split()))
    return counts'''
PROMPT = ("Aşağıdaki Python fonksiyonuna 2-3 kelimelik bir isim öner. "
          "Sadece ismi yaz, açıklama yazma.\n\n" + FUNC)
RUNS = 3


NOTE = ("NOT: temperature/top_p/top_k API 2026-10-21 ile kaldırıldı (400 hatası); "
        "temperature=0 çağrısı yapılmaz. Eskiden 0'da bile tam deterministik değildi.")


def table(rows):
    print(f"{'run':<5}| {'default':<40}")
    print("-" * 48)
    for i, a in enumerate(rows, 1):
        print(f"{i:<5}| {a:<40}")


HEADER = "Düşünme bloğu (1. çağrı), ilk 12 satır:"


def show_thinking(content):
    print("\n" + HEADER)
    for b in content:
        if b.type == "redacted_thinking":
            return print("Düşünme bloğu gizli (redacted_thinking)")
        if b.type == "thinking":
            lines = b.thinking.splitlines()
            print("\n".join("  " + l for l in lines[:12]))
            return print(f"  … (toplam {len(b.thinking)} karakter)")
    print("Düşünme bloğu yok: model bu çağrıda düşünme bloğu döndürmedi.")


def call(client, model, **kw):
    r = client.messages.create(model=model, max_tokens=400,
                               messages=[{"role": "user", "content": PROMPT}], **kw)
    u = r.usage
    # Sonnet 5.5 may return a thinking block first; take the first text block.
    text = next((b.text for b in r.content if getattr(b, "type", "") == "text"), "<no text block>")
    return text.strip().replace("\n", " "), u.input_tokens, u.output_tokens


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    print("PROMPT:\n" + PROMPT + "\n")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY yok: API çağrıları atlandı")
        table(["-"] * RUNS)
        print("\n" + HEADER)
        print("\n" + NOTE)
        return
    import anthropic
    client = anthropic.Anthropic()
    model = MODEL
    try:
        call(client, model)
    except anthropic.NotFoundError:
        model = MODEL + "-latest"
        print(f"{MODEL} reddedildi, {model} deneniyor")
    print("Model:", model)
    rows, usage, first = [], [], None
    for _ in range(RUNS):
        d = call(client, model)
        rows.append(d[0])
        usage.append((d[1], d[2]))
        first = first or d[3]
    table(rows)
    show_thinking(first)
    print("\nusage (input/output tokens)")
    for i, u in enumerate(usage, 1):
        print(f"run {i}: default {u[0]}/{u[1]}")
    print("\n" + NOTE)


if __name__ == "__main__":
    main()
