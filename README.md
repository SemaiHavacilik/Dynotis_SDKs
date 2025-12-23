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

### ✅ System Architecture & Performance

**High-Performance Embedded gRPC Server**  
Unlike traditional test stands that rely on slow serial polling, Dynotis runs an embedded **ASP.NET Core Kestrel** server directly within the application process.

*   **Zero-Latency State Synchronization:** The API injects the exact same Singleton services (`IDevicesManager`, `IBalancerService`) used by the WPF UI. A command sent via Python instantly updates the UI gauges.
*   **HTTP/2 & Protobuf:** We utilize **HTTP/2** for multiplexing and **Protobuf** for compact binary serialization, ensuring minimal network overhead even at high telemetry rates (50Hz+).
*   **Thread-Safe Operations:** All hardware commands are marshaled through thread-safe managers, preventing race conditions between manual UI control and automated API scripts.

### 📡 Connection Modes & Shared State

The Dynotis API operates on the **same memory space (Shared State)** as the desktop application. This means any change made via the API (e.g., `SetPWM`) instantly updates the UI gauges and vice versa.

#### 1. Local Connection (Default)
If your script and Dynotis Desktop are running on the same computer, use the default endpoint:
*   **Endpoint:** `localhost:50051`

#### 2. Network & Remote Lab Setup (Isolated Test Cell)

Dynotis is designed for modern engineering labs where the test stand and the operator might be in different rooms.

*   **PC A (Test Cell):** Runs Dynotis Desktop connected to the hardware via USB.
    *   *Configuration:* Ensure Windows Firewall allows inbound TCP traffic on port `50051`.
*   **PC B (Control Room):** Runs your Python/MATLAB/Node.js script.
    *   *Connection:* `client = DynotisClient("192.168.1.50:50051")`

> This setup protects the operator from noise and physical hazards while maintaining real-time control and data acquisition.

> ⚠️ **SAFETY WARNING**
>
> Calling `UnlockMotor` + `SetPWM` **can spin the motor**.
> Always secure the test rig and follow your lab safety procedures before running any code.

## ⚠️ Safety First

**Please read the following rules carefully before running any code:**

1.  **Propeller-less Testing:** When developing a new script or testing the API for the first time, **never have a propeller installed** on the motor. Only install the propeller once you are 100% confident in your script's logic and limits.
2.  **Hardware Lock:** The moment the `UnlockMotor` command is sent, the motor is live and ready to spin. Ensure physical safety measures (safety cage, protective eyewear) are in place.
3.  **Emergency Stop:**
    *   **Software:** The `client.EmergencyStop(device_request)` command immediately cuts power (PWM Min) and software-locks the motor (`IsLocked = true`).
    *   **Physical:** Always have a physical Emergency Stop (E-Stop) button on your test rig in case of software freezes or network latency.

### 🛡️ Hardware Protection Systems
Dynotis enforces strict software-level safety interlocks to prevent accidents:

1.  **Software Interlock (Motor Lock):** The API initializes with the motor in a `LOCKED` state. You must explicitly call `UnlockMotor()` before `SetPWM()` commands will be honored.
2.  **Keep-Alive Monitoring:** If the telemetry stream or client connection drops, the system automatically cuts power (PWM Min) to prevent runaway scenarios.
3.  **Emergency Stop (E-Stop):** The `EmergencyStop` RPC is a high-priority interrupt that immediately sets PWM to 0, engages the lock, and logs the event with a high-severity flag.

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

## 🛠️ SDK Generation & Integration (Any Language)

Dynotis is language-agnostic. While we provide examples for Python and Node.js, you can generate a client for **C++, C#, Go, Java, or Rust** using the standard Protobuf compiler.

**Python Generation:**
```bash
python -m grpc_tools.protoc -I./Protos --python_out=./Client --grpc_python_out=./Client ./Protos/DynotisAPI.proto
```

