# Bölüm 1 deneyleri

Kurulum (repo kökünden, bir kez; Python 3.12+): `pip install -r episodes/01-llm-nasil-dusunur/experiments/requirements.txt`

API anahtarı (isteğe bağlı): `$env:ANTHROPIC_API_KEY = "..."` (PowerShell). Anahtar yoksa betikler "ANTHROPIC_API_KEY yok: ... atlandı" yazar ve yerel kısımları çalıştırır.

Çalıştırma (repo kökünden):
- `python episodes/01-llm-nasil-dusunur/experiments/d1_sampling.py`
  Prompt'u, sonra aynı prompt'la 3 varsayılan çağrının tablosunu ve usage token'larını basar. `temperature`/`top_p` çağrısı yok: API 2026-10-21 ile kaldırıldı (400 hatası); betik bunu not satırıyla basar. Anahtar yoksa tablo iskeleti ve not satırı. Çalıştırıldı 2026-10-27 (Sonnet 5.5): cevap üçünde aynı, output token farklı; betik ilk metin bloğunu alır (model önce düşünme bloğu döndürür), max_tokens 400. Ayrıca 1. çağrının düşünme bloğunun ilk 12 satırını basar (ekran kaydı E1b).
- `python episodes/01-llm-nasil-dusunur/experiments/d2_tool_use.py` ("Model hiçbir şeyi kendi çalıştırmaz")
  `scratch/silinecek.txt` dosyasını (yoksa) oluşturur, tek araç tanımlar (`delete_file`) ve modelden dosyayı silmesini ister.
  - Faz A (bayraksız): stop_reason, içerik blokları (tool_use: id, name, input), usage ve "Dosya hâlâ duruyor mu" kontrolü. Beklenen: `tool_use`, dosya duruyor.
  - Faz B (`--run`): harness `os.remove` ile kendisi siler, `tool_result` "silindi" gönderir; modelin son cevabı ve `end_turn` beklenir, dosya yok.
  - Faz C (`--deny`): harness reddeder (`is_error: true`, "Politika: silme izni yok. Harness reddetti."); model uyum sağlar, dosya yerinde.
  Anahtar yoksa gönderilecek istek (araç şeması + mesaj) basılır. `scratch/` `.gitignore` içinde.
- `d3_hook/` (D3): Claude Code PreToolUse hook'u, yıkıcı Bash komutlarını engeller. Ayrıntı: [d3_hook/README.md](d3_hook/README.md)

