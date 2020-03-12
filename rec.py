#!/usr/bin/env python3

import os
import subprocess
from contextlib import ExitStack
from datetime import datetime


def get_sources():
    cmd = "pactl list | grep -A2 '^Source #' | grep 'Name: alsa.*' | awk '{print $NF}'"
    cmd_result = subprocess.check_output(cmd, shell=True).decode().strip()
    sources = cmd_result.split("\n")
    return sources


def record_audio(sources, result_file_names):
    assert len(sources) == len(result_file_names)
    cmd_template = "parec -d {source} | sox -t raw -r 44100 -e signed-integer -Lb 16 -c 2 - {result_file_name}"
    with ExitStack() as stack:
        for source, result_file_name in zip(sources, result_file_names):
            cmd = cmd_template.format(source=source, result_file_name=result_file_name)
            stack.enter_context(subprocess.Popen(cmd, shell=True))


def merge_audios(input_file_names, output_file_name):
    cmd = ["sox", "-m"] + input_file_names + [output_file_name]
    subprocess.check_call(cmd)


def rm_files(file_names):
    for file_name in file_names:
        os.unlink(file_name)


def main():
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    sources = get_sources()
    tmp_result_file_names = [
        f"record-{timestamp}-{source}.wav"
        for source in sources
    ]
    result_file_name = f"record-{timestamp}.ogg"

    try:
        print("Recording...")
        record_audio(sources, tmp_result_file_names)
    except KeyboardInterrupt:
        print("\nFinishing...")
        merge_audios(tmp_result_file_names, result_file_name)
        print(f"Result is written into {result_file_name}")
        rm_files(tmp_result_file_names)


if __name__ == "__main__":
    main()
