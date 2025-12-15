# -*- coding: utf-8 -*-
import grpc
# We use a try-except block to handle imports whether run directly or as a library
try:
    from .generated import DynotisAPI_pb2, DynotisAPI_pb2_grpc
except ImportError:
    from generated import DynotisAPI_pb2, DynotisAPI_pb2_grpc

class DynotisClient:
    def __init__(self, target='localhost:50051'):
        """Initializes the Dynotis API client."""
        self.channel = grpc.insecure_channel(target)
        self.stub = DynotisAPI_pb2_grpc.DynotisControllerStub(self.channel)

    # --- CONNECTION & DISCOVERY ---
    def get_device_list(self):
        """Retrieves the list of connected devices."""
        return self.stub.GetDeviceList(DynotisAPI_pb2.Empty()).devices

    def activate_device(self, device_id):
        """Activates the specified device."""
        return self.stub.ActivateDevice(DynotisAPI_pb2.DeviceRequest(device_identifier=device_id))

    def deactivate_device(self, device_id):
        """Deactivates the specified device."""
        return self.stub.DeactivateDevice(DynotisAPI_pb2.DeviceRequest(device_identifier=device_id))

    # --- MOTOR CONTROL ---
    def set_pwm(self, device_id, pwm_value):
        """Sets the PWM value for the motor."""
        req = DynotisAPI_pb2.PwmRequest(device_identifier=device_id, pwm_value=pwm_value)
        return self.stub.SetPWM(req)

    def lock_motor(self, device_id):
        """Locks the motor (Safety)."""
        return self.stub.LockMotor(DynotisAPI_pb2.DeviceRequest(device_identifier=device_id))

    def unlock_motor(self, device_id):
        """Unlocks the motor."""
        return self.stub.UnlockMotor(DynotisAPI_pb2.DeviceRequest(device_identifier=device_id))

    def emergency_stop(self, device_id):
        """Triggers an emergency stop."""
        return self.stub.EmergencyStop(DynotisAPI_pb2.DeviceRequest(device_identifier=device_id))

    # --- SETTINGS ---
    def set_limits(self, device_id, max_current=None, max_rpm=None, max_temp=None):
        """Configures safety limit settings."""
        settings = DynotisAPI_pb2.LimitSettings(is_enabled=True)
        
        if max_current:
            settings.enable_max_current = True
            settings.max_current_a = max_current
        
        if max_rpm:
            settings.enable_max_rpm = True
            settings.max_rpm = max_rpm

        if max_temp:
            settings.enable_max_motor_temp = True
            settings.max_motor_temp_c = max_temp

        req = DynotisAPI_pb2.LimitSettingsRequest(device_identifier=device_id, settings=settings)
        return self.stub.SetLimitSettings(req)

    # --- OPERATIONS ---
    def tare_sensor(self, device_id, sensor_type_enum):
        """
        Tares (zeros) a specific sensor.
        sensor_type_enum: DynotisAPI_pb2.SensorType.SENSOR_THRUST etc.
        """
        req = DynotisAPI_pb2.TareRequest(device_identifier=device_id, sensor_type=sensor_type_enum)
        return self.stub.TareSensor(req)

    # --- TELEMETRY ---
    def get_telemetry_stream(self, device_id):
        """Starts the telemetry data stream."""
        req = DynotisAPI_pb2.DeviceRequest(device_identifier=device_id)
        return self.stub.GetTelemetryStream(req)

    def close(self):
        """Closes the connection."""
        self.channel.close()

