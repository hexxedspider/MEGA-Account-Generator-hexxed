import os
import csv
import sys
import subprocess
import base64
from collections import defaultdict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.prompt import Prompt, IntPrompt
from rich.columns import Columns
from rich import box
from rich.style import Style

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False

console = Console()
SECRET_SALT = b'mega_links_encryption_salt_2025_v1'
ENCRYPTED_FILE = 'mega_links.encrypted'

def _get_cipher():
    if not ENCRYPTION_AVAILABLE:
        return None
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SECRET_SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(SECRET_SALT))
    return Fernet(key)


def add_encrypted_link(link_name, mega_link):
    if not ENCRYPTION_AVAILABLE:
        console.print("[red]Encryption not available. Install: pip install cryptography[/red]")
        return False
    
    cipher = _get_cipher()
    
    links = {}
    if os.path.exists(ENCRYPTED_FILE):
        try:
            with open(ENCRYPTED_FILE, 'rb') as f:
                encrypted_data = f.read()
                if encrypted_data:
                    decrypted_data = cipher.decrypt(encrypted_data).decode('utf-8')
                    for line in decrypted_data.strip().split('\n'):
                        if ':::' in line:
                            name, link = line.split(':::', 1)
                            links[name] = link
        except Exception as e:
            console.print(f"[yellow]⚠️  Warning: Could not read existing file: {e}[/yellow]")
    
    links[link_name] = mega_link
    
    data_to_encrypt = '\n'.join([f"{name}:::{link}" for name, link in links.items()])
    encrypted_data = cipher.encrypt(data_to_encrypt.encode('utf-8'))
    
    with open(ENCRYPTED_FILE, 'wb') as f:
        f.write(encrypted_data)
    
    console.print(f"[green]✅ Added link '{link_name}' to encrypted storage[/green]")
    return True


def get_encrypted_link(link_name):
    links = get_all_encrypted_links()
    return links.get(link_name)


def get_all_encrypted_links():
    """Retrieve all MEGA links from the encrypted file."""
    if not ENCRYPTION_AVAILABLE:
        return {}
    
    if not os.path.exists(ENCRYPTED_FILE):
        return {}
    
    cipher = _get_cipher()
    links = {}
    
    try:
        with open(ENCRYPTED_FILE, 'rb') as f:
            encrypted_data = f.read()
            if encrypted_data:
                decrypted_data = cipher.decrypt(encrypted_data).decode('utf-8')
                for line in decrypted_data.strip().split('\n'):
                    if ':::' in line:
                        name, link = line.split(':::', 1)
                        links[name] = link
    except Exception as e:
        console.print(f"[red]❌ Error decrypting file: {e}[/red]")
        return {}
    
    return links


def remove_encrypted_link(link_name):
    if not ENCRYPTION_AVAILABLE:
        console.print("[red]Encryption not available.[/red]")
        return False
    
    links = get_all_encrypted_links()
    
    if link_name not in links:
        console.print(f"[red]❌ Link '{link_name}' not found[/red]")
        return False
    
    del links[link_name]
    
    cipher = _get_cipher()
    data_to_encrypt = '\n'.join([f"{name}:::{link}" for name, link in links.items()])
    encrypted_data = cipher.encrypt(data_to_encrypt.encode('utf-8'))
    
    with open(ENCRYPTED_FILE, 'wb') as f:
        f.write(encrypted_data)
    
    console.print(f"[green]✅ Removed link '{link_name}'[/green]")
    return True


