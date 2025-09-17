from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import date




class TipoTransacao(str, Enum):
    RECEITA = "RECEITA"
    DESPESA = "DESPESA"




@dataclass
class Transacao:
    id: Optional[int]
    tipo: TipoTransacao
    categoria: str
    descricao: str
    valor: float
    data: date