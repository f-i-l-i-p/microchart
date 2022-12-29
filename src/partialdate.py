class PartialDate:
    """
    Class containing parts of a full date.
    """

    def __init__(self, year: int, month: int, day: int, hour: int):
        self.year = year
        self.month = month
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

    def _to_comparable(self) -> int:
        """
        Returns an integer that can be used for comparing PartialDates.
        """
        return self.year * 12 * 31 * 24 + self.month * 31 * 24 + self.day * 24 + self.hour

    def is_same_hour(self, other: 'PartialDate') -> bool:
        """
        Returns True if a given PartialDate is during the same hour.
        """
        return self._to_comparable() == other._to_comparable()

    def is_in_range(self, before: 'PartialDate', after: 'PartialDate') -> bool:
        """
        Returns True if this PartialData is between two others.
        """
        return self.more_or_equal_to(before) and self.less_or_equal_to(after)

    def more_or_equal_to(self, other: 'PartialDate'):
        return self._to_comparable() >= other._to_comparable()

    def less_or_equal_to(self, other: 'PartialDate'):
        return self._to_comparable() <= other._to_comparable()

    def __str__(self) -> str:
        return f"{self.year}, {self.month}, {self.day}, {self.hour}"
