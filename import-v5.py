from myriad import myriadhost, LogFileGenerator, CartFinder
# import pydub - this could be used to detect and strip out silence at the start/end
import argparse
from sys import argv
import time
import os
import os.path
from shutil import move
from subprocess import Popen, run
from datetime import datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument("files", action="store", nargs="*")
parser.add_argument("--media-directory", action="store",
                    nargs="?", dest="media_dir", default="F:\\Myriad\\Media\\", help="Path to the Media folder")
parser.add_argument("--logs-directory", action="store", nargs="?", dest="logs_dir",
                    default="F:\\Myriad\\Logs\\Main\\", help="Path to write the music logs to")

parsed_args = parser.parse_args(argv[1:])

MYRIAD_CL_PATH = "C:\\Program Files (x86)\\Broadcast Radio\\Myriad Playout v5\\MyriadUtilityCL5.exe"
MYRIAD_CL_ARGS = ["/Database", "HCR Mv5", "/Silent"]

if not os.path.exists(parsed_args.media_dir):
    print("Could not find Media directory:")
    print(parsed_args.psq_data_dir)
    print("Are you sure this is correct?")
    print("Use the --media-directory switch to supply an alternative directory.")
    exit(4)

audio_files: list = parsed_args.files
if(len(audio_files) % 2 != 0):
    print("Amount of audio files must be divisible by two!")
    exit(1)

# Sort the audio files into the correct order - 2x 28min files per hour
audio_files = sorted(audio_files)
print("Supplied audio files have been sorted into the following order:")
for f in audio_files:
    print("\t{0}".format(f))

is_correct_order = "-1"
while is_correct_order != "y" and is_correct_order != "n" and is_correct_order != "":
    is_correct_order = input("Is this correct? [Y/n]: ").lower()

if is_correct_order == "n":
    print("Please rename the files so that they can be sorted in filename order.")
    exit(2)

# Determine what time the files are to be scheduled
datetime_start = datetime.now().replace(minute=0, second=0, microsecond=0)
date_input = "-1"
while True:
    try:
        time.strptime(date_input, "%Y")
        datetime_start = datetime_start.replace(year=int(date_input))
        break
    except:
        date_input = input("What year is this due to be scheduled? [{0}]: ".format(
            time.strftime("%Y")))
        if not date_input:
            date_input = time.strftime("%Y")

date_input = "-1"
while True:
    try:
        time.strptime(date_input, "%m")
        datetime_start = datetime_start.replace(month=int(date_input))
        break
    except:
        date_input = input("What month is this due to be scheduled? [{0}]: ".format(
            time.strftime("%m")))
        if not date_input:
            date_input = time.strftime("%m")

date_input = "-1"
while True:
    try:
        time.strptime(date_input, "%d")
        datetime_start = datetime_start.replace(day=int(date_input))
        break
    except:
        date_input = input("What day is this due to be scheduled? [{0}]: ".format(
            time.strftime("%d")))
        if not date_input:
            date_input = time.strftime("%d")

date_input = "-1"
while True:
    try:
        time.strptime(date_input, "%H")
        datetime_start = datetime_start.replace(hour=int(date_input))
        break
    except:
        date_input = input("What hour is this due to be scheduled?: ")

presenter_name = ""

while not presenter_name:
    presenter_name = input("Who is presenting this show?: ")

datetime_end_of_last_hour = datetime_start + \
    timedelta(hours=int(len(audio_files)/2)-1, minutes=59, seconds=59)
datetime_start_psq = datetime_start.strftime("%Y-%m-%dT%H:%M")
datetime_end_psq = datetime_end_of_last_hour.strftime("%Y-%m-%dT%H:%M:%S")

# Rename the audio files to our format
print("Renaming files...")
for i in range(0, len(audio_files)):
    new_file_name = datetime_start.strftime(
        "%Y%m%d-%H00-") + f"{(i+1):02}" + "-" + presenter_name.replace(" ", "") + os.path.splitext(audio_files[i])[1]
    print("Renaming: {0} -> {1}".format(audio_files[i], new_file_name))
    audio_files[i] = move(audio_files[i], os.path.join(
        os.path.dirname(audio_files[i]), new_file_name))

# Convert the audio files to Wav, if necessary
converted_audio_files: list = []
converter_processes = []
for f in audio_files:
    if not os.path.splitext(f)[1].lower() == ".wav":
        print("Converting to wav file: {0}".format(f))

        converter_processes.append(Popen(["ffmpeg",
                                          "-i", f,
                                          "-c:a", "pcm_s16le",
                                          "-metadata", f'title={os.path.basename(f)}',
                                          "-metadata", f'artist={presenter_name}',
                                          "-metadata", f'copyright=HCR',
                                          "-y",
                                          os.path.abspath(os.path.splitext(
                                              f)[0] + ".wav")
                                          ], shell=True)
                                   )

    converted_audio_files.append(
        os.path.abspath(os.path.splitext(f)[0] + ".wav"))

for proc in converter_processes:
    proc.wait()

# Try to import the carts into Myriad
# First, find the first range of carts free from 1501

#myriad_host = myriadhost.MyriadHost("192.168.0.4")

