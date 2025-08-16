CSP_RULES = {
    "AWS": {
        "score_weights": {
            "bios_boot": 2,
            "uefi_boot": 1,
            "cloud_init": 2,
            "format": 2,
            "refcount_bits": 1,
            "no_backing_file": 1,
            "not_corrupt": 1
        },
        "accepted_formats": ["raw", "vmdk", "vhd", "qcow2"],
        "requires": {
            "cloud_init": True,
            "not_corrupt": True,
            "no_backing_file": True
        }
    },
    "Azure": {
        "score_weights": {
            "uefi_boot": 2,
            "cloud_init": 2,
            "format": 2,
            "no_backing_file": 1,
            "not_corrupt": 1,
            "refcount_bits": 1,
            "lazy_refcounts": 1
        },
        "accepted_formats": ["vhd"],
        "requires": {
            "cloud_init": True,
            "uefi_boot": True
        }
    },
    "GCP": {
        "score_weights": {
            "uefi_boot": 2,
            "cloud_init": 2,
            "format": 2,
            "no_backing_file": 1,
            "not_corrupt": 1,
            "refcount_bits": 1,
            "lazy_refcounts": 1
        },
        "accepted_formats": ["raw", "qcow2"],
        "requires": {
            "cloud_init": True
        }
    },
    "Oracle Cloud": {
        "score_weights": {
            "bios_boot": 2,
            "format": 2,
            "cloud_init": 1,
            "not_corrupt": 1,
            "no_backing_file": 1,
            "refcount_bits": 1,
            "uefi_boot": 1
        },
        "accepted_formats": ["qcow2", "vmdk"],
        "requires": {
            "bios_boot": True,
            "not_corrupt": True
        }
    },
    "Open Source (KVM, Proxmox, etc.)": {
        "score_weights": {
            "bios_boot": 2,
            "uefi_boot": 2,
            "cloud_init": 2,
            "format": 2,
            "refcount_bits": 1,
            "no_backing_file": 1,
            "not_corrupt": 1
        },
        "accepted_formats": ["qcow2", "raw", "vmdk", "vdi"],
        "requires": {
            "not_corrupt": True
        }
    }
}
