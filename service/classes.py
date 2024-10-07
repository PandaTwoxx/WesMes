"""Classes"""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""

class LaunchError(Exception):
    """Used for an launch errors when starting the app"""

class User(UserMixin):
    """User class

    Derives:
        UserMixin
    """
    def __init__(self, name="", email="", password="", username="", profile_pic_link = ""):
        self.id = str()
        self.name = str(name)
        self.email = str(email)
        self.password = generate_password_hash(password)
        self.username = str(username)
        self.profile_pic_link = str(profile_pic_link)


    def check_password(self, password: str) -> bool:
        """Checks Password

        Args:
            password (str): The un-hashed password

        Returns:
            bool: If the password is correct
        """
        return check_password_hash(self.password, password)


    def get_id(self):
        return self.id

    ################################
    # SERIALIZE/DESERIALIZE ########
    ################################

    def serialize(self) -> dict:
        """Serializer

        Returns:
            dict: The serialized object
        """
        result = {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "name": self.name,
            "password": self.password,
            "profile_pic_link": self.profile_pic_link
        }
        return result


    def deserialize(self, data: dict) -> None:
        """
        Deserializes a User from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data["id"]
            self.profile_pic_link = data["profile_pic_link"]
            self.username = data["username"]
            self.name = data["name"]
            self.password = data["password"]
            self.email = data["email"]

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid User: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid User: body of request contained bad or no data "
                + str(error)
            ) from error
