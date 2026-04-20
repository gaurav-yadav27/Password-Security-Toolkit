#!/usr/bin/env python3
"""
Password Security Toolkit - FULLY WORKING Version
All menu options are functional
Author: Gaurav Yadav
"""

import re
import os
import sys
import json
import math
import random
import string
import time
import hashlib
import base64
from datetime import datetime

# ============= COLORS =============
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

# ============= COMMON PASSWORDS =============
COMMON_PASSWORDS = {
    "password", "123456", "123456789", "qwerty", "abc123", "password123",
    "admin", "iloveyou", "welcome", "monkey", "dragon", "master", "sunshine",
    "letmein", "123123", "football", "baseball", "shadow", "654321", "root"
}

# ============= ENCRYPTION =============
class SimpleEncryption:
    @staticmethod
    def encrypt(data, password):
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, 32)
        data_bytes = data.encode()
        result = bytearray()
        for i, byte in enumerate(data_bytes):
            result.append(byte ^ key[i % len(key)])
        combined = salt + bytes(result)
        return base64.b64encode(combined).decode()
    
    @staticmethod
    def decrypt(encrypted_data, password):
        combined = base64.b64decode(encrypted_data)
        salt = combined[:16]
        encrypted = combined[16:]
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000, 32)
        result = bytearray()
        for i, byte in enumerate(encrypted):
            result.append(byte ^ key[i % len(key)])
        return result.decode()

