const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

// Proto dosyasının tam yolunu bul
const PROTO_PATH = path.resolve(__dirname, '../Protos/DynotisAPI.proto');

// Proto dosyasını yükle
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
});

const dynotisProto = grpc.loadPackageDefinition(packageDefinition).dynotis;

class DynotisClient {
    constructor(address = 'localhost:50051') {
        this.client = new dynotisProto.DynotisController(
            address,
            grpc.credentials.createInsecure()
        );
        this.heartbeatTimer = null;
    }

    // --- WATCHDOG / HEARTBEAT ---
    _startHeartbeat(deviceId) {
        if (this.heartbeatTimer) return;
        this.heartbeatTimer = setInterval(() => {
            this.client.SendHeartbeat({ device_identifier: deviceId }, (err) => {
                if (err) console.error("Heartbeat failed:", err.message);
            });
        }, 400);
    }

    _stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    // --- METOTLAR ---
    async getDeviceList() {
        return new Promise((resolve, reject) => {
            this.client.GetDeviceList({}, (err, response) => {
                if (err) reject(err); else resolve(response);
            });
        });
    }

    async activateDevice(deviceId) {
        return new Promise((resolve, reject) => {
            this.client.ActivateDevice({ device_identifier: deviceId }, (err, response) => {
                if (err) reject(err); else resolve(response);
            });
        });
    }

    async setPWM(deviceId, pwmValue) {
        if (pwmValue > 1050) this._startHeartbeat(deviceId);
        else this._stopHeartbeat();

        return new Promise((resolve, reject) => {
            this.client.SetPWM({ device_identifier: deviceId, pwm_value: pwmValue }, (err, response) => {
                if (err) reject(err); else resolve(response);
            });
        });
    }

    async unlockMotor(deviceId) {
        return new Promise((resolve, reject) => {
            this.client.UnlockMotor({ device_identifier: deviceId }, (err, response) => {
                if (err) reject(err); else resolve(response);
            });
        });
    }

    async lockMotor(deviceId) {
        this._stopHeartbeat();
        return new Promise((resolve, reject) => {
            this.client.LockMotor({ device_identifier: deviceId }, (err, response) => {
                if (err) reject(err); else resolve(response);
            });
        });
    }

    async tareSensor(deviceId, sensorType) {
        return new Promise((resolve, reject) => {
            this.client.TareSensor({ device_identifier: deviceId, sensor_type: sensorType }, (err, response) => {
                if (err) reject(err); else resolve(response);
            });
        });
    }

    getTelemetryStream(deviceId) {
        return this.client.GetTelemetryStream({ device_identifier: deviceId });
    }

    close() {
        this._stopHeartbeat();
        this.client.close();
    }
}

module.exports = { DynotisClient };
