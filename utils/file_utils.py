import os

def ensure_directories():
    paths = [
        "outputs",
        "outputs/reports",
        "images",
        "converted"
    ]
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)
