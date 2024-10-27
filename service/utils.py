"""Utility Functions"""

from service.routes import login_manager, r


@login_manager.user_loader
def user_loader(user_id):
    """Returns user object

    Args:
        user_id (str): The id of the user

    Returns:
        User: The loaded user object
    """
    return r.hget('users', user_id)
