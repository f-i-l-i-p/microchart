from partialdate import PartialDate
from display import Display
from requesthandler import RequestHandler
from chart import Chart
import secrets
import machine
import time
import ntptime


def set_time() -> None:
    tries = 5

    for i in range(tries):
        try:
            ntptime.settime()
            return
        except Exception as e:
            if i == tries - 1:
                raise e
        
        time.sleep(10)


def get_data(request_handler) -> tuple:
    json = request_handler.get_json(secrets.API_URL)

    current = json["current"]["startDateTime"]
    year = int(current[0:4])
    month = int(current[5:7])
    day = int(current[8:10])
    hour = int(current[11:13])

    current_time = PartialDate(year, month, day, hour)

    data = []

    intervals = json["intervals"]
    for interval in intervals:
        time = interval["startDateTime"]
        year = int(time[0:4])
        month = int(time[5:7])
        day = int(time[8:10])
        hour = int(time[11:13])
        price = float(interval["price"])

        data.append((PartialDate(year, month, day, hour), price))

    return data, current_time


def update(display: Display) -> int:
    request_handler = RequestHandler()
    chart_data, current_time = get_data(request_handler)

    chart = Chart(display)
    chart.update(chart_data, current_time)

    set_time()

    year, month, day, hour, minute, second, weekday, yearday = time.localtime()
    request_handler._wlan.active(False)
    request_handler._wlan.disconnect()

    minutes_to_next_update = 60 - int(minute) + 5
    return minutes_to_next_update


def run() -> None:
    display = Display()
    display.image.fill(0xff)

    try:
        minutes_to_next_update = update(display)
    except Exception as e:
        name = type(e).__name__
        if hasattr(e, "message"):
            msg = str(e.message)
        else:
            msg = str(e)

        display.image.rect(0, 0, display.WIDTH, 30, display.BLACK, True)
        display.image.text("ERROR", 0, 1, display.WHITE)
        display.image.text(name, 0, 11, display.WHITE)
        display.image.text(msg, 0, 21, display.WHITE)

        minutes_to_next_update = 60

    display.redraw()
    display._delay_ms(500)

    display.sleep()
    display._delay_ms(500)

    sleep_time = 1000 * 60 * minutes_to_next_update
    machine.deepsleep(sleep_time)


if __name__ == '__main__':
    run()
