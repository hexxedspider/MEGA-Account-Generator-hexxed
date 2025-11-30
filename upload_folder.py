import csv
import os
import subprocess
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt, IntPrompt
    from rich import box
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False


def load_accounts():
    csv_file = 'accounts.csv'
    if not os.path.exists(csv_file):
        print_message("Error: accounts.csv not found!", "red")
        return []
    
    accounts = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Email') and row['Email'].strip():
                    accounts.append(row)
    except Exception as e:
        print_message(f"Error loading accounts: {e}", "red")
        return []
    
    return accounts


def print_message(message, color=None):
    if RICH_AVAILABLE and color:
        console.print(f"[{color}]{message}[/{color}]")
    else:
        print(message)


def display_accounts_table(accounts):
    if RICH_AVAILABLE:
        table = Table(title="Available Accounts", box=box.ROUNDED)
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("Email", style="cyan")
        table.add_column("Purpose", style="magenta")
        table.add_column("Storage Usage", justify="right")
        
        for idx, account in enumerate(accounts, start=1):
            email = account.get('Email', '').strip()
            purpose = account.get('Purpose', '-').strip() or '-'
            usage = account.get('Usage', '-').strip() or '-'
            
            table.add_row(str(idx), email, purpose, usage)
        
        console.print()
        console.print(table)
        console.print()
    else:
        print("\n" + "="*70)
        print("AVAILABLE ACCOUNTS")
        print("="*70)
        for idx, account in enumerate(accounts, start=1):
            email = account.get('Email', '').strip()
            purpose = account.get('Purpose', '-').strip() or '-'
            usage = account.get('Usage', '-').strip() or '-'
            print(f"{idx:3}. {email:35} | Purpose: {purpose:15} | Usage: {usage}")
        print("="*70 + "\n")


def select_account(accounts):
    display_accounts_table(accounts)
    
    while True:
        try:
            if RICH_AVAILABLE:
                choice = IntPrompt.ask("Select account number", default=1)
            else:
                choice = int(input("Select account number: ").strip() or "1")
            
            if 1 <= choice <= len(accounts):
                return accounts[choice - 1]
            else:
                print_message(f"Please enter a number between 1 and {len(accounts)}", "red")
        except ValueError:
            print_message("Please enter a valid number", "red")
        except KeyboardInterrupt:
            print_message("\n\nCancelled.", "yellow")
            sys.exit(0)


def select_folder():
    if RICH_AVAILABLE:
        print_message("\nEnter the folder path to upload:", "cyan")
        folder_path = Prompt.ask("Folder path")
    else:
        folder_path = input("\nEnter the folder path to upload: ").strip()
    
    folder_path = folder_path.strip('"').strip("'")
    
    if not os.path.exists(folder_path):
        print_message(f"Error: Folder '{folder_path}' does not exist!", "red")
        return None
    
    if not os.path.isdir(folder_path):
        print_message(f"Error: '{folder_path}' is not a folder!", "red")
        return None
    
    return folder_path


def get_remote_path():
    if RICH_AVAILABLE:
        print_message("\nEnter the remote path on MEGA (e.g., /Root/backups):", "cyan")
        print_message("Leave empty to upload to /Root", "dim")
        remote_path = Prompt.ask("Remote path", default="/Root")
    else:
        print("\nEnter the remote path on MEGA (e.g., /Root/backups)")
        print("Leave empty to upload to /Root")
        remote_path = input("Remote path: ").strip() or "/Root"
    
    if not remote_path.startswith('/'):
        remote_path = '/' + remote_path
    
    return remote_path


