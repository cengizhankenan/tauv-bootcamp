# Araç Kontrol

ArduSub aracını MAVLink (pymavlink) üzerinden süren `Arac` class'ı: [arac.py](arac.py).

| Metot | Ne yapar |
|---|---|
| `baglan()` | Bağlantıyı açar, aracın heartbeat'ini bekler, arka planda heartbeat göndermeye başlar |
| `heartbeat_gonder()` / `heartbeat_baslat()` / `heartbeat_durdur()` | Tek heartbeat gönderir / saniyede bir göndermeye başlar / durdurur |
| `mod_degistir(mod)` | `"manual"`, `"stabilize"`, `"depthhold"` (ArduSub'da `ALT_HOLD`) |
| `arm()` / `disarm()` | Motorları arm / disarm eder |
| `hareket(ileri, yanal, dikey, donus, sure)` | Sanal joystick: eksenler -1..1, `sure` saniye uygular, sonra durur |
| `ileri_git` / `geri_git` / `saga_kay` / `sola_kay` / `yuksel` / `dal` / `don` | `hareket`'in kısa yolları: `(sure, guc)` |
| `dur()` | Bütün eksenleri boşa alır |
| `guncelle()` | Bekleyen mesajları okuyup durumu (mod, arm, konum) günceller |
| `konum()` | `(enlem, boylam, derinlik_m, yön_derece)` |

Her komut, aracın onayını (`COMMAND_ACK`) ve aracın gerçekten yeni duruma geçtiğini (heartbeat) bekler. Reddedilirse ya da cevap gelmezse `AracHatasi` verir.

Hareket, ArduSub'ın `MANUAL_CONTROL` mesajıyla (joystick'in gönderdiği mesaj) yapılır. Araç bu mesajı sadece `MAV_GCS_SYSID` parametresindeki sistem kimliğinden (varsayılan 255) kabul eder; bu yüzden class varsayılan olarak 255 kimliğiyle bağlanır. Mesaj kesilince araç motorları boşa aldığı için `hareket` süre boyunca saniyede 10 kez gönderir.

## Çalıştırma

Üç ayrı terminalde, hiçbirini kapatmadan:

```bash
# 1. ArduSub simülatörü (ilk seferde image'ı derle, ~5-25 dk)
docker build -t ardusub-sitl sitl
docker run --rm -it -p 5760:5760 --name ardusub ardusub-sitl

# 2. MAVProxy: QGroundControl'e 14550, bu koda 14551
mavproxy.py --master=tcp:127.0.0.1:5760 --out=udp:127.0.0.1:14550 --out=udp:127.0.0.1:14551

# 3. QGroundControl'ü aç (14550'yi kendisi dinler)
```

Sonra:

```bash
pip install pymavlink
python3 arac.py
```

Beklenen çıktı:

```
Bağlandı: sistem 1, bileşen 0, mod MANUAL
Mod: MANUAL
Mod: STABILIZE
Mod: ALT_HOLD
Mod: MANUAL
Arm edildi
ileri     kuzey -1.6 m, doğu -0.1 m, derinlik 0.1→0.1 m, yön 184→184°
sağa      kuzey -0.2 m, doğu -1.5 m, derinlik 0.1→0.1 m, yön 184→184°
dal       kuzey -0.1 m, doğu -0.2 m, derinlik 0.1→1.0 m, yön 184→185°
sağa dön  kuzey -0.1 m, doğu -0.2 m, derinlik 1.0→0.8 m, yön 185→259°
Disarm edildi
```

(Araç başlangıçta güneye, ~184°'ye bakıyor; bu yüzden "ileri" güneye, "sağa" batıya gider.)

## Klavyeyle sürmek (WASD)

```bash
python3 klavye.py
```

| Tuş | Hareket | Tuş | Hareket |
|---|---|---|---|
| W / S | ileri / geri | Q / E | sola / sağa dön |
| A / D | sola / sağa kay | R / F | yüksel / dal |
| boşluk | dur | + / - | gücü artır / azalt |
| M | arm / disarm | 1 / 2 / 3 | MANUAL / STABILIZE / DEPTH HOLD |
| X | çıkış (araç disarm edilir) | | |

Alt satırda mod, arm durumu, güç, derinlik ve yön canlı görünür. Terminal tuşun bırakıldığını bildirmediği için hareket, tuş basılı tutulup tekrar ettikçe sürer ve bırakınca kısa süre sonra durur. Aynı anda tek hareket tuşu çalışır.

Kod içinden kullanım:

```python
from arac import Arac

with Arac("udp:127.0.0.1:14551") as arac:
    arac.mod_degistir("depthhold")
    arac.arm()
    arac.ileri_git(3)        # 3 sn, %50 güç
    arac.don(2, guc=-0.3)    # 2 sn sola dön
    arac.disarm()
```

`sitl/Dockerfile`, ArduPilot'un `Sub-4.7.3` sürümünü SITL olarak derler (`vectored` gövde modeli).
