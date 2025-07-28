import os
import time

def main():
    secret = os.getenv("MYSECRET", "no-secret")
    print(f"Using secret: {secret}")
    time.sleep(5)

if __name__ == "__main__":
    main()
