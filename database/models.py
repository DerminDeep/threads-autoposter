import aiosqlite
from datetime import datetime
from typing import Optional, List
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / 'data' / 'posts.db'

async def initDb():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                topic TEXT,
                scheduledTime DATETIME,
                status TEXT DEFAULT 'pending',
                threadsPostId TEXT,
                imagePath TEXT,
                createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
                publishedAt DATETIME
            )
        ''')

        try:
            await db.execute('ALTER TABLE posts ADD COLUMN imagePath TEXT')
        except Exception:
            pass

        await db.execute('''
            CREATE TABLE IF NOT EXISTS topics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                createdAt DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        await db.commit()

async def addPost(content: str, topic: Optional[str] = None, scheduledTime: Optional[datetime] = None, imagePath: Optional[str] = None, initialStatus: str = 'pending') -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'INSERT INTO posts (content, topic, scheduledTime, status, imagePath) VALUES (?, ?, ?, ?, ?)',
            (content, topic, scheduledTime, initialStatus, imagePath)
        )
        await db.commit()
        return cursor.lastrowid

async def getPendingPosts(limit: int = 10) -> List[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        from datetime import datetime
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = await db.execute('''
            SELECT * FROM posts
            WHERE status = 'pending'
            AND (scheduledTime IS NULL OR scheduledTime <= ?)
            ORDER BY createdAt ASC
            LIMIT ?
        ''', (now, limit))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

async def claimPost(postId: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'UPDATE posts SET status = ? WHERE id = ? AND status = ?',
            ('publishing', postId, 'pending')
        )
        await db.commit()
        return cursor.rowcount > 0

async def updatePostStatus(postId: int, status: str, threadsPostId: Optional[str] = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if status == 'published' and threadsPostId:
            await db.execute(
                'UPDATE posts SET status = ?, threadsPostId = ?, publishedAt = datetime("now") WHERE id = ?',
                (status, threadsPostId, postId)
            )
        else:
            await db.execute(
                'UPDATE posts SET status = ? WHERE id = ?',
                (status, postId)
            )
        await db.commit()

async def addTopic(name: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            cursor = await db.execute(
                'INSERT INTO topics (name) VALUES (?)',
                (name,)
            )
            await db.commit()
            return cursor.lastrowid
        except aiosqlite.IntegrityError:
            cursor = await db.execute('SELECT id FROM topics WHERE name = ?', (name,))
            row = await cursor.fetchone()
            return row[0] if row else None

async def getTopics() -> List[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT name FROM topics ORDER BY name')
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

async def getStats() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) as published,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
            FROM posts
        ''')
        row = await cursor.fetchone()
        total = row[0]
        published = row[1] or 0
        pending = row[2] or 0
        failed = row[3] or 0

        cursor = await db.execute('''
            SELECT DATE(publishedAt) as date, COUNT(*) as count
            FROM posts
            WHERE status = 'published' AND publishedAt IS NOT NULL
            AND date >= date('now', '-7 days')
            GROUP BY DATE(publishedAt)
            ORDER BY date DESC
        ''')
        daily_rows = await cursor.fetchall()
        daily = {row[0]: row[1] for row in daily_rows}

        from datetime import datetime, timedelta
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

        today_count = daily.get(today, 0)
        yesterday_count = daily.get(yesterday, 0)

        weekly = []
        for i in range(6, -1, -1):
            d = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            weekly.append((d[-5:], daily.get(d, 0)))

        success_rate = round((published / total * 100), 1) if total > 0 else 0

        return {
            'total': total,
            'published': published,
            'pending': pending,
            'failed': failed,
            'today': today_count,
            'yesterday': yesterday_count,
            'weekly': weekly,
            'successRate': success_rate
        }

async def getSetting(key: str, default: str = None) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT value FROM settings WHERE key = ?', (key,))
        row = await cursor.fetchone()
        return row[0] if row else default

async def setSetting(key: str, value: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
            (key, value)
        )
        await db.commit()
