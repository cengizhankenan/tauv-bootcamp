# Araç Kontrol

ArduSub aracını MAVLink (pymavlink) üzerinden süren `Arac` class'ı: [arac.py](arac.py).

| Metot | Ne yapar |
|---|---|
| `baglan()` | Bağlantıyı açar, aracın heartbeat'ini bekler, arka planda heartbeat göndermeye başlar |
| `heartbeat_gonder()` / `heartbeat_baslat()` / `heartbeat_durdur()` | Tek heartbeat gönderir / saniyede bir göndermeye başlar / durdurur |
| `mod_degistir(mod)` | `"manual"`, `"stabilize"`, `"depthhold"` (ArduSub'da `ALT_HOLD`) |
| `arm()` / `disarm()` | Motorları arm / disarm eder |

Her komut, aracın onayını (`COMMAND_ACK`) ve aracın gerçekten yeni duruma geçtiğini (heartbeat) bekler. Reddedilirse ya da cevap gelmezse `AracHatasi` verir.

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
Disarm edildi
```

Kod içinden kullanım:

```python
from arac import Arac

with Arac("udp:127.0.0.1:14551") as arac:
    arac.mod_degistir("depthhold")
    arac.arm()
    arac.disarm()
```

`sitl/Dockerfile`, ArduPilot'un `Sub-4.7.3` sürümünü SITL olarak derler (`vectored` gövde modeli).
