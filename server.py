import os
import time

def main():
    secret = os.getenv("MYSECRET", "no-secret")
    while True:
        print(f"Working... Using secret: {secret}")
        time.sleep(10)

if __name__ == "__main__":
    main()
