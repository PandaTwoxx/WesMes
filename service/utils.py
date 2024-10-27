"""Utility Functions"""

from service.routes import login_manager, r



# Login-Manager init
login_manager.login_view = "login_page"
login_manager.login_message = "Hey there, Please login to access this page."
login_manager.login_message_category = "error"
login_manager.refresh_view = "login_page"
login_manager.needs_refresh_message = (
    "To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"
login_manager.session_protection = "strong"

@login_manager.user_loader
def user_loader(user_id):
    """Returns user object

    Args:
        user_id (str): The id of the user

    Returns:
        User: The loaded user object
    """
    return r.hget('users', user_id)
