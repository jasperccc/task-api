class AppError(Exception):
    """应用业务异常基类。"""

    status_code = 500

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    """资源不存在。"""

    status_code = 404
