#!/usr/bin/env python3

import subprocess
from contextlib import ExitStack
from datetime import datetime

time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

cmd = "pactl list | grep -A2 '^Source #' | grep 'Name: alsa.*' | awk '{print $NF}'"
x = subprocess.check_output(cmd, shell=True)
sources = x.decode().strip().split('\n')

try:
    with ExitStack() as stack:
        cmd_template = "parec -d {source} | sox -t raw -r 44100 -e signed-integer -Lb 16 -c 2 - record-{time}-{source}.wav"
        processes = [
            stack.enter_context(subprocess.Popen(cmd_template.format(source=source, time=time), shell=True))
            for source in sources
        ]
        print('Recording...')
except KeyboardInterrupt:
    print('\nFinishing...')
    files = ' '.join(
        f'record-{time}-{source}.wav'
        for source in sources
    )
    out_file = f'record-{time}.ogg'
    cmd = f"sox -m {files} {out_file}"
    subprocess.check_call(cmd, shell=True)
    print(f'Result is written into {out_file}')
    subprocess.check_call(f"rm {files}", shell=True)

