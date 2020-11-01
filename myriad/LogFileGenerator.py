from datetime import datetime


def createHourStart(hour_date: datetime, description: str):
    return "+" + hour_date.strftime("%Y/%m/%d %H:%M") + description[:20]


def createCmdSetAutoOn(min: int, sec: int):
    cmd = f'{":": <3} {min:0>2}:{sec:0>2}     {"$AON AUTO ACTIVATE": <57} :00'
    return f'{cmd: <78} N'


def createAdBreak(minute: int):
    min_formatted = f'{minute:0>2}'
    cmd = f'{":": <13} {"BREAK XX:"+min_formatted: <47}'
    return f'{cmd: <78} X'


def createAbsoluteTime(minute: int, second: int):
    min_formatted = f'{minute:0>2}'
    sec_formatted = f'{second:0>2}'
    cmd = f'{":": <3} {min_formatted}:{sec_formatted}     $T{min_formatted}:{sec_formatted}.00'
    cmd_with_end_time = f'{cmd: <71} :00'
    return f'{cmd_with_end_time: <78} N'


def createCart(cart_num: int, title: str, artist: str, intro_len: int, duration_min: int, duration_sec: int, fadeable: bool = False, auto_segue: bool = True):
    duration = f'{duration_min:0>2}:{duration_sec:0>2}'
    segue_char = "X" if auto_segue else "-"
    fadeable_char = "F" if fadeable else "E"

    cmd = f'C {cart_num: <6} {title[:33]: <33} {artist[:20]: <20} {intro_len:0>2}/{duration}/{fadeable_char}'
    return f'{cmd: <78} {segue_char}'


def createLink(cart_num: int, cart_name: str, auto_segue: bool = True):
    segue_char = "X" if auto_segue else "-"
    cmd = f'{":": <13} {cart_name[:40]: <40}{" "*9}{cart_num: <10}'
    return f'{cmd: <78} {segue_char}'
