from dataclasses import dataclass
from hashlib import sha256
from typing import Optional


@dataclass
class Admin:
    id: int
    email: str
    password: Optional[str] = None

    def password_is_correct(self, password: str) -> bool:
        return bool(self.passhash(password) == self.password)

    @staticmethod
    def passhash(password: str) -> str:
        return sha256(password.encode()).hexdigest()

    @classmethod
    def from_dict(cls, dic: dict):
        return cls(id=dic['id'], email=dic['email'])
