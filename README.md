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

The **Dynotis Desktop application** hosts an embedded **gRPC server** (HTTP/2). By leveraging these SDKs, you can automate complex test sequences, integrate Dynotis into your own lab software, and process real-time physics data externally.

These SDKs connect to that server to:

- Discover devices (Serial / Wi-Fi)
- Activate/deactivate a device connection
- Control motor PWM (with software safety lock)
- Configure limits & equipment parameters
- Stream telemetry at a fixed rate (e.g., 100 Hz)

💡 **Important design detail:** The gRPC server injects **existing singleton services** from the UI app (shared RAM/state), meaning the UI and API work on the same live device objects. Any command sent via the SDK (e.g., SetPWM) is instantly reflected on the desktop application's gauges and charts in real-time.

---

### ✅ Architecture
*   **Architecture:** Dynotis Desktop runs as a **gRPC Server** (Kestrel / HTTP2)  
*   **Client:** SDKs act as gRPC Clients.
*   **Endpoint:** Default is `localhost:50051` (HTTP/2).

### ✅ System Architecture & Performance

**High-Performance Embedded gRPC Server**  
Unlike traditional test stands that rely on slow serial polling, Dynotis runs an embedded **ASP.NET Core Kestrel** server directly within the application process.

*   **Zero-Latency State Synchronization:** The API injects the exact same Singleton services (`IDevicesManager`, `IBalancerService`) used by the WPF UI. A command sent via Python instantly updates the UI gauges.
*   **HTTP/2 & Protobuf:** We utilize **HTTP/2** for multiplexing and **Protobuf** for compact binary serialization, ensuring minimal network overhead even at high telemetry rates (100Hz+).
*   **Thread-Safe Operations:** All hardware commands are marshaled through thread-safe managers, preventing race conditions between manual UI control and automated API scripts.

### 📡 Connection Modes & Shared State

The Dynotis API operates on the **same memory space (Shared State)** as the desktop application. This means any change made via the API (e.g., `SetPWM`) instantly updates the UI gauges and vice versa.

#### 1. Local Connection (Default)
If your script and Dynotis Desktop are running on the same computer, use the default endpoint:
*   **Endpoint:** `localhost:50051`

```text
// ✅ Required for h2c (unencrypted HTTP/2) endpoints like http://localhost:50051
AppContext.SetSwitch("System.Net.Http.SocketsHttpHandler.Http2UnencryptedSupport", true);
```

> **Note:** If the server uses http:// (no TLS), .NET requires enabling HTTP/2 unencrypted support.

#### 2. Network & Remote Lab Setup (Isolated Test Cell)

Dynotis is designed for modern engineering labs where the test stand and the operator might be in different rooms.

*   **PC A (Test Cell):** Runs Dynotis Desktop connected to the hardware via USB.
    *   *Configuration:* Ensure Windows Firewall allows inbound TCP traffic on port `50051`.
*   **PC B (Control Room):** Runs your Python/MATLAB/Node.js script.
    *   *Connection:* `client = DynotisClient("192.168.1.50:50051")`

---

### 🌐 Remote Connection & Multi-PC Setup (PC1 Server / PC2 Client)
Dynotis Desktop hosts an embedded **gRPC (HTTP/2) server**. In a remote lab setup, the Dynotis device is connected to **PC1 (Server)** while your automation scripts run on **PC2 (Client)** over the local network.
#### PC1 — Server Configuration (Dynotis Desktop + Hardware)
1. **Allow inbound traffic on TCP 50051**
   - Open **Windows Defender Firewall with Advanced Security**
   - Go to **Inbound Rules** → **New Rule...**
   - Select **Port** → **TCP** → **Specific local ports:** `50051`
   - Choose **Allow the connection**
   - Enable profiles (**Domain / Private / Public**) as required by your lab network
   - Name it: **Dynotis API (gRPC 50051)**

2. **Enable Remote Connections in Dynotis**
   - Go to **Settings → API Settings**
   - Enable **Allow Remote Connections**
   - Click **Apply & Restart API** to listen on all network interfaces

**Find PC1 IP Address**

On PC1, open CMD and run:
```text
ipconfig
```

Note the **IPv4 Address** under Wi-Fi/Ethernet (example: 192.168.1.122).

