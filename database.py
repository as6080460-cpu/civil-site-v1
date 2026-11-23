import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "construction_site.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. 協力廠商表 (vendors)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vendors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            contact_person TEXT NOT NULL,
            phone TEXT NOT NULL,
            tax_id TEXT NOT NULL,
            rating INTEGER DEFAULT 5,
            notes TEXT
        );
    """)

    # 2. 材料進出貨紀錄表 (materials_log) - 關聯 vendors.id
    cur.execute("""
        CREATE TABLE IF NOT EXISTS materials_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT NOT NULL,
            material_name TEXT NOT NULL,
            spec TEXT,
            unit TEXT NOT NULL,
            log_type TEXT NOT NULL CHECK(log_type IN ('進貨', '領料')),
            quantity REAL NOT NULL,
            unit_price REAL DEFAULT 0,
            vendor_id INTEGER,
            payment_status TEXT DEFAULT '未請款' CHECK(payment_status IN ('已請款', '對帳中', '未請款', '不適用')),
            safety_stock REAL DEFAULT 50,
            notes TEXT,
            FOREIGN KEY (vendor_id) REFERENCES vendors(id) ON DELETE SET NULL
        );
    """)

    # 3. 日常行政零用金表 (petty_cash)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS petty_cash (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_date TEXT NOT NULL,
            category TEXT NOT NULL,
            item_name TEXT NOT NULL,
            amount REAL NOT NULL,
            handler TEXT NOT NULL,
            receipt_no TEXT,
            notes TEXT
        );
    """)

    # 4. 小型機具租借登記表 (equipment_rentals)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS equipment_rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_name TEXT NOT NULL,
            serial_no TEXT,
            borrower TEXT NOT NULL,
            borrow_date TEXT NOT NULL,
            expected_return TEXT,
            actual_return TEXT,
            status TEXT NOT NULL DEFAULT '借出中' CHECK(status IN ('借出中', '已歸還', '維修中')),
            notes TEXT
        );
    """)

    # 檢查是否已有資料，若無則寫入初始測試資料
    cur.execute("SELECT COUNT(*) FROM vendors")
    if cur.fetchone()[0] == 0:
        seed_vendors = [
            ("台泥預拌混凝土高雄廠", "預拌/泥作", "林志明", "07-801-2345", "11913502", 5, "供料穩定，配合度高"),
            ("東和鋼鐵企業股份有限公司", "鋼構/鋼筋", "陳建宏", "07-871-6688", "75280209", 5, "SD420W 檢驗報告齊全"),
            ("南星砂石建材行", "砂石/骨材", "張國榮", "07-615-3321", "84521093", 4, "雨季偶爾延遲半天"),
            ("永盛模板工程行", "模板工程", "吳俊傑", "07-382-9910", "53219847", 4, "清水模板品質優良"),
            ("大統水電工程有限公司", "水電工程", "李文豪", "07-551-7742", "28941033", 5, "臨時用電維護迅速")
        ]
        cur.executemany("""
            INSERT INTO vendors (name, category, contact_person, phone, tax_id, rating, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, seed_vendors)

        seed_materials = [
            ("2026-11-18", "卜特蘭水泥", "Type I 50kg/包", "包", "進貨", 200, 185, 1, "已請款", 80, "A區基礎灌漿備料"),
            ("2026-11-19", "卜特蘭水泥", "Type I 50kg/包", "包", "領料", 145, 0, None, "不適用", 80, "A區打底工程領用"),
            ("2026-11-19", "竹節鋼筋 #4", "SD420W 12m", "噸", "進貨", 25, 21500, 2, "對帳中", 10, "柱筋綁紮用"),
            ("2026-11-20", "竹節鋼筋 #4", "SD420W 12m", "噸", "領料", 18, 0, None, "不適用", 10, "1F 柱筋施工領用"),
            ("2026-11-20", "天然河砂", "細骨材", "立方米", "進貨", 60, 1150, 3, "未請款", 20, "粉刷打底用"),
            ("2026-11-21", "天然河砂", "細骨材", "立方米", "領料", 25, 0, None, "不適用", 20, "B棟牆面粉刷"),
            ("2026-11-21", "六分清水模板", "3x6尺", "片", "進貨", 120, 420, 4, "未請款", 50, "2F 樓板組模用"),
            ("2026-11-22", "六分清水模板", "3x6尺", "片", "領料", 90, 0, None, "不適用", 50, "2F 梁柱組模領用")
        ]
        cur.executemany("""
            INSERT INTO materials_log
            (log_date, material_name, spec, unit, log_type, quantity, unit_price, vendor_id, payment_status, safety_stock, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_materials)

        seed_petty = [
            ("2026-11-20", "餐費/便當", "工班加班便當 (15份)", 1650, "王主任", "INV-26112001", "灌漿作業延時"),
            ("2026-11-21", "五金耗材", "鐵線、粉筆、墨斗線一批", 840, "曾品管", "INV-26112104", "放樣與綁紮用"),
            ("2026-11-22", "飲料/飲水", "箱裝礦泉水 6 箱", 720, "陳工務", "INV-26112202", "工地現場補給")
        ]
        cur.executemany("""
            INSERT INTO petty_cash (expense_date, category, item_name, amount, handler, receipt_no, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, seed_petty)

        seed_equip = [
            ("手推式夯實機", "EQ-COMP-01", "林師傅 (泥作班)", "2026-11-20", "2026-11-24", "", "借出中", "回填土夯實作業"),
            ("5kW 移動式發電機", "EQ-GEN-03", "李文豪 (水電班)", "2026-11-19", "2026-11-21", "2026-11-21", "已歸還", "已確認油箱歸還正常"),
            ("雷射水平儀", "EQ-LASER-02", "測量組", "2026-11-22", "2026-11-23", "", "借出中", "2F 高程放樣校驗")
        ]
        cur.executemany("""
            INSERT INTO equipment_rentals
            (equipment_name, serial_no, borrower, borrow_date, expected_return, actual_return, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_equip)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print(f"資料庫初始化完成：{DB_PATH}")
