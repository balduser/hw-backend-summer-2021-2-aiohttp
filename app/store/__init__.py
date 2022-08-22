import typing

from app.store.bot.manager import BotManager
from app.store.database.database import Database
from app.store.vk_api.accessor import VkApiAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


class Store:
    def __init__(self, app: "Application"):
        from app.store.quiz.accessor import QuizAccessor
        from app.store.admin.accessor import AdminAccessor

        self.admins = AdminAccessor(app)
        self.quizzes = QuizAccessor(app)
        self.vk_api = VkApiAccessor(app)
        self.bots_manager = BotManager(app)


def setup_store(app: "Application"):
    app.database = Database()
    app.store = Store(app)
