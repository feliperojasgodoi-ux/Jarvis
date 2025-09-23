import sqlite3
from pathlib import Path
from typing import Iterable


SCHEMA = """
CREATE TABLE IF NOT EXISTS transacoes (
id INTEGER PRIMARY KEY AUTOINCREMENT,
tipo TEXT NOT NULL CHECK(tipo IN ('RECEITA','DESPESA')),
categoria TEXT NOT NULL,
descricao TEXT NOT NULL,
valor REAL NOT NULL,
data TEXT NOT NULL,
banco TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_transacoes_data ON transacoes(data);
"""


class Database:
    def __init__(self, db_path: str = "finance.db") -> None:
        self.path = Path(db_path)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        with sqlite3.connect(self.path) as con:
            con.executescript(SCHEMA)

    def execute(self, sql: str, params: Iterable = ()):  # write
        with sqlite3.connect(self.path) as con:
            cur = con.execute(sql, params)
            con.commit()
            return cur.lastrowid

    def query(self, sql: str, params: Iterable = ()):  # read
        with sqlite3.connect(self.path) as con:
            con.row_factory = sqlite3.Row
            cur = con.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]
