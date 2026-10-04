"""Modelos de dados para reprodução musical."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LoopMode(str, Enum):
    """Modos de repetição de áudio."""

    OFF = "off"
    TRACK = "track"
    QUEUE = "queue"

    @classmethod
    def from_str(cls, value: str) -> LoopMode:
        """Converte string para enum correspondente com fallback seguro."""
        normalized = value.strip().lower()
        for mode in cls:
            if mode.value == normalized:
                return mode
        return cls.OFF


@dataclass
class Track:
    """Representa uma faixa de áudio pronta para reprodução."""

    title: str
    source_url: str
    webpage_url: str
    duration: int
    requester: str
    thumbnail: Optional[str] = None

    @property
    def formatted_duration(self) -> str:
        """Retorna a duração em formato HH:MM:SS ou MM:SS."""
        if self.duration <= 0:
            return "Ao vivo / Desconhecido"
        minutes, seconds = divmod(self.duration, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"
