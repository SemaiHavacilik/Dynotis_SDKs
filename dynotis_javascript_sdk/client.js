const grpc = require('@grpc/grpc-js');
const messages = require('./generated/DynotisAPI_pb');
const services = require('./generated/DynotisAPI_grpc_pb');

class DynotisClient {
    constructor(address = 'localhost:50051') {
        this.client = new services.DynotisControllerClient(
            address,
            grpc.credentials.createInsecure()
        );
    }

    _promisify(method, request) {
        return new Promise((resolve, reject) => {
            this.client[method](request, (err, response) => {
                if (err) reject(err);
                else resolve(response.toObject());
            });
        });
    }

    // --- CONNECTION ---
    async getDeviceList() {
        return this._promisify('getDeviceList', new messages.Empty());
    }

    async activateDevice(deviceId) {
        const req = new messages.DeviceRequest();
        req.setDeviceIdentifier(deviceId);
        return this._promisify('activateDevice', req);
    }

    async deactivateDevice(deviceId) {
        const req = new messages.DeviceRequest();
        req.setDeviceIdentifier(deviceId);
        return this._promisify('deactivateDevice', req);
    }

    // --- MOTOR CONTROL ---
    async setPWM(deviceId, pwmValue) {
        const req = new messages.PwmRequest();
        req.setDeviceIdentifier(deviceId);
        req.setPwmValue(pwmValue);
        return this._promisify('setPWM', req);
    }

    async lockMotor(deviceId) {
        const req = new messages.DeviceRequest();
        req.setDeviceIdentifier(deviceId);
        return this._promisify('lockMotor', req);
    }

    async unlockMotor(deviceId) {
        const req = new messages.DeviceRequest();
        req.setDeviceIdentifier(deviceId);
        return this._promisify('unlockMotor', req);
    }

    async emergencyStop(deviceId) {
        const req = new messages.DeviceRequest();
        req.setDeviceIdentifier(deviceId);
        return this._promisify('emergencyStop', req);
    }

    // --- SETTINGS ---
    async setLimits(deviceId, { maxCurrent, maxRpm, maxTemp } = {}) {
        const settings = new messages.LimitSettings();
        settings.setIsEnabled(true);

        if (maxCurrent !== undefined) {
            settings.setEnableMaxCurrent(true);
            settings.setMaxCurrentA(maxCurrent);
        }
        if (maxRpm !== undefined) {
            settings.setEnableMaxRpm(true);
            settings.setMaxRpm(maxRpm);
        }
        if (maxTemp !== undefined) {
            settings.setEnableMaxMotorTemp(true);
            settings.setMaxMotorTempC(maxTemp);
        }

        const req = new messages.LimitSettingsRequest();
        req.setDeviceIdentifier(deviceId);
        req.setSettings(settings);

        return this._promisify('setLimitSettings', req);
    }

    // --- OPERATIONS ---
    async tareSensor(deviceId, sensorTypeEnum) {
        const req = new messages.TareRequest();
        req.setDeviceIdentifier(deviceId);
        req.setSensorType(sensorTypeEnum);
        return this._promisify('tareSensor', req);
    }

    // --- TELEMETRY ---
    getTelemetryStream(deviceId) {
        const req = new messages.DeviceRequest();
        req.setDeviceIdentifier(deviceId);
        return this.client.getTelemetryStream(req);
    }

    close() {
        this.client.close();
    }
}

module.exports = { DynotisClient, messages };
