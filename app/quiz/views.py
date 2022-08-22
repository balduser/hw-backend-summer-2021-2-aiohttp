from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound
from aiohttp_apispec import request_schema, response_schema, docs, querystring_schema

from app.base.auth import login_required
from app.base.exceptions import RepeatedUniqueValueError, ContentDoesntMatchRulesError, MissingRelationError
from app.quiz.models import Answer
from app.quiz.schemes import (
    ThemeSchema, ThemeListSchema, QuestionSchema, ThemeIdSchema, ListQuestionSchema,
)
from app.web.app import View
from app.web.utils import json_response


class ThemeAddView(View):
    @login_required
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema, 200)
    @docs(tags=['quiz'], summary='Adding a new theme')
    async def post(self):
        title = self.data["title"]
        try:
            theme = await self.store.quizzes.create_theme(title=title)
            return json_response(data=ThemeSchema().dump(theme))
        except RepeatedUniqueValueError:
            raise HTTPConflict


class ThemeListView(View):
    @login_required
    @response_schema(ThemeListSchema, 200)
    @docs(tags=['quiz'], summary='Getting a list of themes')
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data={"themes": [ThemeSchema().dump(theme) for theme in themes]})  # ThemeListSchema().dump(themes))


class QuestionAddView(View):
    @login_required
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    @docs(tags=['quiz'], summary='Adding a new question')
    async def post(self):
        title = self.data["title"]
        theme_id = self.data["theme_id"]
        answers = [Answer.from_dict(answer) for answer in self.data["answers"]]
        try:
            question = await self.store.quizzes.create_question(title=title, theme_id=theme_id, answers=answers)
            return json_response(data=QuestionSchema().dump(question))
        except RepeatedUniqueValueError:
            raise HTTPConflict
        except ContentDoesntMatchRulesError:
            raise HTTPBadRequest
        except MissingRelationError:
            raise HTTPNotFound


class QuestionListView(View):
    @login_required
    @querystring_schema(ThemeIdSchema)
    @response_schema(ListQuestionSchema, 200)
    @docs(tags=['quiz'], summary='Getting a list of questions')
    async def get(self):
        theme_id = int(self.request.query.get('theme_id')) if self.request.query.get('theme_id') else None
        try:
            questions = await self.store.quizzes.list_questions(theme_id)
            return json_response(data={"questions": [QuestionSchema().dump(question) for question in questions]})
        except MissingRelationError:
            raise HTTPNotFound
