import platform
import sys

# Mock platform.system to avoid WMI hang
def my_system():
    return "Windows"

print("Mocking platform.system...")
platform.system = my_system

import time
print("Importing aiohttp...")
start = time.time()
import aiohttp
print(f"aiohttp OK in {time.time() - start:.2f}s")

print("Importing ccxt...")
start = time.time()
import ccxt
print(f"ccxt OK in {time.time() - start:.2f}s")
