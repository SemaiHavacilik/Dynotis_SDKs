# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox
import grpc
import threading
import time
import sys
import os

# SDK yollarını ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from generated import DynotisAPI_pb2, DynotisAPI_pb2_grpc
except ImportError:
    try:
        import DynotisAPI_pb2
        import DynotisAPI_pb2_grpc
    except ImportError:
        print("HATA: Proto dosyaları bulunamadı!")
        sys.exit(1)

# --- PROFESYONEL RENK PALETİ ---
C_BG        = "#F8FAFC"
C_CARD      = "#FFFFFF"
C_TEXT      = "#1E293B"
C_LABEL     = "#64748B"
C_PRIMARY   = "#3B82F6" 
C_ACCENT    = "#10B981" 
C_DANGER    = "#EF4444" 
C_BORDER    = "#E2E8F0"

class DynotisProDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Dynotis Pro - Command & Automation Suite")
        self.root.geometry("1366x850")
        self.root.configure(bg=C_BG)

        # --- Değişkenler ---
        self.stub = None
        self.channel = None
        self.dev_id = None
        self.is_connected = False
        self.is_testing = False
        self.stop_threads = False
        
        # Watchdog Besleme Aralığı (ms)
        self.heartbeat_interval = 0.3 

        # Ayar Değişkenleri
        self.var_prop_diam = tk.DoubleVar(value=12.0)
        self.var_motor_res = tk.DoubleVar(value=45.0)
        self.var_no_load = tk.DoubleVar(value=0.8)
        self.var_armed = tk.BooleanVar(value=False)

        # --- Arayüz Kurulumu ---
        self.setup_styles()
        self.create_layout()
        
        # gRPC Başlat
        self.connect_grpc()
        
        # Arka Plan Thread'leri
        threading.Thread(target=self.telemetry_loop, daemon=True).start()
        threading.Thread(target=self.heartbeat_loop, daemon=True).start()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=C_BG)
        style.configure("Card.TFrame", background=C_CARD, relief="flat")
        style.configure("TLabel", background=C_CARD, foreground=C_TEXT, font=('Segoe UI', 9))
        style.configure("Header.TLabel", font=('Segoe UI', 10, 'bold'), foreground=C_TEXT)
        style.configure("Value.TLabel", font=('Consolas', 11, 'bold'), foreground=C_PRIMARY)

    def create_layout(self):
        main_pad = ttk.Frame(self.root, padding=15)
        main_pad.pack(fill="both", expand=True)

        # 1. ÜST BAR
        self.create_top_bar(main_pad)

        # 2. ANA İÇERİK
        content = ttk.Frame(main_pad)
        content.pack(fill="both", expand=True, pady=10)
        
        # Sol: Kontrol
        self.create_left_panel(content)
        # Orta: Telemetri
        self.create_center_panel(content)
        # Sağ: Ayarlar & Log
        self.create_right_panel(content)

        # 3. ACİL DURDURMA
        self.btn_emergency = tk.Button(main_pad, text="🛑 ACİL DURDURMA (EMERGENCY STOP)", 
                                       bg=C_DANGER, fg="white", font=('Segoe UI', 12, 'bold'),
                                       relief="flat", command=self.emergency_stop, cursor="hand2")
        self.btn_emergency.pack(fill="x", ipady=10)

    def create_top_bar(self, parent):
        bar = ttk.Frame(parent, style="Card.TFrame", padding=10)
        bar.pack(fill="x")

        ttk.Label(bar, text="Cihaz Seçimi:", style="Header.TLabel").pack(side="left", padx=5)
        self.combo_devices = ttk.Combobox(bar, state="readonly", width=30)
        self.combo_devices.pack(side="left", padx=5)
        
        ttk.Button(bar, text="⟳ Tara", command=self.refresh_devices).pack(side="left", padx=5)
        self.btn_connect = tk.Button(bar, text="BAĞLAN", bg=C_PRIMARY, fg="white", 
                                     relief="flat", padx=15, command=self.toggle_connection)
        self.btn_connect.pack(side="left", padx=10)
        
        self.lbl_status = ttk.Label(bar, text="🔴 ÇEVRİMDIŞI", font=('Segoe UI', 9, 'bold'))
        self.lbl_status.pack(side="right", padx=10)

    def create_left_panel(self, parent):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=15)
        frame.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(frame, text="MANUEL KONTROL", style="Header.TLabel").pack(anchor="w")
        self.chk_arm = ttk.Checkbutton(frame, text="MOTOR KİLİDİ (ARM)", variable=self.var_armed, 
                                       command=self.on_arm_changed)
        self.chk_arm.pack(pady=10, anchor="w")

        self.lbl_pwm_val = tk.Label(frame, text="800", font=('Consolas', 32, 'bold'), 
                                    bg=C_CARD, fg=C_PRIMARY)
        self.lbl_pwm_val.pack(pady=5)

        self.slider = ttk.Scale(frame, from_=2200, to=800, orient="vertical", command=self.on_slider_move)
        self.slider.set(800)
        self.slider.state(['disabled'])
        self.slider.pack(fill="y", expand=True, pady=10)

        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=15)
        ttk.Label(frame, text="OTOMASYON", style="Header.TLabel").pack(anchor="w")
        
        self.btn_start_test = tk.Button(frame, text="▶ TESTİ BAŞLAT", bg=C_ACCENT, fg="white",
                                        relief="flat", font=('Segoe UI', 10, 'bold'),
                                        command=self.start_auto_test)
        self.btn_start_test.pack(fill="x", pady=10, ipady=5)

    def create_center_panel(self, parent):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=15)
        frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.telemetry_labels = {}
        
        sections = [
            ("TEMEL SENSÖRLER", [
                ("İtki", "thrust", "gF"), ("Tork", "torque", "Nmm"),
                ("Voltaj", "voltage", "V"), ("Akım", "current", "A"),
                ("RPM", "rpm", "RPM"), ("Motor Sıcaklığı", "temp_motor", "°C")
            ]),
            ("VERİMLİLİK & GÜÇ", [
                ("Sistem Verimi", "eff_sys", "%"), ("Mekanik Güç", "p_mech", "W"),
                ("Elektrik Güç", "p_elec", "W"), ("Verim (g/W)", "g_per_w", "g/W")
            ]),
            ("AERODİNAMİK", [
                ("Hava Yoğunluğu", "air_dens", "kg/m³"), ("Tip Speed", "tip_spd", "m/s"),
                ("Ct (Thrust Coeff)", "ct", ""), ("Cp (Power Coeff)", "cp", "")
            ])
        ]

        for sec_title, items in sections:
            ttk.Label(frame, text=sec_title, style="Header.TLabel").pack(anchor="w", pady=(10, 5))
            grid_f = ttk.Frame(frame, style="Card.TFrame")
            grid_f.pack(fill="x", pady=5)
            
            for i, (name, key, unit) in enumerate(items):
                row, col = divmod(i, 2)
                cell = ttk.Frame(grid_f, style="Card.TFrame", padding=5)
                cell.grid(row=row, column=col, sticky="ew")
                grid_f.columnconfigure(col, weight=1)
                
                # Sol taraf: Sensör Adı
                ttk.Label(cell, text=name, foreground=C_LABEL).pack(side="left")
                
                # Sağ taraf: Değer ve Birim (Sıralama Değiştirildi)
                # Önce birimi sağa yaslıyoruz (en sağda kalır)
                if unit:
                    ttk.Label(cell, text=f" {unit}", foreground=C_LABEL).pack(side="right")
                
                # Sonra değeri sağa yaslıyoruz (birimin solunda kalır)
                val_lbl = ttk.Label(cell, text="--", style="Value.TLabel")
                val_lbl.pack(side="right")
                
                self.telemetry_labels[key] = val_lbl

    def create_right_panel(self, parent):
        frame = ttk.Frame(parent, style="Card.TFrame", padding=15, width=400)
        frame.pack(side="left", fill="both", expand=True)
        frame.pack_propagate(False)

        ttk.Label(frame, text="CİHAZ AYARLARI", style="Header.TLabel").pack(anchor="w")
        set_f = ttk.Frame(frame, style="Card.TFrame")
        set_f.pack(fill="x", pady=10)
        
        self.create_input_row(set_f, "Pervane (in):", self.var_prop_diam)
        self.create_input_row(set_f, "Direnç (mΩ):", self.var_motor_res)
        self.create_input_row(set_f, "Boş Akım (A):", self.var_no_load)
        
        ttk.Button(frame, text="Parametreleri Kaydet", command=self.save_params).pack(fill="x", pady=5)

        ttk.Label(frame, text="SİSTEM LOGLARI", style="Header.TLabel").pack(anchor="w", pady=(20, 5))
        self.log_box = tk.Text(frame, height=20, bg="#F1F5F9", relief="flat", font=('Consolas', 8))
        self.log_box.pack(fill="both", expand=True)

    # --- MANTIK FONKSİYONLARI ---

    def log(self, msg):
        t = time.strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{t}] {msg}\n")
        self.log_box.see(tk.END)

    def connect_grpc(self):
        try:
            self.channel = grpc.insecure_channel('localhost:50051')
            self.stub = DynotisAPI_pb2_grpc.DynotisControllerStub(self.channel)
            self.log("gRPC Sunucusuna bağlanıldı.")
            self.refresh_devices()
        except Exception as e:
            self.log(f"Bağlantı hatası: {e}")

    def heartbeat_loop(self):
        while not self.stop_threads:
            if self.is_connected and self.dev_id:
                try:
                    req = DynotisAPI_pb2.HeartbeatRequest(device_identifier=self.dev_id)
                    self.stub.SendHeartbeat(req)
                except:
                    pass
            time.sleep(self.heartbeat_interval)

    def start_auto_test(self):
        if not self.is_connected:
            messagebox.showwarning("Uyarı", "Önce bir cihaza bağlanın!")
            return
        if self.is_testing: return
        threading.Thread(target=self.run_test_sequence, daemon=True).start()

    def run_test_sequence(self):
        self.is_testing = True
        self.btn_start_test.config(state="disabled", text="⌛ TEST SÜRÜYOR")
        
        try:
            self.log("🚀 Otomatik test senaryosu başlatıldı.")
            self.log("⚖️ Sensörler sıfırlanıyor (Tare)...")
            self.stub.TareSensor(DynotisAPI_pb2.TareRequest(device_identifier=self.dev_id, sensor_type=0))
            time.sleep(1.5)

            self.log("🔓 Motor kilidi açılıyor...")
            self.root.after(0, lambda: self.var_armed.set(True))
            self.stub.UnlockMotor(DynotisAPI_pb2.DeviceRequest(device_identifier=self.dev_id))
            time.sleep(1)

            steps = [1100, 1250, 1400, 1550, 1200]
            for pwm in steps:
                if not self.is_testing: break
                self.log(f"📈 PWM Hedef: {pwm}")
                self.stub.SetPWM(DynotisAPI_pb2.PwmRequest(device_identifier=self.dev_id, pwm_value=pwm))
                time.sleep(3) 

            self.log("🏁 Test bitti. Motor durduruluyor.")
            self.emergency_stop()
            
        except Exception as e:
            self.log(f"❌ Test hatası: {e}")
        finally:
            self.is_testing = False
            self.btn_start_test.config(state="normal", text="▶ TESTİ BAŞLAT")

    def telemetry_loop(self):
        while not self.stop_threads:
            if self.is_connected and self.dev_id:
                try:
                    req = DynotisAPI_pb2.DeviceRequest(device_identifier=self.dev_id)
                    stream = self.stub.GetTelemetryStream(req)
                    for data in stream:
                        if self.stop_threads or not self.is_connected: break
                        self.root.after(0, self.update_ui, data)
                except:
                    time.sleep(1)
            time.sleep(0.5)

    def update_ui(self, data):
        s = data.sensors
        t = data.theoretical
        
        mapping = {
            "thrust": f"{s.thrust_gf:.1f}", "torque": f"{s.torque_nmm:.2f}",
            "voltage": f"{s.voltage_v:.2f}", "current": f"{s.current_a:.2f}",
            "rpm": f"{s.rpm:.0f}", "temp_motor": f"{s.motor_temp_c:.1f}",
            "eff_sys": f"{t.system_efficiency_percent:.1f}", "p_mech": f"{t.mechanical_power_w:.1f}",
            "p_elec": f"{t.electrical_power_w:.1f}", "g_per_w": f"{t.thrust_per_watt_gf_w:.2f}",
            "air_dens": f"{t.air_density_kg_m3:.3f}", "tip_spd": f"{t.tip_speed_ms:.1f}",
            "ct": f"{t.coefficient_thrust_ct:.4f}", "cp": f"{t.coefficient_power_cp:.4f}"
        }
        
        for key, val in mapping.items():
            if key in self.telemetry_labels:
                self.telemetry_labels[key].config(text=val)
        
        self.lbl_pwm_val.config(text=str(int(data.esc_pwm_readout)))
        if data.is_limit_triggered:
            self.lbl_status.config(text="⚠️ LİMİT TETİKLENDİ", foreground=C_DANGER)

    def create_input_row(self, parent, label, var):
        row = ttk.Frame(parent, style="Card.TFrame")
        row.pack(fill="x", pady=2)
        ttk.Label(row, text=label).pack(side="left")
        ttk.Entry(row, textvariable=var, width=10, justify="right").pack(side="right")

    def refresh_devices(self):
        if not self.stub: return
        try:
            resp = self.stub.GetDeviceList(DynotisAPI_pb2.Empty())
            self.combo_devices['values'] = [f"{d.name} ({d.identifier})" for d in resp.devices]
            if resp.devices: self.combo_devices.current(0)
        except: pass

    def toggle_connection(self):
        if not self.is_connected:
            selected = self.combo_devices.get()
            if not selected: return
            self.dev_id = selected.split('(')[1].replace(')', '')
            try:
                req = DynotisAPI_pb2.DeviceRequest(device_identifier=self.dev_id)
                if self.stub.ActivateDevice(req).success:
                    self.is_connected = True
                    self.btn_connect.config(text="KES", bg="#94A3B8")
                    self.lbl_status.config(text="🟢 BAĞLI", foreground=C_ACCENT)
                    self.log(f"Cihaz bağlandı: {self.dev_id}")
            except Exception as e: self.log(f"Bağlantı hatası: {e}")
        else:
            self.is_connected = False
            self.btn_connect.config(text="BAĞLAN", bg=C_PRIMARY)
            self.lbl_status.config(text="🔴 ÇEVRİMDIŞI", foreground=C_TEXT)
            self.log("Bağlantı kesildi.")

    def on_arm_changed(self):
        if not self.is_connected: return
        req = DynotisAPI_pb2.DeviceRequest(device_identifier=self.dev_id)
        if self.var_armed.get():
            self.stub.UnlockMotor(req)
            self.slider.state(['!disabled'])
            self.log("Motor kilidi açıldı (ARMED).")
        else:
            self.stub.LockMotor(req)
            self.slider.set(800)
            self.slider.state(['disabled'])
            self.log("Motor kilitlendi (LOCKED).")

    def on_slider_move(self, val):
        pwm = int(float(val))
        self.lbl_pwm_val.config(text=str(pwm))
        if self.is_connected and self.var_armed.get():
            self.stub.SetPWM(DynotisAPI_pb2.PwmRequest(device_identifier=self.dev_id, pwm_value=pwm))

    def emergency_stop(self):
        self.is_testing = False
        if self.is_connected:
            try:
                self.stub.EmergencyStop(DynotisAPI_pb2.DeviceRequest(device_identifier=self.dev_id))
                self.var_armed.set(False)
                self.on_arm_changed()
                self.log("!!! ACİL DURDURMA TETİKLENDİ !!!")
            except: pass

    def save_params(self):
        if not self.is_connected: return
        params = DynotisAPI_pb2.EquipmentParameters(
            propeller_diameter_inch=self.var_prop_diam.get(),
            motor_resistance_mohm=self.var_motor_res.get(),
            no_load_current_a=self.var_no_load.get()
        )
        self.stub.SetEquipmentParameters(DynotisAPI_pb2.EquipmentParametersRequest(
            device_identifier=self.dev_id, parameters=params))
        self.log("Ekipman parametreleri güncellendi.")

if __name__ == "__main__":
    root = tk.Tk()
    app = DynotisProDashboard(root)
    root.mainloop()
