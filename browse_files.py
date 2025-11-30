import csv
import os
import subprocess
import sys
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.prompt import Prompt, IntPrompt, Confirm
    from rich.panel import Panel
    from rich.text import Text
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


def parse_file_listing(output, current_path):
    """Parse megatools ls output to extract file/folder information."""
    items = []
    lines = output.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('WARNING'):
            continue
        
        parts = line.split(maxsplit=3)
        if len(parts) < 4:
            continue
        
        permissions = parts[0]
        size = parts[1]
        date_time = parts[2]
        path = parts[3]
        
        # Skip the current directory itself
        if path == current_path or path == current_path.rstrip('/'):
            continue
        
        # Determine if it's a directory
        is_dir = permissions.startswith('d')
        
        # Get just the name (last part of path)
        name = path.split('/')[-1]
        
        # Skip if empty name
        if not name:
            continue
        
        items.append({
            'name': name,
            'full_path': path,
            'is_dir': is_dir,
            'size': size,
            'date': date_time,
            'permissions': permissions
        })
    
    return items


def list_files(email, password, path="/Root"):
    """List files and folders at the given path."""
    try:
        result = subprocess.run(
            ['megatools', 'ls', '-l', '-u', email, '-p', password, path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print_message(f"Error listing files: {result.stderr}", "red")
            return None
        
        return parse_file_listing(result.stdout, path)
        
    except FileNotFoundError:
        print_message("Error: megatools not found!", "red")
        print_message("Please install megatools and add it to your PATH.", "yellow")
        return None
    except subprocess.TimeoutExpired:
        print_message("Request timed out.", "red")
        return None
    except Exception as e:
        print_message(f"Error: {e}", "red")
        return None


def display_files_table(items, current_path):
    """Display files and folders in a formatted table."""
    if RICH_AVAILABLE:
        console.print(f"\n[bold cyan]Current Path:[/bold cyan] [white]{current_path}[/white]")
        
        table = Table(box=box.ROUNDED, show_lines=False)
        table.add_column("#", style="dim", width=4, justify="right")
        table.add_column("Type", width=6, justify="center")
        table.add_column("Name", style="cyan")
        table.add_column("Size", justify="right", style="yellow")
        table.add_column("Modified", style="dim")
        
        # Add parent directory option if not at root
        if current_path != "/Root":
            table.add_row("0", "📁", "..", "-", "-")
        
        for idx, item in enumerate(items, start=1):
            type_icon = "📁" if item['is_dir'] else "📄"
            name_style = "[bold cyan]" if item['is_dir'] else "[white]"
            name = f"{name_style}{item['name']}[/]"
            
            table.add_row(
                str(idx),
                type_icon,
                name,
                item['size'],
                item['date']
            )
        
        console.print()
        console.print(table)
        console.print()
    else:
        print(f"\nCurrent Path: {current_path}")
        print("="*70)
        
        if current_path != "/Root":
            print(f"  0. [DIR]  ..")
        
        for idx, item in enumerate(items, start=1):
            type_str = "[DIR] " if item['is_dir'] else "[FILE]"
            print(f"{idx:3}. {type_str} {item['name']:40} {item['size']:>10} {item['date']}")
        
        print("="*70 + "\n")


def download_file(email, password, remote_path, local_path=None):
    """Download a file from MEGA."""
    if not local_path:
        local_path = os.path.join(os.getcwd(), os.path.basename(remote_path))
    
    print_message(f"\nDownloading to: {local_path}", "cyan")
    
    try:
        result = subprocess.run(
            ['megatools', 'get', '-u', email, '-p', password, '--path', os.path.dirname(local_path), remote_path],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print_message(f"✓ Downloaded successfully!", "green")
            return True
        else:
            print_message(f"✗ Download failed", "red")
            return False
            
    except Exception as e:
        print_message(f"Error downloading: {e}", "red")
        return False


def file_browser(account):
    """Interactive file browser for MEGA account."""
    email = account['Email'].strip()
    password = account['MEGA Password'].strip()
    current_path = "/Root"
    
    if RICH_AVAILABLE:
        header = Panel(
            f"[bold cyan]MEGA File Browser[/bold cyan]\n[dim]{email}[/dim]",
            box=box.DOUBLE,
            border_style="blue"
        )
        console.print()
        console.print(header)
    else:
        print("\n" + "="*70)
        print(f"MEGA FILE BROWSER - {email}")
        print("="*70)
    
    while True:
        items = list_files(email, password, current_path)
        
        if items is None:
            print_message("Failed to list files. Returning to account selection.", "red")
            return
        
        if not items and current_path == "/Root":
            print_message("No files found in this account.", "yellow")
            if RICH_AVAILABLE:
                if not Confirm.ask("Continue browsing?", default=False):
                    return
            else:
                choice = input("Continue browsing? (y/n): ").strip().lower()
                if choice != 'y':
                    return
            continue
        
        display_files_table(items, current_path)
        
        if RICH_AVAILABLE:
            console.print("[dim]Commands: Enter number to navigate/download, 'b' to go back, 'q' to quit[/dim]")
            choice = Prompt.ask("[bold yellow]Choose action[/bold yellow]", default="q")
        else:
            print("Commands: Enter number to navigate/download, 'b' to go back, 'q' to quit")
            choice = input("Choose action: ").strip().lower() or 'q'
        
        if choice == 'q':
            break
        elif choice == 'b':
            # Go back one level
            if current_path != "/Root":
                current_path = '/'.join(current_path.rstrip('/').split('/')[:-1]) or "/Root"
            continue
        
        try:
            idx = int(choice)
            
            # Handle parent directory (..)
            if idx == 0 and current_path != "/Root":
                current_path = '/'.join(current_path.rstrip('/').split('/')[:-1]) or "/Root"
                continue
            
            if 1 <= idx <= len(items):
                selected = items[idx - 1]
                
                if selected['is_dir']:
                    # Navigate into directory
                    current_path = selected['full_path']
                else:
                    # File selected - ask to download
                    if RICH_AVAILABLE:
                        console.print(f"\n[cyan]File:[/cyan] {selected['name']}")
                        console.print(f"[cyan]Size:[/cyan] {selected['size']}")
                        console.print(f"[cyan]Path:[/cyan] {selected['full_path']}")
                        
                        if Confirm.ask("\nDownload this file?", default=True):
                            download_file(email, password, selected['full_path'])
                    else:
                        print(f"\nFile: {selected['name']}")
                        print(f"Size: {selected['size']}")
                        print(f"Path: {selected['full_path']}")
                        
                        dl = input("\nDownload this file? (y/n): ").strip().lower()
                        if dl == 'y':
                            download_file(email, password, selected['full_path'])
                    
                    input("\nPress Enter to continue...")
            else:
                print_message("Invalid selection", "red")
                
        except ValueError:
            print_message("Invalid input", "red")
        except KeyboardInterrupt:
            print_message("\n\nReturning to menu...", "yellow")
            break


def main():
    if RICH_AVAILABLE:
        console.print()
        console.print("[bold cyan]MEGA File Browser[/bold cyan]")
        console.print("[dim]Browse and download files from your MEGA accounts[/dim]")
        console.print()
    else:
        print("\n" + "="*70)
        print("MEGA FILE BROWSER")
        print("Browse and download files from your MEGA accounts")
        print("="*70 + "\n")
    
    accounts = load_accounts()
    if not accounts:
        print_message("No accounts found! Please create accounts first.", "red")
        return
    
    account = select_account(accounts)
    file_browser(account)
    
    print_message("\n✓ Done!", "green")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_message("\n\nExiting...", "yellow")
        sys.exit(0)
