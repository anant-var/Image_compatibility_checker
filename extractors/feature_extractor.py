import pytsk3
import sys
import os

def extract_features(image_path):
    features = {
        "boot": False,
        "efi": False,
        "cloud_init": False,
        "os": "Unknown"
    }

    def dir_contains(fs, path, target):
        try:
            subdir = fs.open_dir(path=path)
            for entry in subdir:
                name = entry.info.name.name.decode()
                if name.lower() == target.lower():
                    return True
            return False
        except Exception:
            return False

    def file_exists(fs, path):
        try:
            fs.open(path)
            return True
        except Exception:
            return False

    def detect_cloud_init(fs):
        cloud_paths = [
            "/etc/cloud",
            "/etc/cloud/cloud.cfg",
            "/usr/bin/cloud-init",
            "/usr/lib/cloud-init",
            "/lib/systemd/system/cloud-init.service"
        ]
        for path in cloud_paths:
            if file_exists(fs, path) or dir_contains(fs, os.path.dirname(path), os.path.basename(path)):
                print(f"✅ Detected cloud-init path: {path}")
                return True
        return False

    try:
        img = pytsk3.Img_Info(image_path)
        volume = pytsk3.Volume_Info(img)

        for part in volume:
            desc = part.desc.decode()
            if part.len <= 2048 or 'Unallocated' in desc:
                continue

            offset = part.start * 512  # sector size
            print(f"🔍 Checking partition: {desc}, Offset: {offset}")
            try:
                fs = pytsk3.FS_Info(img, offset=offset)
            except Exception as e:
                print(f"❌ Skipping non-filesystem partition at offset {offset}")
                continue

            # BIOS boot detection
            if dir_contains(fs, "/", "boot"):
                features["boot"] = True
            if dir_contains(fs, "/boot", "grub") or dir_contains(fs, "/boot", "grub2"):
                features["boot"] = True

            # EFI detection
            if dir_contains(fs, "/", "EFI") or dir_contains(fs, "/efi", "BOOT"):
                features["efi"] = True

            # cloud-init detection
            if detect_cloud_init(fs):
                features["cloud_init"] = True

            # OS Detection
            if features["os"] == "Unknown":
                try:
                    file = fs.open("/etc/os-release")
                    data = file.read_random(0, file.info.meta.size).decode(errors="ignore")
                    for line in data.splitlines():
                        if line.startswith("PRETTY_NAME="):
                            features["os"] = line.split("=", 1)[-1].strip('"')
                            break
                except:
                    try:
                        issue = fs.open("/etc/issue")
                        data = issue.read_random(0, issue.info.meta.size).decode(errors="ignore")
                        features["os"] = data.strip().split("\\")[0]
                    except:
                        pass

    except Exception as e:
        print("❌ Error during pytsk3 extraction:", e)

    return features
