"""
TFM: Food environment on grocery online supermarket

Author: Francesc Ferré Tarrés
"""

from utils.utils import get_path_sqlite_db
from dto.gemini_model_data import GeminiModelDTO
import sqlite3, datetime


def update_is_blocked_gemini_models(gemini_models: list) -> None:
    """
    Update is blocked column of all gemini models passed as function parameter.

    Args:
        gemini_models (list: List of gemini models to be blocked.

    Returns:
        None.
    """

    db_path = get_path_sqlite_db()

    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        gemini_model: GeminiModelDTO
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
    """
    Updates last petition column of specific gemini model used in the execution.

    Args:
        gemini_model (GeminiModelDTO): Gemini model to be updated.

    Returns:
        None.
    """

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