def upload_folder(folder_path, account, remote_path):
    email = account['Email'].strip()
    password = account['MEGA Password'].strip()
    
    folder_name = os.path.basename(folder_path)
    
    if RICH_AVAILABLE:
        console.print()
        console.print(f"[bold cyan]Uploading '{folder_name}' to {email}...[/bold cyan]")
        console.print(f"[dim]Local path: {folder_path}[/dim]")
        console.print(f"[dim]Remote path: {remote_path}[/dim]")
        console.print()
    else:
        print(f"\nUploading '{folder_name}' to {email}...")
        print(f"Local path: {folder_path}")
        print(f"Remote path: {remote_path}\n")
    
    try:
        result = subprocess.run(
            [
                'megatools',
                'copy',
                '--local', folder_path,
                '--remote', remote_path,
                '-u', email,
                '-p', password
            ],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print_message(f"\n✓ Successfully uploaded '{folder_name}' to {email}!", "green")
            return True
        else:
            print_message(f"\n✗ Upload failed with exit code {result.returncode}", "red")
            print_message("This might be because 'megatools copy' is not available.", "yellow")
            print_message("Trying alternative method with 'megatools put'...", "yellow")
            
            return upload_folder_alternative(folder_path, account, remote_path)
            
    except FileNotFoundError:
        print_message("\n✗ Error: megatools not found!", "red")
        print_message("Please install megatools and add it to your PATH.", "yellow")
        return False
    except Exception as e:
        print_message(f"\n✗ Error during upload: {e}", "red")
        return False


def upload_folder_alternative(folder_path, account, remote_path):
    email = account['Email'].strip()
    password = account['MEGA Password'].strip()
    
    print_message("\nUsing alternative upload method (file by file)...", "cyan")
    
    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                local_file = os.path.join(root, file)
                relative_path = os.path.relpath(local_file, folder_path)
                
                remote_file_path = os.path.join(remote_path, os.path.basename(folder_path), relative_path).replace('\\', '/')
                remote_dir = os.path.dirname(remote_file_path).replace('\\', '/')
                
                print(f"Uploading: {relative_path}")
                
                result = subprocess.run(
                    [
                        'megatools',
                        'put',
                        local_file,
                        '--path', remote_dir,
                        '-u', email,
                        '-p', password
                    ],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    print_message(f"  ✗ Failed to upload {relative_path}", "red")
                    if result.stderr:
                        print(f"  Error: {result.stderr.strip()}")
                else:
                    print_message(f"  ✓ {relative_path}", "green")
        
        print_message("\n✓ Upload completed!", "green")
        return True
        
    except Exception as e:
        print_message(f"\n✗ Error during alternative upload: {e}", "red")
        return False


def main():
    if RICH_AVAILABLE:
        console.print()
        console.print("[bold cyan]MEGA Folder Upload Tool[/bold cyan]")
        console.print("[dim]Upload local folders to your MEGA accounts[/dim]")
        console.print()
    else:
        print("\n" + "="*70)
        print("MEGA FOLDER UPLOAD TOOL")
        print("Upload local folders to your MEGA accounts")
        print("="*70 + "\n")
    
    accounts = load_accounts()
    if not accounts:
        print_message("No accounts found! Please create accounts first.", "red")
        return
    
    account = select_account(accounts)
    
    folder_path = select_folder()
    if not folder_path:
        return
    
    remote_path = get_remote_path()
    
    if RICH_AVAILABLE:
        confirm = Prompt.ask(
            f"\n[yellow]Upload '{os.path.basename(folder_path)}' to {account['Email'].strip()}?[/yellow]",
            choices=["yes", "no"],
            default="yes"
        )
    else:
        confirm = input(f"\nUpload '{os.path.basename(folder_path)}' to {account['Email'].strip()}? (yes/no): ").strip().lower() or "yes"
    
    if confirm != "yes":
        print_message("Upload cancelled.", "yellow")
        return
    
    success = upload_folder(folder_path, account, remote_path)
    
    if success:
        print_message("\n✓ Done!", "green")
    else:
        print_message("\n✗ Upload failed.", "red")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_message("\n\nUpload cancelled by user.", "yellow")
        sys.exit(0)
