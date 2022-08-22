import typing
from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.admin.models import Admin

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):

    def list_admins(self) -> list:
        return list(self.app.database.admins)

    async def connect(self, app: "Application"):
        await super().connect(app)
        await self.create_admin(email=self.app.config.admin.email, password=self.app.config.admin.password)
        print('AdminAccessor: ', self.app.database.admins)

    async def get_by_email(self, email: str) -> Optional[Admin]:
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin

    async def create_admin(self, email: str, password: str) -> None:
        if await self.get_by_email(email):
            # raise RepeatedUniqueValueError
            # Здесь я хотел запретить повторное создание админа с таким-же email,
            # но не стал, т.к. фикстуры тестов тоже инициализируют AdminAccessor
            pass
        else:
            self.app.database.admins.append(Admin(
                id=self.app.database.next_admin_id,
                email=email,
                password=Admin.passhash(password)
            ))
