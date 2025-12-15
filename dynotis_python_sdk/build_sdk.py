# -*- coding: utf-8 -*-
import os
import sys
import shutil

def build_protos():
    print("========================================================")
    print("     DYNOTIS PYTHON SDK GENERATOR (Python Native)")
    print("========================================================")

    # --- 1. Check Required Libraries ---
    try:
        from grpc_tools import protoc
    except ImportError:
        print("ERROR: 'grpcio-tools' library is missing.")
        print("Please run: pip install grpcio-tools")
        input("Press Enter to exit...")
        return

    # --- 2. Calculate Directory Paths ---
    # The directory where this script is located (dynotis_python_sdk)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Protos directory: One level up from this script
    # Structure: Dynotis_SDKs/dynotis_python_sdk/build_sdk.py
    # Target:    Dynotis_SDKs/Protos
    protos_dir = os.path.abspath(os.path.join(base_dir, '../Protos'))
    
    # Output directory (generated)
    out_dir = os.path.join(base_dir, 'generated')

    proto_file_name = 'DynotisAPI.proto'
    proto_path = os.path.join(protos_dir, proto_file_name)

    # --- 3. Checks and Cleanup ---
    print(f"Proto Path  : {protos_dir}")
    print(f"Output Path : {out_dir}")

    if not os.path.exists(proto_path):
        print(f"\n❌ ERROR: .proto file not found!\nSearched at: {proto_path}")
        input("Press Enter to exit...")
        return

    # Create/Clear generated directory
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        print("-> 'generated' directory created.")

    # --- 4. Compilation Command ---
    command = [
        'grpc_tools.protoc',
        f'-I{protos_dir}',
        f'--python_out={out_dir}',
        f'--grpc_python_out={out_dir}',
        proto_file_name
    ]

    print(f"Compiling: {proto_file_name}...")
    exit_code = protoc.main(command)

    if exit_code != 0:
        print("\n❌ ERROR: Compilation failed.")
        input("Press Enter to exit...")
        return

    # --- 5. Fix Import Error (Critical Step) ---
    # Protoc generates 'import DynotisAPI_pb2', but Python 3 requires 'from . import ...'
    grpc_file = os.path.join(out_dir, 'DynotisAPI_pb2_grpc.py')
    
    if os.path.exists(grpc_file):
        with open(grpc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = content.replace('import DynotisAPI_pb2', 'from . import DynotisAPI_pb2')
        
        with open(grpc_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("-> Relative import error fixed.")

    # Create __init__.py to make it a package
    init_file = os.path.join(out_dir, '__init__.py')
    with open(init_file, 'w') as f:
        pass

    print("\n✅ SUCCESS: Python SDK files updated.")

if __name__ == "__main__":
    build_protos()
    # Keep window open if double-clicked
    input("Press Enter to exit...")
