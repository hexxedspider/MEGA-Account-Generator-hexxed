import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SECRET_SALT = b'mega_links_encryption_salt_2025_v1'

ENCRYPTED_FILE = 'mega_links.encrypted'


def _get_cipher():
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SECRET_SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(SECRET_SALT))
    return Fernet(key)


def add_link(link_name, mega_link):
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
            print(f"⚠️  Warning: Could not read existing file: {e}")
    
    links[link_name] = mega_link
    
    data_to_encrypt = '\n'.join([f"{name}:::{link}" for name, link in links.items()])
    encrypted_data = cipher.encrypt(data_to_encrypt.encode('utf-8'))
    
    with open(ENCRYPTED_FILE, 'wb') as f:
        f.write(encrypted_data)
    
    print(f"✅ Added link '{link_name}' to encrypted storage")


def get_link(link_name):
    links = get_all_links()
    return links.get(link_name)


def get_all_links():
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
        print(f"❌ Error decrypting file: {e}")
        return {}
    
    return links


def list_links():
    links = get_all_links()
    
    if not links:
        print("📭 No links stored yet")
        return
    
    print(f"\n📁 Stored MEGA Links ({len(links)}):")
    print("-" * 60)
    for name, link in links.items():
        print(f"  {name}")
        print(f"    → {link}")
    print("-" * 60)


def remove_link(link_name):
    links = get_all_links()
    
    if link_name not in links:
        print(f"❌ Link '{link_name}' not found")
        return False
    
    del links[link_name]
    
    cipher = _get_cipher()
    data_to_encrypt = '\n'.join([f"{name}:::{link}" for name, link in links.items()])
    encrypted_data = cipher.encrypt(data_to_encrypt.encode('utf-8'))
    
    with open(ENCRYPTED_FILE, 'wb') as f:
        f.write(encrypted_data)
    
    print(f"✅ Removed link '{link_name}'")
    return True


def interactive_mode():
    while True:
        print("\n" + "="*60)
        print("🔒 Encrypted MEGA Links Manager")
        print("="*60)
        print("1. Add a link")
        print("2. View all links")
        print("3. Get a specific link")
        print("4. Remove a link")
        print("5. Exit")
        print("="*60)
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            name = input("Enter link name: ").strip()
            link = input("Enter MEGA link: ").strip()
            if name and link:
                add_link(name, link)
            else:
                print("❌ Name and link cannot be empty")
        
        elif choice == '2':
            list_links()
        
        elif choice == '3':
            name = input("Enter link name: ").strip()
            link = get_link(name)
            if link:
                print(f"\n✅ {name}: {link}")
            else:
                print(f"❌ Link '{name}' not found")
        
        elif choice == '4':
            name = input("Enter link name to remove: ").strip()
            remove_link(name)
        
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option")


if __name__ == '__main__':
    import sys
    
    # Check if cryptography is installed
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        print("❌ Missing dependency: cryptography")
        print("Install with: pip install cryptography")
        sys.exit(1)
    
    # Run interactive mode
    interactive_mode()
