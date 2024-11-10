"""Classes"""
import time
import json
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# Redis object
from service.common.redis_data import r


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
        self.pending_friends = [str] # Pointer to friend's user_id
        self.sent_friends = [str] # Pointer to friend's user_id


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

    def push_to_redis(self):
        """Pushes self to redis
        """
        r.hset(f"users:{self.id}", mapping=self.serialize())

    def pull_from_redis(self, current_id):
        """Pulls self from redis
        """
        self.id = r.hget(f"users:{current_id}", "id")
        self.name = r.hget(f"users:{current_id}", "name")
        self.email = r.hget(f"users:{current_id}", "email")
        self.password = r.hget(f"users:{current_id}", "password")
        self.username = r.hget(f"users:{current_id}", "username")
        self.profile_pic_link = r.hget(f"users:{current_id}", "profile_pic_link")
        self.chats = json.loads(r.hget(f"users:{current_id}", "chats"))
        self.friends = json.loads(r.hget(f"users:{current_id}", "friends"))
        self.pending_friends = json.loads(r.hget(f"users:{current_id}", "pending_friends"))
        self.sent_friends = json.loads(r.hget(f"users:{current_id}", "sent_friends"))

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
            "chats": self.chats,
            "friends": self.friends,
            "pending_friends": self.pending_friends,
            "sent_friends": self.sent_friends
        }
        return result


    def deserialize(self, data: dict):
        """
        Deserializes a User from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.id = str(data["id"])
            self.profile_pic_link = data["profile_pic_link"]
            self.username = data["username"]
            self.name = data["name"]
            self.password = data["password"]
            self.email = data["email"]
            self.chats = data["chats"]
            self.friends = data["friends"]
            self.pending_friends = data["pending_friends"]
            self.sent_friends = data["sent_friends"]

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
    def __init__(self, user: str, content: str, sent_time: float = time.time()):
        """The constructor

        Args:
            user (User): The user who sent the message
            content (str): The message content
            sent_time (float, optional): The time sent. Defaults to time.time().
        """
        self.id = str(id(self))
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

    def push_to_redis(self):
        """Pushes self to redis
        """
        r.hset(f"messages:{self.id}",mapping=self.serialize())

    def pull_from_redis(self, chat_id):
        """Pulls self from redis
        """
        self.id = r.hget(f"messages:{chat_id}", "id")
        self.user = r.hget(f"messages:{chat_id}", "user")
        self.content = r.hget(f"messages:{chat_id}", "content")
        self.edited_time = r.hget(f"messages:{chat_id}", "edited_time")
        self.sent_time = r.hget(f"messages:{chat_id}", "sent_time")

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
            "user": self.user,
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
            self.user = User().deserialize(data["user"])
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
        members: list[str],
        chat_name: str,
        messages: list[str],
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

    def push_to_redis(self):
        """Pushes self to redis
        """
        r.hset(f"chats:{self.id}",mapping=self.serialize())

    def pull_from_redis(self, message_id):
        """Pulls self from redis
        """
        self.id = r.hget(f"chats:{message_id}", "id")
        self.members = json.loads(r.hget(f"chats:{message_id}", "members"))
        self.start_date = r.hget(f"chats:{message_id}", "start_date")
        self.messages = json.loads(r.hget(f"chats:{message_id}", "messages"))
        self.chat_name = r.hget(f"chats:{message_id}", "chat_name")

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
            "members": json.dumps(self.members),
            "messages": json.dumps(self.messages),
            "start_date": self.start_date,
            "chat_name": self.chat_name,
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
