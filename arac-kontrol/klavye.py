"""Aracı terminalden klavyeyle sürer (WASD).

Çalıştırma (simülatör ve MAVProxy açıkken):
    python3 klavye.py

Tuşlar:
    W / S   ileri / geri          Q / E   sola / sağa dön
    A / D   sola / sağa kay       R / F   yüksel / dal
    boşluk  dur                   + / -   gücü artır / azalt
    M       arm / disarm          1 2 3   MANUAL / STABILIZE / DEPTH HOLD
    X       çıkış (Ctrl+C de olur)

Terminal tuşun bırakıldığını bildirmez; basılı tutulan tuş tekrar ettikçe
hareket sürer, tekrar kesilince kısa süre sonra durur. Aynı anda tek hareket
tuşu çalışır (terminal sadece son basılı tuşu tekrarlar).
"""

from __future__ import annotations

import select
import sys
import termios
import time
import tty

from arac import Arac, AracHatasi

# tuş → (eksen, yön)
HAREKET_TUSLARI = {
    "w": ("ileri", +1), "s": ("ileri", -1),
    "d": ("yanal", +1), "a": ("yanal", -1),
    "r": ("dikey", +1), "f": ("dikey", -1),
    "e": ("donus", +1), "q": ("donus", -1),
}
MOD_TUSLARI = {"1": "manual", "2": "stabilize", "3": "depthhold"}

ILK_BASIS_SURESI = 0.6   # ilk basışta: işletim sisteminin tekrar gecikmesini kapsar
TEKRAR_SURESI = 0.15     # tuş tekrar ederken: bırakınca bu kadar sonra durur
DONGU_HZ = 20


def tuslari_oku() -> str:
    """Bekleyen bütün tuşları bloklamadan okur."""
    tuslar = ""
    while select.select([sys.stdin], [], [], 0)[0]:
        tuslar += sys.stdin.read(1)
    return tuslar


def main() -> None:
    guc = 0.5
    aktif: dict[str, tuple[str, int, float]] = {}  # eksen → (tuş, yön, bitiş zamanı)
    mesaj = ""

    with Arac() as arac:
        print(__doc__.split("Tuşlar:")[1].split("Terminal")[0])
        eski_ayar = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())  # tuşlar Enter beklemeden gelsin
        try:
            while True:
                simdi = time.monotonic()
                for tus in tuslari_oku().lower():
                    if tus in HAREKET_TUSLARI:
                        eksen, yon = HAREKET_TUSLARI[tus]
                        onceki = aktif.get(eksen)
                        if onceki is not None and onceki[0] == tus:
                            # tuş tekrar ediyor: ilk basışın süresini kısaltmadan uzat
                            bitis = max(simdi + TEKRAR_SURESI, onceki[2])
                        else:
                            bitis = simdi + ILK_BASIS_SURESI
                        aktif = {eksen: (tus, yon, bitis)}
                    elif tus == " ":
                        aktif.clear()
                    elif tus in "+=":
                        guc = min(1.0, round(guc + 0.1, 1))
                    elif tus == "-":
                        guc = max(0.1, round(guc - 0.1, 1))
                    elif tus in ("m", "1", "2", "3"):
                        aktif.clear()
                        arac.dur()
                        print()
                        try:
                            if tus == "m":
                                arac.disarm() if arac.armli_mi else arac.arm()
                            else:
                                arac.mod_degistir(MOD_TUSLARI[tus])
                            mesaj = ""
                        except AracHatasi as e:
                            mesaj = f"HATA: {e}"
                    elif tus == "x":
                        return

                aktif = {k: v for k, v in aktif.items() if v[2] > simdi}
                eksenler = {k: yon * guc for k, (_, yon, _) in aktif.items()}
                arac.guncelle()
                if arac.armli_mi:
                    arac.kontrol_gonder(**eksenler)

                try:
                    _, _, derinlik, yon_derece = arac.konum(zaman_asimi=0.05)
                    konum = f"derinlik {derinlik:4.1f} m  yön {yon_derece:3.0f}°"
                except AracHatasi:
                    konum = "konum yok"
                hareket = ", ".join(f"{k} {v:+.1f}" for k, v in eksenler.items()) or "duruyor"
                durum = "ARMED" if arac.armli_mi else "disarmed (M ile arm et)"
                sys.stdout.write(f"\r\033[K{arac.mod:9s} {durum:24s} güç {guc:.1f}  "
                                 f"{konum}  | {hareket}  {mesaj}")
                sys.stdout.flush()
                time.sleep(1.0 / DONGU_HZ)
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, eski_ayar)
            if arac.armli_mi:
                print()
                arac.dur()
                arac.disarm()
            print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
