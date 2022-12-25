
class PartialDate:
    """
    Class containing parts of a full date.
    """
    def __init__(self, day: int, hour: int):
        self.day = day
        self.hour = hour
        self.weekday = 0

    def get_weekday(self):
        day = self.weekday
        if day == 0:
            return "Mon"
        if day == 1:
            return "Tue"
        if day == 2:
            return "Wed"
        if day == 3:
            return "Thu"
        if day == 4:
            return "Fri"
        if day == 5:
            return "Sat"
        if day == 6:
            return "Sun"

    def is_same_hour(self, other: 'PartialDate') -> bool:
        """
        Returns True if a given PartialDate is during the same hour.
        """
        return self.day == other.day and self.hour == other.hour

    def is_in_range(self, before: 'PartialDate', after: 'PartialDate') -> bool:
        """
        Returns True if this PartialData is between two others.
        """
        return before.day * 24 + before.hour <= self.day * 24 + self.hour <= after.day * 24 + after.hour

    def more_or_equal_to(self, other: 'PartialDate'):
        return self.day * 24 + self.hour >= other.day * 24 + other.hour

    def less_or_equal_to(self, other: 'PartialDate'):
        return self.day * 24 + self.hour <= other.day * 24 + other.hour
