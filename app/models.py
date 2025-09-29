from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import date


class TipoTransacao(str, Enum):
    RECEITA = "RECEITA"
    DESPESA = "DESPESA"

class Categorias:
    Categorias_PADRAO = [
    "Alimentação", "Transporte", "Saúde", "Moradia",
    "Lazer", "Restaurantes", "Compras/Vestuário", "Educação",
    "Presentes/Doações", "Pets", "Casa/Manutenção", "Tecnologia",
    "Imprevistos/Emergência", "Investimentos", "Dívidas/Parcelas",
    "Taxas/Impostos", "Receita"
    ]


@dataclass
class Transacao:
    id: Optional[int]
    tipo: TipoTransacao
    categoria: str
    descricao: str
    valor: float
    data: date
    banco: str

