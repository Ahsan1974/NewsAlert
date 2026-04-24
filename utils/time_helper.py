from datetime import datetime, timedelta


def convert_to_pkt(time_text):
    """
    Convert ForexFactory time to Pakistan time
    Example: 3:30pm -> 08:30 PM
    """

    try:
        source = datetime.strptime(time_text.lower(), "%I:%M%p")
        pkt = source + timedelta(hours=5)
        return pkt.strftime("%I:%M %p")

    except:
        return time_text