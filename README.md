<?xml version="1.0" encoding="utf-8"?>
<xs:schema targetNamespace="http://tempuri.org/XMLSchema.xsd"
    elementFormDefault="qualified"
    xmlns="http://tempuri.org/XMLSchema.xsd"
    xmlns:mstns="http://tempuri.org/XMLSchema.xsd"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
>


🚀 Dynotis SDKs (Python & JavaScript)
![alt text](https://img.shields.io/badge/version-1.0.0-blue.svg)

![alt text](https://img.shields.io/badge/Python-3.8%2B-yellow.svg)

![alt text](https://img.shields.io/badge/Node.js-16%2B-green.svg)

![alt text](https://img.shields.io/badge/license-MIT-lightgrey.svg)
Bu depo, Dynotis Dinamometre cihazlarını harici yazılımlar üzerinden kontrol etmek ve veri toplamak için geliştirilmiş Python ve JavaScript (Node.js) SDK'larını içerir.
Sistem gRPC protokolü üzerine kuruludur. Dynotis Masaüstü Uygulaması (WPF) bir gRPC Sunucusu olarak çalışır, bu SDK'lar ise İstemci (Client) olarak bağlanır.
📋 İçindekiler
🛠 Gereksinimler
📂 Proje Yapısı
🐍 Python SDK Kullanımı
🟨 JavaScript SDK Kullanımı
📡 API Referansı
❓ Sorun Giderme
🛠 Gereksinimler
SDK'ları sorunsuz kullanabilmek için aşağıdakilerin kurulu olması gerekir:
Dynotis Masaüstü Uygulaması: Uygulama açık olmalı ve gRPC sunucusu çalışıyor olmalıdır.
Varsayılan Port: 50051
Python 3.8+ (Python SDK kullanacaksanız)
Node.js 16+ (JavaScript SDK kullanacaksanız)
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
Not: Eğer requirements.txt yoksa manuel yükleyebilirsiniz:
pip install grpcio grpcio-tools protobuf
2. SDK'yı Derleme (Build)
.proto dosyasından gerekli Python kodlarını üretmek için build scriptini çalıştırın. Bu işlem generated klasörünü oluşturur.
code
Bash
python build_sdk.py
Bu script, Python'daki relative import sorunlarını otomatik olarak düzeltir.
3. Örnek Senaryoyu Çalıştırma
Cihazı bulan, motoru çalıştıran ve verileri okuyan tam test senaryosu:
code
Bash
python examples/full_test_scenario.py
4. Kendi Kodunuzu Yazın
code
Python
from client import DynotisClient

# 1. Bağlan
client = DynotisClient('localhost:50051')

# 2. Cihazı Bul
devices = client.get_device_list()
if not devices:
    print("Cihaz bulunamadı!")
    exit()

dev_id = devices[0].identifier

# 3. Aktif Et ve Motor Kilidini Aç
client.activate_device(dev_id)
client.unlock_motor(dev_id)

# 4. PWM Gönder (Örn: 1200us)
client.set_pwm(dev_id, 1200.0)

# 5. Veri Akışını Başlat
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
Windows kullanıyorsanız dynotis_generate_javascript_sdk.bat dosyasını da çalıştırabilirsiniz.
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

    // 1. Cihazı Bul
    const response = await client.getDeviceList();
    const devId = response.devicesList[0].identifier;

    // 2. Aktif Et
    await client.activateDevice(devId);
    await client.unlockMotor(devId);

    // 3. PWM Ayarla
    await client.setPWM(devId, 1300);

    // 4. Veri Akışı
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
LockMotor	Yazılımsal güvenlik kilidini kapatır (Motor dönmez).
UnlockMotor	Yazılımsal güvenlik kilidini açar.
TareSensor	İtme (Thrust), Tork veya Akım sensörlerini sıfırlar (dara alır).
SetLimitSettings	Maksimum Akım, Sıcaklık veya RPM limitlerini ayarlar.
GetTelemetryStream	(Stream) Canlı sensör verilerini (50Hz) sürekli akış olarak gönderir.
EmergencyStop	Motoru anında durdurur ve kilitler.
❓ Sorun Giderme
<details>
<summary><strong>Hata: "No connection established" veya "Unavailable"</strong></summary>
Dynotis Masaüstü uygulamasının açık olduğundan emin olun.
Uygulamanın alt kısmındaki "API Status" göstergesinin Online olduğunu kontrol edin.
Port 50051'in güvenlik duvarı tarafından engellenmediğinden emin olun.
</details>
<details>
<summary><strong>Hata: "ImportError: No module named..." (Python)</strong></summary>
python build_sdk.py komutunu çalıştırdığınızdan emin olun.
generated klasörünün oluştuğunu teyit edin.
</details>
<details>
<summary><strong>Hata: "Cannot find module..." (JavaScript)</strong></summary>
node build_sdk.js komutunu çalıştırın.
npm install ile paketlerin yüklendiğinden emin olun.
</details>
Dynotis Technology © 2025
</xs:schema>
