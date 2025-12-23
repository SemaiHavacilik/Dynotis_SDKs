# -*- coding: utf-8 -*-
import os
import sys
import subprocess

def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    protos_dir = os.path.abspath(os.path.join(base_dir, '../Protos'))
    out_dir = os.path.join(base_dir, 'generated')
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    print(f"🔨 Building Protos from: {protos_dir}")
    
    try:
        import grpc_tools.protoc
    except ImportError:
        print("❌ Error: grpcio-tools not installed. Run: pip install grpcio-tools")
        return

    proto_file = "DynotisAPI.proto"
    
    command = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"-I{protos_dir}",
        f"--python_out={out_dir}",
        f"--grpc_python_out={out_dir}",
        os.path.join(protos_dir, proto_file)
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Build Failed:\n{result.stderr}")
        return

    # Fix relative imports
    grpc_path = os.path.join(out_dir, "DynotisAPI_pb2_grpc.py")
    with open(grpc_path, 'r') as f:
        content = f.read()
    
    content = content.replace("import DynotisAPI_pb2", "from . import DynotisAPI_pb2")
    
    with open(grpc_path, 'w') as f:
        f.write(content)

    # Create __init__.py
    with open(os.path.join(out_dir, "__init__.py"), "w") as f:
        f.write("from . import DynotisAPI_pb2\nfrom . import DynotisAPI_pb2_grpc\n")

    print("✅ Python SDK Generated Successfully.")

if __name__ == "__main__":
    build()