#### PC2 — Client Configuration (Python / Node.js)

Update the client target from `localhost` to the server IP:

Python
```python
client = DynotisClient("192.168.1.122:50051")
```

Node.js
```javascript
const client = new DynotisClient("192.168.1.122:50051");
```

### Quick Connectivity Checks

- **Ping test (PC2 → PC1):**
```text
ping 192.168.1.122
```

If you see **"No devices found"**, confirm the device is visible/active on PC1 inside Dynotis Desktop.

Ensure TCP **50051** is not blocked or used by another service.

**Security note:** Disable Allow Remote Connections when tests are finished, especially on public networks.

> This setup protects the operator from noise and physical hazards while maintaining real-time control and data acquisition.

> ⚠️ **SAFETY WARNING (CRITICAL)**
>
> Calling `UnlockMotor()` followed by `SetPWM()` **can spin the motor immediately**.  
> Always secure the test rig and follow your laboratory safety procedures **before running any code**.

---

## ⚠️ Safety First

**Read and follow these rules before executing any script:**

1. **Propeller-less Development (Mandatory)**  
   When developing a new script or using the API for the first time, **never install a propeller**.  
   Only install the propeller once you are **100% confident** in your control logic, limits, and stop conditions.

2. **Motor Interlock / Live State**  
   The system starts in a **LOCKED** state by design. The moment you call `UnlockMotor()`, the motor becomes **live** and ready to spin.  
   Ensure the following are in place **before unlocking**:
   - A rigidly secured test stand (no loose fasteners)
   - A safety cage / protective barrier
   - Protective eyewear and appropriate PPE
   - A clear exclusion zone around rotating parts

3. **Emergency Stop (E-Stop) — Always Available**
   - **Software E-Stop:** `client.EmergencyStop(device_request)`  
     Immediately sets PWM to **minimum**, engages the software lock (`IsLocked = true`), and logs the event with a high-severity flag.
   - **Physical E-Stop (Required):**  
     Always keep a physical E-Stop button within reach to handle software freezes, network latency, or unexpected behavior.

---

### 🛡️ Protection & Fail-Safe Systems

Dynotis enforces software-level safety interlocks to reduce risk and prevent runaway scenarios:

1. **Software Interlock (Motor Lock)**  
   The API initializes with the motor in a `LOCKED` state.  
   `SetPWM()` commands are **ignored** until `UnlockMotor()` is explicitly called.

2. **Keep-Alive / Watchdog Monitoring**  
   If the client connection or telemetry stream drops, the system automatically:
   - Cuts output to **PWM minimum**
   - Prevents uncontrolled spin-up due to stale commands

3. **High-Priority Emergency Stop**
   `EmergencyStop` is handled as a high-priority interrupt path that:
   - Forces PWM to **minimum immediately**
   - Engages the motor lock
   - Records the event for traceability

---

### 🧯 Operator Safety Protocols (Recommended)

Use this checklist as a minimum standard when running automated tests:

1. **No propeller during initial development**; validate logic with the motor unloaded first.  
2. **Unlock only when ready**; never unlock “early” or leave the system unlocked unattended.  
3. **Validate limits** (PWM bounds, current/temperature constraints) before ramping up.  
4. **Always implement a safe-exit path** (`try/finally`) that calls `EmergencyStop()` on failure.  
5. **Keep a physical E-Stop within reach** at all times, regardless of software protections.

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
  - `JS uses runtime proto loading; no generated artifacts`

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
  - `@grpc/proto-loader`

---

## 🧠 SDK Technical Architecture (Python vs JavaScript)

Dynotis is **language-agnostic**: all RPC methods and message types are defined in `DynotisAPI.proto`.  
However, the **Python** and **JavaScript (Node.js)** SDKs consume this `.proto` contract using two different, industry-standard approaches.

### 🐍 Python SDK — Static Code Generation

Python uses **pre-generated** gRPC code. In this approach, the `.proto` file is compiled **before runtime**.

**How it works:**
- `build_sdk.py` / `.bat` runs `protoc`
- Generates:
  - `DynotisAPI_pb2.py` (message structures)
  - `DynotisAPI_pb2_grpc.py` (service stubs)
