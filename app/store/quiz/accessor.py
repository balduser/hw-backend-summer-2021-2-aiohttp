from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.base.exceptions import RepeatedUniqueValueError, ContentDoesntMatchRulesError, MissingRelationError
from app.quiz.models import Theme, Question, Answer


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        if title in [theme.title for theme in self.app.database.themes]:
            raise RepeatedUniqueValueError
        theme = Theme(id=self.app.database.next_theme_id, title=str(title))
        self.app.database.themes.append(theme)
        return theme

    async def get_theme_by_title(self, title: str) -> Optional[Theme]:
        for theme in self.app.database.themes:
            if theme.title == title:
                return theme

    async def get_theme_by_id(self, id_: int) -> Optional[Theme]:
        for theme in self.app.database.themes:
            if theme.id == id_:
                return theme

    async def list_themes(self) -> list[Theme]:
        return self.app.database.themes

    async def get_question_by_title(self, title: str) -> Optional[Question]:
        for question in self.app.database.questions:
            if question.title == title:
                return question

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        self.check_question(title, theme_id, answers)
        question = Question(
            id=self.app.database.next_question_id,
            title=title,
            theme_id=theme_id,
            answers=answers,
        )
        self.app.database.questions.append(question)
        return question

    async def list_questions(self, theme_id: Optional[int] = None) -> list[Question]:
        if theme_id:
            if theme_id not in [theme.id for theme in self.app.database.themes]:
                raise MissingRelationError
            return [question for question in self.app.database.questions if question.theme_id == theme_id]
        return self.app.database.questions

    def check_question(self, title: str, theme_id: int, answers: list[Answer]) -> None:
        """При нескольких ответах, у которых is_correct равно True надо выдавать ошибку 400\n
        если ни один ответ не отмечен is_correct: true, то отдавать 400\n
        если у вопроса только один ответ, то отдавать 400\n
        если вопрос с таким title уже есть в базе, то отдавать ошибку 409\n
        если темы с таким id нет, то отдавать 404
        """
        correct_answers = [answer.is_correct for answer in answers]
        if sum(correct_answers) != 1:
            raise ContentDoesntMatchRulesError  # 400
        if len(answers) < 2:
            raise ContentDoesntMatchRulesError  # 400
        if title in [question.title for question in self.app.database.questions]:
            raise RepeatedUniqueValueError  # 409
        if theme_id not in [theme.id for theme in self.app.database.themes]:
            raise MissingRelationError  # 404
