import logging


def configure_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def format_time(seconds: int) -> str:
    seconds = int(seconds)
    if seconds >= 3600:
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return f"{hours}h {minutes}m {seconds}s"
    elif seconds >= 60:
        minutes = seconds // 60
        seconds %= 60
        return f"{minutes}m {seconds}s"
    elif seconds > 0:
        return f"{seconds}s"
    else:
        return "0s"
