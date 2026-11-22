print("Hello, world")
# 1. Metin (String)
ogrenci_adi = "Hevidar"

# 2. Tam sayı (Integer)
yas = 20

# 3. Ondalıklı sayı (Float)
boy = 1.63

# 4. Mantıksal (Boolean)
ogrenci_mi = True

# Ekrana yazdırma T(print)
print(ogrenci_adi)
print(yas)
# Kendi fonksiyonumuzu tanımlıyoruz
def topla(sayi1, sayi2):
    sonuc = sayi1 + sayi2
    return sonuc # Toplama işleminin sonucunu dışarıya veriyoruz

# Fonksiyonu çağırıp ekrana yazdırıyoruz
hesap = topla(5, 10)
print(hesap) # Ekrana 15 yazdıracak

# Koşul YApısı (if-else)
puan = 85

if puan >= 50:
    print("Tebrikler, dersten geçtiniz!")
else:
    print("Maalesef kaldınız.")

#Liste ve For Döngüsü
meyveler = ["elma", "armut", "muz"]

for meyve in meyveler:
    print("Sepetteki meyve:", meyve)

# Hata Fırlatma (raise ValueError)
yas_degeri = 25
if yas_degeri < 0:
    raise ValueError(" Yaş negatif olamaz!")

# Modül Kullanımı (import)
import math

koku = math.sqrt(16)
print("16'nın karekökü:", koku)

def clamp(deger, alt_sinir, ust_sinir):
    if deger < alt_sinir:
        return alt_sinir
    elif deger > ust_sinir:
        return ust_sinir
    return deger
print(clamp(15, 0, 10))
print(clamp(-5, 0, 10))
print(clamp(7, 0, 10))

import math
def wrap_angle(aci):
    return (aci + math.pi) % (2 * math.pi) - math.pi
print(wrap_angle(7.0))
print(wrap_angle(-5.0))

import math

def distance(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.sqrt(dx**2 + dy**2)
print(distance(0, 0, 3, 4))
print(distance(1, 1, 4, 5))
print(distance(2, 3, 7, 15))

import math

def bearing(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    return math.atan2(dy, dx)
print(bearing(0, 0, 1, 1))
print(bearing(0, 0, 1, 0))
print(bearing(0, 0, 3, 2))

def heading_error(hedef_aci, mevcut_aci):
    return wrap_angle(hedef_aci - mevcut_aci)

print("Heading Error Testi:", heading_error(1.57, 0.0))
