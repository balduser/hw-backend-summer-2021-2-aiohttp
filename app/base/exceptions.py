class AppException(Exception):
    pass


class RepeatedUniqueValueError(AppException):
    pass


class ContentDoesntMatchRulesError(AppException):
    pass


class MissingRelationError(AppException):
    pass
