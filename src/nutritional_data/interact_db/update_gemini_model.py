import sqlite3, datetime
from utils.utils import get_path_sqlite_db
from dto.gemini_model_data import GeminiModelDTO


def update_is_blocked_gemini_models(gemini_models: list) -> None:
    db_path = get_path_sqlite_db()

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        for gemini_model in gemini_models:
            is_blocked = 1
            if not gemini_model.get_is_blocked():
                is_blocked = 0
            cur.execute("""
                UPDATE gemini_models
                SET is_blocked = ?
                WHERE model_name = ?
            """, (is_blocked, gemini_model.get_model_name()))
        conn.commit()

    conn.close()

def update_last_petition_gemini_model(gemini_model: GeminiModelDTO) -> None:
    now = datetime.datetime.now()
    ts = int(now.timestamp())

    db_path = get_path_sqlite_db()

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE gemini_models
            SET last_petition = ?
            WHERE model_name = ?
        """, (ts, gemini_model.get_model_name()))
        conn.commit()

    conn.close()