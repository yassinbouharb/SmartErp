from __future__ import annotations

from enum import Enum


from pydantic import BaseModel
from typing import Optional

class Client(BaseModel):
    code: str
    nom: str
    contact: Optional[str] = ""
    telephone: Optional[str] = ""
    ville: Optional[str] = ""
    solde: float = 0.0
    matricule_fiscale: Optional[str] = ""