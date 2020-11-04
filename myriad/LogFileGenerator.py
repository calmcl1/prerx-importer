from datetime import datetime
import os
import os.path


def createHourStart(hour_date: datetime, description: str):
    return "+" + hour_date.strftime("%d/%m/%Y %H:%M") + " " + description[:20]+"\n"


def createCmdSetAutoOn(min: int, sec: int):
    cmd = f'{":": <3} {min:0>2}:{sec:0>2}     {"$AON AUTO ACTIVATE": <57} :00'
    return f'{cmd: <78} N'+"\n"


def createAdBreak(minute: int):
    min_formatted = f'{minute:0>2}'
    cmd = f'{":": <13} {"BREAK XX:"+min_formatted: <47}'
    return f'{cmd: <78} X'+"\n"


def createAbsoluteTime(minute: int, second: int):
    min_formatted = f'{minute:0>2}'
    sec_formatted = f'{second:0>2}'
    cmd = f'{":": <3} {min_formatted}:{sec_formatted}     $T{min_formatted}:{sec_formatted}.00'
    cmd_with_end_time = f'{cmd: <71} :00'
    return f'{cmd_with_end_time: <78} N'+"\n"


def createCart(cart_num: int, title: str, artist: str, intro_len: int, duration_min: int, duration_sec: int, fadeable: bool = False, auto_segue: bool = True):
    duration = f'{duration_min:0>2}:{duration_sec:0>2}'
    segue_char = "X" if auto_segue else "-"
    fadeable_char = "F" if fadeable else "E"

    cmd = f'C {cart_num: <6} {title[:33]: <33} {artist[:20]: <20} {intro_len:0>2}/{duration}/{fadeable_char}'
    return f'{cmd: <78} {segue_char}'+"\n"


def createLink(cart_num: int, cart_name: str, auto_segue: bool = True):
    segue_char = "X" if auto_segue else "-"
    cmd = f'{":": <13} {cart_name[:40]: <40}{" "*9}{cart_num: <10}'
    return f'{cmd: <78} {segue_char}'+"\n"


def splitLogToHours(log_entry_lines: list) -> list:
    if not log_entry_lines[0].startswith("+"):
        raise ValueError("First entry in log hour must be an Hour Start")

    log_hours = []
    while(len(log_entry_lines)):
        print
        log_entry = log_entry_lines.pop(0)
        if(log_entry.startswith("+")):
            log_hours.append(log_entry)
        else:
            log_hours[len(log_hours)-1] += log_entry

        #log_hours[len(log_hours)-1] += "\n"

    return sorted(log_hours, key=lambda x: datetime.strptime(x[1:17], "%d/%m/%Y %H:%M"))


def reorderLogFile(log_file_path: str):
    sorted_hours = ""
    with open(log_file_path, "r") as log_file:
        sorted_hours = splitLogToHours(log_file.readlines())

    os.unlink(log_file_path)
    with open(log_file_path, "w") as log_file:
        log_file.writelines(sorted_hours)


def writeLogFile(log_directory: str, log_entry_lines: list):
    # Concat each string of log hours into string hour-chunks

    log_hours = splitLogToHours(log_entry_lines)

    # For each log hour we have, write it to the necessary log file.
    # However - some hours may already exist, so we'll need to re-parse it
    # afterwards and make sure that all of the hours are in the correct order.

    # print(f'Found hour: {l[1:17]}')
    # print(l)

    log_files_to_reorganize = []

    for l in log_hours:
        # Write the log hour to file
        date_current_hour = datetime.strptime(l[1:17], "%d/%m/%Y %H:%M")
        current_hour_log_path = os.path.join(
            "C:\\PSquared\\Logs", date_current_hour.strftime("MY%y%m%d.LOG"))

        # If it already exists, keep track of it as one we'll need to sort by hour later
        if os.path.exists(current_hour_log_path) and not current_hour_log_path in log_files_to_reorganize:
            log_files_to_reorganize.append(current_hour_log_path)

        with open(current_hour_log_path, "a") as log_file:
            log_file.write(l)

        print(f"Written {l[1:17]} to {current_hour_log_path}")

    for log_file in log_files_to_reorganize:
        reorderLogFile(log_file)
        print(f"Reordered {log_file}")
