# data/fetch_all_data.py
import subprocess
import sys

scripts = [
    "data/fetch_bmd_data.py",
    "data/fetch_bwdb_data.py",
    "data/fetch_iot_data.py",
    "data/fetch_satellite_data.py"
]

processes = []
for script in scripts:
    print(f"🚀 Starting {script}...")
    p = subprocess.Popen([sys.executable, script])
    processes.append(p)

print("✅ All fetchers started! Press Ctrl+C to stop all.")
try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("\n🛑 Stopping all fetchers...")
    for p in processes:
        p.terminate()
