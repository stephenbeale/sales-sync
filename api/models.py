import sqlite3
from datetime import datetime, timezone

from config import DATABASE_PATH


def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ebay_listing_id TEXT,
            vinted_title TEXT,
            status TEXT NOT NULL DEFAULT 'active',
            sold_on TEXT,
            sold_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sync_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            source TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (item_id) REFERENCES items(id)
        );
    """)
    conn.commit()
    conn.close()


def add_item(title, ebay_listing_id=None, vinted_title=None):
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        """INSERT INTO items (title, ebay_listing_id, vinted_title, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?)""",
        (title, ebay_listing_id, vinted_title or title, now, now),
    )
    item_id = cursor.lastrowid
    conn.commit()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    return dict(item)


def get_items(status=None):
    conn = get_db()
    if status:
        rows = conn.execute(
            "SELECT * FROM items WHERE status = ? ORDER BY created_at DESC",
            (status,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM items ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_item(item_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_item(item_id, **kwargs):
    conn = get_db()
    kwargs["updated_at"] = datetime.now(timezone.utc).isoformat()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    values = list(kwargs.values()) + [item_id]
    conn.execute(f"UPDATE items SET {sets} WHERE id = ?", values)
    conn.commit()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    return dict(item) if item else None


def mark_sold(item_id, sold_on):
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    conn.execute(
        "UPDATE items SET status = 'sold', sold_on = ?, sold_at = ?, updated_at = ? WHERE id = ?",
        (sold_on, now, now, item_id),
    )
    conn.commit()
    item = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()
    return dict(item) if item else None


def delete_item(item_id):
    conn = get_db()
    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


def add_sync_log(item_id, action, source, details=None):
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """INSERT INTO sync_log (item_id, action, source, details, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (item_id, action, source, details, now),
    )
    conn.commit()
    conn.close()


def get_sync_logs(item_id=None, limit=50):
    conn = get_db()
    if item_id:
        rows = conn.execute(
            "SELECT * FROM sync_log WHERE item_id = ? ORDER BY created_at DESC LIMIT ?",
            (item_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM sync_log ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def find_item_by_vinted_title(title):
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM items WHERE status = 'active' AND vinted_title LIKE ?",
        (f"%{title}%",),
    ).fetchone()
    conn.close()
    return dict(row) if row else None
