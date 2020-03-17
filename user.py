"""
Module: User

Description:
The user module contains the class of a user.
Each unique chat is stored as a user object.
"""


class User:
    """
    The user class contains attributes of a user.
    These can be returned as dictionary entries.
    """

    def __init__(self, chat_id, name):
        self.chat_id = chat_id
        self.name = name

    def to_dict(self):
        """Returns user attributes as dict.

        Returns:
            Dictionary -- User attributes
        """
        return {
            'chat_id': self.chat_id,
            'name': self.name
        }

    @staticmethod
    def from_dict(user_as_dict):
        """Creates and returns a user object with given dictionary.

        Arguments:
            user_as_dict {Dictionary} -- Dict with chat_id and name

        Returns:
            user.User -- User object
        """
        return User(
            user_as_dict['chat_id'],
            user_as_dict['name']
        )
