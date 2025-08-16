import subprocess
import json
import os

def extract_image_format_info(image_path):
    try:
        result = subprocess.run(
            ["qemu-img", "info", "--output", "json", image_path],
            capture_output=True, text=True, check=True
        )
        info = json.loads(result.stdout)

        # Extract top-level fields
        format_info = {
            "filename": os.path.basename(image_path),
            "format": info.get("format"),
            "virtual_size_bytes": info.get("virtual-size"),
            "virtual_size_human": human_readable_size(info.get("virtual-size", 0)),
            "actual_size_bytes": info.get("actual-size"),
            "actual_size_human": human_readable_size(info.get("actual-size", 0)),
            "dirty_flag": info.get("dirty-flag"),
            "cluster_size": info.get("cluster-size"),
            "backing_file": info.get("backing-file"),
        }

        # Include format-specific details if available
        if "format-specific" in info:
            fmt = info["format-specific"]
            format_info["format_specific_type"] = fmt.get("type")
            format_info.update(fmt.get("data", {}))  # merge format-specific fields

        return format_info
    except subprocess.CalledProcessError as e:
        print("Error running qemu-img info:", e.stderr)
        return {"error": "Failed to extract image info"}
    except json.JSONDecodeError:
        print("❌ Failed to parse qemu-img output")
        return {"error": "Invalid JSON output from qemu-img"}

def human_readable_size(size_in_bytes):
    if size_in_bytes is None:
        return "Unknown"
    elif size_in_bytes >= 1024**3:
        return f"{size_in_bytes / (1024**3):.2f} GB"
    elif size_in_bytes >= 1024**2:
        return f"{size_in_bytes / (1024**2):.2f} MB"
    elif size_in_bytes >= 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    else:
        return f"{size_in_bytes} B"
