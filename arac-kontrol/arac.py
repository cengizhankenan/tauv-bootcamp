"""ArduSub aracını MAVLink üzerinden süren basit class.

Yetenekler: bağlan, heartbeat gönder, mod değiştir (MANUAL / STABILIZE /
ALT_HOLD = depth hold), arm et, disarm et.

Örnek:
    with Arac("udp:127.0.0.1:14551") as arac:
        arac.mod_degistir("depthhold")
        arac.arm()
        arac.disarm()
"""

from __future__ import annotations

import threading
import time

from pymavlink import mavutil


class AracHatasi(RuntimeError):
    """Araç bir komutu reddettiğinde ya da zamanında cevap vermediğinde."""


class Arac:
    # Kullanıcı dostu adlar → ArduSub'daki mod adları
    MOD_TAKMA_ADLARI = {
        "manual": "MANUAL",
        "stabilize": "STABILIZE",
        "stabilized": "STABILIZE",
        "depthhold": "ALT_HOLD",
        "depth_hold": "ALT_HOLD",
        "alt_hold": "ALT_HOLD",
    }

    def __init__(self, adres: str = "udp:127.0.0.1:14551",
                 sistem_id: int = 255, heartbeat_hz: float = 1.0):
        # sistem_id: bizim GCS kimliğimiz. ArduSub joystick (MANUAL_CONTROL)
        # komutlarını sadece MAV_GCS_SYSID parametresindeki kimlikten (varsayılan
        # 255) kabul eder; başka bir değerle hareket komutları yok sayılır.
        self.adres = adres
        self.sistem_id = sistem_id
        self.heartbeat_periyot = 1.0 / heartbeat_hz
        self.baglanti: mavutil.mavfile | None = None
        self._gonderme_kilidi = threading.Lock()
        self._durdur = threading.Event()
        self._hb_thread: threading.Thread | None = None

    @property
    def _b(self) -> mavutil.mavfile:
        if self.baglanti is None:
            raise AracHatasi("Önce baglan() çağrılmalı")
        return self.baglanti

    # ------------------------------------------------------------ bağlantı
    def baglan(self, zaman_asimi: float = 15.0) -> None:
        """Bağlantıyı açar, aracın heartbeat'ini bekler ve heartbeat göndermeye başlar."""
        self.baglanti = mavutil.mavlink_connection(
            self.adres,
            source_system=self.sistem_id,
            source_component=mavutil.mavlink.MAV_COMP_ID_MISSIONPLANNER,
        )
        # UDP'de araç bize ancak biz bir paket gönderince yazar; o yüzden
        # beklemeden önce heartbeat göndermeye başlıyoruz.
        self.heartbeat_baslat()
        hb = self._b.wait_heartbeat(timeout=zaman_asimi)
        if hb is None:
            self.kapat()
            raise AracHatasi(f"{zaman_asimi:.0f} sn içinde araçtan heartbeat gelmedi ({self.adres})")
        print(f"Bağlandı: sistem {self._b.target_system}, "
              f"bileşen {self._b.target_component}, mod {self.mod}")

    def kapat(self) -> None:
        self.heartbeat_durdur()
        if self.baglanti is not None:
            self._b.close()
            self.baglanti = None

    def __enter__(self) -> "Arac":
        self.baglan()
        return self

    def __exit__(self, *_exc) -> None:
        self.kapat()

    # ----------------------------------------------------------- heartbeat
    def heartbeat_gonder(self) -> None:
        """Tek bir GCS heartbeat'i gönderir."""
        with self._gonderme_kilidi:
            self._b.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                0, 0, 0,
            )

    def heartbeat_baslat(self) -> None:
        """Arka planda düzenli heartbeat göndermeye başlar (aracın GCS failsafe'i için)."""
        if self._hb_thread and self._hb_thread.is_alive():
            return
        self._durdur.clear()

        def dongu():
            while not self._durdur.is_set():
                try:
                    self.heartbeat_gonder()
                except OSError:
                    pass  # bağlantı kapanırken olabilir
                self._durdur.wait(self.heartbeat_periyot)

        self._hb_thread = threading.Thread(target=dongu, name="heartbeat", daemon=True)
        self._hb_thread.start()

    def heartbeat_durdur(self) -> None:
        self._durdur.set()
        if self._hb_thread:
            self._hb_thread.join(timeout=2)
            self._hb_thread = None

    # --------------------------------------------------------------- durum
    @property
    def mod(self) -> str:
        return self._b.flightmode

    @property
    def armli_mi(self) -> bool:
        return bool(self._b.motors_armed())

    def _aractan_heartbeat_bekle(self, kosul, zaman_asimi: float) -> bool:
        """Aracın heartbeat'leri koşulu sağlayana kadar bekler."""
        bitis = time.monotonic() + zaman_asimi
        while time.monotonic() < bitis:
            msg = self._b.recv_match(type="HEARTBEAT", blocking=True, timeout=0.5)
            if msg is None or msg.get_srcSystem() != self._b.target_system:
                continue
            if kosul():
                return True
        return False

    def _komut_gonder(self, komut: int, *parametreler: float, zaman_asimi: float = 3.0) -> None:
        """COMMAND_LONG gönderir ve COMMAND_ACK'i bekler; reddedilirse hata verir."""
        p = list(parametreler) + [0.0] * (7 - len(parametreler))
        with self._gonderme_kilidi:
            self._b.mav.command_long_send(
                self._b.target_system, self._b.target_component,
                komut, 0, *p,
            )
        bitis = time.monotonic() + zaman_asimi
        while time.monotonic() < bitis:
            ack = self._b.recv_match(type="COMMAND_ACK", blocking=True, timeout=0.5)
            if ack is None or ack.command != komut:
                continue
            if ack.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
                return
            sonuc = mavutil.mavlink.enums["MAV_RESULT"][ack.result].name
            raise AracHatasi(f"Komut {komut} reddedildi: {sonuc}")
        raise AracHatasi(f"Komut {komut} için {zaman_asimi:.0f} sn içinde cevap gelmedi")

    # ------------------------------------------------------------- komutlar
    def mod_degistir(self, mod: str, zaman_asimi: float = 5.0) -> None:
        """Modu değiştirir: 'manual', 'stabilize'/'stabilized', 'depthhold' (ALT_HOLD)."""
        ad = self.MOD_TAKMA_ADLARI.get(mod.lower().replace(" ", ""), mod.upper())
        modlar = self._b.mode_mapping()
        if ad not in modlar:
            raise AracHatasi(f"Bilinmeyen mod: {mod!r}. Geçerli: {sorted(modlar)}")
        mod_id = modlar[ad]
        self._komut_gonder(
            mavutil.mavlink.MAV_CMD_DO_SET_MODE,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mod_id,
        )
        if not self._aractan_heartbeat_bekle(lambda: self.mod == ad, zaman_asimi):
            raise AracHatasi(f"Mod {ad} olmadı (şu an: {self.mod})")
        print(f"Mod: {ad}")

    def arm(self, zorla: bool = False, zaman_asimi: float = 5.0) -> None:
        """Motorları arm eder. zorla=True ön kontrolleri atlar (sadece test için)."""
        self._arm_disarm(True, zorla, zaman_asimi)

    def disarm(self, zorla: bool = False, zaman_asimi: float = 5.0) -> None:
        self._arm_disarm(False, zorla, zaman_asimi)

    def _arm_disarm(self, arm: bool, zorla: bool, zaman_asimi: float) -> None:
        self._komut_gonder(
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            1 if arm else 0,
            21196 if zorla else 0,  # ArduPilot'un "zorla" sihirli sayısı
        )
        if not self._aractan_heartbeat_bekle(lambda: self.armli_mi == arm, zaman_asimi):
            raise AracHatasi("Arm olmadı" if arm else "Disarm olmadı")
        print("Arm edildi" if arm else "Disarm edildi")

    # -------------------------------------------------------------- hareket
    def kontrol_gonder(self, ileri: float = 0.0, yanal: float = 0.0,
                       dikey: float = 0.0, donus: float = 0.0) -> None:
        """Tek bir MANUAL_CONTROL (sanal joystick) mesajı gönderir.

        Değerler -1..1 arası: ileri (+ileri/-geri), yanal (+sağ/-sol),
        dikey (+yukarı/-aşağı), donus (+saat yönü/-tersi). 0 = boşta.
        """
        def olcekle(v: float) -> int:
            return int(max(-1.0, min(1.0, v)) * 1000)

        with self._gonderme_kilidi:
            self._b.mav.manual_control_send(
                self._b.target_system,
                olcekle(ileri),
                olcekle(yanal),
                500 + olcekle(dikey) // 2,  # z: 0..1000, 500 = boşta
                olcekle(donus),
                0,  # buton yok
            )

    def hareket(self, ileri: float = 0.0, yanal: float = 0.0, dikey: float = 0.0,
                donus: float = 0.0, sure: float = 1.0, hz: float = 10.0) -> None:
        """Verilen komutu `sure` saniye boyunca uygular, sonra aracı durdurur.

        ArduSub joystick komutu kesilince motorları boşa aldığı için mesaj
        süre boyunca saniyede `hz` kez tekrar gönderilir. Araç armed olmalı.
        """
        if not self.armli_mi:
            raise AracHatasi("Hareket için önce arm() çağrılmalı")
        bitis = time.monotonic() + sure
        while time.monotonic() < bitis:
            self.kontrol_gonder(ileri, yanal, dikey, donus)
            self.guncelle()
            time.sleep(1.0 / hz)
        self.dur()

    def guncelle(self) -> None:
        """Bekleyen bütün mesajları okur; araç durumu (mod, arm, konum) güncellenir."""
        while self._b.recv_match(blocking=False) is not None:
            pass

    def dur(self) -> None:
        """Bütün eksenleri boşa alır."""
        for _ in range(3):
            self.kontrol_gonder()
            time.sleep(0.05)

    def ileri_git(self, sure: float, guc: float = 0.5) -> None:
        self.hareket(ileri=guc, sure=sure)

    def geri_git(self, sure: float, guc: float = 0.5) -> None:
        self.hareket(ileri=-guc, sure=sure)

    def saga_kay(self, sure: float, guc: float = 0.5) -> None:
        self.hareket(yanal=guc, sure=sure)

    def sola_kay(self, sure: float, guc: float = 0.5) -> None:
        self.hareket(yanal=-guc, sure=sure)

    def yuksel(self, sure: float, guc: float = 0.5) -> None:
        self.hareket(dikey=guc, sure=sure)

    def dal(self, sure: float, guc: float = 0.5) -> None:
        self.hareket(dikey=-guc, sure=sure)

    def don(self, sure: float, guc: float = 0.3) -> None:
        """guc > 0 sağa (saat yönü), guc < 0 sola döner."""
        self.hareket(donus=guc, sure=sure)

    def konum(self, zaman_asimi: float = 2.0) -> tuple[float, float, float, float]:
        """(enlem, boylam, derinlik_m, yön_derece) döndürür. Derinlik yüzeyde 0, aşağı +."""
        self.guncelle()  # tampondaki eski mesajları at, en günceli kalsın
        msg = self._b.messages.get("GLOBAL_POSITION_INT")
        if msg is None:
            msg = self._b.recv_match(type="GLOBAL_POSITION_INT", blocking=True, timeout=zaman_asimi)
        if msg is None:
            raise AracHatasi("Konum bilgisi gelmedi")
        return msg.lat / 1e7, msg.lon / 1e7, -msg.relative_alt / 1000, msg.hdg / 100


