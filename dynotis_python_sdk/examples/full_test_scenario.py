# -*- coding: utf-8 -*-
import time
import sys
import os
import threading

# SDK yollarını ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from client import DynotisClient
from generated import DynotisAPI_pb2

# --- TERMİNAL RENKLERİ ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_dashboard(data):
    """Terminal ekranını temizlemeden verileri tablo gibi yazdırır."""
    s = data.sensors
    t = data.theoretical
    e = data.environment
    
    # Terminali temizle (Opsiyonel, daha temiz görüntü için)
    # os.system('cls' if os.name == 'nt' else 'clear')
    
    dashboard = f"""
{Colors.HEADER}=== DYNOTIS LIVE TELEMETRY DASHBOARD ==={Colors.ENDC}
{Colors.BLUE}[SENSORS]{Colors.ENDC}
  PWM: {data.esc_pwm_readout:4.0f} µs | RPM: {s.rpm:5.0f} | Thrust: {s.thrust_gf:6.1f} g | Torque: {s.torque_nmm:5.2f} Nmm
  Volt: {s.voltage_v:5.2f} V | Curr: {s.current_a:5.2f} A | Power: {t.electrical_power_w:6.1f} W
  Temp: Motor {s.motor_temp_c:4.1f}°C / ESC {s.esc_temp_c:4.1f}°C

{Colors.GREEN}[ANALYSIS]{Colors.ENDC}
  System Eff: {t.system_efficiency_percent:5.1f} % | Prop Eff: {t.propeller_efficiency_percent:5.1f} %
  Thrust/Watt: {t.thrust_per_watt_gf_w:5.2f} g/W | F.O.M: {t.figure_of_merit_percent:5.2f} %
  Tip Speed: {t.tip_speed_ms:5.1f} m/s | Mach: {t.mach_tip:4.2f} | Air Dens: {t.air_density_kg_m3:5.3f} kg/m³

{Colors.WARNING}[STATUS]{Colors.ENDC}
  Limit Triggered: {Colors.FAIL if data.is_limit_triggered else Colors.GREEN}{data.is_limit_triggered}{Colors.ENDC}
-------------------------------------------"""
    sys.stdout.write("\033[H") # Cursor'ı en üste taşı (Ekran titremesini önler)
    sys.stdout.write(dashboard)
    sys.stdout.flush()

def run_advanced_test():
    # 1. Başlatma
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{Colors.BOLD}Dynotis Advanced Test Scenario Starting...{Colors.ENDC}")
    
    client = DynotisClient('localhost:50051')
    dev_id = None

    try:
        # 2. Cihaz Keşfi
        devices = client.get_device_list()
        if not devices:
            print(f"{Colors.FAIL}❌ No devices found!{Colors.ENDC}")
            return
        
        device = devices[0]
        dev_id = device.identifier
        print(f"✅ Connected to: {Colors.GREEN}{device.name}{Colors.ENDC} [{dev_id}]")

        # 3. Aktivasyon ve Konfigürasyon (gui.py'deki gibi detaylı)
        client.activate_device(dev_id)
        
        print("⚙️ Configuring safety limits...")
        client.set_limits(dev_id, 
                         max_current_a=45.0, enable_max_current=True,
                         max_motor_temp_c=75.0, enable_max_motor_temp=True,
                         max_rpm=25000.0, enable_max_rpm=True)

        print("⚙️ Setting equipment parameters...")
        client.set_equipment(dev_id, diameter=12.0, resistance=55.0, no_load_current=0.8)

        # 4. Sensör Sıfırlama (Tare)
        print("⚖️ Taring sensors (Thrust & Torque)...")
        client.tare_sensor(dev_id, DynotisAPI_pb2.SENSOR_THRUST)
        time.sleep(0.5)
        client.tare_sensor(dev_id, DynotisAPI_pb2.SENSOR_TORQUE)
        time.sleep(0.5)

        # 5. Kayıt Başlatma (Server-side Logging)
        print("💾 Starting data log session...")
        client.start_logging(dev_id, "SDK_Advanced_Ramp_Test", hz=50, notes="Automated test with Python SDK")

        # 6. Test Akışı (Ramp)
        print(f"\n{Colors.WARNING}⚠️ UNLOCKING MOTOR IN 2 SECONDS...{Colors.ENDC}")
        time.sleep(2)
        client.unlock_motor(dev_id)
        
        # Telemetri akışını başlat
        telemetry_stream = client.get_telemetry_stream(dev_id)
        
        # Test adımları: (PWM, Süre)
        test_steps = [
            (1100, 3), # %10 civarı
            (1250, 4), # %25 civarı
            (1400, 4), # %40 civarı
            (1200, 2), # Düşüş
            (1000, 2)  # Durdur
        ]

        os.system('cls' if os.name == 'nt' else 'clear') # Dashboard için ekranı temizle

        for target_pwm, duration in test_steps:
            client.set_pwm(dev_id, target_pwm)
            start_time = time.time()
            
            while time.time() - start_time < duration:
                try:
                    # Telemetri paketini al
                    data = next(telemetry_stream)
                    
                    # Dashboard'u güncelle
                    print_dashboard(data)
                    
                    # Güvenlik Kontrolü: Eğer sunucu tarafında bir limit tetiklendiyse testi durdur
                    if data.is_limit_triggered:
                        print(f"\n{Colors.FAIL}🚨 EMERGENCY: Limit triggered by server! Aborting...{Colors.ENDC}")
                        raise Exception("Hardware Limit Triggered")

                except StopIteration:
                    break
                
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}🛑 Test interrupted by user!{Colors.ENDC}")
    except Exception as e:
        print(f"\n\n{Colors.FAIL}❌ Test Error: {e}{Colors.ENDC}")
    
    finally:
        # 7. Güvenli Kapatma (Her durumda çalışır)
        if dev_id:
            print(f"\n{Colors.BOLD}Performing Safe Shutdown...{Colors.ENDC}")
            client.set_pwm(dev_id, 1000)
            client.lock_motor(dev_id)
            client.stop_logging(dev_id)
            client.deactivate_device(dev_id)
            print(f"{Colors.GREEN}✅ Device secured and disconnected.{Colors.ENDC}")
        
        client.close()
        print("Test Finished.")

if __name__ == "__main__":
    run_advanced_test()
