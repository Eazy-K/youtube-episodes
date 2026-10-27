# D3: destructive_guard (Claude Code PreToolUse hook)

Model komut önerir, harness karar verir. Bu hook, Bash aracı çalışmadan önce komutu okur; `rm -rf`, `git reset --hard`, `git push --force`, `git branch -D`, `del /s`, `rd /s`, `Remove-Item ... -Recurse` gibi kalıplardan biri varsa çağrıyı reddeder ve gerekçeyi Claude'a döndürür. Sadece Python 3 standart kütüphanesi kullanır.

## Kurulum

1. Boş bir deneme projesi aç (ör. `scratch-proje/`), içinde `.claude/settings.json` oluştur.
2. `settings.example.json` içeriğini oraya kopyala.
3. `<ABSOLUTE PATH>` yerine bu klasörün mutlak yolunu yaz (JSON'da yorum satırı olmadığı için not burada). Windows'ta ters bölüleri `/` yap ya da `\` olarak kaçır.

Hızlı test: `python episodes/01-llm-nasil-dusunur/experiments/d3_hook/destructive_guard.py --self-test` (5 yıkıcı, 4 zararsız komut; 9 satırın hepsi PASS olmalı).

## Kamerada demo

Deneme projesinde Claude Code'a söyle: `output klasörünü sil`. Beklenen: komut çalışmaz, `destructive-guard: 'rm -rf' engellendi. Silme ve geri alınamaz git işlemleri için kullanıcıdan onay al.` mesajı görünür ve Claude başka yol önerir.

## Sınır

Bu bir kalıp listesidir, garanti değil. Örneğin bir betik dosyasının içindeki komut ya da farklı yazılmış bir silme (`find -delete`, Python `shutil.rmtree`) yakalanmaz.

## Doğrulama

Hook çıktı biçimi (`hookSpecificOutput` / `hookEventName: "PreToolUse"` / `permissionDecision: "deny"` / `permissionDecisionReason`) ve ayar yapısı (event > matcher > hooks) https://code.claude.com/docs/en/hooks sayfasından 2026-10-27 tarihinde kontrol edildi (sayfanın ilk ~100 bin karakteri okundu; sürüm numarası sayfada görünmüyor).
