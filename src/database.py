"""
Module: database

Description:

The module provides the other teams with the current data
and handles various interactions with the database.

Usage:

1. Create reference to database class:     database = Database(path_to_json)

2. Initialize data:                        database.init_json()

General (Access all debt and user objects):      users = database.users / debts = database.debts


Functions for defined interfaces:

Team 1 :     add_user(self, chat_id, name)  |   user_exists(self, chat_id)

Team 2:      add_debt(self, creditor, category, amount, deadline, debtor)   |   database.users

Team 3:      get_debt_by_debt_id(self, debt_id) , get_user_by_chat_id(self, chat_id)

Team 4:      set_accepted(self, debt_id, is_accepted)

Team 6:      set_paid(self, debt_id, is_paid)

"""

import json
import uuid
from user import User
from debt import Debt


class Database:
    """
    The Database class contains functions that interact with the database and
    provides necessary data with the other teams via defined interfaces.

    """

    def __init__(self, path_to_json):

        self.path_to_json = path_to_json
        self.users = []
        self.debts = []

    def init_json(self):
        """Loads data from JSON file and initializes list of users and debts.
        """

        try:

            with open(self.path_to_json) as json_database:

                raw_json = json_database.read()

            try:

                json_database = json.loads(raw_json)

            except json.decoder.JSONDecodeError:

                pass

            self.users = [User.from_dict(user)
                          for user in json_database['users']]
            self.debts = [Debt.from_dict(debt)
                          for debt in json_database['debts']]

        except FileNotFoundError:
            self.update_json()

    def update_json(self):
        """Saves current users and debts to the JSON file
        """

        users_as_dict = [User.to_dict(user) for user in self.users]
        debts_as_dict = [Debt.to_dict(debt) for debt in self.debts]

        default_json = {
            'users': users_as_dict,
            'debts': debts_as_dict
        }

        try:

            with open(self.path_to_json, 'w') as json_database:

                json_database.write(json.dumps(default_json))

        except FileNotFoundError:

            pass

    def user_exists(self, chat_id):
        """Checks whether a users exists in the database

        Arguments:
            chat_id {String} -- Telegram Chat_ID

        Returns:
            Boolean -- User exists
        """

        user_exists = False

        for user in self.users:

            if user.chat_id == chat_id:

                user_exists = True

        return user_exists

    def add_user(self, chat_id, name):
        """Adds new user to the database

        Arguments:
            chat_id {String} -- Telegram Chat_ID
            name {String} -- Telegram username
        """

        if self.user_exists(chat_id):
            return

        user = User(chat_id, name)
        self.users.append(user)
        self.update_json()

    def add_debt(self, creditor, category, amount, deadline, debtor):
        """Ads a new debt to the database

        Arguments:
            creditor {String} -- Chat_ID of creditor
            category {String} -- Category of the debt
            amount {String} -- Amount
            deadline {String} -- Deadline for notification. Format: YYYY.MM.DD
            debtor {String} -- Chat_ID of debtor

        Returns:
            debt.Debt -- Object of the recently added debt
        """

        debt = Debt(str(uuid.uuid1()), creditor, category, amount, deadline, debtor)
        self.debts.append(debt)
        self.update_json()
        print(debt)

        return debt

    def get_open_debts(self, chat_id):
        """Shows all open debts form a user

        Returns:
            debt.Debt -- Debt objects where given user is debtor
        """

        return [debt for debt in self.debts if not debt.is_paid and debt.is_accepted and debt.debtor == chat_id]

    def get_open_claims(self, chat_id):
        """Shows all open claims form a user

        Returns:
            debt.Debt -- Debt objects where given user is creditor
        """

        return [debt for debt in self.debts if not debt.is_paid and debt.is_accepted and debt.creditor == chat_id]

    def get_debt_by_debt_id(self, debt_id):
        """Returns the debt of a given debt_id

        Arguments:
            debt_id {String} -- ID of a debt

        Returns:
            debt.Debt -- Object of filtered debt
        """

        for debt in self.debts:
            if debt.debt_id == debt_id:
                return debt
        return None

    def get_user_by_chat_id(self, chat_id):
        """Returns the user of a given Chat_id

        Arguments:
            chat_id {String} -- Telegram Chat_ID

        Returns:
            user.User -- Object of filtered user
        """

        for user in self.users:
            if user.chat_id == chat_id:
                return user
        return None

    def set_accepted(self, debt_id, is_accepted):
        """Sets the accepted status of a debt request

        Arguments:
            debt_id {String} -- Unique ID of a debt
            is_accepted {bool} -- Debtors answer to debt request

        Returns:
            debt.Debt -- Object of the current debt
        """
        debt_object = 0

        for debt in self.debts:
            if debt.debt_id == debt_id:
                debt.is_accepted = is_accepted
                debt_object = debt
                self.update_json()

        return debt_object

    def set_paid(self, debt_id, is_paid):
        """Sets the paid status of a debt request

        Arguments:
            debt_id {String} -- Unique ID of a debt
            is_paid {bool} -- Paid status

        Returns:
            debt.Debt -- Object of the current debt
        """
        debt_object = 0

        for debt in self.debts:
            if debt.debt_id == debt_id:
                debt.is_paid = is_paid
                debt_object = debt
                self.update_json()

        return debt_object