def manage_encrypted_links():
    if not ENCRYPTION_AVAILABLE:
        console.print("\n[red]❌ Encryption module not available![/red]")
        console.print("[yellow]Install with: pip install cryptography[/yellow]")
        console.print(f"\n[dim]Press Enter to return to menu...[/dim]")
        input()
        return
    
    while True:
        clear_screen()
        console.print(Panel("[bold cyan]🔒 Encrypted MEGA Links Manager[/bold cyan]", 
                          border_style="cyan"))
        console.print()
        
        links = get_all_encrypted_links()
        if links:
            table = Table(title=f"Stored Links ({len(links)})", box=box.ROUNDED)
            table.add_column("Name", style="cyan")
            table.add_column("MEGA Link", style="green")
            
            for name, link in links.items():
                table.add_row(name, link)
            
            console.print(table)
            console.print()
        else:
            console.print("[dim]📭 No encrypted links stored yet[/dim]\n")
        
        console.print("[bold yellow]Options:[/bold yellow]")
        console.print("  [cyan]1.[/cyan] Add a link")
        console.print("  [cyan]2.[/cyan] Get a specific link")
        console.print("  [cyan]3.[/cyan] Remove a link")
        console.print("  [cyan]0.[/cyan] Return to main menu")
        console.print()
        
        choice = Prompt.ask("[bold yellow]Choose an option[/bold yellow]", default="0")
        
        if choice == '1':
            console.print()
            name = Prompt.ask("Enter link name (e.g., 'My Photos', 'Backups')")
            link = Prompt.ask("Enter MEGA folder link")
            if name and link:
                add_encrypted_link(name, link)
                console.print(f"\n[dim]Press Enter to continue...[/dim]")
                input()
        
        elif choice == '2':
            if not links:
                console.print("\n[yellow]No links to retrieve[/yellow]")
                console.print(f"\n[dim]Press Enter to continue...[/dim]")
                input()
            else:
                console.print()
                name = Prompt.ask("Enter link name")
                link = get_encrypted_link(name)
                if link:
                    console.print(f"\n[green]✅ {name}:[/green]")
                    console.print(f"[cyan]{link}[/cyan]")
                else:
                    console.print(f"\n[red]❌ Link '{name}' not found[/red]")
                console.print(f"\n[dim]Press Enter to continue...[/dim]")
                input()
        
        elif choice == '3':
            if not links:
                console.print("\n[yellow]No links to remove[/yellow]")
                console.print(f"\n[dim]Press Enter to continue...[/dim]")
                input()
            else:
                console.print()
                name = Prompt.ask("Enter link name to remove")
                remove_encrypted_link(name)
                console.print(f"\n[dim]Press Enter to continue...[/dim]")
                input()
        
        elif choice == '0':
            break
        
        else:
            console.print("\n[red]Invalid option![/red]")
            console.print(f"\n[dim]Press Enter to continue...[/dim]")
            input()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def load_accounts():
    csv_file = 'accounts.csv'
    if not os.path.exists(csv_file):
        return []
    
    accounts = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Email') and row['Email'].strip():
                    accounts.append(row)
    except Exception as e:
        console.print(f"[red]Error loading accounts: {e}[/red]")
        return []
    
    return accounts


def parse_storage_usage(usage_str):
    if not usage_str or usage_str == '-' or 'Error' in usage_str or 'failed' in usage_str:
        return None
    
    try:
        if '(' in usage_str and '%' in usage_str:
            percentage_str = usage_str.split('(')[1].split('%')[0]
            return float(percentage_str)
    except:
        pass
    
    return None


def get_storage_color(percentage):
    if percentage is None:
        return "white"
    elif percentage < 50:
        return "green"
    elif percentage < 80:
        return "yellow"
    else:
        return "red"


def get_dashboard_stats(accounts):
    stats = {
        'total_accounts': len(accounts),
        'tagged_accounts': 0,
        'total_storage_gb': 0,
        'used_storage_gb': 0,
        'purposes': defaultdict(int),
        'storage_issues': 0,
        'high_usage': 0,
    }
    
    for account in accounts:
        purpose = account.get('Purpose', '-').strip() or '-'
        if purpose != '-':
            stats['tagged_accounts'] += 1
            stats['purposes'][purpose] += 1
        
        usage = account.get('Usage', '-').strip()
        if usage and usage != '-':
            try:
                if '/' in usage:
                    parts = usage.split('/')
                    total_part = parts[1].split('(')[0].strip()
                    
                    # Handle cases with and without space (e.g. "50 GB" or "50GB")
                    import re
                    match = re.match(r'([\d.]+)\s*([KMGT]?B)', total_part)
                    if match:
                        total_value = float(match.group(1))
                        total_unit = match.group(2)
                        
                        if total_unit == 'TB':
                            total_gb = total_value * 1024
                        elif total_unit == 'GB':
                            total_gb = total_value
                        elif total_unit == 'MB':
                            total_gb = total_value / 1024
                        elif total_unit == 'KB':
                            total_gb = total_value / (1024 * 1024)
                        else:
                            total_gb = 0
                    else:
                        total_gb = 0
                    
                    stats['total_storage_gb'] += total_gb
                    
                    percentage = parse_storage_usage(usage)
                    if percentage is not None:
                        used_gb = total_gb * (percentage / 100)
                        stats['used_storage_gb'] += used_gb
                        
                        if percentage > 80:
                            stats['high_usage'] += 1
                else:
                    stats['storage_issues'] += 1
            except:
                stats['storage_issues'] += 1
        else:
            stats['storage_issues'] += 1
    
    return stats


