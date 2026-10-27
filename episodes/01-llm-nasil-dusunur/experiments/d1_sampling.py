"""D1: same prompt 3x, default sampling. temperature/top_p were removed in API 2026-10-21 (400 error), so no temperature=0 run.
Sonnet 5.5 always thinks (adaptive, effort high by default; "enabled"+budget_tokens and "disabled" give 400),
but `display` defaults to "omitted": the thinking block comes back with empty text and only a signature, while
the thinking tokens are still billed. `--thinking` sets display="summarized" (and effort high explicitly) so a
summary of the thinking is returned. Raw chain of thought is never returned. Seen 2026-10-27; docs:
https://platform.claude.com/docs/en/build-with-claude/thinking#controlling-thinking-display"""
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


HEADER = "Düşünme bloğu (bulunan ilk çağrı), ilk 12 satır:"


def show_thinking(contents):
    print("\n" + HEADER)
    for i, content in enumerate(contents, 1):
        for b in content:
            if b.type == "redacted_thinking":
                return print(f"  çağrı {i}: düşünme bloğu gizli (redacted_thinking)")
            if b.type == "thinking":
                lines = b.thinking.splitlines()
                print(f"  çağrı {i}:")
                print("\n".join("  " + l for l in lines[:12]))
                return print(f"  … (toplam {len(b.thinking)} karakter)")
    print("Düşünme bloğu yok: hiçbir çağrıda düşünme bloğu dönmedi.")


def call(client, model, thinking=False):
    # API 2026-10-27: "thinking.type.enabled" is not supported for this model;
    # use thinking.type.adaptive + output_config.effort instead.
    # display="summarized" is required to get the thinking text; the model default omits it.
    extra = ({"thinking": {"type": "adaptive", "display": "summarized"},
              "output_config": {"effort": "high"}} if thinking else {})
    r = client.messages.create(model=model, max_tokens=2000 if thinking else 400,
                               messages=[{"role": "user", "content": PROMPT}], **extra)
    u = r.usage
    # Sonnet 5.5 may return a thinking block first; take the first text block.
    text = next((b.text for b in r.content if getattr(b, "type", "") == "text"), "<no text block>")
    return text.strip().replace("\n", " "), u.input_tokens, u.output_tokens, r.content


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    thinking = "--thinking" in sys.argv
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
        call(client, model, thinking)
    except anthropic.NotFoundError:
        model = MODEL + "-latest"
        print(f"{MODEL} reddedildi, {model} deneniyor")
    print("Model:", model)
    print("thinking: adaptive, effort high, display summarized" if thinking else "thinking: default")
    rows, usage, contents = [], [], []
    for _ in range(RUNS):
        d = call(client, model, thinking)
        rows.append(d[0])
        usage.append((d[1], d[2]))
        contents.append(d[3])
    table(rows)
    show_thinking(contents)
    print("\nusage (input/output tokens)")
    for i, u in enumerate(usage, 1):
        print(f"run {i}: default {u[0]}/{u[1]}")
    print("\n" + NOTE)


if __name__ == "__main__":
    main()
