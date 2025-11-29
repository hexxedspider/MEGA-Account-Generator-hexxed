import csv
import subprocess
import time


def main():
    with open("accounts.csv") as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            if not row or row[0] == "Email":
                continue

            time.sleep(1)

            email = row[0].strip()
            password = row[1].strip()

            login = subprocess.run(
                [
                    "megatools",
                    "ls",
                    "-u",
                    email,
                    "-p",
                    password,
                ],
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if "/Root" in login.stdout:
                print(f"\r> [{email}]: Successfully logged in", end="\033[K\n", flush=True)
            else:
                error_msg = login.stderr.strip() if login.stderr else "Unknown error"
                print(f"\r> [{email}]: ERROR - {error_msg}", end="\033[K\n", flush=True)


if __name__ == "__main__":
    main()
