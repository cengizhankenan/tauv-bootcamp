def not_hesapla(vize: float, final: float, devam_tamam: bool) -> tuple[float, str]:
    if not (0 <= vize <= 100) or not (0 <= final <= 100):
        raise ValueError("Vize ve final notları 0 ile 100 arasında olmalıdır.")

    if not devam_tamam:
        return 0.0, "FF (Devamsız)"

    ortalama = vize * 0.4 + final * 0.6

    if ortalama >= 85 and final >= 50:
        durum = "AA"
    elif ortalama >= 60 or final >= 70:
        durum = "CB"
    else:
        durum = "FF"

    return ortalama, durum


def gecenleri_filtrele(ogrenci_notlari: list[tuple[str, float]]) -> list[str]:
    gecenler = []
    for isim, puan in ogrenci_notlari:
        if puan >= 60:
            gecenler.append(isim)
    return gecenler


def geri_sayim(baslangic: int) -> list[int]:
    if baslangic <= 0:
        raise ValueError("Başlangıç sayısı pozitif bir tam sayı olmalıdır.")

    sayac = baslangic
    adimlar = []
    while sayac > 0:
        adimlar.append(sayac)
        sayac -= 1
    return adimlar
