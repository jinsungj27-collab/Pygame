"""
Kiro Discord Rich Presence
Shows "Using Kiro" with an elapsed timer on your Discord profile.

Usage:
  1. Replace CLIENT_ID below with your Discord Application ID.
  2. Run this script while Kiro and Discord are both open:
       python kiro_discord_rpc.py
  3. Your Discord profile will show activity with a timer.
  4. Press Ctrl+C to stop.
"""

import time
import sys
import os
import tempfile
from pypresence import Presence

# ─── Replace this with your Application ID from Discord Developer Portal ─────
CLIENT_ID = "1515355140612161748"
# ──────────────────────────────────────────────────────────────────────────────


def main():
    # Prevent multiple instances from stacking
    lock_file = os.path.join(tempfile.gettempdir(), "kiro_discord_rpc.lock")
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                pid = int(f.read().strip())
            # Check if that process is still alive
            os.kill(pid, 0)
            # Process exists — already running, exit silently
            sys.exit(0)
        except (OSError, ValueError):
            # Process is dead or lock is stale, continue
            pass

    # Write our PID to lock file
    with open(lock_file, "w") as f:
        f.write(str(os.getpid()))

    if CLIENT_ID == "YOUR_APPLICATION_ID_HERE":
        print("ERROR: You need to set your CLIENT_ID first!")
        print("1. Go to https://discord.com/developers/applications")
        print("2. Create an application (name it 'Kiro')")
        print("3. Copy the Application ID")
        print("4. Paste it into CLIENT_ID in this script")
        sys.exit(1)

    print("Connecting to Discord...")
    rpc = Presence(CLIENT_ID)

    try:
        rpc.connect()
    except Exception as e:
        print(f"Could not connect to Discord: {e}")
        print("Make sure Discord is running on your computer.")
        sys.exit(1)

    start_time = time.time()

    rpc.update(
        state="Working on a project",
        details="Using Kiro",
        start=start_time,
    )

    print("Discord Rich Presence is active!")
    print("Your profile now shows 'Using Kiro' with a timer.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(15)
    except KeyboardInterrupt:
        print("\nStopping Rich Presence...")
        rpc.close()
        # Clean up lock file
        try:
            os.remove(lock_file)
        except OSError:
            pass
        print("Done.")


if __name__ == "__main__":
    main()
