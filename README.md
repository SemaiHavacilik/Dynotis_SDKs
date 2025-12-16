<div align="center">
  
<img src="https://dynotis.semai.com.tr/wp-content/uploads/2024/04/IMG_8400-scaled.jpg" align="left" width="200" style="margin-right: 20px; margin-top: 20px;" alt="Dynotis Left Setup" />

<img src="https://dynotis.semai.com.tr/wp-content/uploads/2024/04/IMG_8427-scaled.jpg" align="right" width="200" style="margin-left: 20px; margin-top: 10px;" alt="Dynotis Right Setup" />

<p align="center">
  <img src="https://dynotis.semai.com.tr/wp-content/uploads/2024/03/dynotis_logo.svg"
       alt="Dynotis"
       width="240" />
</p>

# Dynotis SDKs 

<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.herokuapp.com/?font=Fira+Code&pause=1000&color=2196F3&center=true&vCenter=true&width=435&lines=Python+%26+JavaScript+Control;Advanced+Telemetry+Stream" alt="Typing SVG" />
</a>

**Control Dynotis devices and stream live telemetry from your external applications.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-16%2B-green?logo=node.js&logoColor=white)](https://nodejs.org/)
[![gRPC](https://img.shields.io/badge/Protocol-gRPC-red?logo=google-cloud&logoColor=white)](https://grpc.io/)

</div>

---

## 📖 Overview

The **Dynotis Desktop application** hosts an embedded **gRPC server** (HTTP/2).  
These SDKs connect to that server to:

- Discover devices (Serial / Wi-Fi)
- Activate/deactivate a device connection
- Control motor PWM (with software safety lock)
- Configure limits & equipment parameters
- Stream telemetry at a fixed rate (e.g., 1000 Hz)

💡 **Important design detail:** The gRPC server injects **existing singleton services** from the UI app (shared RAM/state), meaning the UI and API work on the same live device objects.

---

### ✅ Architecture
*   **Architecture:** Dynotis Desktop runs as a **gRPC Server** (Kestrel / HTTP2)  
*   **Client:** SDKs act as gRPC Clients.
*   **Endpoint:** Default is `localhost:50051` (HTTP/2).

> ⚠️ **SAFETY WARNING**
>
> Calling `UnlockMotor` + `SetPWM` **can spin the motor**.
> Always secure the test rig and follow your lab safety procedures before running any code.

---

## 📌 Table of Contents

- [📖 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🧠 How It Works](#-how-it-works)
- [🛠 Requirements](#-requirements)
- [📂 Repository Structure](#-repository-structure)
- [⚡ Quick Start SDK](#-quick-start-sdk)
- [🐍 Python SDK](#-python-sdk)
- [🟨 JavaScript SDK](#-javascript-sdk)
- [🧩 Proto & API Reference](#-proto--api-reference)
- [⚙️ Telemetry Stream Notes](#️-telemetry-stream-notes)
- [🧯 Troubleshooting](#-troubleshooting)
- [🧪 Development & Contribution](#-development--contribution)
- [📄 License](#-license)

---

## ✨ Key Features

| Category | What you can do | Main Methods |
| :--- | :--- | :--- |
| 🔍 **Discovery** | Connected devices are found automatically and listed with statuses. | `GetDeviceList` |
| 🔌 **Session** | Open/close the communication channel to a specific device. | `ActivateDevice`, `DeactivateDevice` |
| 🎮 **Control** | Drive the ESC with microsecond PWM commands (controlled & explicit). | `SetPWM` |
| 🔒 **Safety** | Prevent accidental spin-up, unlock intentionally, or stop immediately. | `LockMotor`, `UnlockMotor`, `EmergencyStop` |
| ⚖️ **Calibration** | Zero (tare) sensors for reliable measurements before tests. | `TareSensor` |
| ⚙️ **Limits & Protection** | Configure safety limits (current/temp/RPM/etc.) and enforce them during operation. | `SetLimitSettings` |
| 📡 **Telemetry** | Stream live data (Thrust, Torque, RPM, Voltage, Current, Temps, etc.). | `GetTelemetryStream` |

---

## 🧠 How It Works

### Server Side (Dynotis Desktop)

- Uses **Kestrel** configured for **HTTP/2** (required for gRPC)
- Maps the gRPC service `DynotisAPIService`
- Injects live services like:
  - `IDevicesManager`
  - `ILogService`
  - `IBalancerService`
  - `IAnalysisDashboardManager`

### Client Side (SDKs)

- Python and Node.js clients call gRPC methods defined in:
  - `Protos/DynotisAPI.proto`
- Generated code lives under:
  - `dynotis_python_sdk/generated/`
  - `dynotis_javascript_sdk/generated/`

---

## 🛠 Requirements

### ✅ Server (Dynotis Desktop)
- **Dynotis Desktop app must be running**
- gRPC server must be **Online** in the UI (status/footer)
- Default port: `50051` (HTTP/2)

### 🐍 Python SDK
- Python **3.8+**
- Dependencies:
  - `grpcio`
  - `grpcio-tools`
  - `protobuf`

### 🟨 JavaScript SDK (Node.js)
- Node.js **16+**
- Dependencies:
  - `@grpc/grpc-js`
  - `google-protobuf`
  - `grpc-tools`

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
│   └── dynotis_generate_javascript_sdk.bat
└── dynotis_python_sdk/
    ├── examples/
    │   └── full_test_scenario.py
    ├── generated/
    ├── build_sdk.py
    ├── client.py
    └── dynotis_generate_python_sdk.bat
```

### ⚡ Quick Start SDK
*   Start Dynotis Desktop.
*   Confirm API Status is Online ✅.
*   Run SDK build scripts (only needed if .proto changed)
*   Run an example test scenario to validate end-to-end communication

## 🐍 Python SDK

### Install Python
```text
cd dynotis_python_sdk

# If you have requirements.txt
pip install -r requirements.txt

# If not:
pip install grpcio grpcio-tools protobuf

```
### Generate Python SDK (from .proto)
```text
cd dynotis_python_sdk
python build_sdk.py
```
### Windows alternative:
```text
dynotis_generate_python_sdk.bat
```

✅ This generates files under dynotis_python_sdk/generated/

✅ It also fixes the common relative-import issue in DynotisAPI_pb2_grpc.py.

### Run Python Demo Scenario
```text
cd dynotis_python_sdk
python examples/full_test_scenario.py
```

### Minimal Python Usage Example
```python
from client import DynotisClient
from generated import DynotisAPI_pb2

client = DynotisClient("localhost:50051")

devices = client.get_device_list()
if not devices:
    raise SystemExit("No devices found. Is Dynotis Desktop running and API Online?")

dev_id = devices[0].identifier

# Activate + unlock
client.activate_device(dev_id)
client.unlock_motor(dev_id)

# Optional: set safety limits + tare thrust
client.set_limits(dev_id, max_current=40.0, max_temp=80.0)
client.tare_sensor(dev_id, DynotisAPI_pb2.SensorType.SENSOR_THRUST)

# Send PWM
client.set_pwm(dev_id, 1200.0)

# Telemetry stream
stream = client.get_telemetry_stream(dev_id)
for msg in stream:
    print(f"RPM={msg.sensors.rpm:6.0f} | Thrust={msg.sensors.thrust_gf:8.1f} g", end="\r")

```

## 🟨 JavaScript SDK (Node.js)

### Install JavaScript
```text
cd dynotis_javascript_sdk
npm install
```
### Generate JavaScript SDK (from .proto)
```text
cd dynotis_javascript_sdk
node build_sdk.js
```
### Windows alternative:
```text
dynotis_generate_javascript_sdk.bat
```
### Run JavaScript Demo Scenario
```text
cd dynotis_javascript_sdk
node examples/full_test_scenario.js
```
### Minimal JavaScript Usage Example
```javascript
const { DynotisClient, messages } = require("./client");

async function main() {
  const client = new DynotisClient("localhost:50051");

  const list = await client.getDeviceList();
  if (!list.devicesList || list.devicesList.length === 0) {
    throw new Error("No devices found. Is Dynotis Desktop running and API Online?");
  }

  const devId = list.devicesList[0].identifier;

  await client.activateDevice(devId);
  await client.setLimits(devId, { maxCurrent: 40.0, maxTemp: 80.0 });
  await client.tareSensor(devId, messages.SensorType.SENSOR_THRUST);

  await client.unlockMotor(devId);
  await client.setPWM(devId, 1200);

  const stream = client.getTelemetryStream(devId);

  stream.on("data", (msg) => {
    const s = msg.getSensors();
    process.stdout.write(
      `RPM=${s.getRpm().toFixed(0).padStart(6)} | ` +
      `Thrust=${s.getThrustGf().toFixed(1).padStart(8)} g | ` +
      `Current=${s.getCurrentA().toFixed(1).padStart(5)} A\r`
    );
  });

  stream.on("error", (err) => {
    // gRPC CANCELLED is normal when client cancels stream
    if (err.code !== 1) console.error("\nStream Error:", err);
  });

  // stop after 10 seconds (demo)
  setTimeout(async () => {
    stream.cancel();

    await client.setPWM(devId, 1000);
    await client.lockMotor(devId);
    await client.deactivateDevice(devId);

    client.close();
    console.log("\nDone.");
  }, 10_000);
}

main().catch(console.error);
```

## 🧩 Proto & API Reference

The full gRPC contract is defined in:

- **Proto file:** `Protos/DynotisAPI.proto`
- **Service:** `DynotisController`

| RPC Method | Description |
| :--- | :--- |
| `GetDeviceList` | Returns all connected/discovered devices with status. |
| `ActivateDevice` | Opens communication for a specific device. |
| `DeactivateDevice` | Closes communication for a device. |
| `SetPWM` | Sends PWM value to ESC (typically 800–2200 µs). |
| `LockMotor` | Software-locks the motor (prevents spin). |
| `UnlockMotor` | Unlocks motor for PWM control. |
| `EmergencyStop` | Immediately stops motor, locks it, and logs event. |
| `SetEquipmentParameters` | Sets prop diameter, motor resistance, etc. |
| `SetLimitSettings` | Enables/configures safety limits (Max Current/Temp). |
| `TareSensor` | Tares thrust, torque, current, or accelerometer. |
| `GetTelemetryStream` | Server-side streaming telemetry (50Hz default). |
| `StartLogging` | Starts logging (Requires DI wiring on server). |
| `StopLogging` | Stops logging (Requires DI wiring on server). |

> **🧩 Logging Note:** StartLogging/StopLogging currently require DataLoggerManager to be registered in the DI container as a **singleton** and injected into DynotisAPIService.

## ⚙️ Telemetry Stream Notes

 * Typical stream rate: 1000 Hz (PeriodicTimer(1ms))
 * Stream message includes:
   - sensors: thrust/torque/voltage/current/rpm/temps/accel/wind
   - theoretical: power, efficiencies, FOM, coefficients, etc.
   - environment: ambient temperature, pressure

✅ Expected behavior:
 * If the client cancels the stream, server may throw OperationCanceledException (*normal*).

## 🧯 Troubleshooting

❌ UNAVAILABLE: failed to connect to all addresses
✅ Checklist:
* Dynotis Desktop running?
* UI shows **API Online?**
* Correct endpoint: localhost:50051
* Firewall blocking port 50051?

❌ **HTTP/2 / protocol errors**
* gRPC requires HTTP/2
* Server must listen with HttpProtocols.Http2 (Kestrel)

❌ **Python**: *ImportError* **in generated code**

### Run:
```text
cd dynotis_python_sdk
python build_sdk.py
```
### Ensure:
 * generated/__init__.py exists
 * DynotisAPI_pb2_grpc.py contains: from . import DynotisAPI_pb2

❌ **JavaScript:** Cannot find module ./generated/...

### Run:
```text
cd dynotis_javascript_sdk
npm install
node build_sdk.js
```
### Confirm:
 * *generated/* folder exists and contains **_pb.js* files

**⚠️ Device list works but telemetry is always zero**
 * Ensure device is **activated**
 * Ensure the device is streaming sensor data in current mode
 * Try: Activate → wait ~1s → start stream

## 🧪 Development & Contribution

**When** .proto **changes**

 **1**.Update Protos/DynotisAPI.proto
 
 **2**.Regenerate SDKs:

 ### Python:
```text
cd dynotis_python_sdk
python build_sdk.py
```
 ### JavaScript:
```text
cd dynotis_javascript_sdk
node build_sdk.js
```
 ### Branch naming:
 * feature/<name>

 * fix/<name>

 * chore/<name>

 ### Logging (API support):
To support *StartLogging/StopLogging*:

 * Register *DataLoggerManager* in DI (*AddSingleton*)

 * Inject into *DynotisAPIService*

## ✅ Optional: C# gRPC Client Example

```csharp
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
```

<div align="center">

### Semai Aviation R&D Advanced Engineering © 2025

</div>
