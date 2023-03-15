from util import EmbedBuilder

class embeds():
    """
    This class creates embeds when a user is DENIED for an application.
    See docstrings below for reasons a user can be DENIED.
    """
    def __init__(self) -> None:
        pass

    def min_reqs(self, msg_count, join_time):
        """
        User does not meet the minimum requirements to apply for staff.
        """
        ...

    def marked_spam(self):
        """
        User is marked spam by staff for a previous offence.
        """
        ...

    def cooldown(self):
        """
        User has recently applied for staff and was denied.
        A cooldown is in place to prevent a user from immediatly re-applying.
        """
        ...

    def ongoing(self):
        """
        User still has an ongoing application.
        """
        ...