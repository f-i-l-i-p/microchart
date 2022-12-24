from display import Display
from partialdate import PartialDate


class Chart:
    CHAR_WIDTH = 8
    CHAR_HEIGHT = 8

    DETAIL_CHART_HEIGHT = 200
    OVERVIEW_CHART_HEIGHT = 100

    def __init__(self, display: Display):
        self._display = display
        self._data = []
        self._max_value = 0

    def update(self, data: list) -> None:
        """
        Redraws the chart to the display buffer.
        :param data: Data to show in chart. Ordered list of tuples formatted as (time: PartialDate, value: float).
        """
        self._data = data
        self._max_value = 0
        for data_point in data:
            if self._max_value < data_point[1]:
                self._max_value = data_point[1]

        start = self._data[-22][0]
        stop = self._data[-3][0]
        self._draw_detail_chart(start, stop)
        self._draw_overview_chart(start, stop)

    def _draw_detail_chart(self, start: PartialDate, stop: PartialDate) -> None:
        data_to_draw = [data_point for data_point in self._data if data_point[0].is_between(start, stop)]

        point_distance = self._display.WIDTH / (len(data_to_draw) - 2)
        graph_height = self.DETAIL_CHART_HEIGHT - self.CHAR_HEIGHT
        value_scale_factor = graph_height / self._max_value

        previous_x = previous_y = None

        for index, (time, value) in enumerate(data_to_draw):
            point_x = int(index * point_distance - point_distance / 2)
            point_y = int(graph_height - value * value_scale_factor)

            if index != 0:
                self._display.image.line(previous_x, previous_y, point_x, point_y, self._display.BLACK)

                if index != len(data_to_draw) - 1:
                    text = _format_str(time.hour, 2)
                    text_y = self.DETAIL_CHART_HEIGHT - self.CHAR_HEIGHT // 2
                    self._draw_centered_text(text, point_x, text_y, self._display.BLACK)

            previous_x = point_x
            previous_y = point_y

        self._draw_y_axis_values(value_scale_factor)

    def _draw_y_axis_values(self, value_scale_factor: float) -> None:
        if self._max_value >= 200:
            floor_to = 200
        else:
            floor_to = 20
        max_draw_value = (self._max_value // floor_to) * floor_to

        values_to_draw = [max_draw_value, max_draw_value * 3 / 4, max_draw_value * 1 / 2, max_draw_value * 1 / 4]
        digits = len(str(max_draw_value))

        for value in values_to_draw:
            text = _format_str(value, digits)
            y_pos = int(self.DETAIL_CHART_HEIGHT - value * value_scale_factor)
            x_pos = 5
            self._display.image.text(text, x_pos, y_pos, self._display.DARK_GRAY)

    def _draw_overview_chart(self, detail_start: PartialDate, detail_end: PartialDate) -> None:
        point_distance = self._display.WIDTH / (len(self._data) - 1)
        value_scale_factor = self.OVERVIEW_CHART_HEIGHT / self._max_value

        previous_x = previous_y = None

        for index, (time, value) in enumerate(self._data):
            point_x = int(index * point_distance)
            point_y = int(self.DETAIL_CHART_HEIGHT + self.OVERVIEW_CHART_HEIGHT - value * value_scale_factor)

            if time.more_or_equal_to(detail_start) and time.less_then(detail_end):
                y = self.DETAIL_CHART_HEIGHT
                w = int(point_distance) + 1
                h = self.OVERVIEW_CHART_HEIGHT
                self._display.image.rect(point_x, y, w, h, self._display.LIGHT_GRAY, True)

            if index != 0:
                self._display.image.line(previous_x, previous_y, point_x, point_y, self._display.BLACK)

            previous_x = point_x
            previous_y = point_y

    def _draw_centered_text(self, text: str, x: int, y: int, color) -> None:
        x -= (self.CHAR_WIDTH * len(text)) // 2
        y -= self.CHAR_HEIGHT // 2
        self._display.image.text(text, x, y, color)


def draw_chart(display: Display, top_offset: int, data: list, current_hour: float, average: float, max_value: float) -> None:
    """
    Draws a chart with times in x-axis and values in y-axis.

    :param display: Display containing the buffer to draw the chart to.
    :param top_offset: Distance from top of display to draw.
    :param current_hour: Current hour.
    :param max_value: The maximum value that the chart should be able to display.
    """
    slot_width = display.WIDTH / len(data)
    chart_height = 200 - top_offset

    char_size = 8
    char_offset = (slot_width - 2 * char_size) / 2

    value_scale = chart_height / max_value

    previous_dot = None

    for index, (hour, value) in enumerate(data):
        time_text = _format_str(hour, 2)
        time_x_pos = int(index * slot_width + char_offset)

        display.image.text(time_text, time_x_pos, chart_height, display.BLACK)

        dot_x_pos = int((index + 1/2) * slot_width)
        dot_y_pos = int(chart_height - value * value_scale + top_offset)

        if previous_dot:
            display.image.line(previous_dot[0], previous_dot[1], dot_x_pos, dot_y_pos, display.BLACK)

        previous_dot = (dot_x_pos, dot_y_pos)

        if hour == int(current_hour):
            timeline_x_pos = int(dot_x_pos + slot_width * (current_hour % 1))
            display.image.line(timeline_x_pos, top_offset, timeline_x_pos, chart_height, display.LIGHT_GRAY)

            # Interpolate
            interpolated_value = _interpolate_between(value, data[index + 1][1], current_hour % 1)
            text = _format_str(interpolated_value)
            y_offset = 8 if value < data[index + 1][1] else -8
            y_pos = int(chart_height - interpolated_value * value_scale + top_offset)
            x_pos = int(timeline_x_pos)
            display.image.text(text, x_pos + 3, int(y_pos - char_size/2 + y_offset), Display.BLACK)
            display.image.ellipse(timeline_x_pos, y_pos, 2, 2, Display.BLACK, True)

    _draw_dashed_line(display, chart_height - int(average * value_scale), int(average))
    _draw_y_axis_values(display, max_value, value_scale, chart_height)


def _interpolate_between(value1, value2, hour) -> float:
    return value1 + (value2 - value1) * hour


def _draw_dashed_line(display: Display, y_pos: int, value: int) -> None:
    dash_len = 4

    for start_x in range(dash_len // 2, display.WIDTH, dash_len * 2):
        end_x = start_x + dash_len - 1
        display.image.line(start_x, y_pos, end_x, y_pos, display.DARK_GRAY)

    text = _format_str(value)
    display.image.text(text, display.WIDTH - 8*3 - 5, y_pos - 9, display.DARK_GRAY)


def _draw_y_axis_values(display: Display, max_value: float, value_scale: float, height: int) -> None:
    if max_value >= 200:
        floor_to = 200
    else:
        floor_to = 20
    max_draw_value = (max_value // floor_to) * floor_to

    values_to_draw = [max_draw_value, max_draw_value * 3/4, max_draw_value * 1/2, max_draw_value * 1/4]
    digits = len(str(max_draw_value))

    for value in values_to_draw:
        text = _format_str(value, digits)
        y_pos = height - int(value * value_scale)
        x_pos = 5
        display.image.text(text, x_pos, y_pos, display.DARK_GRAY)


def _format_str(value: float, length: int = 1) -> str:
    value = int(value)
    missing = length - len(str(value))
    return "0" * missing + str(value)
