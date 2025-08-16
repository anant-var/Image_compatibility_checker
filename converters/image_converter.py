import os
import subprocess

def convert_image_to_raw(input_path, output_dir="outputs/converted"):
    os.makedirs(output_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, base_name + ".raw")

    if os.path.exists(output_path):
        print(f"⚠️ Raw image already exists at: {output_path}")
        return output_path

    try:
        print(f"🔄 Converting image to raw format using qemu-img...")
        cmd = ["qemu-img", "convert", "-O", "raw", input_path, output_path]
        subprocess.run(cmd, check=True)
        print(f"✅ Successfully converted to raw: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print("❌ qemu-img conversion failed.")
        print("Error:", e)
        return input_path
