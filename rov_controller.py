import time
from pymavlink import mavutil


class ROVController:
    def __init__(self, connection_string="udpin:127.0.0.1:14551"):
        self.connection_string = connection_string
        self.master = None

    def connect(self):
        """Araca bağlanır ve ilk heartbeat sinyalini bekler."""
        print(f"Bağlanılıyor: {self.connection_string}...")
        self.master = mavutil.mavlink_connection(self.connection_string)
        self.master.wait_heartbeat()
        print(
            f"Bağlantı başarılı! Sistem ID: {self.master.target_system}, "
            f"Bileşen ID: {self.master.target_component}"
        )

    def send_heartbeat(self):
        """Yer kontrol istasyonu (GCS) olarak araca heartbeat gönderir."""
        if not self.master:
            raise RuntimeError("Önce connect() metodunu çağırmalısınız.")
        self.master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0,
            0,
            0,
        )
        print("Heartbeat gönderildi.")

    def set_mode(self, mode_name):
        """Uçuş modunu değiştirir: depthhold, stabilized, manual."""
        if not self.master:
            raise RuntimeError("Önce connect() metodunu çağırmalısınız.")

        # ArduSub'da Depth Hold modu MAVLink içinde ALT_HOLD olarak tanımlıdır
        mode_aliases = {
            "DEPTHHOLD": "ALT_HOLD",
            "DEPTH_HOLD": "ALT_HOLD",
            "STABILIZED": "STABILIZE",
            "STABILIZE": "STABILIZE",
            "MANUAL": "MANUAL",
        }
        target_mode = mode_aliases.get(mode_name.upper(), mode_name.upper())

        mode_mapping = self.master.mode_mapping()
        if target_mode not in mode_mapping:
            raise ValueError(f"Geçersiz mod: {mode_name}. Geçerli modlar: {list(mode_mapping.keys())}")

        mode_id = mode_mapping[target_mode]
        self.master.mav.set_mode_send(
            self.master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id,
        )
        print(f"Mod değiştirildi -> {target_mode} ({mode_name})")

    def arm(self):
        """Motorları aktif (ARM) duruma getirir."""
        if not self.master:
            raise RuntimeError("Önce connect() metodunu çağırmalısınız.")
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1, 0, 0, 0, 0, 0, 0,
        )
        self.master.motors_armed_wait()
        print("Araç ARM edildi.")

    def disarm(self):
        """Motorları pasif (DISARM) duruma getirir."""
        if not self.master:
            raise RuntimeError("Önce connect() metodunu çağırmalısınız.")
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            0, 0, 0, 0, 0, 0, 0,
        )
        self.master.motors_disarmed_wait()
        print("Araç DISARM edildi.")


if __name__ == "__main__":
    rov = ROVController("udpin:127.0.0.1:14551")
    rov.connect()
    rov.send_heartbeat()

    rov.set_mode("stabilized")
    time.sleep(1)

    rov.arm()
    time.sleep(2)

    rov.set_mode("depthhold")
    time.sleep(2)

    rov.set_mode("manual")
    time.sleep(1)

    rov.disarm()
