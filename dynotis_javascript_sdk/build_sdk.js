const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

function buildProtos() {
    console.log("========================================================");
    console.log("     DYNOTIS JAVASCRIPT SDK GENERATOR (Node.js)");
    console.log("========================================================");

    // --- 1. Yolları Hesapla (Calculate Paths) ---
    const baseDir = __dirname;
    // Protos klasörü bir üst dizinde: Dynotis_SDKs/Protos
    const protosDir = path.resolve(baseDir, '../Protos');
    const outDir = path.join(baseDir, 'generated');
    const protoFileName = 'DynotisAPI.proto';
    const protoFilePath = path.join(protosDir, protoFileName);

    // --- 2. Kontroller (Checks) ---
    console.log(`Proto Path  : ${protosDir}`);
    console.log(`Output Path : ${outDir}`);

    if (!fs.existsSync(protoFilePath)) {
        console.error(`\n❌ ERROR: .proto file not found!\nSearched at: ${protoFilePath}`);
        return;
    }

    // --- 3. Temizlik ve Hazırlık (Cleanup & Setup) ---
    if (!fs.existsSync(outDir)) {
        fs.mkdirSync(outDir, { recursive: true });
        console.log("-> 'generated' directory created.");
    }

    // --- 4. Derleyici Yolunu Bulma (Find Compiler) ---
    // npx yerine doğrudan node_modules içindeki dosyayı hedefliyoruz.
    // Bu yöntem Windows'ta daha kararlıdır.
    const binDir = path.resolve(baseDir, 'node_modules', '.bin');

    // Windows'ta .cmd uzantısı gereklidir, Mac/Linux'ta gerekmez.
    const executableName = process.platform === 'win32' ? 'grpc_tools_node_protoc.cmd' : 'grpc_tools_node_protoc';
    const compilerPath = path.join(binDir, executableName);

    if (!fs.existsSync(compilerPath)) {
        console.error("\n❌ ERROR: 'grpc-tools' not found in node_modules.");
        console.error(`Expected at: ${compilerPath}`);
        console.error("👉 Please run: npm install");
        return;
    }

    // --- 5. Derleme Komutu (Compilation Command) ---
    console.log(`Compiling: ${protoFileName}...`);

    try {
        // Komutu oluşturuyoruz. Tırnak işaretleri ("") dosya yollarındaki boşluklar için önemlidir.
        const cmd = `"${compilerPath}" --js_out=import_style=commonjs,binary:./generated --grpc_out=grpc_js:./generated -I "${protosDir}" "${protoFilePath}"`;

        // Komutu çalıştır
        execSync(cmd, { stdio: 'inherit', cwd: baseDir, shell: true });

        console.log("\n✅ SUCCESS: JavaScript SDK files updated.");
    } catch (error) {
        console.error("\n------------------------------------------------");
        console.error("❌ ERROR: Compilation failed.");
        console.error("------------------------------------------------");
        console.error("\nDetails:", error.message);
        console.error("------------------------------------------------");
    }
}

buildProtos();
