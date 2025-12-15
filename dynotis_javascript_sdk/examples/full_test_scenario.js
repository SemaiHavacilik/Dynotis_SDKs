const { DynotisClient, messages } = require('../client');

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function main() {
    console.log("============================================");
    console.log("   DYNOTIS AUTOMATED TEST SCENARIO (DEMO)   ");
    console.log("============================================");

    const client = new DynotisClient('localhost:50051');

    try {
        // --- STEP 1: Device Discovery ---
        console.log("\n[1/6] Searching for devices...");
        const response = await client.getDeviceList();

        if (!response.devicesList || response.devicesList.length === 0) {
            console.error("❌ ERROR: No devices found! Please ensure the device is connected.");
            return;
        }

        const targetDevice = response.devicesList[0];
        const devId = targetDevice.identifier;
        console.log(`✅ Device Found: ${targetDevice.name} (ID: ${devId})`);

        // --- STEP 2: Activation ---
        console.log("\n[2/6] Activating device...");
        await client.activateDevice(devId);
        await sleep(1000);

        // --- STEP 3: Safety Limits & Tare ---
        console.log("\n[3/6] Setting safety limits and taring sensors...");
        await client.setLimits(devId, { maxCurrent: 40.0, maxTemp: 80.0 });
        await client.tareSensor(devId, messages.SensorType.SENSOR_THRUST);
        console.log("-> Limits set, Thrust sensor tared.");

        // --- STEP 4: Unlock Motor ---
        console.log("\n[4/6] Unlocking motor (WARNING!)...");
        await client.unlockMotor(devId);
        await sleep(500);

        // --- STEP 5: Test Run (Ramp Up) ---
        console.log("\n[5/6] Test Starting! Motor will spin up...");

        const testPwmValues = [1100, 1200, 1300, 1100];
        const stream = client.getTelemetryStream(devId);

        stream.on('data', (data) => {
            const sensors = data.getSensors();
            process.stdout.write(
                `   RPM: ${sensors.getRpm().toFixed(0).padStart(5)} | ` +
                `Thrust: ${sensors.getThrustGf().toFixed(1).padStart(6)} g | ` +
                `Current: ${sensors.getCurrentA().toFixed(1).padStart(4)} A | ` +
                `Voltage: ${sensors.getVoltageV().toFixed(1).padStart(4)} V\r`
            );
        });

        stream.on('error', (err) => {
            if (err.code !== 1) console.error("\nStream Error:", err);
        });

        for (const targetPwm of testPwmValues) {
            console.log(`\n>>> Setting PWM: ${targetPwm}`);
            await client.setPWM(devId, targetPwm);
            await sleep(2000);
        }

        console.log("");
        stream.cancel();

    } catch (err) {
        console.error("\n\n❌ UNEXPECTED ERROR:", err);
    } finally {
        // --- STEP 6: Safe Shutdown ---
        console.log("\n\n[6/6] Performing safe shutdown...");
        try {
            await client.setPWM(devId, 1000);
            await client.lockMotor(devId);
            console.log("✅ Motor stopped and locked.");
            await client.deactivateDevice(devId);
            console.log("✅ Device disconnected.");
        } catch (e) {
            // Ignore errors
        }

        client.close();
        console.log("Test Completed.");
    }
}

main();