# ============= PASSWORD MANAGER =============
class PasswordManager:
    def __init__(self):
        self.data_file = "passwords.vault"
        self.passwords = {}
        self.master_password = None
        self.is_unlocked = False
    
    def create_vault(self, master_password):
        """Create new vault"""
        self.master_password = master_password
        self.passwords = {}
        self.is_unlocked = True
        self._save()
        return True
    
    def unlock(self, master_password):
        """Unlock existing vault"""
        if not os.path.exists(self.data_file):
            return False
        try:
            with open(self.data_file, 'r') as f:
                encrypted = f.read()
            decrypted = SimpleEncryption.decrypt(encrypted, master_password)
            data = json.loads(decrypted)
            self.passwords = data
            self.master_password = master_password
            self.is_unlocked = True
            return True
        except:
            return False
    
    def _save(self):
        """Save vault"""
        if not self.is_unlocked:
            return False
        encrypted = SimpleEncryption.encrypt(json.dumps(self.passwords), self.master_password)
        with open(self.data_file, 'w') as f:
            f.write(encrypted)
        return True
    
    def add_password(self, service, username, password, category="General"):
        """Add or update password"""
        if not self.is_unlocked:
            return False
        
        if service not in self.passwords:
            self.passwords[service] = []
        
        entry = {
            "username": username,
            "password": password,
            "category": category,
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Check if username exists
        for i, existing in enumerate(self.passwords[service]):
            if existing["username"] == username:
                self.passwords[service][i] = entry
                self._save()
                return "updated"
        
        self.passwords[service].append(entry)
        self._save()
        return "added"
    
    def get_password(self, service, username=None):
        """Get password(s)"""
        if not self.is_unlocked:
            return None
        if service not in self.passwords:
            return None
        if username:
            for entry in self.passwords[service]:
                if entry["username"] == username:
                    return entry
            return None
        return self.passwords[service]
    
    def list_services(self):
        """List all services"""
        if not self.is_unlocked:
            return []
        return [(service, len(entries)) for service, entries in self.passwords.items()]
    
    def search(self, keyword):
        """Search passwords"""
        if not self.is_unlocked:
            return []
        results = []
        keyword = keyword.lower()
        for service, entries in self.passwords.items():
            if keyword in service.lower():
                results.append((service, entries))
            else:
                for entry in entries:
                    if keyword in entry["username"].lower():
                        results.append((service, entries))
                        break
        return results
    
    def delete_password(self, service, username=None):
        """Delete password"""
        if not self.is_unlocked:
            return False
        if service not in self.passwords:
            return False
        if username:
            for i, entry in enumerate(self.passwords[service]):
                if entry["username"] == username:
                    del self.passwords[service][i]
                    if not self.passwords[service]:
                        del self.passwords[service]
                    self._save()
                    return True
            return False
        else:
            del self.passwords[service]
            self._save()
            return True
    
    def get_strength_report(self):
        """Get strength report for all passwords"""
        if not self.is_unlocked:
            return {}
        report = {}
        for service, entries in self.passwords.items():
            for entry in entries:
                strength = self._analyze_strength(entry["password"])
                key = f"{service} - {entry['username']}"
                report[key] = strength
        return report
    
    def _analyze_strength(self, password):
        """Analyze password strength"""
        score = 0
        if len(password) >= 12: score += 30
        elif len(password) >= 8: score += 15
        if re.search(r'[a-z]', password): score += 10
        if re.search(r'[A-Z]', password): score += 10
        if re.search(r'[0-9]', password): score += 10
        if re.search(r'[^a-zA-Z0-9]', password): score += 15
        if password.lower() in COMMON_PASSWORDS: score -= 20
        score = max(0, min(100, score))
        
        if score >= 70: rating = "STRONG"; emoji = "✅"
        elif score >= 40: rating = "MODERATE"; emoji = "⚠️"
        else: rating = "WEAK"; emoji = "❌"
        
        return {"score": score, "rating": rating, "emoji": emoji}
    
    def lock(self):
        """Lock the vault"""
        self.is_unlocked = False
        self.passwords = {}
        self.master_password = None

# ============= UTILITY FUNCTIONS =============
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    print(Colors.PURPLE + """
╔═══════════════════════════════════════════════════════════════╗
║           PASSWORD SECURITY TOOLKIT - Complete               ║
║         Password Manager + Analyzer + Generator              ║
╚═══════════════════════════════════════════════════════════════╝
    """ + Colors.RESET)
    print(Colors.DIM + f"~ Created by Gaurav Yadav ~{Colors.RESET}")
    print(Colors.DIM + "="*55 + Colors.RESET)
    print()

def mask_password(password):
    if len(password) <= 8:
        return '*' * len(password)
    return password[:3] + '*' * (len(password) - 6) + password[-3:]

def calculate_entropy(password):
    charset = 0
    if re.search(r'[a-z]', password): charset += 26
    if re.search(r'[A-Z]', password): charset += 26
    if re.search(r'[0-9]', password): charset += 10
    if re.search(r'[^a-zA-Z0-9]', password): charset += 32
    if charset == 0: return 0
    return len(password) * math.log2(charset)

def generate_password(length=16):
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*()_+-=[]{}|"
    all_chars = lower + upper + digits + special
    password = [
        random.choice(lower),
        random.choice(upper),
        random.choice(digits),
        random.choice(special)
    ]
    password += random.choices(all_chars, k=length-4)
    random.shuffle(password)
    return ''.join(password)

def analyze_password(password):
    """Analyze a single password"""
    score = 0
    issues = []
    good = []
    
    # Length
    if len(password) >= 16:
        score += 30
        good.append(f"Excellent length ({len(password)} chars)")
    elif len(password) >= 12:
        score += 20
        good.append(f"Good length ({len(password)} chars)")
    elif len(password) >= 8:
        score += 10
    else:
        issues.append(f"Too short ({len(password)} chars)")
    
    # Character variety
    if re.search(r'[a-z]', password): score += 10
    else: issues.append("Missing lowercase letters")
    
    if re.search(r'[A-Z]', password): score += 10
    else: issues.append("Missing uppercase letters")
    
    if re.search(r'[0-9]', password): score += 10
    else: issues.append("Missing numbers")
    
    if re.search(r'[^a-zA-Z0-9]', password): score += 15
    else: issues.append("Missing special characters")
    
    # Common password
    if password.lower() in COMMON_PASSWORDS:
        score -= 20
        issues.append("Common password!")
    
    # Patterns
    if re.search(r'12345|qwerty|asdfgh', password.lower()):
        score -= 10
        issues.append("Keyboard pattern detected")
    
    if re.search(r'(.)\1{2,}', password):
        score -= 8
        issues.append("Repeated characters")
    
    score = max(0, min(100, score))
    entropy = calculate_entropy(password)
    
    if score >= 70:
        rating = "STRONG"; emoji = "✅"; color = Colors.GREEN
    elif score >= 40:
        rating = "MODERATE"; emoji = "⚠️"; color = Colors.YELLOW
    else:
        rating = "WEAK"; emoji = "❌"; color = Colors.RED
    
    return {
        'score': score, 'rating': rating, 'emoji': emoji, 'color': color,
        'entropy': round(entropy, 2), 'issues': issues, 'good': good
    }

# ============= PASSWORD MANAGER MENU =============
def password_manager_menu(pm):
    """Working password manager menu"""
    while True:
        clear_screen()
        show_banner()
        
        print(f"{Colors.YELLOW}┌─────────────────────────────────────────┐{Colors.RESET}")
        print(f"{Colors.YELLOW}│         🔐 PASSWORD MANAGER              │{Colors.RESET}")
        print(f"{Colors.YELLOW}├─────────────────────────────────────────┤{Colors.RESET}")
        print(f"{Colors.YELLOW}│{Colors.RESET}  1. 📝  Add/Update Password              {Colors.YELLOW}│{Colors.RESET}")
        print(f"{Colors.YELLOW}│{Colors.RESET}  2. 🔍  Get Password                       {Colors.YELLOW}│{Colors.RESET}")
        print(f"{Colors.YELLOW}│{Colors.RESET}  3. 📋  List All Services                  {Colors.YELLOW}│{Colors.RESET}")
        print(f"{Colors.YELLOW}│{Colors.RESET}  4. 🔎  Search Passwords                   {Colors.YELLOW}│{Colors.RESET}")
        print(f"{Colors.YELLOW}│{Colors.RESET}  5. 🗑️   Delete Password                    {Colors.YELLOW}│{Colors.RESET}")
        print(f"{Colors.YELLOW}│{Colors.RESET}  6. 📊  Password Strength Report           {Colors.YELLOW}│{Colors.RESET}")
        print(f"{Colors.YELLOW}│{Colors.RESET}  7. 🔒  Lock Vault                         {Colors.YELLOW}│{Colors.RESET}")
        print(f"{Colors.YELLOW}└─────────────────────────────────────────┘{Colors.RESET}")
        
        choice = input(f"\n{Colors.BLUE}👉 Select option (1-7): {Colors.RESET}")
        
        # ===== OPTION 1: Add Password =====
        if choice == '1':
            clear_screen()
            show_banner()
            print(f"{Colors.BLUE}📝 Add New Password{Colors.RESET}\n")
            
            service = input(f"{Colors.YELLOW}Service/Website: {Colors.RESET}").strip()
            if not service:
                print(f"{Colors.RED}Cancelled{Colors.RESET}")
                time.sleep(1)
                continue
            
            username = input(f"{Colors.YELLOW}Username/Email: {Colors.RESET}").strip()
            if not username:
                print(f"{Colors.RED}Cancelled{Colors.RESET}")
                time.sleep(1)
                continue
            
            print(f"\n{Colors.BLUE}Password options:{Colors.RESET}")
            print("  1. Enter manually")
            print("  2. Generate strong password")
            
            pwd_choice = input(f"\n{Colors.YELLOW}Choose (1-2): {Colors.RESET}")
            
            if pwd_choice == '2':
                length = 16
                password = generate_password(length)
                print(f"\n{Colors.GREEN}Generated: {password}{Colors.RESET}")
                confirm = input(f"{Colors.BLUE}Save this password? (y/n): {Colors.RESET}")
                if confirm.lower() != 'y':
                    continue
            else:
                password = input(f"{Colors.YELLOW}Password: {Colors.RESET}")
                if not password:
                    continue
            
            category = input(f"{Colors.YELLOW}Category (General/Social/Banking/Work): {Colors.RESET}")
            if not category:
                category = "General"
            
            result = pm.add_password(service, username, password, category)
            
            if result == "added":
                print(f"\n{Colors.GREEN}✓ Password added successfully!{Colors.RESET}")
            else:
                print(f"\n{Colors.GREEN}✓ Password updated successfully!{Colors.RESET}")
            
            time.sleep(1.5)
        
        # ===== OPTION 2: Get Password =====
        elif choice == '2':
            clear_screen()
            show_banner()
            print(f"{Colors.BLUE}🔍 Retrieve Password{Colors.RESET}\n")
            
            service = input(f"{Colors.YELLOW}Service/Website: {Colors.RESET}").strip()
            if not service:
                continue
            
            entries = pm.get_password(service)
            
            if entries:
                if len(entries) == 1:
                    entry = entries[0]
                    print(f"\n{Colors.CYAN}┌─────────────────────────────────────────┐{Colors.RESET}")
                    print(f"{Colors.CYAN}│  {Colors.BOLD}{service}{Colors.RESET}{' ' * (38 - len(service))}{Colors.CYAN}│{Colors.RESET}")
                    print(f"{Colors.CYAN}├─────────────────────────────────────────┤{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}  Username: {entry['username']}")
                    print(f"{Colors.CYAN}│{Colors.RESET}  Password: {Colors.YELLOW}{entry['password']}{Colors.RESET}")
                    print(f"{Colors.CYAN}│{Colors.RESET}  Category: {entry['category']}")
                    print(f"{Colors.CYAN}│{Colors.RESET}  Created:  {entry['created']}")
                    print(f"{Colors.CYAN}└─────────────────────────────────────────┘{Colors.RESET}")
                    
                    strength = pm._analyze_strength(entry['password'])
                    print(f"\n  Strength: {strength['emoji']} {strength['rating']} ({strength['score']}/100)")
                else:
                    print(f"\n{Colors.YELLOW}Multiple accounts for {service}:{Colors.RESET}")
                    for i, entry in enumerate(entries, 1):
                        print(f"  {i}. {entry['username']}")
                    
                    choice_idx = input(f"\n{Colors.BLUE}Select number (0 to cancel): {Colors.RESET}")
                    try:
                        idx = int(choice_idx) - 1
                        if 0 <= idx < len(entries):
                            entry = entries[idx]
                            print(f"\n{Colors.GREEN}Username: {entry['username']}{Colors.RESET}")
                            print(f"{Colors.GREEN}Password: {Colors.YELLOW}{entry['password']}{Colors.RESET}")
                    except:
                        pass
            else:
                print(f"\n{Colors.RED}No passwords found for '{service}'{Colors.RESET}")
            
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        # ===== OPTION 3: List Services =====
        elif choice == '3':
            clear_screen()
            show_banner()
            print(f"{Colors.BLUE}📋 Saved Services{Colors.RESET}\n")
            
            services = pm.list_services()
            
            if services:
                print(f"{Colors.CYAN}┌─────────────────────────────────────────┐{Colors.RESET}")
                print(f"{Colors.CYAN}│  {Colors.BOLD}Service{' ' * 30}Count{Colors.RESET}{Colors.CYAN}│{Colors.RESET}")
                print(f"{Colors.CYAN}├─────────────────────────────────────────┤{Colors.RESET}")
                for service, count in sorted(services):
                    print(f"{Colors.CYAN}│{Colors.RESET}  {service:<35} {count:<5} {Colors.CYAN}│{Colors.RESET}")
                print(f"{Colors.CYAN}└─────────────────────────────────────────┘{Colors.RESET}")
                print(f"\n{Colors.DIM}Total: {len(services)} services{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}No passwords saved yet!{Colors.RESET}")
            
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        # ===== OPTION 4: Search =====
        elif choice == '4':
            clear_screen()
            show_banner()
            print(f"{Colors.BLUE}🔎 Search Passwords{Colors.RESET}\n")
            
            keyword = input(f"{Colors.YELLOW}Search keyword: {Colors.RESET}").strip()
            if not keyword:
                continue
            
            results = pm.search(keyword)
            
            if results:
                print(f"\n{Colors.GREEN}Found {len(results)} result(s):{Colors.RESET}\n")
                for service, entries in results:
                    print(f"{Colors.CYAN}▶ {service}{Colors.RESET}")
                    for entry in entries:
                        print(f"     └─ {entry['username']} ({entry['category']})")
            else:
                print(f"\n{Colors.YELLOW}No results found for '{keyword}'{Colors.RESET}")
            
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        # ===== OPTION 5: Delete =====
        elif choice == '5':
            clear_screen()
            show_banner()
            print(f"{Colors.RED}🗑️ Delete Password{Colors.RESET}\n")
            
            service = input(f"{Colors.YELLOW}Service/Website: {Colors.RESET}").strip()
            if not service:
                continue
            
            entries = pm.get_password(service)
            
            if entries:
                if len(entries) == 1:
                    confirm = input(f"{Colors.RED}Delete '{service}'? (y/n): {Colors.RESET}")
                    if confirm.lower() == 'y':
                        pm.delete_password(service)
                        print(f"{Colors.GREEN}✓ Deleted!{Colors.RESET}")
                else:
                    print(f"\n{Colors.YELLOW}Multiple accounts:{Colors.RESET}")
                    for i, entry in enumerate(entries, 1):
                        print(f"  {i}. {entry['username']}")
                    
                    choice_idx = input(f"\n{Colors.RED}Select number to delete (0 to cancel): {Colors.RESET}")
                    try:
                        idx = int(choice_idx) - 1
                        if 0 <= idx < len(entries):
                            username = entries[idx]['username']
                            confirm = input(f"{Colors.RED}Delete '{service} - {username}'? (y/n): {Colors.RESET}")
                            if confirm.lower() == 'y':
                                pm.delete_password(service, username)
                                print(f"{Colors.GREEN}✓ Deleted!{Colors.RESET}")
                    except:
                        pass
            else:
                print(f"\n{Colors.RED}No passwords found for '{service}'{Colors.RESET}")
            
            time.sleep(1.5)
        
        # ===== OPTION 6: Strength Report =====
        elif choice == '6':
            clear_screen()
            show_banner()
            print(f"{Colors.BLUE}📊 Password Strength Report{Colors.RESET}\n")
            
            report = pm.get_strength_report()
            
            if report:
                strong = weak = moderate = 0
                
                print(f"{Colors.CYAN}┌─────────────────────────────────────────────────────────┐{Colors.RESET}")
                print(f"{Colors.CYAN}│  {Colors.BOLD}Entry{' ' * 40}Strength{Colors.RESET}{Colors.CYAN}│{Colors.RESET}")
                print(f"{Colors.CYAN}├─────────────────────────────────────────────────────────┤{Colors.RESET}")
                
                for entry, strength in report.items():
                    if strength['score'] >= 70:
                        strong += 1
                        status = f"{Colors.GREEN}{strength['emoji']} {strength['rating']}{Colors.RESET}"
                    elif strength['score'] >= 40:
                        moderate += 1
                        status = f"{Colors.YELLOW}{strength['emoji']} {strength['rating']}{Colors.RESET}"
                    else:
                        weak += 1
                        status = f"{Colors.RED}{strength['emoji']} {strength['rating']}{Colors.RESET}"
                    
                    display_entry = entry[:45] + "..." if len(entry) > 45 else entry
                    print(f"{Colors.CYAN}│{Colors.RESET}  {display_entry:<47} {status:<12} {Colors.CYAN}│{Colors.RESET}")
                
                print(f"{Colors.CYAN}└─────────────────────────────────────────────────────────┘{Colors.RESET}")
                print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
                print(f"  {Colors.GREEN}✓ Strong: {strong}{Colors.RESET}")
                print(f"  {Colors.YELLOW}⚠️ Moderate: {moderate}{Colors.RESET}")
                print(f"  {Colors.RED}❌ Weak: {weak}{Colors.RESET}")
                
                if weak > 0:
                    print(f"\n{Colors.RED}⚠️ Warning: {weak} weak passwords detected!{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}No passwords saved yet!{Colors.RESET}")
            
            input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        # ===== OPTION 7: Lock Vault =====
        elif choice == '7':
            pm.lock()
            print(f"\n{Colors.YELLOW}🔒 Vault locked!{Colors.RESET}")
            time.sleep(1.5)
            return
        
        else:
            print(f"{Colors.RED}❌ Invalid option!{Colors.RESET}")
            time.sleep(1)

# ============= PASSWORD ANALYZER =============
def password_analyzer():
    clear_screen()
    show_banner()
    print(f"{Colors.BLUE}🔍 Password Analyzer{Colors.RESET}\n")
    
    password = input(f"{Colors.YELLOW}Enter password to analyze: {Colors.RESET}")
    if not password:
        return
    
    result = analyze_password(password)
    
    clear_screen()
    show_banner()
    
    masked = mask_password(password)
    print(f"{Colors.BOLD}Password:{Colors.RESET} {Colors.CYAN}{masked}{Colors.RESET}\n")
    
    # Strength meter
    bar_length = 50
    filled = int(bar_length * result['score'] / 100)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f"{Colors.BOLD}Strength:{Colors.RESET} {result['color']}{bar}{Colors.RESET} {result['score']}/100")
    print(f"{Colors.BOLD}Rating:{Colors.RESET} {result['color']}{result['emoji']} {result['rating']}{Colors.RESET}")
    print(f"{Colors.BOLD}Entropy:{Colors.RESET} {result['entropy']} bits\n")
    
    if result['issues']:
        print(f"{Colors.RED}Issues:{Colors.RESET}")
        for issue in result['issues'][:5]:
            print(f"  • {issue}")
        print()
    
    if result['good']:
        print(f"{Colors.GREEN}Good:{Colors.RESET}")
        for good in result['good'][:3]:
            print(f"  • {good}")
    
    input(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}")

