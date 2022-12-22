from display import Display


def draw_chart(display: Display, top_offset: int, data: list, current_hour: float, average: float, max_value: float) -> None:
    """
    Draws a chart with times in x-axis and values in y-axis.

    :param display: Display containing the buffer to draw the chart to.
    :param top_offset: Distance from top of display to draw.
    :param data: Data to show in chart. Ordered list of tuples formatted as (hour: int, value: float).
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
