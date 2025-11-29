import csv
import pyperclip
import os

def main():
    csv_file = os.path.join(os.path.dirname(__file__), 'accounts.csv')
    
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return
    
    accounts = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Email') and row['Email'].strip():
                accounts.append({
                    'email': row['Email'].strip(),
                    'password': row['MEGA Password'].strip(),
                    'purpose': row.get('Purpose', '-').strip() or '-',
                    'usage': row.get('Usage', '-').strip() or '-'
                })
    
    if not accounts:
        print("No accounts found in the CSV file!")
        return
    
    print("\n" + "="*70)
    print("AVAILABLE ACCOUNTS")
    print("="*70)
    for idx, account in enumerate(accounts, start=1):
        username = account['email'].split('@')[0]
        purpose = account.get('purpose', '-') or '-'
        usage = account.get('usage', '-') or '-'
        
        info = f"{idx:3}. {username:30}"
        if purpose != '-':
            info += f" | Purpose: {purpose:15}"
        if usage != '-':
            info += f" | Usage: {usage}"
        
        print(info)
    print("="*70)
    
    while True:
        try:
            choice = input("\nEnter account number: ").strip()
            account_num = int(choice)
            
            if 1 <= account_num <= len(accounts):
                selected_account = accounts[account_num - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(accounts)}")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nClosing...")
            return
    
    while True:
        try:
            data_choice = input("\n1 = Email\n2 = Password\n3 = Both (email:password)\nSelect: ").strip()
            
            if data_choice == '1':
                to_copy = selected_account['email']
                data_type = "Email"
                break
            elif data_choice == '2':
                to_copy = selected_account['password']
                data_type = "Password"
                break
            elif data_choice == '3':
                to_copy = f"{selected_account['email']}:{selected_account['password']}"
                data_type = "Both (email:password)"
                break
            else:
                print("Please enter 1, 2, or 3")
        except KeyboardInterrupt:
            print("\n\nClosing...")
            return
    
    pyperclip.copy(to_copy)
    print(f"\n{data_type} copied to clipboard: {to_copy}")

if __name__ == "__main__":
    main()
