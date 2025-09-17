from typing import List
from datetime import date
from .models import Transacao, TipoTransacao
from .db import Database


class TransacaoRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    # CRUD básico
    def adicionar(self, t: Transacao) -> int:
        sql = (
            "INSERT INTO transacoes(tipo, categoria, descricao, valor, data)\n"
            "VALUES (?,?,?,?,?)"
        )
        return self.db.execute(
            sql,
            (t.tipo.value, t.categoria, t.descricao, t.valor, t.data.isoformat()),
        )

    def listar(self) -> List[Transacao]:
        rows = self.db.query(
            "SELECT * FROM transacoes ORDER BY date(data) DESC, id DESC"
        )
        return [self._row_to_model(r) for r in rows]

    def remover(self, transacao_id: int) -> None:
        self.db.execute("DELETE FROM transacoes WHERE id=?", (transacao_id,))

    def por_intervalo(self, inicio: date, fim: date) -> List[Transacao]:
        rows = self.db.query(
            "SELECT * FROM transacoes WHERE date(data) BETWEEN date(?) AND date(?) ORDER BY date(data)",
            (inicio.isoformat(), fim.isoformat()),
        )
        return [self._row_to_model(r) for r in rows]

    def soma_por_categoria(self, tipo: TipoTransacao):
        sql = (
            "SELECT categoria, SUM(valor) as total FROM transacoes "
            "WHERE tipo=? GROUP BY categoria ORDER BY total DESC"
        )
        return self.db.query(sql, (tipo.value,))

    def saldo_mensal(self):
        sql = (
            "SELECT strftime('%Y-%m', data) AS mes, "
            "SUM(CASE WHEN tipo='RECEITA' THEN valor ELSE 0 END) AS receitas, "
            "SUM(CASE WHEN tipo='DESPESA' THEN valor ELSE 0 END) AS despesas, "
            "SUM(CASE WHEN tipo='RECEITA' THEN valor ELSE -valor END) AS saldo "
            "FROM transacoes GROUP BY mes ORDER BY mes"
        )
        return self.db.query(sql)

    @staticmethod
    def _row_to_model(r: dict) -> Transacao:
        return Transacao(
            id=r["id"],
            tipo=TipoTransacao(r["tipo"]),
            categoria=r["categoria"],
            descricao=r["descricao"],
            valor=float(r["valor"]),
            data=date.fromisoformat(r["data"]),
        )