def display_header():
    title = Text()
    title.append("MEGA", style="bold cyan")
    title.append(".nz ", style="bold white")
    title.append("Account Manager", style="bold magenta")
    
    subtitle = Text("Unified Management Dashboard", style="italic dim")
    
    header = Panel(
        Columns([title, subtitle], align="center", expand=True),
        style="bold blue",
        box=box.DOUBLE,
        padding=(1, 2)
    )
    
    console.print(header)
    console.print()


def display_dashboard(accounts):
    stats = get_dashboard_stats(accounts)
    
    account_info = Table.grid(padding=(0, 2))
    account_info.add_column(style="cyan", justify="right")
    account_info.add_column(style="bold white")
    
    account_info.add_row("Total Accounts:", str(stats['total_accounts']))
    account_info.add_row("Tagged Accounts:", str(stats['tagged_accounts']))
    account_info.add_row("Untagged:", str(stats['total_accounts'] - stats['tagged_accounts']))
    
    storage_info = Table.grid(padding=(0, 2))
    storage_info.add_column(style="cyan", justify="right")
    storage_info.add_column(style="bold white")
    
    total_storage = f"{stats['total_storage_gb']:.2f} GB"
    used_storage = f"{stats['used_storage_gb']:.2f} GB"
    usage_percent = (stats['used_storage_gb'] / stats['total_storage_gb'] * 100) if stats['total_storage_gb'] > 0 else 0
    
    storage_color = get_storage_color(usage_percent)
    
    storage_info.add_row("Total Storage:", total_storage)
    storage_info.add_row("Used Storage:", f"[{storage_color}]{used_storage}[/{storage_color}]")
    storage_info.add_row("Usage:", f"[{storage_color}]{usage_percent:.1f}%[/{storage_color}]")
    storage_info.add_row("High Usage (>80%):", f"[{'red' if stats['high_usage'] > 0 else 'green'}]{stats['high_usage']}[/]")
    
    purpose_info = Table.grid(padding=(0, 2))
    purpose_info.add_column(style="cyan", justify="right")
    purpose_info.add_column(style="bold white")
    
    if stats['purposes']:
        sorted_purposes = sorted(stats['purposes'].items(), key=lambda x: x[1], reverse=True)
        for purpose, count in sorted_purposes[:5]:  # Show top 5
            purpose_info.add_row(f"{purpose}:", str(count))
    else:
        purpose_info.add_row("No tags yet", "")
    
    panels = [
        Panel(account_info, title="[bold]📊 Accounts[/bold]", border_style="blue", box=box.ROUNDED),
        Panel(storage_info, title="[bold]💾 Storage[/bold]", border_style="green", box=box.ROUNDED),
        Panel(purpose_info, title="[bold]🏷️  Top Purposes[/bold]", border_style="magenta", box=box.ROUNDED),
    ]
    
    console.print(Columns(panels, equal=True, expand=True))
    console.print()


def display_menu():
    menu = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    menu.add_column(style="bold cyan", justify="right", width=3)
    menu.add_column(style="white")
    menu.add_column(style="dim")
    
    menu.add_row("1.", "Generate New Accounts", "Create new MEGA accounts")
    menu.add_row("2.", "Sign In to All Accounts", "Keep accounts alive")
    menu.add_row("3.", "Check Storage Usage", "Update storage statistics")
    menu.add_row("4.", "Manage Tags/Purposes", "Organize accounts")
    menu.add_row("5.", "Select Account", "Copy credentials to clipboard")
    menu.add_row("6.", "Setup Auto-Login Scheduler", "Configure weekly signin")
    menu.add_row("7.", "View All Accounts", "List accounts with details")
    menu.add_row("8.", "Upload Folder", "Upload local folder to account")
    menu.add_row("9.", "Browse Files", "Browse and download files")
    menu.add_row("10.", "Refresh Dashboard", "Reload statistics")
    menu.add_row("11.", "Encrypted Links", "Store MEGA links securely")
    menu.add_row("0.", "Exit", "Close manager")
    
    console.print(Panel(menu, title="[bold]Main Menu[/bold]", border_style="yellow", box=box.ROUNDED))
    console.print()


def run_script(script_name, args=None):
    console.print(f"\n[bold cyan]Running {script_name}...[/bold cyan]\n")
    
    try:
        cmd = [sys.executable, script_name]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        console.print(f"\n[dim]Press Enter to return to menu...[/dim]")
        input()
        return result.returncode == 0
    except Exception as e:
        console.print(f"[red]Error running {script_name}: {e}[/red]")
        console.print(f"\n[dim]Press Enter to return to menu...[/dim]")
        input()
        return False


