🚀 Dynotis SDKs (Python & JavaScript)
Bu depo, Dynotis Dinamometre cihazlarını harici yazılımlar üzerinden kontrol etmek ve veri toplamak için geliştirilmiş Python ve JavaScript (Node.js) SDK'larını içerir.
Sistem gRPC protokolü üzerine kuruludur. Dynotis Masaüstü Uygulaması (WPF) bir gRPC Sunucusu olarak çalışır, bu SDK'lar ise İstemci (Client) olarak bağlanır.
📋 İçindekiler
Gereksinimler
Proje Yapısı
🐍 Python SDK Kullanımı
🟨 JavaScript SDK Kullanımı
📡 API Referansı (Proto)
Sorun Giderme
🛠 Gereksinimler
SDK'ları kullanabilmek için aşağıdakilerin kurulu olması gerekir:
Dynotis Masaüstü Uygulaması: Uygulama açık olmalı ve gRPC sunucusu çalışıyor olmalıdır (Varsayılan Port: 50051).
Python 3.8+ (Python SDK için)
Node.js 16+ (JavaScript SDK için)
📂 Proje Yapısı
code
Text
Dynotis_SDKs/
├── Protos/
│   └── DynotisAPI.proto          # Tüm sistemin ortak sözleşme dosyası (gRPC)
├── dynotis_javascript_sdk/       # Node.js İstemcisi
│   ├── examples/                 # Örnek senaryolar
│   ├── build_sdk.js              # Proto dosyasını JS'e derleyen script
│   └── client.js                 # Kullanımı kolaylaştırılmış Wrapper sınıfı
└── dynotis_python_sdk/           # Python İstemcisi
    ├── examples/                 # Örnek senaryolar
    ├── build_sdk.py              # Proto dosyasını Python'a derleyen script
    └── client.py                 # Kullanımı kolaylaştırılmış Wrapper sınıfı
🐍 Python SDK Kullanımı
Python ile Dynotis cihazlarını kontrol etmek için aşağıdaki adımları izleyin.
1. Kurulum
Gerekli kütüphaneleri (grpcio, grpcio-tools, protobuf) yükleyin:
code
Bash
cd dynotis_python_sdk
pip install -r requirements.txt
# Eğer requirements.txt yoksa:
# pip install grpcio grpcio-tools protobuf
2. SDK'yı Derleme (Build)
.proto dosyasından gerekli Python kodlarını üretmek için build scriptini çalıştırın. Bu işlem generated klasörünü oluşturur.
code
Bash
python build_sdk.py
Not: Bu script, Python'daki relative import sorunlarını otomatik olarak düzeltir.
3. Örnek Senaryoyu Çalıştırma
Cihazı bulan, motoru çalıştıran ve verileri okuyan tam test senaryosu:
code
Bash
python examples/full_test_scenario.py
4. Kendi Kodunuzu Yazın
code
Python
from client import DynotisClient

# Bağlan
client = DynotisClient('localhost:50051')

# Cihazları Listele
devices = client.get_device_list()
dev_id = devices[0].identifier

# Aktif Et ve Motoru Aç
client.activate_device(dev_id)
client.unlock_motor(dev_id)

# PWM Gönder (Örn: 1200us)
client.set_pwm(dev_id, 1200.0)

# Veri Akışını Başlat
stream = client.get_telemetry_stream(dev_id)
for data in stream:
    print(f"RPM: {data.sensors.rpm} | Thrust: {data.sensors.thrust_gf} g")
🟨 JavaScript SDK Kullanımı
Node.js ile entegrasyon sağlamak için aşağıdaki adımları izleyin.
1. Kurulum
Bağımlılıkları yükleyin:
code
Bash
cd dynotis_javascript_sdk
npm install
2. SDK'yı Derleme (Build)
.proto dosyasından gerekli JS kodlarını üretmek için:
code
Bash
node build_sdk.js
# Veya Windows kullanıyorsanız:
# dynotis_generate_javascript_sdk.bat
3. Örnek Senaryoyu Çalıştırma
code
Bash
node examples/full_test_scenario.js
4. Kendi Kodunuzu Yazın
code
JavaScript
const { DynotisClient } = require('./client');

async function run() {
    const client = new DynotisClient('localhost:50051');

    // Cihazı Bul
    const response = await client.getDeviceList();
    const devId = response.devicesList[0].identifier;

    // Aktif Et
    await client.activateDevice(devId);
    await client.unlockMotor(devId);

    // PWM Ayarla
    await client.setPWM(devId, 1300);

    // Veri Akışı
    const stream = client.getTelemetryStream(devId);
    stream.on('data', (data) => {
        const sensors = data.getSensors();
        console.log(`Thrust: ${sensors.getThrustGf()} g`);
    });
}

run();
📡 API Referansı
DynotisAPI.proto dosyasında tanımlanan ana fonksiyonlar şunlardır:
Metot	Açıklama
GetDeviceList	Bağlı olan tüm cihazların listesini ve durumlarını döndürür.
ActivateDevice	Seçilen cihazla seri/kablosuz port iletişimini başlatır.
DeactivateDevice	Cihaz bağlantısını keser.
SetPWM	Motora PWM sinyali (1000-2000us) gönderir.
LockMotor / UnlockMotor	Yazılımsal güvenlik kilidini açar veya kapatır.
TareSensor	İtme (Thrust), Tork veya Akım sensörlerini sıfırlar (dara alır).
SetLimitSettings	Maksimum Akım, Sıcaklık veya RPM limitlerini ayarlar.
GetTelemetryStream	(Stream) Canlı sensör verilerini (50Hz) sürekli akış olarak gönderir.
EmergencyStop	Motoru anında durdurur ve kilitler.
❓ Sorun Giderme
Hata: "No connection established" veya "Unavailable"
Dynotis Masaüstü uygulamasının açık olduğundan emin olun.
Uygulamanın alt kısmındaki "API Status" göstergesinin Online olduğunu kontrol edin.
Port 50051'in güvenlik duvarı tarafından engellenmediğinden emin olun.
Hata: "ImportError: No module named..." (Python)
python build_sdk.py komutunu çalıştırdığınızdan emin olun.
generated klasörünün oluştuğunu teyit edin.
Hata: "Cannot find module..." (JavaScript)
node build_sdk.js komutunu çalıştırın.
npm install ile paketlerin yüklendiğinden emin olun.
Dynotis Technology © 2025

