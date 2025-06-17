import os

def check_file_for_null_bytes(filepath):
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
            if b'\x00' in content:
                print(f"Found null bytes in: {filepath}")
                return True
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    return False

def scan_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                check_file_for_null_bytes(filepath)

if __name__ == "__main__":
    scan_directory("app") 