- Output is stored under the `generated/` folder

**Why it’s useful:**
- **Strong IDE autocomplete** and type hints
- **No runtime parsing overhead**
- Stable message classes and imports (consistent module structure)

### 🟨 JavaScript SDK — Dynamic Proto Loading

Node.js uses **runtime loading**, which is common in modern JS gRPC projects.

**How it works:**
- `@grpc/proto-loader` reads `DynotisAPI.proto` at startup
- Creates service methods dynamically in memory (runtime-generated stubs)

**Why there is no `generated/` folder:**
- JavaScript does **not** require precompiled artifacts
- Updating `.proto` usually requires **no rebuild** (restart is enough)
- More portable across OS environments (avoids `protoc` / DLL issues)

---

### 📊 Comparison

| Feature | Static | Dynamic |
| :--- | :---: | :---: |
| Approach | Pre-compiled | Runtime loading |
| Needs `generated/` | ✅ Yes | ❌ No |
| Proto update | Rebuild required | Usually just restart |
| IDE support | Excellent | Medium (great with TS) |
| Setup complexity | `grpcio-tools` needed | Simple, OS-friendly |

---

> **Developer note:** Both clients connect to the same Dynotis gRPC server and provide the same API capabilities and performance profile.  
> Use **Python** for stronger typing and data workflows, and **Node.js** for plug-and-play automation and web-oriented stacks.

---

## 📂 Repository Structure

```text
Dynotis_SDKs/
├── Protos/
│   └── DynotisAPI.proto
├── dynotis_javascript_sdk/
│   ├── client.js
│   ├── examples/full_test_scenario.js
│   └── index.js
└── dynotis_python_sdk/
    ├── generated/
    ├── client.py
    ├── build_sdk.py
    └── examples/full_test_scenario.py
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
### Generate JavaScript SDK (Runtime Proto Loading)
```text
No code generation is required.
The SDK loads `Protos/DynotisAPI.proto` at runtime using `@grpc/proto-loader`.
If the `.proto` changes, simply restart the Node.js process.
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
| `GetTelemetryStream` | Server-side streaming telemetry (100Hz default). |
| `StartLogging` | Starts logging (Requires DI wiring on server). |
| `StopLogging` | Stops logging (Requires DI wiring on server). |

> **🧩 Logging Note:** StartLogging/StopLogging currently require DataLoggerManager to be registered in the DI container as a **singleton** and injected into DynotisAPIService.

## ⚙️ Telemetry Stream Notes

 * Typical stream rate: 100 Hz (PeriodicTimer(10ms))
 * Stream message includes:
   - sensors: thrust/torque/voltage/current/rpm/temps/accel/wind
   - theoretical: power, efficiencies, FOM, coefficients, etc.
   - environment: ambient temperature, pressure

✅ Expected behavior:
 * If the client cancels the stream, server may throw OperationCanceledException (*normal*).

## ⚙️ Real-Time Physics & Telemetry Engine

Dynotis doesn't just stream raw sensor voltages. It includes an integrated **physics engine** that computes aerodynamic and electrical metrics on-the-fly, saving you from post-processing large datasets.

**Streamed Metrics (100Hz Default):**
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

❌ **JavaScript:** Proto load failed / Cannot find proto file

### Symptoms
- `Error: ENOENT: no such file or directory, open '.../DynotisAPI.proto'`
- `Failed to load proto`
- `Invalid include path`
- `unimplemented` / `service not found` (yanlış proto veya paket adı)

### Fix (Dynamic Proto Loading)
1) **Dependencies**
```text
cd dynotis_javascript_sdk
npm install
```

2) **Verify proto path**

- Ensure the file exists: `Protos/DynotisAPI.proto`
- Ensure your Node SDK points to the correct location (example):
-- `../Protos/DynotisAPI.proto` (relative to `dynotis_javascript_sdk/`)

3) **Restart**

- No build step is required.
- If `.proto` changed, **restart** the Node process:

 ```text
node examples/full_test_scenario.js
```

### Confirm:
- There is **no** `generated/` folder in the Node.js SDK (expected).
- The SDK loads `DynotisAPI.proto` at runtime via `@grpc/proto-loader`.

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
