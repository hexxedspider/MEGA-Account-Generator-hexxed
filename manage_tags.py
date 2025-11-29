import csv
import os

def load_accounts():
    csv_file = 'accounts.csv'
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return None
    
    accounts = []
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('Email') and row['Email'].strip():
                accounts.append(row)
    return accounts

def save_accounts(accounts):
    csv_file = 'accounts.csv'
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['Email', 'MEGA Password', 'Usage', 'Mail.tm Password', 'Mail.tm ID', 'Purpose']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(accounts)

def list_accounts(accounts, show_purpose=True):
    if not accounts:
        print("No accounts found!")
        return
    
    print("\n" + "="*70)
    print("ACCOUNTS LIST")
    print("="*70)
    
    for idx, account in enumerate(accounts, start=1):
        username = account['Email'].split('@')[0]
        purpose = account.get('Purpose', '-').strip() or '-'
        usage = account.get('Usage', '-').strip() or '-'
        
        if show_purpose:
            print(f"{idx:3}. {username:30} | Purpose: {purpose:15} | Usage: {usage}")
        else:
            print(f"{idx:3}. {username}")
    
    print("="*70 + "\n")

def tag_account(accounts):
    list_accounts(accounts, show_purpose=True)
    
    try:
        selection = input("Enter account number(s) to tag (comma-separated or range like 1-3): ").strip()
        
        indices = []
        for part in selection.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                indices.extend(range(start-1, end))
            else:
                indices.append(int(part) - 1)
        
        valid_indices = [i for i in indices if 0 <= i < len(accounts)]
        if not valid_indices:
            print("Invalid selection!")
            return
        
        purpose = input("\nEnter purpose/tag for selected account(s): ").strip()
        
        if not purpose:
            print("Purpose cannot be empty!")
            return
        
        updated = 0
        for idx in valid_indices:
            accounts[idx]['Purpose'] = purpose
            updated += 1
        
        save_accounts(accounts)
        print(f"\nSuccessfully tagged {updated} account(s) with purpose: '{purpose}'")
        
    except (ValueError, IndexError) as e:
        print(f"Invalid input: {e}")
    except KeyboardInterrupt:
        print("\n\nCancelled.")

def clear_tags(accounts):
    list_accounts(accounts, show_purpose=True)
    
    try:
        selection = input("Enter account number(s) to clear tags (comma-separated or 'all'): ").strip().lower()
        
        if selection == 'all':
            for account in accounts:
                account['Purpose'] = '-'
            save_accounts(accounts)
            print(f"\nCleared tags from all {len(accounts)} accounts")
            return
        
        indices = []
        for part in selection.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                indices.extend(range(start-1, end))
            else:
                indices.append(int(part) - 1)
        
        updated = 0
        for idx in indices:
            if 0 <= idx < len(accounts):
                accounts[idx]['Purpose'] = '-'
                updated += 1
        
        save_accounts(accounts)
        print(f"\nCleared tags from {updated} account(s)")
        
    except (ValueError, IndexError) as e:
        print(f"Invalid input: {e}")
    except KeyboardInterrupt:
        print("\n\nCancelled.")

def filter_by_purpose(accounts):
    purposes = set()
    for account in accounts:
        purpose = account.get('Purpose', '-').strip() or '-'
        if purpose != '-':
            purposes.add(purpose)
    
    if not purposes:
        print("\nNo accounts have been tagged yet!")
        return
    
    print("\nAvailable purposes:")
    purpose_list = sorted(purposes)
    for idx, purpose in enumerate(purpose_list, start=1):
        count = sum(1 for a in accounts if a.get('Purpose', '').strip() == purpose)
        print(f"  {idx}. {purpose} ({count} account(s))")
    
    try:
        choice = input("\nEnter purpose number to filter: ").strip()
        purpose_idx = int(choice) - 1
        
        if 0 <= purpose_idx < len(purpose_list):
            selected_purpose = purpose_list[purpose_idx]
            filtered = [a for a in accounts if a.get('Purpose', '').strip() == selected_purpose]
            
            print(f"\n{'='*70}")
            print(f"ACCOUNTS WITH PURPOSE: {selected_purpose}")
            print(f"{'='*70}")
            
            for idx, account in enumerate(filtered, start=1):
                username = account['Email'].split('@')[0]
                usage = account.get('Usage', '-').strip() or '-'
                print(f"{idx:3}. {username:30} | Usage: {usage}")
            
            print(f"{'='*70}\n")
        else:
            print("Invalid selection!")
            
    except (ValueError, IndexError) as e:
        print(f"Invalid input: {e}")
    except KeyboardInterrupt:
        print("\n\nCancelled.")

def show_by_purpose(accounts):
    if not accounts:
        print("No accounts found!")
        return
    
    groups = {}
    for account in accounts:
        purpose = account.get('Purpose', '-').strip() or '-'
        if purpose not in groups:
            groups[purpose] = []
        groups[purpose].append(account)
    
    print("\n" + "="*70)
    print("ACCOUNTS GROUPED BY PURPOSE")
    print("="*70 + "\n")
    
    sorted_keys = sorted(groups.keys(), key=lambda x: (x == '-', x))
    
    for purpose in sorted_keys:
        purpose_accounts = groups[purpose]
        print(f"📁 {purpose} ({len(purpose_accounts)} account(s)):")
        
        for account in purpose_accounts:
            username = account['Email'].split('@')[0]
            usage = account.get('Usage', '-').strip() or '-'
            print(f"   • {username:30} | Usage: {usage}")
        
        print()
    
    print("="*70 + "\n")

def main():
    while True:
        accounts = load_accounts()
        if accounts is None:
            return
        
        print("\n" + "="*70)
        print("MEGA ACCOUNT TAG MANAGER")
        print("="*70)
        print("\n1. Tag account(s)")
        print("2. Clear tag(s)")
        print("3. Filter by purpose")
        print("4. Show all (grouped by purpose)")
        print("5. List all accounts")
        print("6. Exit")
        
        try:
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                tag_account(accounts)
            elif choice == '2':
                clear_tags(accounts)
            elif choice == '3':
                filter_by_purpose(accounts)
            elif choice == '4':
                show_by_purpose(accounts)
            elif choice == '5':
                list_accounts(accounts)
            elif choice == '6':
                print("\nExiting...")
                break
            else:
                print("Invalid option!")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break

if __name__ == "__main__":
    main()