if __name__ == "__main__":
    import argparse
    import math

    ap = argparse.ArgumentParser(description="Arac class'ını uçtan uca dener.")
    ap.add_argument("--adres", default="udp:127.0.0.1:14551")
    args = ap.parse_args()

    with Arac(args.adres) as arac:
        for m in ("manual", "stabilize", "depthhold"):
            arac.mod_degistir(m)
        arac.mod_degistir("manual")
        arac.arm()

        hareketler = [
            ("ileri", lambda: arac.ileri_git(3)),
            ("sağa", lambda: arac.saga_kay(3)),
            ("dal", lambda: arac.dal(3)),
            ("sağa dön", lambda: arac.don(3)),
        ]
        for ad, hareket in hareketler:
            once = arac.konum()
            hareket()
            time.sleep(1)  # aracın biraz yavaşlaması için
            sonra = arac.konum()
            kuzey = (sonra[0] - once[0]) * 111_320
            dogu = (sonra[1] - once[1]) * 111_320 * math.cos(math.radians(once[0]))
            print(f"{ad:9s} kuzey {kuzey:+.1f} m, doğu {dogu:+.1f} m, "
                  f"derinlik {once[2]:.1f}→{sonra[2]:.1f} m, yön {once[3]:.0f}→{sonra[3]:.0f}°")

        arac.disarm()
