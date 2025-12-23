const { DynotisClient } = require('../client');

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

async function main() {
    console.log("🚀 Dynotis JS Dynamic Test Suite Starting...");
    const client = new DynotisClient('127.0.0.1:50051');
    let devId = null;

    try {
        const response = await client.getDeviceList();
        if (!response.devices || response.devices.length === 0) {
            console.log("❌ No devices found!");
            return;
        }

        devId = response.devices[0].identifier;
        console.log(`✅ Connected to: ${response.devices[0].name}`);

        await client.activateDevice(devId);
        await client.tareSensor(devId, 0); // 0 = SENSOR_THRUST

        console.log("🔓 Unlocking motor...");
        await sleep(1000);
        await client.unlockMotor(devId);

        const stream = client.getTelemetryStream(devId);
        stream.on('data', (data) => {
            const s = data.sensors;
            process.stdout.write(`\rPWM: ${data.esc_pwm_readout.toFixed(0)} | RPM: ${s.rpm.toFixed(0)} | Thrust: ${s.thrust_gf.toFixed(1)}g    `);
        });

        const steps = [1100, 1200, 1300, 1000];
        for (const pwm of steps) {
            console.log(`\n>>> Setting PWM: ${pwm}`);
            await client.setPWM(devId, pwm);
            await sleep(3000);
        }

    } catch (err) {
        console.error("\n❌ Error:", err.message);
    } finally {
        if (devId) {
            await client.setPWM(devId, 1000);
            await client.lockMotor(devId);
        }
        client.close();
        process.exit();
    }
}

main();
