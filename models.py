"""
مدل‌های پایگاه داده برای اکوسیستم ربات‌های هوشمند اسرائیل
Database Models for Israeli Smart Bot Ecosystem
"""

import sqlite3
import json
import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """مدیریت پایگاه داده SQLite"""
    
    def __init__(self, db_path: str = "israel_rp.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """ایجاد جداول پایگاه داده"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # جدول کاربران
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        username TEXT NOT NULL,
                        display_name TEXT,
                        role TEXT DEFAULT 'توریست',
                        balance INTEGER DEFAULT 1000,
                        experience_points INTEGER DEFAULT 0,
                        join_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        last_active TEXT DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        skills TEXT DEFAULT '{}',
                        achievements TEXT DEFAULT '[]',
                        properties TEXT DEFAULT '[]',
                        job TEXT,
                        education TEXT,
                        political_party TEXT,
                        military_rank TEXT,
                        intelligence_level INTEGER DEFAULT 0,
                        criminal_record TEXT DEFAULT '[]',
                        diplomatic_relations TEXT DEFAULT '{}',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # جدول رول‌ها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS roles (
                        role_id TEXT PRIMARY KEY,
                        role_name TEXT NOT NULL,
                        role_type TEXT NOT NULL,
                        permissions TEXT DEFAULT '[]',
                        color INTEGER DEFAULT 0xFFFFFF,
                        position INTEGER DEFAULT 0,
                        is_hoist BOOLEAN DEFAULT 0,
                        is_mentionable BOOLEAN DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول کانال‌ها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS channels (
                        channel_id TEXT PRIMARY KEY,
                        channel_name TEXT NOT NULL,
                        channel_type TEXT NOT NULL,
                        category TEXT,
                        permissions TEXT DEFAULT '{}',
                        is_private BOOLEAN DEFAULT 0,
                        owner_id TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول دولت
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS government (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        government_type TEXT DEFAULT 'دموکراسی پارلمانی',
                        prime_minister_id TEXT,
                        knesset_members TEXT DEFAULT '[]',
                        cabinet_members TEXT DEFAULT '{}',
                        laws TEXT DEFAULT '[]',
                        elections TEXT DEFAULT '[]',
                        public_approval INTEGER DEFAULT 75,
                        budget INTEGER DEFAULT 1000000,
                        tax_rate REAL DEFAULT 0.15,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول ارتش
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS military (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        defcon_level INTEGER DEFAULT 5,
                        total_forces INTEGER DEFAULT 1000,
                        air_force INTEGER DEFAULT 200,
                        ground_forces INTEGER DEFAULT 500,
                        navy INTEGER DEFAULT 200,
                        intelligence_units INTEGER DEFAULT 100,
                        equipment TEXT DEFAULT '{}',
                        missions TEXT DEFAULT '[]',
                        war_history TEXT DEFAULT '[]',
                        alliances TEXT DEFAULT '[]',
                        enemies TEXT DEFAULT '[]',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول اقتصاد
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS economy (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        national_currency TEXT DEFAULT 'شِکِل',
                        exchange_rate REAL DEFAULT 1.0,
                        inflation_rate REAL DEFAULT 0.02,
                        gdp INTEGER DEFAULT 10000000,
                        national_debt INTEGER DEFAULT 0,
                        resources TEXT DEFAULT '{}',
                        companies TEXT DEFAULT '[]',
                        stock_market TEXT DEFAULT '{}',
                        trade_relations TEXT DEFAULT '{}',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول رویدادها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_type TEXT NOT NULL,
                        event_name TEXT NOT NULL,
                        event_description TEXT,
                        event_data TEXT DEFAULT '{}',
                        severity TEXT DEFAULT 'normal',
                        affected_users TEXT DEFAULT '[]',
                        affected_channels TEXT DEFAULT '[]',
                        start_time TEXT DEFAULT CURRENT_TIMESTAMP,
                        end_time TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول مأموریت‌ها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS missions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        mission_name TEXT NOT NULL,
                        mission_type TEXT NOT NULL,
                        mission_description TEXT,
                        mission_requirements TEXT DEFAULT '{}',
                        mission_rewards TEXT DEFAULT '{}',
                        assigned_users TEXT DEFAULT '[]',
                        mission_status TEXT DEFAULT 'active',
                        start_time TEXT DEFAULT CURRENT_TIMESTAMP,
                        end_time TEXT,
                        difficulty TEXT DEFAULT 'medium',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول قوانین
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS laws (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        law_name TEXT NOT NULL,
                        law_description TEXT,
                        law_type TEXT NOT NULL,
                        proposed_by TEXT NOT NULL,
                        proposed_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        voting_status TEXT DEFAULT 'active',
                        votes_for INTEGER DEFAULT 0,
                        votes_against INTEGER DEFAULT 0,
                        votes_abstain INTEGER DEFAULT 0,
                        required_majority INTEGER DEFAULT 51,
                        is_passed BOOLEAN DEFAULT 0,
                        passed_date TEXT,
                        law_effects TEXT DEFAULT '{}',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول انتخابات
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS elections (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        election_type TEXT NOT NULL,
                        election_name TEXT NOT NULL,
                        election_description TEXT,
                        candidates TEXT DEFAULT '[]',
                        registered_voters TEXT DEFAULT '[]',
                        votes TEXT DEFAULT '{}',
                        election_status TEXT DEFAULT 'upcoming',
                        start_date TEXT,
                        end_date TEXT,
                        results TEXT DEFAULT '{}',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول شرکت‌ها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS companies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_name TEXT NOT NULL,
                        company_type TEXT NOT NULL,
                        owner_id TEXT NOT NULL,
                        company_description TEXT,
                        company_assets TEXT DEFAULT '{}',
                        company_employees TEXT DEFAULT '[]',
                        company_products TEXT DEFAULT '[]',
                        company_balance INTEGER DEFAULT 10000,
                        company_reputation INTEGER DEFAULT 50,
                        company_created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول املاک
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS properties (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        property_name TEXT NOT NULL,
                        property_type TEXT NOT NULL,
                        owner_id TEXT NOT NULL,
                        property_location TEXT,
                        property_value INTEGER DEFAULT 10000,
                        property_features TEXT DEFAULT '[]',
                        property_tenants TEXT DEFAULT '[]',
                        property_created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                        is_active BOOLEAN DEFAULT 1,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول مهارت‌ها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS skills (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        skill_name TEXT NOT NULL,
                        skill_type TEXT NOT NULL,
                        skill_description TEXT,
                        max_level INTEGER DEFAULT 10,
                        xp_per_level INTEGER DEFAULT 1000,
                        skill_effects TEXT DEFAULT '{}',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول دستاوردها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS achievements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        achievement_name TEXT NOT NULL,
                        achievement_description TEXT,
                        achievement_type TEXT NOT NULL,
                        achievement_icon TEXT,
                        achievement_reward INTEGER DEFAULT 0,
                        achievement_requirements TEXT DEFAULT '{}',
                        is_hidden BOOLEAN DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول لاگ‌ها
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        log_type TEXT NOT NULL,
                        log_message TEXT NOT NULL,
                        user_id TEXT,
                        channel_id TEXT,
                        guild_id TEXT,
                        log_data TEXT DEFAULT '{}',
                        log_level TEXT DEFAULT 'INFO',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # جدول تنظیمات
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        setting_key TEXT PRIMARY KEY,
                        setting_value TEXT NOT NULL,
                        setting_description TEXT,
                        setting_type TEXT DEFAULT 'string',
                        is_public BOOLEAN DEFAULT 0,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
 ''')
                
                # ایجاد ایندکس‌ها
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_balance ON users(balance)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_experience ON users(experience_points)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_active ON events(is_active)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_missions_status ON missions(mission_status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_laws_status ON laws(voting_status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_elections_status ON elections(election_status)')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def get_connection(self):
        """دریافت اتصال به پایگاه داده"""
        return sqlite3.connect(self.db_path)
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """اجرای کوئری SELECT"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
    
    def execute_update(self, query: str, params: tuple = ()) -> bool:
        """اجرای کوئری INSERT/UPDATE/DELETE"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error executing update: {e}")
            return False
    
    def execute_many(self, query: str, params_list: List[tuple]) -> bool:
        """اجرای چندین کوئری همزمان"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error executing many: {e}")
            return False

class User:
    """کلاس کاربر"""
    
    def __init__(self, user_id: str, db_manager: DatabaseManager):
        self.user_id = user_id
        self.db_manager = db_manager
        self.load_user_data()
    
    def load_user_data(self):
        """بارگذاری اطلاعات کاربر از پایگاه داده"""
        query = "SELECT * FROM users WHERE user_id = ?"
        result = self.db_manager.execute_query(query, (self.user_id,))
        
        if result:
            row = result[0]
            self.username = row[1]
            self.display_name = row[2]
            self.role = row[3]
            self.balance = row[4]
            self.experience_points = row[5]
            self.join_date = row[6]
            self.last_active = row[7]
            self.is_active = bool(row[8])
            self.skills = json.loads(row[9]) if row[9] else {}
            self.achievements = json.loads(row[10]) if row[10] else []
            self.properties = json.loads(row[11]) if row[11] else []
            self.job = row[12]
            self.education = row[13]
            self.political_party = row[14]
            self.military_rank = row[15]
            self.intelligence_level = row[16]
            self.criminal_record = json.loads(row[17]) if row[17] else []
            self.diplomatic_relations = json.loads(row[18]) if row[18] else {}
        else:
            # ایجاد کاربر جدید
            self.create_new_user()
    
    def create_new_user(self):
        """ایجاد کاربر جدید"""
        query = """
            INSERT INTO users (user_id, username, display_name, role, balance, experience_points, join_date, last_active, is_active, skills, achievements, properties)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            self.user_id,
            self.username or "Unknown",
            self.display_name or "Unknown",
            "توریست",
            1000,
            0,
            datetime.datetime.now().isoformat(),
            datetime.datetime.now().isoformat(),
            1,
            "{}",
            "[]",
            "[]"
        )
        
        if self.db_manager.execute_update(query, params):
            self.role = "توریست"
            self.balance = 1000
            self.experience_points = 0
            self.skills = {}
            self.achievements = []
            self.properties = []
    
    def update_user_data(self):
        """به‌روزرسانی اطلاعات کاربر در پایگاه داده"""
        query = """
            UPDATE users SET 
                username = ?, display_name = ?, role = ?, balance = ?, experience_points = ?, 
                last_active = ?, skills = ?, achievements = ?, properties = ?, job = ?, 
                education = ?, political_party = ?, military_rank = ?, intelligence_level = ?,
                criminal_record = ?, diplomatic_relations = ?, updated_at = ?
            WHERE user_id = ?
        """
        
        params = (
            self.username,
            self.display_name,
            self.role,
            self.balance,
            self.experience_points,
            datetime.datetime.now().isoformat(),
            json.dumps(self.skills),
            json.dumps(self.achievements),
            json.dumps(self.properties),
            self.job,
            self.education,
            self.political_party,
            self.military_rank,
            self.intelligence_level,
            json.dumps(self.criminal_record),
            json.dumps(self.diplomatic_relations),
            datetime.datetime.now().isoformat(),
            self.user_id
        )
        
        return self.db_manager.execute_update(query, params)
    
    def add_experience(self, amount: int):
        """افزودن تجربه به کاربر"""
        self.experience_points += amount
        self.update_user_data()
    
    def add_balance(self, amount: int):
        """افزودن موجودی به کاربر"""
        self.balance += amount
        self.update_user_data()
    
    def remove_balance(self, amount: int) -> bool:
        """کاهش موجودی کاربر"""
        if self.balance >= amount:
            self.balance -= amount
            self.update_user_data()
            return True
        return False
    
    def change_role(self, new_role: str):
        """تغییر رول کاربر"""
        self.role = new_role
        self.update_user_data()
    
    def add_achievement(self, achievement_id: str):
        """افزودن دستاورد به کاربر"""
        if achievement_id not in self.achievements:
            self.achievements.append(achievement_id)
            self.update_user_data()
    
    def add_skill(self, skill_name: str, level: int = 1):
        """افزودن یا ارتقای مهارت"""
        self.skills[skill_name] = level
        self.update_user_data()
    
    def get_skill_level(self, skill_name: str) -> int:
        """دریافت سطح مهارت"""
        return self.skills.get(skill_name, 0)

class Government:
    """کلاس دولت"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.load_government_data()
    
    def load_government_data(self):
        """بارگذاری اطلاعات دولت از پایگاه داده"""
        query = "SELECT * FROM government ORDER BY id DESC LIMIT 1"
        result = self.db_manager.execute_query(query)
        
        if result:
            row = result[0]
            self.id = row[0]
            self.government_type = row[1]
            self.prime_minister_id = row[2]
            self.knesset_members = json.loads(row[3]) if row[3] else []
            self.cabinet_members = json.loads(row[4]) if row[4] else {}
            self.laws = json.loads(row[5]) if row[5] else []
            self.elections = json.loads(row[6]) if row[6] else []
            self.public_approval = row[7]
            self.budget = row[8]
            self.tax_rate = row[9]
        else:
            # ایجاد دولت جدید
            self.create_new_government()
    
    def create_new_government(self):
        """ایجاد دولت جدید"""
        query = """
            INSERT INTO government (government_type, prime_minister_id, knesset_members, cabinet_members, laws, elections, public_approval, budget, tax_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            "دموکراسی پارلمانی",
            None,
            "[]",
            "{}",
            "[]",
            "[]",
            75,
            1000000,
            0.15
        )
        
        if self.db_manager.execute_update(query, params):
            self.government_type = "دموکراسی پارلمانی"
            self.prime_minister_id = None
            self.knesset_members = []
            self.cabinet_members = {}
            self.laws = []
            self.elections = []
            self.public_approval = 75
            self.budget = 1000000
            self.tax_rate = 0.15
    
    def update_government_data(self):
        """به‌روزرسانی اطلاعات دولت در پایگاه داده"""
        query = """
            UPDATE government SET 
                government_type = ?, prime_minister_id = ?, knesset_members = ?, 
                cabinet_members = ?, laws = ?, elections = ?, public_approval = ?, 
                budget = ?, tax_rate = ?, updated_at = ?
            WHERE id = ?
        """
        
        params = (
            self.government_type,
            self.prime_minister_id,
            json.dumps(self.knesset_members),
            json.dumps(self.cabinet_members),
            json.dumps(self.laws),
            json.dumps(self.elections),
            self.public_approval,
            self.budget,
            self.tax_rate,
            datetime.datetime.now().isoformat(),
            self.id
        )
        
        return self.db_manager.execute_update(query, params)
    
    def set_prime_minister(self, user_id: str):
        """تنظیم نخست‌وزیر"""
        self.prime_minister_id = user_id
        self.update_government_data()
    
    def add_knesset_member(self, user_id: str):
        """افزودن عضو کنست"""
        if user_id not in self.knesset_members:
            self.knesset_members.append(user_id)
            self.update_government_data()
    
    def remove_knesset_member(self, user_id: str):
        """حذف عضو کنست"""
        if user_id in self.knesset_members:
            self.knesset_members.remove(user_id)
            self.update_government_data()
    
    def add_cabinet_member(self, position: str, user_id: str):
        """افزودن وزیر کابینه"""
        self.cabinet_members[position] = user_id
        self.update_government_data()
    
    def remove_cabinet_member(self, position: str):
        """حذف وزیر کابینه"""
        if position in self.cabinet_members:
            del self.cabinet_members[position]
            self.update_government_data()
    
    def add_law(self, law_id: str):
        """افزودن قانون"""
        if law_id not in self.laws:
            self.laws.append(law_id)
            self.update_government_data()
    
    def add_election(self, election_id: str):
        """افزودن انتخابات"""
        if election_id not in self.elections:
            self.elections.append(election_id)
            self.update_government_data()
    
    def change_public_approval(self, change: int):
        """تغییر رضایت عمومی"""
        self.public_approval = max(0, min(100, self.public_approval + change))
        self.update_government_data()
    
    def change_budget(self, change: int):
        """تغییر بودجه"""
        self.budget += change
        self.update_government_data()
    
    def change_tax_rate(self, new_rate: float):
        """تغییر نرخ مالیات"""
        self.tax_rate = max(0.0, min(1.0, new_rate))
        self.update_government_data()

class Military:
    """کلاس ارتش"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.load_military_data()
    
    def load_military_data(self):
        """بارگذاری اطلاعات ارتش از پایگاه داده"""
        query = "SELECT * FROM military ORDER BY id DESC LIMIT 1"
        result = self.db_manager.execute_query(query)
        
        if result:
            row = result[0]
            self.id = row[0]
            self.defcon_level = row[1]
            self.total_forces = row[2]
            self.air_force = row[3]
            self.ground_forces = row[4]
            self.navy = row[5]
            self.intelligence_units = row[6]
            self.equipment = json.loads(row[7]) if row[7] else {}
            self.missions = json.loads(row[8]) if row[8] else []
            self.war_history = json.loads(row[9]) if row[9] else []
            self.alliances = json.loads(row[10]) if row[10] else []
            self.enemies = json.loads(row[11]) if row[11] else []
        else:
            # ایجاد ارتش جدید
            self.create_new_military()
    
    def create_new_military(self):
        """ایجاد ارتش جدید"""
        query = """
            INSERT INTO military (defcon_level, total_forces, air_force, ground_forces, navy, intelligence_units, equipment, missions, war_history, alliances, enemies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            5,
            1000,
            200,
            500,
            200,
            100,
            "{}",
            "[]",
            "[]",
            "[]",
            "[]"
        )
        
        if self.db_manager.execute_update(query, params):
            self.defcon_level = 5
            self.total_forces = 1000
            self.air_force = 200
            self.ground_forces = 500
            self.navy = 200
            self.intelligence_units = 100
            self.equipment = {}
            self.missions = []
            self.war_history = []
            self.alliances = []
            self.enemies = []
    
    def update_military_data(self):
        """به‌روزرسانی اطلاعات ارتش در پایگاه داده"""
        query = """
            UPDATE military SET 
                defcon_level = ?, total_forces = ?, air_force = ?, ground_forces = ?, 
                navy = ?, intelligence_units = ?, equipment = ?, missions = ?, 
                war_history = ?, alliances = ?, enemies = ?, updated_at = ?
            WHERE id = ?
        """
        
        params = (
            self.defcon_level,
            self.total_forces,
            self.air_force,
            self.ground_forces,
            self.navy,
            self.intelligence_units,
            json.dumps(self.equipment),
            json.dumps(self.missions),
            json.dumps(self.war_history),
            json.dumps(self.alliances),
            json.dumps(self.enemies),
            datetime.datetime.now().isoformat(),
            self.id
        )
        
        return self.db_manager.execute_update(query, params)
    
    def change_defcon_level(self, new_level: int):
        """تغییر سطح DEFCON"""
        if 1 <= new_level <= 5:
            self.defcon_level = new_level
            self.update_military_data()
    
    def add_forces(self, force_type: str, amount: int):
        """افزودن نیرو"""
        if force_type == "air_force":
            self.air_force += amount
        elif force_type == "ground_forces":
            self.ground_forces += amount
        elif force_type == "navy":
            self.navy += amount
        elif force_type == "intelligence_units":
            self.intelligence_units += amount
        
        self.total_forces = self.air_force + self.ground_forces + self.navy + self.intelligence_units
        self.update_military_data()
    
    def remove_forces(self, force_type: str, amount: int):
        """کاهش نیرو"""
        if force_type == "air_force":
            self.air_force = max(0, self.air_force - amount)
        elif force_type == "ground_forces":
            self.ground_forces = max(0, self.ground_forces - amount)
        elif force_type == "navy":
            self.navy = max(0, self.navy - amount)
        elif force_type == "intelligence_units":
            self.intelligence_units = max(0, self.intelligence_units - amount)
        
        self.total_forces = self.air_force + self.ground_forces + self.navy + self.intelligence_units
        self.update_military_data()
    
    def add_equipment(self, equipment_type: str, amount: int):
        """افزودن تجهیزات"""
        if equipment_type in self.equipment:
            self.equipment[equipment_type] += amount
        else:
            self.equipment[equipment_type] = amount
        self.update_military_data()
    
    def remove_equipment(self, equipment_type: str, amount: int):
        """کاهش تجهیزات"""
        if equipment_type in self.equipment:
            self.equipment[equipment_type] = max(0, self.equipment[equipment_type] - amount)
            if self.equipment[equipment_type] == 0:
                del self.equipment[equipment_type]
        self.update_military_data()
    
    def add_mission(self, mission_id: str):
        """افزودن مأموریت"""
        if mission_id not in self.missions:
            self.missions.append(mission_id)
            self.update_military_data()
    
    def remove_mission(self, mission_id: str):
        """حذف مأموریت"""
        if mission_id in self.missions:
            self.missions.remove(mission_id)
            self.update_military_data()
    
    def add_war_record(self, war_data: dict):
        """افزودن رکورد جنگ"""
        self.war_history.append(war_data)
        self.update_military_data()
    
    def add_alliance(self, alliance_data: dict):
        """افزودن اتحاد"""
        self.alliances.append(alliance_data)
        self.update_military_data()
    
    def remove_alliance(self, alliance_id: str):
        """حذف اتحاد"""
        self.alliances = [a for a in self.alliances if a.get('id') != alliance_id]
        self.update_military_data()
    
    def add_enemy(self, enemy_data: dict):
        """افزودن دشمن"""
        self.enemies.append(enemy_data)
        self.update_military_data()
    
    def remove_enemy(self, enemy_id: str):
        """حذف دشمن"""
        self.enemies = [e for e in self.enemies if e.get('id') != enemy_id]
        self.update_military_data()

class Economy:
    """کلاس اقتصاد"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.load_economy_data()
    
    def load_economy_data(self):
        """بارگذاری اطلاعات اقتصاد از پایگاه داده"""
        query = "SELECT * FROM economy ORDER BY id DESC LIMIT 1"
        result = self.db_manager.execute_query(query)
        
        if result:
            row = result[0]
            self.id = row[0]
            self.national_currency = row[1]
            self.exchange_rate = row[2]
            self.inflation_rate = row[3]
            self.gdp = row[4]
            self.national_debt = row[5]
            self.resources = json.loads(row[6]) if row[6] else {}
            self.companies = json.loads(row[7]) if row[7] else []
            self.stock_market = json.loads(row[8]) if row[8] else {}
            self.trade_relations = json.loads(row[9]) if row[9] else {}
        else:
            # ایجاد اقتصاد جدید
            self.create_new_economy()
    
    def create_new_economy(self):
        """ایجاد اقتصاد جدید"""
        query = """
            INSERT INTO economy (national_currency, exchange_rate, inflation_rate, gdp, national_debt, resources, companies, stock_market, trade_relations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            "شِکِل",
            1.0,
            0.02,
            10000000,
            0,
            "{}",
            "[]",
            "{}",
            "{}"
        )
        
        if self.db_manager.execute_update(query, params):
            self.national_currency = "شِکِل"
            self.exchange_rate = 1.0
            self.inflation_rate = 0.02
            self.gdp = 10000000
            self.national_debt = 0
            self.resources = {}
            self.companies = []
            self.stock_market = {}
            self.trade_relations = {}
    
    def update_economy_data(self):
        """به‌روزرسانی اطلاعات اقتصاد در پایگاه داده"""
        query = """
            UPDATE economy SET 
                national_currency = ?, exchange_rate = ?, inflation_rate = ?, gdp = ?, 
                national_debt = ?, resources = ?, companies = ?, stock_market = ?, 
                trade_relations = ?, updated_at = ?
            WHERE id = ?
        """
        
        params = (
            self.national_currency,
            self.exchange_rate,
            self.inflation_rate,
            self.gdp,
            self.national_debt,
            json.dumps(self.resources),
            json.dumps(self.companies),
            json.dumps(self.stock_market),
            json.dumps(self.trade_relations),
            datetime.datetime.now().isoformat(),
            self.id
        )
        
        return self.db_manager.execute_update(query, params)
    
    def change_gdp(self, change: int):
        """تغییر تولید ناخالص داخلی"""
        self.gdp += change
        self.update_economy_data()
    
    def change_national_debt(self, change: int):
        """تغییر بدهی ملی"""
        self.national_debt += change
        self.update_economy_data()
    
    def change_inflation_rate(self, new_rate: float):
        """تغییر نرخ تورم"""
        self.inflation_rate = max(0.0, new_rate)
        self.update_economy_data()
    
    def add_resource(self, resource_type: str, amount: int):
        """افزودن منابع"""
        if resource_type in self.resources:
            self.resources[resource_type] += amount
        else:
            self.resources[resource_type] = amount
        self.update_economy_data()
    
    def remove_resource(self, resource_type: str, amount: int):
        """کاهش منابع"""
        if resource_type in self.resources:
            self.resources[resource_type] = max(0, self.resources[resource_type] - amount)
            if self.resources[resource_type] == 0:
                del self.resources[resource_type]
        self.update_economy_data()
    
    def add_company(self, company_id: str):
        """افزودن شرکت"""
        if company_id not in self.companies:
            self.companies.append(company_id)
            self.update_economy_data()
    
    def remove_company(self, company_id: str):
        """حذف شرکت"""
        if company_id in self.companies:
            self.companies.remove(company_id)
            self.update_economy_data()
    
    def update_stock_market(self, company_id: str, stock_data: dict):
        """به‌روزرسانی بازار بورس"""
        self.stock_market[company_id] = stock_data
        self.update_economy_data()
    
    def add_trade_relation(self, country_id: str, trade_data: dict):
        """افزودن روابط تجاری"""
        self.trade_relations[country_id] = trade_data
        self.update_economy_data()
    
    def remove_trade_relation(self, country_id: str):
        """حذف روابط تجاری"""
        if country_id in self.trade_relations:
            del self.trade_relations[country_id]
            self.update_economy_data()

# Global database manager instance
db_manager = DatabaseManager()

# Export classes
__all__ = ['DatabaseManager', 'User', 'Government', 'Military', 'Economy', 'db_manager']