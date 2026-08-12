from fastapi import Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

class CommentFetchingError(Exception):
    """Exception class for errors on fetching comments from PRAW"""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


def comment_error_handler(request: Request, exception: CommentFetchingError):

    context = {
        "message": exception.message
    }

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context=context
    )
