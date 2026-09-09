"""Classes de entidades do sistema"""
from dataclasses import dataclass, field
from typing import Optional
import uuid


@dataclass
class Transacao:
    tipo: str
    data: str
    conta: str
    categoria: str
    valor: float
    descricao: str
    parcelado: bool = False
    parcela_atual: int = 1
    total_parcelas: int = 1
    agendado: bool = False
    conta_destino: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Meta:
    nome: str
    emoji: str
    valor_atual: float
    valor_alvo: float
    categoria: str
    prioritaria: bool = False
    ordem: int = 0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class Acao:
    ticker: str
    quantidade: int
    preco_medio: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self):
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, d):
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
