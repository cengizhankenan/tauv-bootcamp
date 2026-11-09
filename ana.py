import islemler

ort, harf = islemler.not_hesapla(vize=70, final=80, devam_tamam=True)
print(f"Ortalama: {ort:.1f} | Durum: {harf}")

kayitlar = [("Ali", 76.0), ("Ayşe", 45.5), ("Mehmet", 88.0)]
gecen_isimler = islemler.gecenleri_filtrele(kayitlar)
print("Geçenler:", gecen_isimler)

print("Geri sayım:", islemler.geri_sayim(4))

try:
    islemler.not_hesapla(vize=120, final=50, devam_tamam=True)
except ValueError as hata:
    print("Hata yakalandı:", hata)
