"""D2: the model only emits a tool_use request; our code (the harness) runs or denies it.
No temperature/top_p is sent (removed in API 2026-10-21, 400 error)."""
import json
import os
import sys

MODEL = "claude-sonnet-5-5"
HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.join(HERE, "scratch")
FILE = os.path.join(SCRATCH, "silinecek.txt")
PROMPT = "scratch/silinecek.txt dosyasını sil."
TOOLS = [{"name": "delete_file", "description": "Verilen yoldaki dosyayı siler.",
          "input_schema": {"type": "object", "properties": {"path": {"type": "string"}},
                           "required": ["path"]}}]
DENY_MSG = "Politika: silme izni yok. Harness reddetti."


def exists_line():
    print("Dosya hâlâ duruyor mu:", "EVET" if os.path.exists(FILE) else "HAYIR")


def ask(client, messages):
    return client.messages.create(model=MODEL, max_tokens=400, tools=TOOLS, messages=messages)


def show(r, title):
    print(f"\n=== {title} ===\nstop_reason: {r.stop_reason}")
    for b in r.content:
        d = {"type": b.type}
        if b.type == "tool_use":
            d.update(id=b.id, name=b.name, input=b.input)
        elif b.type == "text":
            d["text"] = b.text
        print(json.dumps(d, ensure_ascii=False, indent=2))
    print(f"usage: input {r.usage.input_tokens} / output {r.usage.output_tokens} token")


def harness(tool, deny):
    # this is the harness: the only code that touches the file
    if deny:
        return {"type": "tool_result", "tool_use_id": tool.id, "is_error": True, "content": DENY_MSG}
    path = os.path.realpath(os.path.join(HERE, tool.input["path"]))
    if os.path.commonpath([path, SCRATCH]) != SCRATCH:
        return {"type": "tool_result", "tool_use_id": tool.id, "is_error": True,
                "content": "Yol scratch/ dışında, harness reddetti."}
    os.remove(path)
    return {"type": "tool_result", "tool_use_id": tool.id, "content": "silindi"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    run, deny = "--run" in sys.argv, "--deny" in sys.argv
    os.makedirs(SCRATCH, exist_ok=True)
    if not os.path.exists(FILE):
        with open(FILE, "w", encoding="utf-8") as f:
            f.write("Bu dosya deney için var.\n")
    messages = [{"role": "user", "content": PROMPT}]
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY yok: API çağrısı atlandı. Gönderilecek istek:")
        print(json.dumps({"model": MODEL, "max_tokens": 400, "tools": TOOLS, "messages": messages},
                         ensure_ascii=False, indent=2))
        return
    import anthropic
    client = anthropic.Anthropic()
    r = ask(client, messages)
    show(r, "Faz A: model ne döndürdü?")
    exists_line()
    tool = next((b for b in r.content if b.type == "tool_use"), None)
    if not (run or deny):
        print("\nÖzet: Model sadece istek üretti. Dosyaya kimse dokunmadı.")
        return
    if tool is None:
        print("tool_use bloğu yok, devam edilemiyor.")
        return
    result = harness(tool, deny)
    print("\nHarness:", "reddetti" if result.get("is_error") else "çalıştırdı", "->", result["content"])
    exists_line()
    messages += [{"role": "assistant", "content": [b.model_dump(exclude_none=True) for b in r.content]},
                 {"role": "user", "content": [result]}]
    r2 = ask(client, messages)
    show(r2, "Faz C: model reddi nasıl karşıladı?" if deny else "Faz B: model sonucu nasıl yorumladı?")
    exists_line()


if __name__ == "__main__":
    main()
