import csv
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "lost_found.db"

class Database:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL CHECK(item_type IN ('Lost','Found')),
            item_name TEXT NOT NULL,
            description TEXT DEFAULT '',
            location TEXT NOT NULL,
            date TEXT NOT NULL,
            contact TEXT NOT NULL,
            image TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active',
            created_at TEXT NOT NULL
        )""")
        # Upgrade databases created by the earlier version.
        cols = {r["name"] for r in self.conn.execute("PRAGMA table_info(items)")}
        upgrades = [
            ("description", "TEXT DEFAULT ''"),
            ("status", "TEXT NOT NULL DEFAULT 'Active'"),
            ("created_at", "TEXT DEFAULT ''"),
        ]
        for name, definition in upgrades:
            if name not in cols:
                self.conn.execute(f"ALTER TABLE items ADD COLUMN {name} {definition}")
        self.conn.execute(
            "UPDATE items SET created_at=? WHERE created_at IS NULL OR created_at=''",
            (datetime.now().isoformat(timespec="seconds"),)
        )
        self.conn.commit()

    def add_item(self, item_type, item_name, description, location, date, contact, image):
        cur = self.conn.execute("""
            INSERT INTO items
            (item_type,item_name,description,location,date,contact,image,status,created_at)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (item_type, item_name, description, location, date, contact, image,
              "Active", datetime.now().isoformat(timespec="seconds")))
        self.conn.commit()
        return cur.lastrowid

    def get_item(self, item_id):
        return self.conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()

    def get_all(self, item_type=None, status=None, search=None):
        sql = "SELECT * FROM items WHERE 1=1"
        args = []
        if item_type:
            sql += " AND item_type=?"; args.append(item_type)
        if status:
            sql += " AND status=?"; args.append(status)
        if search:
            sql += """ AND (item_name LIKE ? OR location LIKE ? OR description LIKE ? OR contact LIKE ?)"""
            q=f"%{search}%"; args += [q,q,q,q]
        sql += " ORDER BY id DESC"
        return self.conn.execute(sql, args).fetchall()

    def update_status(self, item_id, status):
        self.conn.execute("UPDATE items SET status=? WHERE id=?", (status, item_id))
        self.conn.commit()

    def delete_item(self, item_id):
        self.conn.execute("DELETE FROM items WHERE id=?", (item_id,))
        self.conn.commit()

    def stats(self):
        q=lambda sql: self.conn.execute(sql).fetchone()[0]
        return {
            "total": q("SELECT COUNT(*) FROM items"),
            "lost": q("SELECT COUNT(*) FROM items WHERE item_type='Lost'"),
            "found": q("SELECT COUNT(*) FROM items WHERE item_type='Found'"),
            "active": q("SELECT COUNT(*) FROM items WHERE status='Active'"),
            "resolved": q("SELECT COUNT(*) FROM items WHERE status='Resolved'"),
        }

    def export_csv(self, path):
        rows = self.get_all()
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["ID","Type","Item Name","Description","Location","Date","Contact","Image","Status","Created At"])
            for r in rows:
                writer.writerow([r["id"],r["item_type"],r["item_name"],r["description"],
                                 r["location"],r["date"],r["contact"],r["image"],
                                 r["status"],r["created_at"]])

    def close(self):
        self.conn.close()
