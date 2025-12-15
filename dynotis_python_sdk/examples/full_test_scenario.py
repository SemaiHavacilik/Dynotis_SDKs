# -*- coding: utf-8 -*-
import time
import sys
import os

# 1. Add parent directory to path to import the SDK correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from client import DynotisClient
from generated import DynotisAPI_pb2

def main():
    print("============================================")
    print("   DYNOTIS AUTOMATED TEST SCENARIO (DEMO)   ")
    print("============================================")

    # Initialize Client
    client = DynotisClient('localhost:50051')

    try:
        # --- STEP 1: Device Discovery ---
        print("\n[1/6] Searching for devices...")
        devices = client.get_device_list()
        
        if not devices:
            print("❌ ERROR: No devices found! Please ensure the device is connected.")
            return

        # Select the first device
        target_device = devices[0]
        dev_id = target_device.identifier
        print(f"✅ Device Found: {target_device.name} (ID: {dev_id})")

        # --- STEP 2: Activation ---
        print("\n[2/6] Activating device...")
        client.activate_device(dev_id)
        time.sleep(1) # Wait for connection to settle

        # --- STEP 3: Safety Limits & Tare ---
        print("\n[3/6] Setting safety limits and taring sensors...")
        
        # Set 40A Current Limit, 80C Temp Limit
        client.set_limits(dev_id, max_current=40.0, max_temp=80.0)
        
        # Tare Thrust Sensor
        client.tare_sensor(dev_id, DynotisAPI_pb2.SensorType.SENSOR_THRUST)
        print("-> Limits set, Thrust sensor tared.")

        # --- STEP 4: Unlock Motor ---
        print("\n[4/6] Unlocking motor (WARNING!)...")
        client.unlock_motor(dev_id)
        time.sleep(0.5)

        # --- STEP 5: Test Run (Ramp Up) ---
        print("\n[5/6] Test Starting! Motor will spin up...")
        
        test_pwm_values = [1100, 1200, 1300, 1100] # Test steps
        
        # Start Data Stream (Generator)
        stream = client.get_telemetry_stream(dev_id)
        
        # Manual iterator control
        stream_iterator = iter(stream)

        for target_pwm in test_pwm_values:
            print(f"\n>>> Setting PWM: {target_pwm}")
            client.set_pwm(dev_id, float(target_pwm))
            
            # Read data for 2 seconds per step
            start_step = time.time()
            while time.time() - start_step < 2.0:
                try:
                    # Get next packet
                    data = next(stream_iterator)
                    
                    # Print Data
                    print(f"   RPM: {data.sensors.rpm:5.0f} | "
                          f"Thrust: {data.sensors.thrust_gf:6.1f} g | "
                          f"Current: {data.sensors.current_a:4.1f} A | "
                          f"Voltage: {data.sensors.voltage_v:4.1f} V", end='\r')
                except StopIteration:
                    break
            print("") # New line

    except KeyboardInterrupt:
        print("\n\n⚠️ User stopped the test!")
    except Exception as e:
        print(f"\n\n❌ UNEXPECTED ERROR: {e}")
    finally:
        # --- STEP 6: Safe Shutdown (Always runs) ---
        print("\n\n[6/6] Performing safe shutdown...")
        try:
            client.set_pwm(dev_id, 1000.0) # Stop Motor (Min PWM)
            client.lock_motor(dev_id)      # Lock Motor
            print("✅ Motor stopped and locked.")
            
            client.deactivate_device(dev_id)
            print("✅ Device disconnected.")
        except:
            pass
        
        client.close()
        print("Test Completed.")

if __name__ == "__main__":
    main()

