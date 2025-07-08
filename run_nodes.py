import subprocess
import time
import sys

# Script to launch 3 nodes as separate processes

def run_node(node_id):
    return subprocess.Popen([
        sys.executable, "main.py", "--id", str(node_id)
    ])

def main():
    processes = []
    for node_id in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        print(f"Starting node {node_id}")
        p = run_node(node_id)
        processes.append(p)
        time.sleep(1)  # Stagger startup for clarity
    try:
        print("All nodes started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all nodes...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.wait()
        print("All nodes stopped.")

if __name__ == "__main__":
    main()
