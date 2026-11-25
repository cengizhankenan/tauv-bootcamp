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
                 sistem_id: int = 200, heartbeat_hz: float = 1.0):
        # sistem_id: bizim GCS kimliğimiz. QGC ve MAVProxy 255 kullandığı için
        # çakışmasın diye farklı bir değer seçildi.
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


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Arac class'ını uçtan uca dener.")
    ap.add_argument("--adres", default="udp:127.0.0.1:14551")
    args = ap.parse_args()

    with Arac(args.adres) as arac:
        for m in ("manual", "stabilize", "depthhold"):
            arac.mod_degistir(m)
        arac.mod_degistir("manual")
        arac.arm()
        time.sleep(2)
        arac.disarm()
