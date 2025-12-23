# -*- coding: utf-8 -*-
import grpc
import threading
import time
import logging
from typing import List, Generator

try:
    from .generated import DynotisAPI_pb2, DynotisAPI_pb2_grpc
except ImportError:
    from generated import DynotisAPI_pb2, DynotisAPI_pb2_grpc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DynotisClient:
    def __init__(self, target: str = 'localhost:50051'):
        self.channel = grpc.insecure_channel(target)
        self.stub = DynotisAPI_pb2_grpc.DynotisControllerStub(self.channel)
        self._heartbeat_thread = None
        self._stop_heartbeat = threading.Event()

    def _heartbeat_worker(self, device_id: str):
        while not self._stop_heartbeat.is_set():
            try:
                self.stub.SendHeartbeat(DynotisAPI_pb2.HeartbeatRequest(device_identifier=device_id))
                time.sleep(0.5)
            except: break

    def get_device_list(self) -> List:
        try: return self.stub.GetDeviceList(DynotisAPI_pb2.Empty()).devices
        except: return []

    def activate_device(self, device_id: str):
        return self.stub.ActivateDevice(DynotisAPI_pb2.DeviceRequest(device_identifier=device_id))

    def deactivate_device(self, device_id: str):
        self._stop_heartbeat.set()
        return self.stub.DeactivateDevice(DynotisAPI_pb2.DeviceRequest(device_identifier=device_id))

    def set_pwm(self, device_id: str, pwm_value: float):
        if pwm_value > 1050 and (not self._heartbeat_thread or not self._heartbeat_thread.is_alive()):
            self._stop_heartbeat.clear()
            self._heartbeat_thread = threading.Thread(target=self._heartbeat_worker, args=(device_id,), daemon=True)
            self._heartbeat_thread.start()
        return self.stub.SetPWM(DynotisAPI_pb2.PwmRequest(device_identifier=device_id, pwm_value=pwm_value))

    def lock_motor(self, device_id: str):
        self._stop_heartbeat.set()
        return self.stub.LockMotor(DynotisAPI_pb2.DeviceRequest(device_identifier=device_id))

    def unlock_motor(self, device_id: str):
        return self.stub.UnlockMotor(DynotisAPI_pb2.DeviceRequest(device_identifier=device_id))

    def emergency_stop(self, device_id: str):
        self._stop_heartbeat.set()
        return self.stub.EmergencyStop(DynotisAPI_pb2.DeviceRequest(device_identifier=device_id))

    def tare_sensor(self, device_id: str, sensor_type_enum):
        req = DynotisAPI_pb2.TareRequest(device_identifier=device_id, sensor_type=sensor_type_enum)
        return self.stub.TareSensor(req)

    def set_limits(self, device_id: str, **kwargs):
        settings = DynotisAPI_pb2.LimitSettings(is_enabled=True)
        for key, value in kwargs.items():
            if hasattr(settings, key): setattr(settings, key, value)
        return self.stub.SetLimitSettings(DynotisAPI_pb2.LimitSettingsRequest(device_identifier=device_id, settings=settings))

    def set_equipment(self, device_id: str, diameter: float, resistance: float, no_load_current: float):
        params = DynotisAPI_pb2.EquipmentParameters(propeller_diameter_inch=diameter, motor_resistance_mohm=resistance, no_load_current_a=no_load_current)
        return self.stub.SetEquipmentParameters(DynotisAPI_pb2.EquipmentParametersRequest(device_identifier=device_id, parameters=params))

    def get_telemetry_stream(self, device_id: str) -> Generator:
        return self.stub.GetTelemetryStream(DynotisAPI_pb2.DeviceRequest(device_identifier=device_id))

    def start_logging(self, device_id: str, session_name: str, hz: int = 50, notes: str = ""):
        req = DynotisAPI_pb2.LogRequest(device_identifier=device_id, session_name=session_name, sampling_rate_hz=hz, test_notes=notes)
        return self.stub.StartLogging(req)

    def stop_logging(self, device_id: str):
        return self.stub.StopLogging(DynotisAPI_pb2.DeviceRequest(device_identifier=device_id))

    def close(self):
        self._stop_heartbeat.set()
        self.channel.close()