# ============= PASSWORD GENERATOR =============
def password_generator():
    clear_screen()
    show_banner()
    print(f"{Colors.BLUE}🔐 Password Generator{Colors.RESET}\n")
    
    len_input = input(f"{Colors.YELLOW}Length (12-32, default 16): {Colors.RESET}")
    try:
        length = int(len_input) if len_input else 16
        length = max(12, min(32, length))
    except:
        length = 16
    
    count_input = input(f"{Colors.YELLOW}How many? (1-5, default 3): {Colors.RESET}")
    try:
        count = int(count_input) if count_input else 3
        count = max(1, min(5, count))
    except:
        count = 3
    
    print(f"\n{Colors.GREEN}Generated Passwords:{Colors.RESET}\n")
    
    for i in range(count):
        pwd = generate_password(length)
        entropy = calculate_entropy(pwd)
        strength = "STRONG" if entropy >= 60 else "MODERATE" if entropy >= 40 else "WEAK"
        print(f"{Colors.CYAN}{i+1}.{Colors.RESET} {Colors.BOLD}{pwd}{Colors.RESET}")
        print(f"   {Colors.DIM}Entropy: {entropy:.1f} bits | Strength: {strength}{Colors.RESET}\n")
    
    input(f"{Colors.DIM}Press Enter to continue...{Colors.RESET}")

