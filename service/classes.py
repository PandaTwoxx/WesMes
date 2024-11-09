"""Classes"""
import time
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
        self.id = str(id(self))
        self.name = str(name)
        self.email = str(email)
        self.password = generate_password_hash(password)
        self.username = str(username)
        self.profile_pic_link = str(profile_pic_link) # TODO: Create place to store profile pics
        self.chats = [str] # Pointer to the the chat_id
        self.friends = [str] # Pointer to friend's user_id


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
            "profile_pic_link": self.profile_pic_link,
            "chats": []
        }
        for chat in self.chats:
            result["chats"].append(chat)
        return result


    def deserialize(self, data: dict):
        """
        Deserializes a User from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = int(data["id"])
            self.profile_pic_link = data["profile_pic_link"]
            self.username = data["username"]
            self.name = data["name"]
            self.password = data["password"]
            self.email = data["email"]
            for chat in data["chats"]:
                self.chats.append(chat)

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
        return self
class Message:
    """Message class"""
    def __init__(self, user: User, content: str, sent_time: float = time.time()):
        """The constructor

        Args:
            user (User): The user who sent the message
            content (str): The message content
            sent_time (float, optional): The time sent. Defaults to time.time().
        """
        self.id = id(self)
        self.user = user
        self.content = content
        self.edited_time = sent_time
        self.sent_time = sent_time

    def get_id(self):
        """Gets id"""
        return self.id

    def update_message(self, new_message: str):
        """Updates message content"""
        self.content = new_message
        self.edited_time = time.time()
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
            "content": self.content,
            "edited_time": self.edited_time,
            "sent_time": self.sent_time,
            "user": self.user.serialize(),
        }
        return result


    def deserialize(self, data: dict):
        """
        Deserializes a User from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data["id"]
            self.content = data["content"]
            self.edited_time = data["edited_time"]
            self.sent_time = data["sent_time"]
            new_user = User()
            new_user.deserialize(data["user"])
            self.user = new_user
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
        return self

class Chat:
    """The chat class"""
    def __init__(
        self,
        members: list[User],
        chat_name: str,
        messages: list[Message],
        start_date: float = time.time()
                ):
        """The constructor

        Args:
            members (list[User]): The list of members
            name (str): The name of the chat
            messages (list[Message]): The array of messages
            start_date (float, optional): The time the chat was created. Defaults to time.time().
        """
        self.id = str(id(self))
        self.members = members
        self.start_date = start_date
        self.messages = messages
        self.chat_name = chat_name

    def get_id(self):
        """Gets id"""
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
            "members": [],
            "messages": [],
            "start_date": self.start_date,
            "chat_name": self.chat_name,
        }
        for member in self.members:
            result["members"].append(member.serialize())
        for message in self.messages:
            result["messages"].append(message.serialize())
        return result


    def deserialize(self, data: dict):
        """
        Deserializes a User from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = data["id"]
            self.start_date = data["start_date"]
            self.chat_name = data["chat_name"]
            for message in data["messages"]:
                new_message = Message(User(),"")
                new_message.deserialize(message)
                self.messages.append(new_message)
            for member in data["members"]:
                new_user = User()
                new_user.deserialize(member)
                self.messages.append(new_user)
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
        return self
