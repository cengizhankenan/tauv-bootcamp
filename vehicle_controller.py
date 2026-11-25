import time
from pymavlink import mavutil


class VehicleController:
    MODE_ALIASES = {
        "depthold": "ALT_HOLD",
        "depth_hold": "ALT_HOLD",
        "alt_hold": "ALT_HOLD",
        "stabilized": "STABILIZE",
        "stabilize": "STABILIZE",
        "manual": "MANUAL",
    }

    def __init__(self, connection_string: str = "udpin:0.0.0.0:14551"):
        self.connection_string = connection_string
        self.master = None

    def connect(self) -> None:
        print(f"Baglaniliyor: {self.connection_string}")
        self.master = mavutil.mavlink_connection(self.connection_string)
        self.master.wait_heartbeat()
        print(f"Baglanti basarili! (System: {self.master.target_system})")

    def send_heartbeat(self) -> None:
        self._ensure_connected()
        self.master.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS,
            mavutil.mavlink.MAV_AUTOPILOT_INVALID,
            0, 0, 0,
        )

    def set_mode(self, mode_name: str) -> None:
        self._ensure_connected()
        target_mode = self.MODE_ALIASES.get(mode_name.strip().lower())
        if not target_mode:
            raise ValueError(f"Desteklenmeyen mod: {mode_name}")

        mode_mapping = self.master.mode_mapping()
        if target_mode not in mode_mapping:
            raise ValueError(f"Arac bu modu desteklemiyor: {target_mode}")

        mode_id = mode_mapping[target_mode]
        self.master.mav.set_mode_send(
            self.master.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            mode_id,
        )
        ack = self.master.recv_match(type="COMMAND_ACK", blocking=True, timeout=3)
        print(f"Mod degistirildi: {target_mode} (ACK: {ack})")

    def arm(self) -> None:
        self._ensure_connected()
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            1, 0, 0, 0, 0, 0, 0,
        )
        self.master.motors_armed_wait()
        print("Arac ARM edildi.")

    def disarm(self) -> None:
        self._ensure_connected()
        self.master.mav.command_long_send(
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0,
            0, 0, 0, 0, 0, 0, 0,
        )
        self.master.motors_disarmed_wait()
        print("Arac DISARM edildi.")

    def _ensure_connected(self) -> None:
        if self.master is None:
            raise RuntimeError("Once connect() metodunu cagirmalisin.")


if __name__ == "__main__":
    vehicle = VehicleController("udpin:0.0.0.0:14551")
    vehicle.connect()
    vehicle.send_heartbeat()

    vehicle.set_mode("stabilized")
    time.sleep(2)
    vehicle.set_mode("depthold")
    time.sleep(2)
    vehicle.set_mode("manual")
    time.sleep(2)

    vehicle.arm()
    time.sleep(3)
    vehicle.disarm()