print("Finding free space for carts in AudioWall...")
start_cart = 1501
cart_range_found = False
while not cart_range_found and start_cart < 1600:
    #print("Trying cart {0}".format(start_cart))
    #start_result = myriad_host.send("AUDIOWALL CUE 1,{0}".format(start_cart))
    start_result = os.path.exists(os.path.join(
        parsed_args.media_dir, "1000s", f"MYR{start_cart:0>5}.wav"))

    if start_result:  # Cart exists, move on
        start_cart += 1
    else:  # Cart does not exist here, try the next carts
        for i in range(1, len(audio_files)):
            test_cart = start_cart+i
            # range_result = myriad_host.send(
            #     "AUDIOWALL CUE 1,{0}".format(start_cart + i))
            range_result = os.path.exists(os.path.join(
                parsed_args.media_dir, "1000s", f"MYR{test_cart:0>5}.wav"))
            # print(os.path.join(
            #     "C:\\PSquared\\Audiowall\\1000s", f"MYR{test_cart:0>5}.wav"))
            # print(range_result)
            if range_result:
                start_cart += i+1
                break

            # print(i)
            if test_cart == start_cart+len(audio_files)-1:
                cart_range_found = True

# Clear the cart we were using for testing
#myriad_host.send("AUDIOWALL EJECT 1")

# Quit if no carts available
if cart_range_found:
    print("Found carts: {0}-{1}".format(start_cart,
                                        start_cart+len(converted_audio_files)-1))
else:
    print("No carts available between 1500 and 1600!")
    exit(3)

# Import audio onto audiowall
print("Importing audio to AudioWall...")

for i in range(0, len(audio_files)):
    print(
        f"Importing {os.path.basename(converted_audio_files[i])} to cart {start_cart + i}")

    #myriad_import_cmd = f"AUDIOWALL IMPORTFILE \"{converted_audio_files[i]}\",{start_cart + i}"
    myriad_args = MYRIAD_CL_ARGS.copy()
    myriad_args.extend(
        ["/Action=ImportMediaFile", f"/MediaId={start_cart+i}", f"/Filename='{converted_audio_files[i]}'"])

    full_args = [MYRIAD_CL_PATH]
    full_args.extend(myriad_args)
    print(full_args)
    proc = run(full_args)
    if(proc.returncode):
        print("Failed to import cart! "+converted_audio_files[i])
        exit(4)

    # Delete the converted WAV file, if it's not the original
    # if os.path.basename(converted_audio_files[i]) != os.path.basename(audio_files[i]):
    #     myriad_import_cmd += ",DELETE"

    # And finally import the audio
    # if not myriad_host.send(myriad_import_cmd):
    #     print("Failed to import cart! "+converted_audio_files[i])
    #     exit(4)

    # Myriad crashes if it imports too much, too quickly
    # if(i != len(audio_files)-1):
    #     time.sleep(15)

# Create log file for hour
print("Creating Myriad Log entries...")
print(f"... show begins {datetime_start_psq}")
log_entry = []

for i in range(0, len(converted_audio_files), 2):
    # The format per hour should be:
    # HOUR START
    # NEWS
    # PRE-REC PART 1
    #
    # JINGLE
    # AD BREAK 1
    # JINGLE
    #
    # PRE-REC PART 2
    #
    # JINGLE
    # AD BREAK 2
    # ABSOLUTE TIME: 59:45
    # NEWS IN JINGLE

    log_entry.extend([
        # Hour Start
        LogFileGenerator.createHourStart(datetime_start.replace(hour=int(
            datetime_start.strftime("%H"))+int(i/2)), f"{presenter_name}'s Pre-Record"),
        LogFileGenerator.createCmdSetAutoOn(0, 0),

        # News
        LogFileGenerator.createCart(
            15000, "RNH NEWS + JINGLE + AD", "RADIO NEWSHUB", 4, 2, 30),

        # Pre-rec part 1
        LogFileGenerator.createCart(
            start_cart+i, f"{presenter_name}'s Pre-Record Part {i+1}", presenter_name, 2, 28, 00),

        # Jingles and ad break 1
        LogFileGenerator.createLink(
            CartFinder.findStationIdent(), "Station Ident"),
        LogFileGenerator.createAdBreak(30),
        LogFileGenerator.createCart(
            CartFinder.findRNHAd(), "RNH Advert", "Radio Newshub", 2, 0, 30),
        LogFileGenerator.createLink(
            CartFinder.findStationIdent(), "Station Ident"),

        # Pre-rec part 2
        LogFileGenerator.createCart(
            start_cart+i+1, f"{presenter_name}'s Pre-Record Part {i+2}", presenter_name, 2, 28, 00),

        # Jingles and ad break 2
        LogFileGenerator.createLink(
            CartFinder.findStationIdent(), "Station Ident"),
        LogFileGenerator.createAdBreak(58),

        # End of hour + news
        LogFileGenerator.createAbsoluteTime(59, 45),
        LogFileGenerator.createCart(
            14997, "News In", "HCR News In", 3, 0, 16)
    ])
print(f"... show ends {datetime_end_psq}")

print("Writing log file...")
LogFileGenerator.writeLogFile(parsed_args.logs_dir, log_entry, true)

# The hour may already have been scheduled in advance, so remove it
#print("Attempting to remove the hour from the scheduled log...")
#myriad_host.send(f"LOG REMOVE RANGE,{datetime_start_psq},{datetime_end_psq}")
