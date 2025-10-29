import os

# Path to src/data
data_dir = r"C:\Users\ELITEBOOK 840\defi-yield-monitor\src\data"

for root, dirs, files in os.walk(data_dir):
    print(f"Directory: {root}")
    for f in files:
        print(f"  {f}")
