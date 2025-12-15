# 🚀 Dynotis SDKs (Python & JavaScript)

Dynotis SDKs provide **Python** and **JavaScript (Node.js)** client libraries to control Dynotis dynamometer devices and stream live telemetry from external applications.

✅ Architecture: **Dynotis Desktop (WPF) = gRPC Server**  
✅ SDKs act as **gRPC Clients**  
✅ Default endpoint: `localhost:50051` (HTTP/2)

> ⚠️ **Safety Warning:** Calling `UnlockMotor` + `SetPWM` can spin the motor. Always secure the test rig and follow your lab safety procedures.

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Requirements](#-requirements)
- [Repository Structure](#-repository-structure)
- [Quick Start](#-quick-start)
- [🐍 Python SDK](#-python-sdk)
- [🟨 JavaScript SDK](#-javascript-sdk)
- [🧩 Proto & API Reference](#-proto--api-reference)
- [⚙️ Telemetry Stream Notes](#️-telemetry-stream-notes)
- [🧯 Troubleshooting](#-troubleshooting)
- [🧪 Development & Contribution](#-development--contribution)
- [📄 License](#-license)

---

## 🔎 Overview

The Dynotis Desktop application (WPF) runs an embedded **gRPC server** (Kestrel/HTTP2).  
The SDKs connect to this server to:

- Discover devices (Serial / Wi-Fi)
- Activate/deactivate a device connection
- Control motor PWM (with safety lock)
- Configure limits & equipment parameters
- Stream telemetry at a fixed rate (e.g., 50 Hz)

A key design goal is that the gRPC service **uses the same live singleton services** as the WPF UI (shared runtime state).

---

## ✨ Key Features

✅ Device discovery (`GetDeviceList`)  
✅ Device activation/deactivation  
✅ Motor PWM control (`SetPWM`)  
✅ Safety lock/unlock (`LockMotor` / `UnlockMotor`)  
✅ Emergency stop (`EmergencyStop`)  
✅ Sensor tare (`TareSensor`)  
✅ Limit configuration (`SetLimitSettings`)  
✅ Live telemetry streaming (`GetTelemetryStream`)

---

## 🛠 Requirements

### Server (Dynotis Desktop / WPF)
- Dynotis Desktop app must be running
- gRPC server must be **Online** in the UI footer/status bar
- Default port: `50051` (HTTP/2)

### Python SDK
- Python **3.8+**
- Dependencies: `grpcio`, `grpcio-tools`, `protobuf`

### JavaScript SDK (Node.js)
- Node.js **16+**
- Dependencies: `@grpc/grpc-js`, `google-protobuf`, `grpc-tools`

---

## 📂 Repository Structure

```text
Dynotis_SDKs/
├── Protos/
│   └── DynotisAPI.proto
├── dynotis_javascript_sdk/
│   ├── examples/
│   │   └── full_test_scenario.js
│   ├── generated/
│   ├── build_sdk.js
│   ├── client.js
│   ├── index.js
│   ├── dynotis_generate_javascript_sdk.bat
│   └── package.json
└── dynotis_python_sdk/
    ├── examples/
    │   └── full_test_scenario.py
    ├── generated/
    ├── build_sdk.py
    ├── client.py
    ├── dynotis_generate_python_sdk.bat
    └── requirements.txt
⚡ Quick Start
Start Dynotis Desktop (WPF)

Confirm API Status = Online ✅

Run SDK build scripts (only needed after .proto changes)

Execute an example scenario to verify end-to-end operation

🐍 Python SDK
1) Install Dependencies
bash
Kodu kopyala
cd dynotis_python_sdk
pip install -r requirements.txt
If requirements.txt is missing:

bash
Kodu kopyala
pip install grpcio grpcio-tools protobuf
2) Generate Python gRPC Code
bash
Kodu kopyala
python build_sdk.py
Windows alternative:

bat
Kodu kopyala
dynotis_generate_python_sdk.bat
This process generates code under dynotis_python_sdk/generated/
and applies a common fix for Python relative imports.

3) Run the Demo Scenario
bash
Kodu kopyala
python examples/full_test_scenario.py
4) Minimal Example
python
Kodu kopyala
from client import DynotisClient
from generated import DynotisAPI_pb2

client = DynotisClient("localhost:50051")

devices = client.get_device_list()
if not devices:
    raise SystemExit("No devices found. Is Dynotis Desktop running and API Online?")

dev_id = devices[0].identifier

client.activate_device(dev_id)
client.unlock_motor(dev_id)

client.set_pwm(dev_id, 1200.0)

stream = client.get_telemetry_stream(dev_id)
for data in stream:
    print(f"RPM: {data.sensors.rpm:.0f} | Thrust: {data.sensors.thrust_gf:.1f} g")
5) Limits + Tare Example
python
Kodu kopyala
client.set_limits(dev_id, max_current=40.0, max_temp=80.0)
client.tare_sensor(dev_id, DynotisAPI_pb2.SensorType.SENSOR_THRUST)
🟨 JavaScript SDK
1) Install Dependencies
bash
Kodu kopyala
cd dynotis_javascript_sdk
npm install
2) Generate JS gRPC Code
bash
Kodu kopyala
node build_sdk.js
Windows alternative:

bat
Kodu kopyala
dynotis_generate_javascript_sdk.bat
3) Run the Demo Scenario
bash
Kodu kopyala
node examples/full_test_scenario.js
4) Minimal Example
js
Kodu kopyala
const { DynotisClient } = require("./client");

async function main() {
  const client = new DynotisClient("localhost:50051");

  const list = await client.getDeviceList();
  if (!list.devicesList || list.devicesList.length === 0) {
    throw new Error("No devices found. Is Dynotis Desktop running and API Online?");
  }

  const devId = list.devicesList[0].identifier;

  await client.activateDevice(devId);
  await client.unlockMotor(devId);

  await client.setPWM(devId, 1200);

  const stream = client.getTelemetryStream(devId);
  stream.on("data", (data) => {
    const s = data.getSensors();
    console.log(`RPM=${s.getRpm().toFixed(0)} Thrust=${s.getThrustGf().toFixed(1)}g`);
  });

  stream.on("error", (err) => {
    // gRPC "CANCELLED" is normal when you cancel the stream
    if (err.code !== 1) console.error(err);
  });
}

main().catch(console.error);
🧩 Proto & API Reference
The full contract is defined in:

Protos/DynotisAPI.proto

Service: DynotisController
RPC	Description
GetDeviceList(Empty)	Returns all connected/discovered devices with status
ActivateDevice(DeviceRequest)	Opens communication for a specific device
DeactivateDevice(DeviceRequest)	Closes communication for a device
SetPWM(PwmRequest)	Sends PWM value to ESC (typically 800–2200 µs)
LockMotor(DeviceRequest)	Software-locks the motor
UnlockMotor(DeviceRequest)	Unlocks motor for PWM control
EmergencyStop(DeviceRequest)	Immediately stops motor, locks, logs event
SetEquipmentParameters(EquipmentParametersRequest)	Sets prop diameter, motor resistance, etc.
SetLimitSettings(LimitSettingsRequest)	Enables/configures safety limits
TareSensor(TareRequest)	Tares thrust/torque/current/accelerometer
GetTelemetryStream(DeviceRequest)	Server-side streaming telemetry
StartLogging(LogRequest)	Starts logging (currently requires DI wiring)
StopLogging(DeviceRequest)	Stops logging (currently requires DI wiring)

🧩 Note: StartLogging/StopLogging currently return a message indicating that DataLoggerManager must be registered in the DI container (singleton) to support logging through the API.

⚙️ Telemetry Stream Notes
Server example rate: 50 Hz (PeriodicTimer(20ms))

Stream message includes:

sensors: thrust/torque/voltage/current/rpm/temps/accel/wind

theoretical: power, efficiencies, FOM, coefficients, etc.

environment: ambient temperature, pressure

Expected behavior:

If the client cancels the stream, the server typically catches an OperationCanceledException (normal)

🧯 Troubleshooting
❌ UNAVAILABLE: failed to connect to all addresses
✅ Checklist:

Dynotis Desktop running?

UI shows API Online?

Correct endpoint/port (localhost:50051)?

Firewall blocking 50051?

❌ HTTP/2 / protocol errors
gRPC requires HTTP/2

Server must listen with HttpProtocols.Http2 (Kestrel)

❌ Python ImportError in generated code
Run:

bash
Kodu kopyala
python build_sdk.py
Ensure generated/__init__.py exists

The build script applies a common fix:
import DynotisAPI_pb2 → from . import DynotisAPI_pb2

❌ JS Cannot find module ./generated/...
Run:

bash
Kodu kopyala
npm install
node build_sdk.js
Confirm generated/ exists

⚠️ Device list works, telemetry is always zero
Ensure the device is activated

Ensure the device is actually streaming sensor data in its current mode

Try: Activate → wait ~1s → start stream

🧪 Development & Contribution
When .proto changes
Update Protos/DynotisAPI.proto

Regenerate SDK code:

Python

bash
Kodu kopyala
cd dynotis_python_sdk
python build_sdk.py
JavaScript

bash
Kodu kopyala
cd dynotis_javascript_sdk
node build_sdk.js
Branch naming suggestion
feature/<name>

fix/<name>

chore/<name>

Notes on logging support
To enable StartLogging/StopLogging through the API:

Move DataLoggerManager into the DI container

Register as a singleton

Inject into DynotisAPIService

(Optional) ✅ C# gRPC Client Example
Even though this repo ships Python/JS SDKs, here’s a minimal C# example for quick testing.

csharp
Kodu kopyala
using System;
using System.Threading.Tasks;
using Grpc.Net.Client;
using Dynotis.API.Protos;

class Program
{
    static async Task Main()
    {
        using var channel = GrpcChannel.ForAddress("http://localhost:50051");
        var client = new DynotisController.DynotisControllerClient(channel);

        var list = await client.GetDeviceListAsync(new Empty());
        if (list.Devices.Count == 0)
        {
            Console.WriteLine("No devices found.");
            return;
        }

        var devId = list.Devices[0].Identifier;

        await client.ActivateDeviceAsync(new DeviceRequest { DeviceIdentifier = devId });
        await client.UnlockMotorAsync(new DeviceRequest { DeviceIdentifier = devId });
        await client.SetPWMAsync(new PwmRequest { DeviceIdentifier = devId, PwmValue = 1200 });

        using var call = client.GetTelemetryStream(new DeviceRequest { DeviceIdentifier = devId });
        await foreach (var msg in call.ResponseStream.ReadAllAsync())
        {
            Console.WriteLine($"RPM={msg.Sensors.Rpm:0} Thrust={msg.Sensors.ThrustGf:0.0}g");
        }
    }
}
📄 License
TBD (e.g., MIT / Proprietary).
Add a LICENSE file and update this section accordingly.

🧾 Support
Please open a GitHub Issue with:

OS + Dynotis Desktop version

SDK version / commit hash

Steps to reproduce

Logs / error output

Dynotis Technology © 2025

Kodu kopyala

