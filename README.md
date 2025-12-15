<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dynotis SDKs Documentation</title>
    <style>
        :root {
            --primary-color: #0366d6;
            --text-color: #24292e;
            --bg-color: #ffffff;
            --code-bg: #282c34;
            --code-text: #abb2bf;
            --border-color: #e1e4e8;
            --accent-color: #f6f8fa;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--bg-color);
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        /* Header & Badges */
        header {
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
            margin-bottom: 30px;
        }

        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .badges {
            display: flex;
            gap: 5px;
            margin-bottom: 15px;
        }

        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            color: white;
        }
        .badge-blue { background-color: #007ec6; }
        .badge-yellow { background-color: #dfb317; color: #000; }
        .badge-green { background-color: #4c1; }
        .badge-grey { background-color: #555; }

        /* Typography */
        h2 {
            margin-top: 40px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
        }

        h3 {
            margin-top: 25px;
            color: #444;
        }

        a { color: var(--primary-color); text-decoration: none; }
        a:hover { text-decoration: underline; }

        /* Code Blocks */
        pre {
            background-color: var(--code-bg);
            color: var(--code-text);
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 0.9rem;
            margin: 15px 0;
        }

        code {
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        }

        p code, li code {
            background-color: rgba(27,31,35,0.05);
            padding: 2px 4px;
            border-radius: 3px;
            color: #d73a49; /* Reddish for inline code */
            font-size: 0.9em;
        }

        /* Table */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }

        th, td {
            border: 1px solid var(--border-color);
            padding: 12px;
            text-align: left;
        }

        th {
            background-color: var(--accent-color);
            font-weight: 600;
        }

        tr:nth-child(even) {
            background-color: #fcfcfc;
        }

        /* Troubleshooting Details */
        details {
            background-color: var(--accent-color);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 10px;
            margin-bottom: 10px;
        }

        summary {
            cursor: pointer;
            font-weight: 600;
            outline: none;
        }

        details[open] summary {
            margin-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 5px;
        }

        /* Footer */
        footer {
            margin-top: 60px;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
            text-align: center;
            color: #666;
            font-size: 0.9rem;
        }

        /* Syntax Highlighting Simulation */
        .kwd { color: #c678dd; } /* Keyword */
        .str { color: #98c379; } /* String */
        .com { color: #5c6370; font-style: italic; } /* Comment */
        .func { color: #61afef; } /* Function */
        .num { color: #d19a66; } /* Number */
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>🚀 Dynotis SDKs</h1>
        <div class="badges">
            <span class="badge badge-blue">v1.0.0</span>
            <span class="badge badge-yellow">Python 3.8+</span>
            <span class="badge badge-green">Node.js 16+</span>
            <span class="badge badge-grey">MIT License</span>
        </div>
        <p>
            Bu depo, <strong>Dynotis Dinamometre</strong> cihazlarını harici yazılımlar üzerinden kontrol etmek ve veri toplamak için geliştirilmiş 
            <strong>Python</strong> ve <strong>JavaScript (Node.js)</strong> SDK'larını içerir.
        </p>
        <p>
            Sistem <strong>gRPC</strong> protokolü üzerine kuruludur. Dynotis Masaüstü Uygulaması (WPF) bir gRPC Sunucusu olarak çalışır, 
            bu SDK'lar ise İstemci (Client) olarak bağlanır.
        </p>
    </header>

    <nav>
        <h3>📋 İçindekiler</h3>
        <ul>
            <li><a href="#requirements">Gereksinimler</a></li>
            <li><a href="#structure">Proje Yapısı</a></li>
            <li><a href="#python">Python SDK Kullanımı</a></li>
            <li><a href="#javascript">JavaScript SDK Kullanımı</a></li>
            <li><a href="#api">API Referansı</a></li>
            <li><a href="#troubleshooting">Sorun Giderme</a></li>
        </ul>
    </nav>

    <section id="requirements">
        <h2>🛠 Gereksinimler</h2>
        <p>SDK'ları kullanabilmek için aşağıdakilerin kurulu olması gerekir:</p>
        <ol>
            <li><strong>Dynotis Masaüstü Uygulaması:</strong> Uygulama açık olmalı ve gRPC sunucusu çalışıyor olmalıdır (Varsayılan Port: <code>50051</code>).</li>
            <li><strong>Python 3.8+</strong> (Python SDK için)</li>
            <li><strong>Node.js 16+</strong> (JavaScript SDK için)</li>
        </ol>
    </section>

    <section id="structure">
        <h2>📂 Proje Yapısı</h2>
<pre>
Dynotis_SDKs/
├── Protos/
│   └── DynotisAPI.proto          <span class="com"># Tüm sistemin ortak sözleşme dosyası (gRPC)</span>
├── dynotis_javascript_sdk/       <span class="com"># Node.js İstemcisi</span>
│   ├── examples/                 <span class="com"># Örnek senaryolar</span>
│   ├── build_sdk.js              <span class="com"># Proto dosyasını JS'e derleyen script</span>
│   └── client.js                 <span class="com"># Kullanımı kolaylaştırılmış Wrapper sınıfı</span>
└── dynotis_python_sdk/           <span class="com"># Python İstemcisi</span>
    ├── examples/                 <span class="com"># Örnek senaryolar</span>
    ├── build_sdk.py              <span class="com"># Proto dosyasını Python'a derleyen script</span>
    └── client.py                 <span class="com"># Kullanımı kolaylaştırılmış Wrapper sınıfı</span>
</pre>
    </section>

    <section id="python">
        <h2>🐍 Python SDK Kullanımı</h2>
        <p>Python ile Dynotis cihazlarını kontrol etmek için aşağıdaki adımları izleyin.</p>

        <h3>1. Kurulum</h3>
        <p>Gerekli kütüphaneleri (<code>grpcio</code>, <code>grpcio-tools</code>, <code>protobuf</code>) yükleyin:</p>
<pre>
cd dynotis_python_sdk
pip install -r requirements.txt

<span class="com"># Eğer requirements.txt yoksa:</span>
<span class="com"># pip install grpcio grpcio-tools protobuf</span>
</pre>

        <h3>2. SDK'yı Derleme (Build)</h3>
        <p><code>.proto</code> dosyasından gerekli Python kodlarını üretmek için build scriptini çalıştırın. Bu işlem <code>generated</code> klasörünü oluşturur.</p>
<pre>
python build_sdk.py
</pre>
        <p><em>Not: Bu script, Python'daki relative import sorunlarını otomatik olarak düzeltir.</em></p>

        <h3>3. Örnek Senaryoyu Çalıştırma</h3>
        <p>Cihazı bulan, motoru çalıştıran ve verileri okuyan tam test senaryosu:</p>
<pre>
python examples/full_test_scenario.py
</pre>

        <h3>4. Kendi Kodunuzu Yazın</h3>
<pre>
<span class="kwd">from</span> client <span class="kwd">import</span> DynotisClient

<span class="com"># Bağlan</span>
client = <span class="func">DynotisClient</span>(<span class="str">'localhost:50051'</span>)

<span class="com"># Cihazları Listele</span>
devices = client.<span class="func">get_device_list</span>()
dev_id = devices[<span class="num">0</span>].identifier

<span class="com"># Aktif Et ve Motoru Aç</span>
client.<span class="func">activate_device</span>(dev_id)
client.<span class="func">unlock_motor</span>(dev_id)

<span class="com"># PWM Gönder (Örn: 1200us)</span>
client.<span class="func">set_pwm</span>(dev_id, <span class="num">1200.0</span>)

<span class="com"># Veri Akışını Başlat</span>
stream = client.<span class="func">get_telemetry_stream</span>(dev_id)
<span class="kwd">for</span> data <span class="kwd">in</span> stream:
    <span class="func">print</span>(f<span class="str">"RPM: {data.sensors.rpm} | Thrust: {data.sensors.thrust_gf} g"</span>)
</pre>
    </section>

    <section id="javascript">
        <h2>🟨 JavaScript SDK Kullanımı</h2>
        <p>Node.js ile entegrasyon sağlamak için aşağıdaki adımları izleyin.</p>

        <h3>1. Kurulum</h3>
        <p>Bağımlılıkları yükleyin:</p>
<pre>
cd dynotis_javascript_sdk
npm install
</pre>

        <h3>2. SDK'yı Derleme (Build)</h3>
        <p><code>.proto</code> dosyasından gerekli JS kodlarını üretmek için:</p>
<pre>
node build_sdk.js
<span class="com"># Veya Windows kullanıyorsanız:</span>
<span class="com"># dynotis_generate_javascript_sdk.bat</span>
</pre>

        <h3>3. Örnek Senaryoyu Çalıştırma</h3>
<pre>
node examples/full_test_scenario.js
</pre>

        <h3>4. Kendi Kodunuzu Yazın</h3>
<pre>
<span class="kwd">const</span> { DynotisClient } = <span class="func">require</span>(<span class="str">'./client'</span>);

<span class="kwd">async function</span> <span class="func">run</span>() {
    <span class="kwd">const</span> client = <span class="kwd">new</span> <span class="func">DynotisClient</span>(<span class="str">'localhost:50051'</span>);

    <span class="com">// Cihazı Bul</span>
    <span class="kwd">const</span> response = <span class="kwd">await</span> client.<span class="func">getDeviceList</span>();
    <span class="kwd">const</span> devId = response.devicesList[<span class="num">0</span>].identifier;

    <span class="com">// Aktif Et</span>
    <span class="kwd">await</span> client.<span class="func">activateDevice</span>(devId);
    <span class="kwd">await</span> client.<span class="func">unlockMotor</span>(devId);

    <span class="com">// PWM Ayarla</span>
    <span class="kwd">await</span> client.<span class="func">setPWM</span>(devId, <span class="num">1300</span>);

    <span class="com">// Veri Akışı</span>
    <span class="kwd">const</span> stream = client.<span class="func">getTelemetryStream</span>(devId);
    stream.<span class="func">on</span>(<span class="str">'data'</span>, (data) => {
        <span class="kwd">const</span> sensors = data.<span class="func">getSensors</span>();
        console.<span class="func">log</span>(`Thrust: ${sensors.<span class="func">getThrustGf</span>()} g`);
    });
}

<span class="func">run</span>();
</pre>
    </section>

    <section id="api">
        <h2>📡 API Referansı</h2>
        <p><code>DynotisAPI.proto</code> dosyasında tanımlanan ana fonksiyonlar şunlardır:</p>
        <table>
            <thead>
                <tr>
                    <th>Metot</th>
                    <th>Açıklama</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><code>GetDeviceList</code></td>
                    <td>Bağlı olan tüm cihazların listesini ve durumlarını döndürür.</td>
                </tr>
                <tr>
                    <td><code>ActivateDevice</code></td>
                    <td>Seçilen cihazla seri/kablosuz port iletişimini başlatır.</td>
                </tr>
                <tr>
                    <td><code>DeactivateDevice</code></td>
                    <td>Cihaz bağlantısını keser.</td>
                </tr>
                <tr>
                    <td><code>SetPWM</code></td>
                    <td>Motora PWM sinyali (1000-2000us) gönderir.</td>
                </tr>
                <tr>
                    <td><code>LockMotor</code> / <code>UnlockMotor</code></td>
                    <td>Yazılımsal güvenlik kilidini açar veya kapatır.</td>
                </tr>
                <tr>
                    <td><code>TareSensor</code></td>
                    <td>İtme (Thrust), Tork veya Akım sensörlerini sıfırlar (dara alır).</td>
                </tr>
                <tr>
                    <td><code>SetLimitSettings</code></td>
                    <td>Maksimum Akım, Sıcaklık veya RPM limitlerini ayarlar.</td>
                </tr>
                <tr>
                    <td><code>GetTelemetryStream</code></td>
                    <td><strong>(Stream)</strong> Canlı sensör verilerini (50Hz) sürekli akış olarak gönderir.</td>
                </tr>
                <tr>
                    <td><code>EmergencyStop</code></td>
                    <td>Motoru anında durdurur ve kilitler.</td>
                </tr>
            </tbody>
        </table>
    </section>

    <section id="troubleshooting">
        <h2>❓ Sorun Giderme</h2>
        
        <details>
            <summary>Hata: "No connection established" veya "Unavailable"</summary>
            <ul>
                <li>Dynotis Masaüstü uygulamasının açık olduğundan emin olun.</li>
                <li>Uygulamanın alt kısmındaki "API Status" göstergesinin <strong>Online</strong> olduğunu kontrol edin.</li>
                <li>Port <code>50051</code>'in güvenlik duvarı tarafından engellenmediğinden emin olun.</li>
            </ul>
        </details>

        <details>
            <summary>Hata: "ImportError: No module named..." (Python)</summary>
            <ul>
                <li><code>python build_sdk.py</code> komutunu çalıştırdığınızdan emin olun.</li>
                <li><code>generated</code> klasörünün oluştuğunu teyit edin.</li>
            </ul>
        </details>

        <details>
            <summary>Hata: "Cannot find module..." (JavaScript)</summary>
            <ul>
                <li><code>node build_sdk.js</code> komutunu çalıştırın.</li>
                <li><code>npm install</code> ile paketlerin yüklendiğinden emin olun.</li>
            </ul>
        </details>
    </section>

    <footer>
        <p><strong>Dynotis Technology</strong> &copy; 2025</p>
    </footer>
</div>

</body>
</html>
