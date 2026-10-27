# youtube-episodes

Kursad Kucuk YouTube kanalının (youtube.com/@kursadkucuk) bölümlerinde gösterilen deney betikleri ve hook'lar. Her bölüm `episodes/<slug>/` altında durur.

Kurulum: Python 3.12+, `pip install -r episodes/<slug>/experiments/requirements.txt`. Anthropic API anahtarı `ANTHROPIC_API_KEY` ortam değişkeninden okunur (anahtar yoksa betikler API çağrılarını atlar).

| Klasör | Bölüm | Deneyler |
|---|---|---|
| `episodes/01-llm-nasil-dusunur` | Bölüm 1: LLM nasıl düşünür, ajan ne demek | D1 örnekleme, D2 tool_use, D3 PreToolUse hook |
