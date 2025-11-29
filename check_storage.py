import csv
import subprocess
import re
import os

def parse_storage_output(output):
    lines = output.strip().split('\n')
    for line in lines:
        if 'Total' in line or 'Cloud' in line:
            parts = re.findall(r'[\d.]+\s*[KMGT]?B', line)
            if len(parts) >= 2:
                used = parts[0].strip()
                total = parts[1].strip()
                return used, total
    return None, None

def convert_to_bytes(size_str):
    size_str = size_str.strip().upper()
    match = re.match(r'([\d.]+)\s*([KMGT]?B)', size_str)
    if not match:
        return 0
    
    value = float(match.group(1))
    unit = match.group(2)
    
    multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4
    }
    
    return int(value * multipliers.get(unit, 1))

def bytes_to_readable(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"

def check_storage():
    csv_file = 'accounts.csv'
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return
    
    accounts = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Email') and row['Email'].strip():
                accounts.append(row)
    
    if not accounts:
        print("No accounts found in the CSV file!")
        return
    
    print("\n" + "="*70)
    print("MEGA ACCOUNT STORAGE CHECKER")
    print("="*70 + "\n")
    
    total_used_bytes = 0
    total_available_bytes = 0
    successful_checks = 0
    updated_accounts = []
    
    for idx, account in enumerate(accounts, start=1):
        email = account['Email'].strip()
        password = account['MEGA Password'].strip()
        
        print(f"[{idx}/{len(accounts)}] Checking {email}...", end=' ', flush=True)
        
        try:
            result = subprocess.run(
                ['megatools', 'df', '-u', email, '-p', password],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                used, total = parse_storage_output(result.stdout)
                
                if used and total:
                    used_bytes = convert_to_bytes(used)
                    total_bytes = convert_to_bytes(total)
                    percentage = (used_bytes / total_bytes * 100) if total_bytes > 0 else 0
                    
                    usage_str = f"{used}/{total} ({percentage:.1f}%)"
                    account['Usage'] = usage_str
                    
                    total_used_bytes += used_bytes
                    total_available_bytes += total_bytes
                    successful_checks += 1
                    
                    print(f"{usage_str}")
                else:
                    account['Usage'] = "Error parsing"
                    print("Could not parse storage info")
            else:
                account['Usage'] = "Login failed"
                print("Authentication failed")
                
        except subprocess.TimeoutExpired:
            account['Usage'] = "Timeout"
            print("Request timeout")
        except FileNotFoundError:
            print("\n\nError: megatools not found! Please install megatools and add to PATH.")
            return
        except Exception as e:
            account['Usage'] = "Error"
            print(f"Error: {str(e)[:30]}")
        
        updated_accounts.append(account)
    
    print("\n" + "-"*70)
    print("Updating accounts.csv with storage data...")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Email', 'MEGA Password', 'Usage', 'Mail.tm Password', 'Mail.tm ID', 'Purpose']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_accounts)
    
    print("CSV updated successfully!")
    
    print("\n" + "="*70)
    print("STORAGE SUMMARY")
    print("="*70)
    print(f"Total Accounts:     {len(accounts)}")
    print(f"Successful Checks:  {successful_checks}")
    print(f"Failed Checks:      {len(accounts) - successful_checks}")
    
    if successful_checks > 0:
        print(f"\nTotal Used:         {bytes_to_readable(total_used_bytes)}")
        print(f"Total Available:    {bytes_to_readable(total_available_bytes)}")
        overall_percentage = (total_used_bytes / total_available_bytes * 100) if total_available_bytes > 0 else 0
        print(f"Overall Usage:      {overall_percentage:.1f}%")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    check_storage()
