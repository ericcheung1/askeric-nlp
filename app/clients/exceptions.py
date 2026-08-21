from fastapi import Request, status
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")

class CommentFetchingError(Exception):
    """Exception class for errors on fetching comments from PRAW"""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

        super().__init__(message)


def comment_error_handler(request: Request, exception: CommentFetchingError):
    """Handles CommentFetchingError by returning error HTML template"""

    # NOTE: return 400 status to server output
    context = {
        "message": exception.message
    }

    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context=context,
        status_code=status.HTTP_400_BAD_REQUEST
    )
