from sqlalchemy.orm import Mapped
from app.database import Base, str_uniq, int_pk


class User(Base):
    id: Mapped[int_pk]
    first_name: Mapped[str]
    last_name: Mapped[str]
    phone_number: Mapped[str_uniq]
    password: Mapped[str]
    role: Mapped[str]

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"