# ============= MAIN MENU =============
def main():
    pm = PasswordManager()
    
    while True:
        show_banner()
        
        print(f"{Colors.YELLOW}┌─────────────────────────────────────────┐{Colors.RESET}")
        print(f"{Colors.YELLOW}│              MAIN MENU                    │{Colors.RESET}")
        print(f"{Colors.YELLOW}├─────────────────────────────────────────┤{Colors.RESET}")
        print(f"{Colors.YELLOW}│{Colors.RESET}  1. 🔐  Password Manager                  {Colors.YELLOW}│{Colors.RESET}")
        print(f"{Colors.YELLOW}│{Colors.RESET}  2. 🔍  Password Analyzer                  {Colors.YELLOW}│{Colors.RESET}")
        print(f"{Colors.YELLOW}│{Colors.RESET}  3. 🔐  Password Generator                 {Colors.YELLOW}│{Colors.RESET}")
        print(f"{Colors.YELLOW}│{Colors.RESET}  4. ℹ️   About                             {Colors.YELLOW}│{Colors.RESET}")
        print(f"{Colors.YELLOW}│{Colors.RESET}  5. 🚪  Exit                              {Colors.YELLOW}│{Colors.RESET}")
        print(f"{Colors.YELLOW}└─────────────────────────────────────────┘{Colors.RESET}")
        
        choice = input(f"\n{Colors.BLUE}👉 Select option (1-5): {Colors.RESET}")
        
        if choice == '1':
            clear_screen()
            show_banner()
            print(f"{Colors.BLUE}🔐 Password Manager{Colors.RESET}\n")
            print("1. Create New Vault")
            print("2. Unlock Existing Vault")
            print("3. Back")
            
            sub = input(f"\n{Colors.YELLOW}Choose: {Colors.RESET}")
            
            if sub == '1':
                print(f"\n{Colors.BLUE}Create Master Password:{Colors.RESET}")
                print(f"{Colors.DIM}⚠️ This password cannot be recovered!{Colors.RESET}")
                master1 = input(f"{Colors.YELLOW}> {Colors.RESET}")
                master2 = input(f"{Colors.YELLOW}Confirm: {Colors.RESET}")
                
                if master1 == master2 and master1:
                    if pm.create_vault(master1):
                        print(f"{Colors.GREEN}✓ Vault created!{Colors.RESET}")
                        password_manager_menu(pm)
                    else:
                        print(f"{Colors.RED}Error!{Colors.RESET}")
                else:
                    print(f"{Colors.RED}Passwords don't match!{Colors.RESET}")
                time.sleep(1.5)
            
            elif sub == '2':
                print(f"\n{Colors.BLUE}Enter Master Password:{Colors.RESET}")
                master = input(f"{Colors.YELLOW}> {Colors.RESET}")
                
                if pm.unlock(master):
                    print(f"{Colors.GREEN}✓ Vault unlocked!{Colors.RESET}")
                    password_manager_menu(pm)
                else:
                    print(f"{Colors.RED}Wrong password or no vault!{Colors.RESET}")
                    time.sleep(1.5)
        
        elif choice == '2':
            password_analyzer()
        
        elif choice == '3':
            password_generator()
        
        elif choice == '4':
            clear_screen()
            show_banner()
            print(f"{Colors.CYAN}About Password Security Toolkit{Colors.RESET}\n")
            print(f"Version: 2.0 (Fully Working)")
            print(f"Author: Gaurav Yadav")
            print(f"Python: {sys.version.split()[0]}\n")
            print(f"{Colors.YELLOW}Features:{Colors.RESET}")
            print(f"  • Password Manager (encrypted vault)")
            print(f"  • Password Strength Analyzer")
            print(f"  • Strong Password Generator")
            print(f"  • Breach Detection")
            print(f"  • Pattern Recognition\n")
            input(f"{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        
        elif choice == '5':
            print(f"\n{Colors.GREEN}👋 Stay secure! - Gaurav Yadav{Colors.RESET}\n")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Goodbye!{Colors.RESET}")
        sys.exit(0)