def view_all_accounts(accounts):
    if not accounts:
        console.print("[yellow]No accounts found![/yellow]")
        console.print(f"\n[dim]Press Enter to return to menu...[/dim]")
        input()
        return
    
    table = Table(title="All Accounts", box=box.ROUNDED, show_lines=True)
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Email", style="cyan")
    table.add_column("Purpose", style="magenta")
    table.add_column("Storage Usage", justify="right")
    table.add_column("Status", justify="center")
    
    for idx, account in enumerate(accounts, start=1):
        email = account.get('Email', '').strip()
        purpose = account.get('Purpose', '-').strip() or '-'
        usage = account.get('Usage', '-').strip() or '-'
        
        if usage == '-':
            status = "[dim]❓ Unknown[/dim]"
            usage_display = "-"
        elif 'Error' in usage or 'failed' in usage:
            status = "[red]✗ Error[/red]"
            usage_display = f"[red]{usage}[/red]"
        else:
            percentage = parse_storage_usage(usage)
            color = get_storage_color(percentage)
            status = f"[green]✓ Active[/green]"
            usage_display = f"[{color}]{usage}[/{color}]"
        
        table.add_row(
            str(idx),
            email,
            purpose,
            usage_display,
            status
        )
    
    console.print()
    console.print(table)
    console.print()
    console.print(f"[dim]Press Enter to return to menu...[/dim]")
    input()


def main():
    while True:
        clear_screen()
        display_header()
        
        accounts = load_accounts()
        
        display_dashboard(accounts)
        
        display_menu()
        
        try:
            choice = Prompt.ask("[bold yellow]Choose an option[/bold yellow]", default="0")
            
            if choice == "1":
                console.print("\n[bold]Generate New Accounts[/bold]")
                num_accounts = IntPrompt.ask("How many accounts to generate?", default=3)
                
                use_threads = Prompt.ask("Use multi-threading? (faster but may hit rate limits)", 
                                        choices=["y", "n"], default="n")
                
                args = ["-n", str(num_accounts)]
                if use_threads == "y":
                    threads = IntPrompt.ask("Number of threads (max 8)?", default=2)
                    args.extend(["-t", str(threads)])
                
                use_same_password = Prompt.ask("Use the same password for all accounts?", 
                                              choices=["y", "n"], default="n")
                if use_same_password == "y":
                    password = Prompt.ask("Enter password", password=True)
                    args.extend(["-p", password])
                
                run_script("generate_accounts.py", args)
                
            elif choice == "2":
                run_script("signin_accounts.py")
                
            elif choice == "3":
                run_script("check_storage.py")
                
            elif choice == "4":
                run_script("manage_tags.py")
                
            elif choice == "5":
                run_script("account_selector.py")
                
            elif choice == "6":
                console.print("\n[bold]Setup Auto-Login Scheduler[/bold]")
                action = Prompt.ask("Install or remove scheduler?", 
                                   choices=["install", "remove"], default="install")
                
                if action == "remove":
                    run_script("setup_scheduler.py", ["--remove"])
                else:
                    run_script("setup_scheduler.py")
                
            elif choice == "7":
                view_all_accounts(accounts)
                
            elif choice == "8":
                run_script("upload_folder.py")
                
            elif choice == "9":
                run_script("browse_files.py")
                
            elif choice == "10":
                continue
            
            elif choice == "11":
                manage_encrypted_links()
                
            elif choice == "0":
                console.print("\n[bold green]Thanks for using MEGA Account Manager![/bold green]")
                console.print("[dim purple]Provided by Hexxed.[/dim purple]\n")
                break
                
            else:
                console.print("[red]Invalid option![/red]")
                console.print(f"\n[dim]Press Enter to continue...[/dim]")
                input()
                
        except KeyboardInterrupt:
            console.print("\n\n[yellow]Interrupted. Returning to menu...[/yellow]")
            console.print(f"\n[dim]Press Enter to continue...[/dim]")
            input()
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            console.print(f"\n[dim]Press Enter to continue...[/dim]")
            input()


if __name__ == "__main__":
    if not os.path.exists("accounts.csv"):
        console.print("[yellow]No accounts.csv found. Creating new file...[/yellow]")
        with open("accounts.csv", "w", newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(["Email", "MEGA Password", "Usage", "Mail.tm Password", "Mail.tm ID", "Purpose"])
        console.print("[green]Created accounts.csv[/green]\n")
    
    main()
