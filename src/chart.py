from display import Display
from partialdate import PartialDate


class Chart:
    CHAR_WIDTH = 8
    CHAR_HEIGHT = 8

    TOP_BAR_HEIGHT = 10
    DETAIL_CHART_HEIGHT = 190
    OVERVIEW_CHART_HEIGHT = 100

    def __init__(self, display: Display):
        self._display = display
        self._data = []
        self._current_value = 0
        self._max_value = 0
        self._min_value = 0
        self._avg_value = 0

    def update(self, data: list) -> None:
        """
        Redraws the chart to the display buffer.
        :param data: Data to show in chart. Ordered list of tuples formatted as (time: PartialDate, value: float).
        """
        self._data = data
        self._max_value = 0
        self._min_value = data[0][1]
        self._avg_value = 0
        for data_point in data:
            value = data_point[1]
            self._avg_value += value

            if self._max_value < value:
                self._max_value = value

            if self._min_value > value:
                self._min_value = value

        self._avg_value /= len(data)

        start = self._data[-20][0]
        stop = self._data[-5][0]

        self._draw_top_bar()
        self._draw_detail_chart(start, stop)
        self._draw_overview_chart(start, stop)

    def _draw_top_bar(self) -> None:
        color = self._display.BLACK

        now_str = _format_float_str(self._current_value, 3, 2)
        avg_str = _format_float_str(self._avg_value, 3, 2)
        max_str = _format_float_str(self._max_value, 3, 2)
        min_str = _format_float_str(self._min_value, 3, 2)

        x = self.CHAR_WIDTH // 2
        y = 1
        self._display.image.text(f"Nu: {now_str}  Avg: {avg_str}  Max: {max_str}  Min: {min_str}", x, y, color)

        self._display.image.line(0, self.TOP_BAR_HEIGHT - 1, self._display.WIDTH - 1, self.TOP_BAR_HEIGHT - 1, color)

    def _draw_detail_chart(self, start: PartialDate, stop: PartialDate) -> None:
        data_to_draw = [data_point for data_point in self._data if data_point[0].is_in_range(start, stop)]

        point_distance = self._display.WIDTH / (len(data_to_draw) - 2)
        bottom_spacing = 2
        graph_height = self.DETAIL_CHART_HEIGHT - self.CHAR_HEIGHT - bottom_spacing
        value_scale_factor = graph_height / self._max_value

        previous_x = previous_y = None

        for index, (time, value) in enumerate(data_to_draw):
            point_x = int(index * point_distance - point_distance / 2)
            point_y = int(self.TOP_BAR_HEIGHT + graph_height - value * value_scale_factor)

            if index != 0:
                self._display.image.line(previous_x, previous_y, point_x, point_y, self._display.BLACK)

                if index != len(data_to_draw) - 1:
                    text = _format_int_str(time.hour, 2)
                    text_y = self.TOP_BAR_HEIGHT + graph_height + 1 + self.CHAR_HEIGHT // 2
                    self._draw_centered_text(text, point_x, text_y, self._display.BLACK)

            previous_x = point_x
            previous_y = point_y

        self._draw_dashed_line(int(self.TOP_BAR_HEIGHT + graph_height - self._avg_value * value_scale_factor))
        self._draw_y_axis_values(graph_height, value_scale_factor)

        divider_y = self.TOP_BAR_HEIGHT + self.DETAIL_CHART_HEIGHT - 1
        self._display.image.line(0, divider_y, self._display.WIDTH - 1, divider_y, self._display.BLACK)

    def _draw_y_axis_values(self, graph_height: int, value_scale_factor: float) -> None:
        if self._max_value >= 200:
            floor_to = 200
        else:
            floor_to = 20
        max_draw_value = (self._max_value // floor_to) * floor_to

        values_to_draw = [max_draw_value, max_draw_value * 3 / 4, max_draw_value * 1 / 2, max_draw_value * 1 / 4]
        digits = len(str(max_draw_value))

        for value in values_to_draw:
            text = _format_int_str(value, digits)
            y_pos = int(self.TOP_BAR_HEIGHT + graph_height - value * value_scale_factor)
            x_pos = 5
            self._display.image.text(text, x_pos, y_pos, self._display.DARK_GRAY)

    def _draw_overview_chart(self, detail_start: PartialDate, detail_end: PartialDate) -> None:
        point_distance = self._display.WIDTH / (len(self._data) - 1)
        value_scale_factor = self.OVERVIEW_CHART_HEIGHT / self._max_value
        start_height = self.TOP_BAR_HEIGHT + self.DETAIL_CHART_HEIGHT

        start = None
        end = None
        for index, (time, value) in enumerate(self._data):
            if start is None and time.more_or_equal_to(detail_start):
                start = int(index * point_distance + point_distance / 2)

            if start is not None and time.less_or_equal_to(detail_end):
                end = int(index * point_distance - point_distance / 2)

        width = end - start
        height = self.OVERVIEW_CHART_HEIGHT
        self._display.image.rect(start, start_height, width, height, self._display.LIGHT_GRAY, True)

        previous_x = None
        previous_y = None

        for index, (time, value) in enumerate(self._data):
            point_x = int(index * point_distance)
            point_y = int(start_height + self.OVERVIEW_CHART_HEIGHT - value * value_scale_factor)

            if index != 0:
                self._display.image.line(previous_x, previous_y, point_x, point_y, self._display.BLACK)

            if time.hour == 0:
                text_y = start_height + self.OVERVIEW_CHART_HEIGHT - self.CHAR_HEIGHT
                self._display.image.text(time.get_weekday(), point_x, text_y, self._display.BLACK)

            previous_x = point_x
            previous_y = point_y

        line_y = int(start_height + self.OVERVIEW_CHART_HEIGHT - self._avg_value * value_scale_factor)
        self._draw_dashed_line(line_y)

    def _draw_dashed_line(self, y_pos: int) -> None:
        dash_len = 4

        for start_x in range(dash_len // 2, self._display.WIDTH, dash_len * 2):
            end_x = start_x + dash_len - 1
            self._display.image.line(start_x, y_pos, end_x, y_pos, self._display.DARK_GRAY)

    def _draw_centered_text(self, text: str, x: int, y: int, color) -> None:
        x -= (self.CHAR_WIDTH * len(text)) // 2
        y -= self.CHAR_HEIGHT // 2
        self._display.image.text(text, x, y, color)


def _interpolate_between(value1, value2, hour) -> float:
    return value1 + (value2 - value1) * hour


def _format_int_str(value: float, length: int = 1) -> str:
    value = int(value)
    missing = length - len(str(value))
    return "0" * missing + str(value)


def _format_float_str(value: float, integers: int, decimals: int) -> str:
    decimal_str = str(float(value) % 1)[1:]
    missing_decimals = decimals - len(decimal_str) + 1
    decimal_str += "0" * missing_decimals
    return (_format_int_str(value, integers) + decimal_str)[:integers + decimals + 1]