**Node.js Generation:**
```bash
grpc_tools_node_protoc --js_out=import_style=commonjs,binary:./Client --grpc_out=./Client --plugin=protoc-gen-grpc=`which grpc_tools_node_protoc_plugin` ./Protos/DynotisAPI.proto
```

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

## ⚙️ Real-Time Physics & Telemetry Engine

Dynotis doesn't just stream raw sensor voltages. It includes an integrated **physics engine** that computes aerodynamic and electrical metrics on-the-fly, saving you from post-processing large datasets.

**Streamed Metrics (50Hz Default):**
*   **Raw Sensors:** Thrust (gf), Torque (Nmm), Voltage (V), Current (A), RPM, Vibration (g).
*   **Aerodynamics:** Propeller Efficiency ($\eta_{prop}$), Advance Ratio ($J$), Tip Speed (Mach), Air Density ($\rho$).
*   **Electrical:** Motor Efficiency, System Efficiency (g/W), Electrical Power vs. Mechanical Power.
*   **Environment:** Ambient Temp, Pressure, Wind Speed/Direction.

> *Data is streamed via server-side gRPC streaming, ensuring time-aligned snapshots of all sensors.*

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

| Error Message / Issue | Possible Cause | Solution |
| :--- | :--- | :--- |
| **RPC Exception: Unavailable** | Dynotis Desktop is closed or Port is blocked. | Ensure the app is running. Allow port `50051` in Windows Firewall. |
| **Stream Error (HTTP/2)** | Proxy or VPN usage. | gRPC requires HTTP/2. Disable VPN or add an exception for `localhost`. |
| **Device Not Found** | Wrong COM port or device inactive. | Verify Device ID via `GetDeviceList` and ensure `ActivateDevice` is called. |
| **Logging Error** | Service injection failure. | Ensure `DataLoggerManager` is registered as a Singleton in `App.xaml.cs`. |

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

## 💡 Common Usage Scenarios

### Scenario 1: Ramp Up Test
Safely start the motor and gradually increase RPM within a specific PWM range.

```python
import time
# ... client initialization ...

dev_id = "COM3" # Your Device ID

# 1. Safety & Preparation
client.activate_device(dev_id)
client.set_limits(dev_id, max_current=40.0, max_temp=80.0) # Set safety limits
client.tare_sensor(dev_id, SensorType.SENSOR_THRUST)       # Zero the thrust sensor

# 2. Start Motor
client.unlock_motor(dev_id)
print("Motor Unlocked. Starting Test...")

# 3. Ramp (1100 -> 1500 PWM)
try:
    for pwm in range(1100, 1501, 50):
        client.set_pwm(dev_id, float(pwm))
        print(f"PWM set to: {pwm}")
        time.sleep(1.0) # Wait 1 second per step
finally:
    # 4. Safe Stop (Executes even if an error occurs)
    client.set_pwm(dev_id, 1000.0) # Min PWM
    client.lock_motor(dev_id)
    print("Test Finished. Motor Locked.")
```

## 🤖 Coding with AI Assistant

You can use ChatGPT, Claude, or GitHub Copilot to write Dynotis scripts quickly. Use the following prompt template to get accurate results:

**Copy-Paste Prompt:**

> "I am using the Dynotis gRPC API (Protobuf) for a drone motor test stand.
> The client has methods like `SetPWM(device_id, value)`, `GetTelemetryStream(device_id)`, and `TareSensor(device_id, sensor_type)`.
> The telemetry object has fields: `sensors.thrust_gf`, `sensors.torque_nmm`, `sensors.current_a`, `sensors.rpm`.
>
> Please write a Python script that:
> 1. Connects to 'localhost:50051'.
> 2. Activates the device named 'COM3'.
> 3. Tares the Thrust and Torque sensors.
> 4. Runs a step test: 1200 PWM for 5 seconds, then 1500 PWM for 5 seconds.
> 5. Prints the average Thrust and Efficiency (g/W) for each step.
> 6. Safely stops the motor at the end."


<div align="center">

### Semai Aviation R&D Advanced Engineering © 2025

</div>
