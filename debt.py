"""
Module: debt

Description:
The debt module contains the class of a debt.
Each unique debt is stored as a debt object.
"""

class Debt:
    """
    The debt class contains attributes of a debt.
    These can be returned as dictionary entries.
    """

    def __init__(self, debt_id, creditor, category, amount, deadline, debtor, is_accepted=False, is_paid=False):
        self.debt_id = debt_id
        self.creditor = creditor
        self.category = category
        self.amount = amount
        self.deadline = deadline
        self.debtor = debtor
        self.is_accepted = is_accepted
        self.is_paid = is_paid


    def to_dict(self):
        """Returns debt attributes as dict.

        Returns:
            Dictionary -- Debt attributes
        """

        return {
            'debt_id': self.debt_id,
            'creditor': self.creditor,
            'category': self.category,
            'amount': self.amount,
            'deadline': self.deadline,
            'debtor': self.debtor,
            'is_accepted': self.is_accepted,
            'is_paid': self.is_paid
        }


    @staticmethod
    def from_dict(debt_as_dict):
        """Creates and returns a debt object with given dictionary.

        Arguments:
            debt_as_dict {Dictionary} -- Dict with necessary attributes

        Returns:
            debt.Debt -- Debt object
        """
        return Debt(
            debt_as_dict['debt_id'],
            debt_as_dict['creditor'],
            debt_as_dict['category'],
            debt_as_dict['amount'],
            debt_as_dict['deadline'],
            debt_as_dict['debtor'],
            debt_as_dict['is_accepted'],
            debt_as_dict['is_paid']
        )
        