#!/usr/bin/env python3
"""
Brute Force Lab - المحاكي التفاعلي المتقدم
أداة تعليمية متطورة مع واجهة غنية وإمكانيات متقدمة
"""

import sys
import time
import os
import random
import json
import hashlib
import threading
import queue
from datetime import datetime
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
from colorama import init, Fore, Back, Style

# تهيئة colorama للألوان في الويندوز
init()

class AttackMode(Enum):
    """أنماط الهجوم المتاحة"""
    BASIC = "basic"
    DICTIONARY = "dictionary"
    COMBINATOR = "combinator"
    MASK = "mask"
    HYBRID = "hybrid"

class Protocol(Enum):
    """البروتوكولات المدعومة"""
    SSH = "ssh"
    FTP = "ftp"
    HTTP = "http"
    TELNET = "telnet"
    RDP = "rdp"
    MYSQL = "mysql"
    CUSTOM = "custom"

@dataclass
class AttackResult:
    """هيكل بيانات لنتائج الهجوم"""
    target: str
    protocol: str
    start_time: datetime
    end_time: datetime
    attempts: int
    success: bool
    credentials: Dict[str, str]
    speed: float  # محاولات في الثانية
    user_agent: str

class InteractiveBruteForcer:
    def __init__(self):
        self.users = []
        self.passwords = []
        self.target = ""
        self.protocol = Protocol.SSH.value
        self.port = 22
        self.attempts = 0
        self.found = False
        self.credentials = None
        self.results = []
        self.attack_mode = AttackMode.BASIC.value
        self.timeout = 5
        self.threads = 4
        self.proxy = None
        self.user_agent = "BruteForceLab/2.0"
        
        # قوائم مدمجة
        self.common_users = [
            'admin', 'administrator', 'root', 'user', 'test', 
            'guest', 'manager', 'operator', 'support', 'service'
        ]
        
        self.common_passwords = [
            '123456', 'password', 'admin123', 'test', '123456789',
            'qwerty', 'password123', 'admin@123', 'welcome', '12345',
            '12345678', '1234567', '123123', '111111', 'letmein',
            'abc123', 'password1', 'admin@1234', 'superman', 'iloveyou'
        ]
        
        # أنماط الهجوم
        self.attack_modes_info = {
            'basic': 'هجوم أساسي بقوائم المستخدمين وكلمات المرور',
            'dictionary': 'هجوم بقواميس مخصصة',
            'combinator': 'دمج قوائم المستخدمين وكلمات المرور بطرق مختلفة',
            'mask': 'هجوم باستخدام أقنعة محددة',
            'hybrid': 'هجوم هجين يجمع بين الطرق'
        }
        
        # إحصائيات متقدمة
        self.stats = {
            'total_attempts': 0,
            'successful_attacks': 0,
            'failed_attacks': 0,
            'total_time': 0,
            'avg_speed': 0,
            'common_patterns': {}
        }
    
    def clear_screen(self):
        """مسح الشاشة"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_banner(self):
        """طباعة شعار متطور"""
        banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗
║{Fore.YELLOW}      ██████╗ ██████╗ ██╗   ██╗████████╗███████╗       {Fore.CYAN}║
║{Fore.YELLOW}      ██╔══██╗██╔══██╗██║   ██║╚══██╔══╝██╔════╝       {Fore.CYAN}║
║{Fore.YELLOW}      ██████╔╝██████╔╝██║   ██║   ██║   █████╗         {Fore.CYAN}║
║{Fore.YELLOW}      ██╔══██╗██╔═══╝ ██║   ██║   ██║   ██╔══╝         {Fore.CYAN}║
║{Fore.YELLOW}      ██████╔╝██║     ╚██████╔╝   ██║   ███████╗       {Fore.CYAN}║
║{Fore.YELLOW}      ╚═════╝ ╚═╝      ╚═════╝    ╚═╝   ╚══════╝       {Fore.CYAN}║
║                                                              ║
║{Fore.WHITE}            مختبر التخمين التفاعلي المتقدم - V2.0          {Fore.CYAN}║
║{Fore.WHITE}               للأغراض التعليمية والأكاديمية              {Fore.CYAN}║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        print(banner)
    
    def ethical_warning(self):
        """تحذير أخلاقي مطور"""
        self.clear_screen()
        warning = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════╗
║{Fore.YELLOW}                     ⚠️  تحذير هام ⚠️                     {Fore.RED}║
╠══════════════════════════════════════════════════════════════╣{Fore.WHITE}
║                                                              ║
║  هذا البرنامج مخصص حصريًا للأغراض التالية:                  ║
║                                                              ║
║  • الاختبارات الأمنية القانونية                              ║
║  • التعليم والتدريب الأكاديمي                               ║
║  • اختبار الأنظمة التي تمتلك تصريحًا لاختبارها              ║
║  • زيادة الوعي الأمني                                        ║
║                                                              ║
║  ⚖️  المسؤولية القانونية:                                   ║
║                                                              ║
║  أنت المسؤول قانونيًا عن أي استخدام غير مصرح به            ║
║  لهذه الأداة. يُحظر استخدامها لأي نشاط غير قانوني.         ║
║                                                              ║
║  🔒 الأهداف المسموح بها:                                    ║
║                                                              ║
║  • أنظمة الاختبار المحلية (127.0.0.1)                       ║
║  • أنظمة المعامل التعليمية                                 ║
║  • الأنظمة التي تملك تصريح كتابي لاختبارها                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
        """
        print(warning)
        
        print(f"\n{Fore.YELLOW}هل توافق على شروط الاستخدام؟{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1. نعم، أوافق على الشروط{Style.RESET_ALL}")
        print(f"{Fore.RED}2. لا، لا أوافق (الخروج){Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.CYAN}اختر (1/2): {Style.RESET_ALL}").strip()
        
        if choice != '1':
            print(f"\n{Fore.GREEN}شكرًا لك على الالتزام بالأخلاقيات الأمنية.{Style.RESET_ALL}")
            sys.exit(0)
        
        # تسجيل موافقة المستخدم
        self.log_activity("USER_AGREEMENT", "User agreed to terms")
    
    def get_target_configuration(self):
        """إعدادات الهدف المتقدمة"""
        self.clear_screen()
        self.print_banner()
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🎯 مرحلة التكوين المتقدم{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        # إدخال الهدف
        print(f"\n{Fore.WHITE}📌 إدخال معلومات الهدف:{Style.RESET_ALL}")
        
        while True:
            target = input(f"{Fore.CYAN}• عنوان الهدف (IP/Domain): {Style.RESET_ALL}").strip()
            
            if target.lower() == 'demo':
                self.target = "127.0.0.1"
                print(f"{Fore.GREEN}[*] تم تعيين وضع التجربة على 127.0.0.1{Style.RESET_ALL}")
                break
            elif not target:
                print(f"{Fore.RED}[!] يجب إدخال هدف{Style.RESET_ALL}")
                continue
            else:
                self.target = target
                break
        
        # اختيار البروتوكول
        print(f"\n{Fore.WHITE}🌐 اختيار البروتوكول:{Style.RESET_ALL}")
        for i, protocol in enumerate(Protocol, 1):
            print(f"{Fore.CYAN}{i}. {protocol.value.upper()} {Style.RESET_ALL}")
        
        proto_choice = input(f"\n{Fore.CYAN}اختر البروتوكول (1-{len(list(Protocol))}): {Style.RESET_ALL}").strip()
        try:
            protocol_list = list(Protocol)
            self.protocol = protocol_list[int(proto_choice)-1].value
        except:
            self.protocol = Protocol.SSH.value
        
        # إدخال المنفذ
        default_ports = {
            'ssh': 22, 'ftp': 21, 'http': 80, 'telnet': 23,
            'rdp': 3389, 'mysql': 3306, 'custom': 9999
        }
        
        port = input(f"{Fore.CYAN}• المنفذ (افتراضي {default_ports.get(self.protocol, 22)}): {Style.RESET_ALL}").strip()
        self.port = int(port) if port.isdigit() else default_ports.get(self.protocol, 22)
        
        # إعدادات متقدمة
        print(f"\n{Fore.WHITE}⚙️  الإعدادات المتقدمة:{Style.RESET_ALL}")
        
        self.timeout = input(f"{Fore.CYAN}• مهلة الاتصال (ثواني، افتراضي 5): {Style.RESET_ALL}").strip()
        self.timeout = int(self.timeout) if self.timeout.isdigit() else 5
        
        threads = input(f"{Fore.CYAN}• عدد الخيوط (افتراضي 4): {Style.RESET_ALL}").strip()
        self.threads = int(threads) if threads.isdigit() else 4
        
        # اختيار نمط الهجوم
        print(f"\n{Fore.WHITE}🎭 اختيار نمط الهجوم:{Style.RESET_ALL}")
        for i, (mode, desc) in enumerate(self.attack_modes_info.items(), 1):
            print(f"{Fore.CYAN}{i}. {mode.upper()} - {desc}{Style.RESET_ALL}")
        
        mode_choice = input(f"\n{Fore.CYAN}اختر نمط الهجوم (1-{len(self.attack_modes_info)}): {Style.RESET_ALL}").strip()
        try:
            mode_keys = list(self.attack_modes_info.keys())
            self.attack_mode = mode_keys[int(mode_choice)-1]
        except:
            self.attack_mode = AttackMode.BASIC.value
    
    def input_users_advanced(self):
        """إدخال متقدم لقائمة المستخدمين"""
        self.clear_screen()
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}👤 مرحلة إدخال المستخدمين المتقدم{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        print(f"\n{Fore.WHITE}📝 طرق إدخال المستخدمين:{Style.RESET_ALL}")
        methods = [
            "1. إدخال يدوي (سطر بسطر)",
            "2. لصق قائمة كاملة",
            "3. استخدام قائمة شائعة",
            "4. توليد أسماء مستخدمين",
            "5. تحميل من ملف"
        ]
        
        for method in methods:
            print(f"{Fore.CYAN}{method}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.CYAN}اختر طريقة الإدخال (1-5): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            self.users = self._manual_input("المستخدم")
        elif choice == '2':
            self.users = self._paste_list("المستخدمين")
        elif choice == '3':
            self.users = self.common_users.copy()
            print(f"{Fore.GREEN}[*] تم تعيين القائمة الشائعة ({len(self.users)} مستخدم){Style.RESET_ALL}")
        elif choice == '4':
            self.users = self._generate_usernames()
        elif choice == '5':
            self.users = self._load_from_file("usernames")
        else:
            print(f"{Fore.YELLOW}[*] استخدام القائمة الافتراضية{Style.RESET_ALL}")
            self.users = self.common_users[:5]
        
        if not self.users:
            self.users = self.common_users[:3]
            print(f"{Fore.YELLOW}[!] استخدام القائمة الافتراضية{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}✅ تم إدخال {len(self.users)} مستخدم{Style.RESET_ALL}")
    
    def input_passwords_advanced(self):
        """إدخال متقدم لكلمات المرور"""
        self.clear_screen()
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🔑 مرحلة إدخال كلمات المرور المتقدم{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        print(f"\n{Fore.WHITE}📝 طرق إدخال كلمات المرور:{Style.RESET_ALL}")
        methods = [
            "1. إدخال يدوي",
            "2. لصق قائمة كاملة",
            "3. استخدام قائمة شائعة",
            "4. توليد كلمات مرور رقمية",
            "5. توليد باستخدام أقنعة",
            "6. تحميل من ملف قواميس",
            "7. إنشاء قائمة هجينة"
        ]
        
        for method in methods:
            print(f"{Fore.CYAN}{method}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.CYAN}اختر طريقة الإدخال (1-7): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            self.passwords = self._manual_input("كلمة المرور")
        elif choice == '2':
            self.passwords = self._paste_list("كلمات المرور")
        elif choice == '3':
            self.passwords = self.common_passwords.copy()
            print(f"{Fore.GREEN}[*] تم تعيين القائمة الشائعة ({len(self.passwords)} كلمة){Style.RESET_ALL}")
        elif choice == '4':
            self.passwords = self._generate_numeric_passwords()
        elif choice == '5':
            self.passwords = self._generate_masked_passwords()
        elif choice == '6':
            self.passwords = self._load_from_file("passwords")
        elif choice == '7':
            self.passwords = self._generate_hybrid_list()
        else:
            self.passwords = self.common_passwords[:5]
            print(f"{Fore.YELLOW}[*] استخدام القائمة الافتراضية{Style.RESET_ALL}")
        
        if not self.passwords:
            self.passwords = self.common_passwords[:3]
            print(f"{Fore.YELLOW}[!] استخدام القائمة الافتراضية{Style.RESET_ALL}")
        
        print(f"{Fore.GREEN}✅ تم إدخال {len(self.passwords)} كلمة مرور{Style.RESET_ALL}")
    
    def _manual_input(self, item_type: str) -> List[str]:
        """إدخال يدوي"""
        items = []
        print(f"\n{Fore.WHITE}أدخل {item_type} (سطر لكل عنصر){Style.RESET_ALL}")
        print(f"{Fore.YELLOW}اكتب 'end' لإنهاء الإدخال{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*40}{Style.RESET_ALL}")
        
        count = 1
        while True:
            item = input(f"{Fore.CYAN}{item_type} #{count}: {Style.RESET_ALL}").strip()
            if item.lower() == 'end':
                break
            if item and item not in items:
                items.append(item)
                count += 1
        
        return items
    
    def _paste_list(self, item_type: str) -> List[str]:
        """لصق قائمة"""
        print(f"\n{Fore.WHITE}🔽 الصق قائمة {item_type} (سطر لكل عنصر):{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}مثال: item1\\nitem2\\nitem3{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*40}{Style.RESET_ALL}")
        
        data = []
        print(f"{Fore.YELLOW}أدخل/الصق البيانات (اضغط Ctrl+D أو اكتب 'END' للإنهاء):{Style.RESET_ALL}")
        
        try:
            while True:
                line = input()
                if line.strip().upper() == 'END':
                    break
                data.append(line.strip())
        except EOFError:
            pass
        
        return [item for item in data if item]
    
    def _generate_usernames(self) -> List[str]:
        """توليد أسماء مستخدمين"""
        usernames = []
        
        print(f"\n{Fore.WHITE}🔧 توليد أسماء المستخدمين:{Style.RESET_ALL}")
        
        # أنواع التوليد
        print(f"{Fore.CYAN}1. أسماء مستخدمين إدارية{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. أسماء عامة{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. أسماء بناءً على الهدف{Style.RESET_ALL}")
        
        gen_type = input(f"\n{Fore.CYAN}اختر نوع التوليد (1-3): {Style.RESET_ALL}").strip()
        
        if gen_type == '1':
            usernames = [
                'admin', 'administrator', 'root', 'superuser', 
                'sysadmin', 'webadmin', 'dbadmin', 'operator'
            ]
        elif gen_type == '2':
            usernames = [
                'user', 'test', 'guest', 'demo', 'temp',
                'backup', 'support', 'service', 'info'
            ]
        elif gen_type == '3':
            # توليد بناءً على الهدف
            domain = self.target.split('.')[0] if '.' in self.target else self.target
            usernames = [
                f"{domain}_admin", f"{domain}_user", f"admin_{domain}",
                f"user_{domain}", f"{domain}123", f"{domain}admin"
            ]
        
        return usernames
    
    def _generate_numeric_passwords(self) -> List[str]:
        """توليد كلمات مرور رقمية"""
        print(f"\n{Fore.WHITE}🔢 توليد كلمات مرور رقمية:{Style.RESET_ALL}")
        
        start = input(f"{Fore.CYAN}الرقم البدائي (مثال: 1): {Style.RESET_ALL}").strip()
        end = input(f"{Fore.CYAN}الرقم النهائي (مثال: 1000): {Style.RESET_ALL}").strip()
        
        try:
            start_num = int(start)
            end_num = int(end)
            
            if end_num - start_num > 10000:
                confirm = input(f"{Fore.YELLOW}[؟] سيتم توليد {end_num - start_num + 1} كلمة. هل تريد المتابعة؟ (نعم/لا): {Style.RESET_ALL}")
                if confirm.lower() not in ['نعم', 'yes', 'y', 'ن']:
                    end_num = start_num + 1000
            
            passwords = [str(i) for i in range(start_num, end_num + 1)]
            
            # إضافة أشكال مختلفة
            variations = []
            for pwd in passwords[:100]:  # تقييد التباينات
                variations.extend([
                    pwd, 
                    pwd + '!', 
                    pwd + '@123',
                    'P@ss' + pwd,
                    pwd + pwd
                ])
            
            return passwords + variations[:1000]  # الحد الأقصى 1000 كلمة
        
        except ValueError:
            print(f"{Fore.RED}[!] إدخال غير صالح{Style.RESET_ALL}")
            return self.common_passwords
    
    def _generate_masked_passwords(self) -> List[str]:
        """توليد كلمات مرور باستخدام أقنعة"""
        print(f"\n{Fore.WHITE}🎭 توليد كلمات مرور باستخدام أقنعة:{Style.RESET_ALL}")
        
        masks = [
            "?l?l?l?l?l?l",      # أحرف صغيرة فقط
            "?u?u?u?u?u",        # أحرف كبيرة فقط
            "?l?l?l?d?d?d",      # 3 أحرف + 3 أرقام
            "?u?l?l?d?d?s",      # حرف كبير، حرفين صغيرين، رقمين، رمز
            "?d?d?d?d?d?d",      # 6 أرقام
            "?l?l?l?l?d?d",      # 4 أحرف + 2 أرقام
        ]
        
        print(f"{Fore.CYAN}الأقنعة المتاحة:{Style.RESET_ALL}")
        for i, mask in enumerate(masks, 1):
            print(f"{Fore.CYAN}{i}. {mask}{Style.RESET_ALL}")
        
        mask_choice = input(f"\n{Fore.CYAN}اختر القناع (1-{len(masks)}): {Style.RESET_ALL}").strip()
        
        try:
            selected_mask = masks[int(mask_choice)-1]
            return self._expand_mask(selected_mask)[:1000]  # الحد الأقصى 1000 كلمة
        except:
            return ['password123', 'admin123', 'test123']
    
    def _expand_mask(self, mask: str) -> List[str]:
        """توسيع القناع إلى قائمة كلمات مرور"""
        import itertools
        
        # تعيين مجموعات الأحرف لكل رمز
        char_sets = {
            '?l': 'abcdefghijklmnopqrstuvwxyz',
            '?u': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            '?d': '0123456789',
            '?s': '!@#$%^&*()_+-=[]{}|;:,.<>?'
        }
        
        # تحويل القناع إلى قائمة مجموعات
        sets = []
        i = 0
        while i < len(mask):
            if mask[i] == '?':
                symbol = mask[i:i+2]
                if symbol in char_sets:
                    sets.append(list(char_sets[symbol]))
                    i += 2
                else:
                    sets.append([mask[i]])
                    i += 1
            else:
                sets.append([mask[i]])
                i += 1
        
        # توليد جميع التركيبات
        passwords = []
        for combo in itertools.product(*sets):
            passwords.append(''.join(combo))
        
        return passwords
    
    def _generate_hybrid_list(self) -> List[str]:
        """إنشاء قائمة هجينة"""
        print(f"\n{Fore.WHITE}🧬 إنشاء قائمة كلمات مرور هجينة:{Style.RESET_ALL}")
        
        base_words = ['admin', 'user', 'pass', 'test', 'system', 'server']
        suffixes = ['123', '1234', '12345', '!@#', '2023', '2024', '!']
        prefixes = ['P@ss', 'Sec', 'My', 'Super', 'Ultra']
        
        passwords = []
        
        # توليد تركيبيات
        for base in base_words:
            for suffix in suffixes:
                passwords.append(base + suffix)
            for prefix in prefixes:
                passwords.append(prefix + base)
        
        # إضافة تبديل حالة الأحرف
        variations = []
        for pwd in passwords[:50]:
            variations.append(pwd)
            variations.append(pwd.upper())
            variations.append(pwd.capitalize())
        
        return list(set(variations))  # إزالة التكرارات
    
    def _load_from_file(self, file_type: str) -> List[str]:
        """تحميل قائمة من ملف"""
        filename = input(f"{Fore.CYAN}أدخل اسم الملف (افتراضي: {file_type}.txt): {Style.RESET_ALL}").strip()
        if not filename:
            filename = f"{file_type}.txt"
        
        try:
            if not os.path.exists(filename):
                # إنشاء ملف تجريبي إذا لم يوجد
                sample_data = self.common_users if file_type == "usernames" else self.common_passwords
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(sample_data))
                print(f"{Fore.YELLOW}[*] تم إنشاء ملف تجريبي: {filename}{Style.RESET_ALL}")
            
            with open(filename, 'r', encoding='utf-8') as f:
                items = [line.strip() for line in f if line.strip()]
            
            print(f"{Fore.GREEN}[*] تم تحميل {len(items)} عنصر من {filename}{Style.RESET_ALL}")
            return items
        
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ في تحميل الملف: {e}{Style.RESET_ALL}")
            return []
    
    def simulate_advanced_attack(self):
        """محاكاة هجوم متقدم"""
        self.clear_screen()
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚡ بدء محاكاة الهجوم المتقدم{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        # عرض إحصائيات الهجوم
        total_combinations = len(self.users) * len(self.passwords)
        
        print(f"\n{Fore.WHITE}📊 إحصائيات الهجوم:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   • الهدف:{Style.RESET_ALL} {self.target}:{self.port}")
        print(f"{Fore.CYAN}   • البروتوكول:{Style.RESET_ALL} {self.protocol.upper()}")
        print(f"{Fore.CYAN}   • نمط الهجوم:{Style.RESET_ALL} {self.attack_mode}")
        print(f"{Fore.CYAN}   • عدد المستخدمين:{Style.RESET_ALL} {len(self.users)}")
        print(f"{Fore.CYAN}   • عدد كلمات المرور:{Style.RESET_ALL} {len(self.passwords)}")
        print(f"{Fore.CYAN}   • إجمالي المجموعات:{Style.RESET_ALL} {total_combinations:,}")
        print(f"{Fore.CYAN}   • عدد الخيوط:{Style.RESET_ALL} {self.threads}")
        
        if total_combinations > 10000:
            print(f"\n{Fore.YELLOW}[!] عدد المجموعات كبير جدًا ({total_combinations:,}){Style.RESET_ALL}")
            limit = input(f"{Fore.CYAN}[؟] أدخل الحد الأقصى للمحاولات (افتراضي: 5000): {Style.RESET_ALL}").strip()
            max_attempts = int(limit) if limit.isdigit() else 5000
        else:
            max_attempts = total_combinations
        
        input(f"\n{Fore.GREEN}اضغط Enter لبدء المحاكاة...{Style.RESET_ALL}")
        
        # بدء المحاكاة
        start_time = time.time()
        
        print(f"\n{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] جارٍ تنفيذ الهجوم...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        
        # محاكاة بيانات اعتماد صحيحة
        valid_user = random.choice(self.users) if self.users else 'admin'
        valid_password = random.choice(self.passwords) if self.passwords else 'admin123'
        
        # إعداد قائمة المحاولات
        attempts_list = []
        for user in self.users[:100]:  # تحديد للمحاكاة
            for password in self.passwords[:100]:
                if len(attempts_list) >= max_attempts:
                    break
                attempts_list.append((user, password))
        
        # محاكاة الهجوم بخيوط متعددة
        print(f"\n{Fore.CYAN}[*] بدء {self.threads} خيوط هجوم...{Style.RESET_ALL}")
        
        results_queue = queue.Queue()
        stop_event = threading.Event()
        
        # إنشاء خيوط الهجوم
        threads = []
        chunk_size = len(attempts_list) // self.threads
        
        for i in range(self.threads):
            start_idx = i * chunk_size
            end_idx = start_idx + chunk_size if i < self.threads - 1 else len(attempts_list)
            thread_attempts = attempts_list[start_idx:end_idx]
            
            thread = threading.Thread(
                target=self._attack_thread,
                args=(i, thread_attempts, valid_user, valid_password, results_queue, stop_event)
            )
            threads.append(thread)
            thread.start()
        
        # عرض التقدم
        completed = 0
        success_found = False
        
        while any(t.is_alive() for t in threads) and not success_found:
            completed = sum(1 for t in threads if not t.is_alive()) * chunk_size
            
            # عرض شريط التقدم
            progress = (completed / len(attempts_list)) * 100
            bar_length = 40
            filled_length = int(bar_length * progress // 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            
            sys.stdout.write(f"\r{Fore.GREEN}[{bar}] {progress:.1f}% | المحاولات: {completed}/{len(attempts_list)} | السرعة: {completed/max(1, time.time()-start_time):.1f}/ث{Style.RESET_ALL}")
            sys.stdout.flush()
            
            time.sleep(0.1)
            
            # التحقق من النتائج
            if not results_queue.empty():
                result = results_queue.get()
                if result:
                    self.found = True
                    self.credentials = result
                    success_found = True
                    stop_event.set()
        
        # انتظار انتهاء جميع الخيوط
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        self.attempts = completed
        
        # عرض النتائج
        print(f"\n\n{Fore.CYAN}{'─'*60}{Style.RESET_ALL}")
        
        if self.found and self.credentials:
            print(f"\n{Fore.GREEN}🎉 [SUCCESS] تم العثور على بيانات الاعتماد!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}   👤 المستخدم:{Style.RESET_ALL} {self.credentials[0]}")
            print(f"{Fore.CYAN}   🔑 كلمة المرور:{Style.RESET_ALL} {self.credentials[1]}")
            print(f"{Fore.CYAN}   ⚡ الوقت المستغرق:{Style.RESET_ALL} {elapsed:.2f} ثانية")
            print(f"{Fore.CYAN}   📊 المحاولات:{Style.RESET_ALL} {self.attempts}")
            print(f"{Fore.CYAN}   🚀 السرعة:{Style.RESET_ALL} {self.attempts/elapsed:.1f} محاولة/ثانية")
        else:
            print(f"\n{Fore.RED}❌ [FAILED] لم يتم العثور على بيانات اعتماد صحيحة{Style.RESET_ALL}")
            print(f"{Fore.CYAN}   ⏱️  الوقت المستغرق:{Style.RESET_ALL} {elapsed:.2f} ثانية")
            print(f"{Fore.CYAN}   📊 المحاولات:{Style.RESET_ALL} {self.attempts}")
            print(f"{Fore.CYAN}   🚀 السرعة:{Style.RESET_ALL} {self.attempts/elapsed:.1f} محاولة/ثانية")
        
        # حفظ النتيجة
        result = AttackResult(
            target=self.target,
            protocol=self.protocol,
            start_time=datetime.fromtimestamp(start_time),
            end_time=datetime.fromtimestamp(end_time),
            attempts=self.attempts,
            success=self.found,
            credentials={'username': self.credentials[0], 'password': self.credentials[1]} if self.credentials else {},
            speed=self.attempts/elapsed if elapsed > 0 else 0,
            user_agent=self.user_agent
        )
        self.results.append(result)
        
        # تحديث الإحصائيات
        self.stats['total_attempts'] += self.attempts
        if self.found:
            self.stats['successful_attacks'] += 1
        else:
            self.stats['failed_attacks'] += 1
        self.stats['total_time'] += elapsed
    
    def _attack_thread(self, thread_id, attempts, valid_user, valid_password, results_queue, stop_event):
        """خيط الهجوم"""
        for user, password in attempts:
            if stop_event.is_set():
                return
            
            self.attempts += 1
            
            # محاكاة تأخير الشبكة
            time.sleep(random.uniform(0.01, 0.1))
            
            # محاكاة النجاح
            if (user == valid_user and password == valid_password) or \
               (random.random() < 0.001):  # 0.1% فرصة نجاح عشوائية
                results_queue.put((user, password))
                return
    
    def export_results_advanced(self):
        """تصدير النتائج بشكل متقدم"""
        self.clear_screen()
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💾 تصدير النتائج المتقدم{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        if not self.results:
            print(f"\n{Fore.RED}[!] لا توجد نتائج للتصدير{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.WHITE}📁 تنسيقات التصدير:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. ملف نصي (TXT){Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. ملف JSON{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. ملف HTML (تقرير مفصل){Style.RESET_ALL}")
        print(f"{Fore.CYAN}4. ملف CSV{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.CYAN}اختر تنسيق التصدير (1-4): {Style.RESET_ALL}").strip()
        
        filename = input(f"{Fore.CYAN}أدخل اسم الملف (بدون امتداد): {Style.RESET_ALL}").strip()
        if not filename:
            filename = "bruteforce_report"
        
        try:
            if choice == '1':
                self._export_txt(filename + '.txt')
            elif choice == '2':
                self._export_json(filename + '.json')
            elif choice == '3':
                self._export_html(filename + '.html')
            elif choice == '4':
                self._export_csv(filename + '.csv')
            else:
                self._export_txt(filename + '.txt')
            
            print(f"\n{Fore.GREEN}✅ تم تصدير النتائج بنجاح{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"{Fore.RED}[!] خطأ في التصدير: {e}{Style.RESET_ALL}")
    
    def _export_txt(self, filename: str):
        """تصدير إلى ملف نصي"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("تقرير مختبر التخمين التفاعلي المتقدم\n")
            f.write("=" * 80 + "\n\n")
            
            # معلومات الجلسة
            f.write("معلومات الجلسة:\n")
            f.write("-" * 40 + "\n")
            f.write(f"وقت التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"إصدار الأداة: 2.0\n")
            f.write(f"نظام التشغيل: {os.name}\n\n")
            
            # الإحصائيات العامة
            f.write("الإحصائيات العامة:\n")
            f.write("-" * 40 + "\n")
            f.write(f"إجمالي الهجمات: {len(self.results)}\n")
            f.write(f"الهجمات الناجحة: {sum(1 for r in self.results if r.success)}\n")
            f.write(f"إجمالي المحاولات: {self.stats['total_attempts']}\n")
            f.write(f"إجمالي الوقت: {self.stats['total_time']:.2f} ثانية\n")
            f.write(f"متوسط السرعة: {self.stats['avg_speed']:.1f} محاولة/ثانية\n\n")
            
            # التفاصيل
            for i, result in enumerate(self.results, 1):
                f.write(f"الهجوم #{i}:\n")
                f.write(f"  الهدف: {result.target}:{self.port}\n")
                f.write(f"  البروتوكول: {result.protocol}\n")
                f.write(f"  النتيجة: {'نجاح' if result.success else 'فشل'}\n")
                if result.success:
                    f.write(f"  المستخدم: {result.credentials.get('username', '')}\n")
                    f.write(f"  كلمة المرور: {result.credentials.get('password', '')}\n")
                f.write(f"  المحاولات: {result.attempts}\n")
                f.write(f"  الوقت: {(result.end_time - result.start_time).total_seconds():.2f} ثانية\n")
                f.write(f"  السرعة: {result.speed:.1f} محاولة/ثانية\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("نهاية التقرير\n")
            f.write("=" * 80 + "\n")
    
    def _export_json(self, filename: str):
        """تصدير إلى JSON"""
        data = {
            'metadata': {
                'tool': 'BruteForceLab Advanced',
                'version': '2.0',
                'export_date': datetime.now().isoformat()
            },
            'statistics': self.stats,
            'attack_config': {
                'target': self.target,
                'protocol': self.protocol,
                'port': self.port,
                'attack_mode': self.attack_mode,
                'threads': self.threads
            },
            'results': [asdict(r) for r in self.results],
            'users_count': len(self.users),
            'passwords_count': len(self.passwords)
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    
    def _export_html(self, filename: str):
        """تصدير إلى HTML"""
        html = f"""
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير BruteForceLab</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            padding: 30px;
            margin-top: 20px;
        }}
        .header {{
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }}
        .success {{
            color: #28a745;
            font-weight: bold;
        }}
        .failure {{
            color: #dc3545;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: right;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>تقرير BruteForceLab المتقدم</h1>
            <p>أداة تعليمية للاختبارات الأمنية</p>
            <p>تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <h2>📊 الإحصائيات العامة</h2>
        <div class="stats-grid">
            <div class="stat-card">
                <h3>إجمالي الهجمات</h3>
                <p>{len(self.results)}</p>
            </div>
            <div class="stat-card">
                <h3>الهجمات الناجحة</h3>
                <p class="success">{sum(1 for r in self.results if r.success)}</p>
            </div>
            <div class="stat-card">
                <h3>إجمالي المحاولات</h3>
                <p>{self.stats['total_attempts']:,}</p>
            </div>
            <div class="stat-card">
                <h3>متوسط السرعة</h3>
                <p>{self.stats['avg_speed']:.1f} محاولة/ثانية</p>
            </div>
        </div>
        
        <h2>🎯 معلومات الهجوم</h2>
        <div class="stat-card">
            <p><strong>الهدف:</strong> {self.target}</p>
            <p><strong>البروتوكول:</strong> {self.protocol}</p>
            <p><strong>المنفذ:</strong> {self.port}</p>
            <p><strong>نمط الهجوم:</strong> {self.attack_mode}</p>
        </div>
        
        <h2>📋 نتائج الهجمات</h2>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>الهدف</th>
                    <th>النتيجة</th>
                    <th>المستخدم</th>
                    <th>كلمة المرور</th>
                    <th>المحاولات</th>
                    <th>الوقت (ث)</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for i, result in enumerate(self.results, 1):
            status_class = "success" if result.success else "failure"
            status_text = "نجاح" if result.success else "فشل"
            username = result.credentials.get('username', '-') if result.credentials else '-'
            password = result.credentials.get('password', '-') if result.credentials else '-'
            
            html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{result.target}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{username}</td>
                    <td>{password}</td>
                    <td>{result.attempts}</td>
                    <td>{(result.end_time - result.start_time).total_seconds():.2f}</td>
                </tr>
            """
        
        html += """
            </tbody>
        </table>
        
        <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
            <h3>ملاحظات:</h3>
            <p>• هذا التقرير للأغراض التعليمية والتدريبية فقط</p>
            <p>• تم إنشاؤه بواسطة BruteForceLab Advanced v2.0</p>
            <p>• جميع البيانات في هذا التقرير هي بيانات محاكاة لأغراض تعليمية</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _export_csv(self, filename: str):
        """تصدير إلى CSV"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            
            # كتابة العنوان
            writer.writerow(['#', 'الهدف', 'البروتوكول', 'النتيجة', 'المستخدم', 'كلمة المرور', 'المحاولات', 'الوقت (ث)', 'السرعة'])
            
            # كتابة البيانات
            for i, result in enumerate(self.results, 1):
                status = 'نجاح' if result.success else 'فشل'
                username = result.credentials.get('username', '') if result.credentials else ''
                password = result.credentials.get('password', '') if result.credentials else ''
                time_taken = (result.end_time - result.start_time).total_seconds()
                
                writer.writerow([
                    i,
                    result.target,
                    result.protocol,
                    status,
                    username,
                    password,
                    result.attempts,
                    f"{time_taken:.2f}",
                    f"{result.speed:.1f}"
                ])
    
    def show_dashboard(self):
        """عرض لوحة التحكم"""
        self.clear_screen()
        self.print_banner()
        
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📊 لوحة التحكم الرئيسية{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        # عرض حالة النظام
        print(f"\n{Fore.WHITE}🖥️  حالة النظام:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}• نظام التشغيل:{Style.RESET_ALL} {os.name}")
        print(f"{Fore.CYAN}• إصدار بايثون:{Style.RESET_ALL} {sys.version.split()[0]}")
        
        # عرض الإحصائيات
        print(f"\n{Fore.WHITE}📈 الإحصائيات:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}• إجمالي الهجمات:{Style.RESET_ALL} {len(self.results)}")
        print(f"{Fore.CYAN}• الهجمات الناجحة:{Style.RESET_ALL} {sum(1 for r in self.results if r.success)}")
        print(f"{Fore.CYAN}• إجمالي المحاولات:{Style.RESET_ALL} {self.stats['total_attempts']:,}")
        
        # عرض الإعدادات الحالية
        print(f"\n{Fore.WHITE}⚙️  الإعدادات الحالية:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}• الهدف:{Style.RESET_ALL} {self.target if self.target else 'غير محدد'}")
        print(f"{Fore.CYAN}• البروتوكول:{Style.RESET_ALL} {self.protocol.upper()}")
        print(f"{Fore.CYAN}• المستخدمين:{Style.RESET_ALL} {len(self.users)} مستخدم")
        print(f"{Fore.CYAN}• كلمات المرور:{Style.RESET_ALL} {len(self.passwords)} كلمة")
        
        # آخر 5 هجمات
        if self.results:
            print(f"\n{Fore.WHITE}🕐 آخر الهجمات:{Style.RESET_ALL}")
            recent_results = self.results[-5:]
            for i, result in enumerate(recent_results, 1):
                status = f"{Fore.GREEN}✓" if result.success else f"{Fore.RED}✗"
                print(f"{status}{Style.RESET_ALL} {result.target} - {result.attempts} محاولة")
    
    def show_menu(self):
        """عرض القائمة الرئيسية المتقدمة"""
        while True:
            self.clear_screen()
            self.print_banner()
            
            print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}القائمة الرئيسية المتقدمة{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            
            self.show_dashboard()
            
            print(f"\n{Fore.WHITE}📋 الخيارات المتاحة:{Style.RESET_ALL}")
            menu_options = [
                f"{Fore.CYAN}1.{Style.RESET_ALL} ⚙️  إعدادات متقدمة",
                f"{Fore.CYAN}2.{Style.RESET_ALL} 👤 إدخال المستخدمين (متقدم)",
                f"{Fore.CYAN}3.{Style.RESET_ALL} 🔑 إدخال كلمات المرور (متقدم)",
                f"{Fore.CYAN}4.{Style.RESET_ALL} ⚡ بدء هجوم متقدم",
                f"{Fore.CYAN}5.{Style.RESET_ALL} 📊 عرض التقارير",
                f"{Fore.CYAN}6.{Style.RESET_ALL} 💾 تصدير النتائج",
                f"{Fore.CYAN}7.{Style.RESET_ALL} 🛠️  أدوات مساعدة",
                f"{Fore.CYAN}8.{Style.RESET_ALL} 🚪 خروج"
            ]
            
            for option in menu_options:
                print(option)
            
            choice = input(f"\n{Fore.YELLOW}اختر رقم الخيار (1-8): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                self.get_target_configuration()
            elif choice == '2':
                self.input_users_advanced()
            elif choice == '3':
                self.input_passwords_advanced()
            elif choice == '4':
                if not self.target or not self.users or not self.passwords:
                    print(f"\n{Fore.RED}[!] يجب تعيين الهدف والمستخدمين وكلمات المرور أولاً{Style.RESET_ALL}")
                    input(f"{Fore.YELLOW}اضغط Enter للمتابعة...{Style.RESET_ALL}")
                else:
                    self.simulate_advanced_attack()
                    input(f"\n{Fore.YELLOW}اضغط Enter للعودة للقائمة...{Style.RESET_ALL}")
            elif choice == '5':
                self.show_reports()
                input(f"\n{Fore.YELLOW}اضغط Enter للمتابعة...{Style.RESET_ALL}")
            elif choice == '6':
                if not self.results:
                    print(f"\n{Fore.RED}[!] لا توجد نتائج للتصدير{Style.RESET_ALL}")
                else:
                    self.export_results_advanced()
                input(f"\n{Fore.YELLOW}اضغط Enter للمتابعة...{Style.RESET_ALL}")
            elif choice == '7':
                self.tools_menu()
            elif choice == '8':
                print(f"\n{Fore.GREEN}👋 مع السلامة!{Style.RESET_ALL}")
                break
            else:
                print(f"{Fore.RED}[!] خيار غير صالح{Style.RESET_ALL}")
                time.sleep(1)
    
    def show_reports(self):
        """عرض التقارير"""
        self.clear_screen()
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📊 التقارير والإحصائيات{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        if not self.results:
            print(f"\n{Fore.YELLOW}لا توجد نتائج لعرضها بعد{Style.RESET_ALL}")
            return
        
        # إحصائيات عامة
        total_attacks = len(self.results)
        successful = sum(1 for r in self.results if r.success)
        success_rate = (successful / total_attacks * 100) if total_attacks > 0 else 0
        
        print(f"\n{Fore.WHITE}📈 الإحصائيات العامة:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}• إجمالي الهجمات:{Style.RESET_ALL} {total_attacks}")
        print(f"{Fore.CYAN}• الهجمات الناجحة:{Style.RESET_ALL} {successful}")
        print(f"{Fore.CYAN}• معدل النجاح:{Style.RESET_ALL} {success_rate:.1f}%")
        print(f"{Fore.CYAN}• إجمالي المحاولات:{Style.RESET_ALL} {self.stats['total_attempts']:,}")
        print(f"{Fore.CYAN}• إجمالي الوقت:{Style.RESET_ALL} {self.stats['total_time']:.2f} ثانية")
        
        # تفاصيل الهجمات
        print(f"\n{Fore.WHITE}🎯 تفاصيل الهجمات:{Style.RESET_ALL}")
        for i, result in enumerate(self.results, 1):
            status = f"{Fore.GREEN}[نجاح]" if result.success else f"{Fore.RED}[فشل]"
            print(f"\n{status}{Style.RESET_ALL} الهجوم #{i}:")
            print(f"  {Fore.CYAN}• الهدف:{Style.RESET_ALL} {result.target}")
            print(f"  {Fore.CYAN}• البروتوكول:{Style.RESET_ALL} {result.protocol}")
            print(f"  {Fore.CYAN}• المحاولات:{Style.RESET_ALL} {result.attempts}")
            print(f"  {Fore.CYAN}• الوقت:{Style.RESET_ALL} {(result.end_time - result.start_time).total_seconds():.2f} ثانية")
            if result.success:
                print(f"  {Fore.CYAN}• المستخدم:{Style.RESET_ALL} {result.credentials.get('username', '')}")
                print(f"  {Fore.CYAN}• كلمة المرور:{Style.RESET_ALL} {result.credentials.get('password', '')}")
    
    def tools_menu(self):
        """قائمة الأدوات المساعدة"""
        while True:
            self.clear_screen()
            print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}🛠️  الأدوات المساعدة{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
            
            print(f"\n{Fore.WHITE}الأدوات المتاحة:{Style.RESET_ALL}")
            tools = [
                f"{Fore.CYAN}1.{Style.RESET_ALL} 🔧 تحليل قوة كلمات المرور",
                f"{Fore.CYAN}2.{Style.RESET_ALL} 📊 إحصائيات القوائم",
                f"{Fore.CYAN}3.{Style.RESET_ALL} 🔄 تحويل التنسيقات",
                f"{Fore.CYAN}4.{Style.RESET_ALL} 🧹 تنظيف البيانات",
                f"{Fore.CYAN}5.{Style.RESET_ALL} 🔙 العودة للقائمة الرئيسية"
            ]
            
            for tool in tools:
                print(tool)
            
            choice = input(f"\n{Fore.YELLOW}اختر أداة (1-5): {Style.RESET_ALL}").strip()
            
            if choice == '1':
                self.password_strength_analyzer()
            elif choice == '2':
                self.list_statistics()
            elif choice == '3':
                self.convert_formats()
            elif choice == '4':
                self.clean_data()
            elif choice == '5':
                break
            else:
                print(f"{Fore.RED}[!] خيار غير صالح{Style.RESET_ALL}")
                time.sleep(1)
    
    def password_strength_analyzer(self):
        """تحليل قوة كلمات المرور"""
        self.clear_screen()
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🔧 تحليل قوة كلمات المرور{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        if not self.passwords:
            print(f"\n{Fore.RED}[!] لا توجد كلمات مرور لتحليلها{Style.RESET_ALL}")
            return
        
        # تحليل قوة كل كلمة مرور
        strengths = []
        for password in self.passwords[:50]:  # تحليل أول 50 كلمة فقط
            strength = self._calculate_password_strength(password)
            strengths.append((password, strength))
        
        # عرض النتائج
        print(f"\n{Fore.WHITE}📊 نتائج التحليل:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'كلمة المرور':<20} {'القوة':<10} {'التقييم'}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")
        
        for password, strength in strengths:
            if strength >= 80:
                rating = f"{Fore.GREEN}قوية جدًا{Style.RESET_ALL}"
            elif strength >= 60:
                rating = f"{Fore.YELLOW}قوية{Style.RESET_ALL}"
            elif strength >= 40:
                rating = f"{Fore.YELLOW}متوسطة{Style.RESET_ALL}"
            else:
                rating = f"{Fore.RED}ضعيفة{Style.RESET_ALL}"
            
            print(f"{password:<20} {strength:<10} {rating}")
    
    def _calculate_password_strength(self, password: str) -> int:
        """حساب قوة كلمة المرور"""
        score = 0
        
        # طول كلمة المرور
        if len(password) >= 12:
            score += 30
        elif len(password) >= 8:
            score += 20
        elif len(password) >= 6:
            score += 10
        
        # تنوع الأحرف
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        char_types = sum([has_lower, has_upper, has_digit, has_special])
        score += char_types * 15
        
        # تعقيد إضافي
        if password.lower() in self.common_passwords:
            score -= 20
        
        return min(100, max(0, score))
    
    def list_statistics(self):
        """إحصائيات القوائم"""
        self.clear_screen()
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}📊 إحصائيات القوائم{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        print(f"\n{Fore.WHITE}👤 إحصائيات المستخدمين:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}• العدد الإجمالي:{Style.RESET_ALL} {len(self.users)}")
        if self.users:
            avg_length = sum(len(u) for u in self.users) / len(self.users)
            print(f"{Fore.CYAN}• متوسط الطول:{Style.RESET_ALL} {avg_length:.1f} حرف")
            
            # أكثر المستخدمين شيوعًا
            print(f"{Fore.CYAN}• أول 5 مستخدمين:{Style.RESET_ALL}")
            for user in self.users[:5]:
                print(f"  - {user}")
        
        print(f"\n{Fore.WHITE}🔑 إحصائيات كلمات المرور:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}• العدد الإجمالي:{Style.RESET_ALL} {len(self.passwords)}")
        if self.passwords:
            avg_length = sum(len(p) for p in self.passwords) / len(self.passwords)
            print(f"{Fore.CYAN}• متوسط الطول:{Style.RESET_ALL} {avg_length:.1f} حرف")
            
            # أنواع الأحرف
            char_types = {'أحرف صغيرة': 0, 'أحرف كبيرة': 0, 'أرقام': 0, 'رموز': 0}
            for pwd in self.passwords[:100]:  # عينة
                if any(c.islower() for c in pwd):
                    char_types['أحرف صغيرة'] += 1
                if any(c.isupper() for c in pwd):
                    char_types['أحرف كبيرة'] += 1
                if any(c.isdigit() for c in pwd):
                    char_types['أرقام'] += 1
                if any(not c.isalnum() for c in pwd):
                    char_types['رموز'] += 1
            
            print(f"{Fore.CYAN}• توزيع أنواع الأحرف (من العينة):{Style.RESET_ALL}")
            for char_type, count in char_types.items():
                percentage = (count / min(100, len(self.passwords))) * 100
                print(f"  - {char_type}: {percentage:.1f}%")
    
    def log_activity(self, activity_type: str, details: str):
        """تسجيل نشاط المستخدم"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': activity_type,
            'details': details,
            'target': self.target,
            'user_agent': self.user_agent
        }
        
        # في بيئة حقيقية، هنا سيتم حفظ السجل في ملف أو قاعدة بيانات
        pass

def main():
    """الدالة الرئيسية"""
    try:
        # التحقق من المتطلبات
        try:
            import colorama
        except ImportError:
            print("⚠️  جاري تثبيت حزم إضافية...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
            import colorama
        
        simulator = InteractiveBruteForcer()
        simulator.clear_screen()
        simulator.print_banner()
        simulator.ethical_warning()
        simulator.show_menu()
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️  تم إيقاف البرنامج بواسطة المستخدم{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}[!] خطأ غير متوقع: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
