print('importing...')
import pyaudio
import numpy as np
from threading import Lock
import random
from time import sleep
import wave
try:
    from interactive import listen, inputChin
    from streamProfiler import StreamProfiler
    from selectAudioDevice import selectAudioDevice
    from jdt import Jdt
except ImportError as e:
    module_name = str(e).split('No module named ', 1)[1].strip().strip('"\'')
    print(f'Missing module {module_name}. Please download at')
    print(f'https://github.com/Daniel-Chin/Python_Lib/blob/master/{module_name}.py')
    input('Press Enter to quit...')
    raise e

print('Preparing...')
PAGE_LEN = 512
SR = 22050
BUFFER_N_PAGES = round(3.8 * SR / PAGE_LEN)
WRITE_FILE = f'demo_{random.randint(0, 99999)}.wav'
# WRITE_FILE = None
DO_PROFILE = False

MASTER_VOLUME = .1
DTYPE_BUF = (np.float32, pyaudio.paFloat32)
DTYPE_IO = (np.int32, pyaudio.paInt32)
FADE_IN = np.linspace(0, 1, PAGE_LEN, dtype=DTYPE_BUF[0])

streamOutContainer = []
terminate_flag = 0
terminateLock = Lock()
profiler = StreamProfiler(PAGE_LEN / SR, DO_PROFILE)

buffer = [
    np.zeros((PAGE_LEN, ), dtype=DTYPE_BUF[0]) 
    for _ in range(BUFFER_N_PAGES)
]
cursor = 0
epoch = 1
j = Jdt(BUFFER_N_PAGES)
first = True

if DO_PROFILE:
    _print = print
    def print(*a, **k):
        _print()
        _print(*a, **k)

def main():
    global terminate_flag, f
    print('Press ESC to quit. ')
    terminateLock.acquire()
    pa = pyaudio.PyAudio()
    in_i, out_i = selectAudioDevice(pa)
    streamOutContainer.append(pa.open(
        format = DTYPE_IO[1], channels = 1, rate = SR, 
        output = True, frames_per_buffer = PAGE_LEN,
        output_device_index = out_i, 
    ))
    if WRITE_FILE is not None:
        f = wave.open(WRITE_FILE, 'wb')
        f.setnchannels(1)
        f.setsampwidth(4)
        f.setframerate(SR)
    streamIn = pa.open(
        format = DTYPE_IO[1], channels = 1, rate = SR, 
        input = True, frames_per_buffer = PAGE_LEN,
        stream_callback = onAudioIn, 
        input_device_index = in_i, 
    )
    streamIn.start_stream()
    try:
        while streamIn.is_active():
            op = listen(b'\x1b', 1, priorize_esc_or_arrow=True)
            if op == b'\x1b':
                print('Esc received. Shutting down. ')
                break
    except KeyboardInterrupt:
        print('Ctrl+C received. Shutting down. ')
    finally:
        print('Releasing resources... ')
        terminate_flag = 1
        terminateLock.acquire()
        terminateLock.release()
        streamOutContainer[0].stop_stream()
        streamOutContainer[0].close()
        if WRITE_FILE is not None:
            f.close()
        while streamIn.is_active():
            sleep(.1)   # not perfect
        streamIn.stop_stream()
        streamIn.close()
        pa.terminate()
        print('Resources released. ')

def onAudioIn(in_data, sample_count, *_):
    global terminate_flag, f, cursor, epoch, first
    try:
        if terminate_flag == 1:
            terminate_flag = 2
            terminateLock.release()
            print('PA handler terminating. ')
            # Sadly, there is no way to notify main thread after returning. 
            return (None, pyaudio.paComplete)

        if sample_count > PAGE_LEN:
            print('Discarding audio page!')
            in_data = in_data[-PAGE_LEN:]

        profiler.gonna('read')
        page = np.frombuffer(
            in_data, dtype = DTYPE_IO[0]
        )

        profiler.gonna('mix')
        if first:
            first = False
            page = page * FADE_IN
        buffer[cursor] += page
        # buffer[cursor] = buffer[cursor] * .8 + page * .2

        profiler.gonna('norm')
        normalized = buffer[cursor] / epoch
        # normalized = buffer[cursor] / epoch ** 0.5  # THIS IS WRONG. LINEAR IS CORRECT
        # normalized = buffer[cursor]

        normalized = np.rint(normalized).astype(DTYPE_IO[0])

        profiler.gonna('write')
        streamOutContainer[0].write(
            normalized, PAGE_LEN, 
        )
        if WRITE_FILE is not None:
            f.writeframes(normalized)
        
        profiler.gonna('acc')
        cursor += 1
        if cursor == BUFFER_N_PAGES:
            cursor = 0
            epoch += 1

        profiler.gonna('vis')
        j.update(cursor)

        profiler.display(same_line=True)
        profiler.gonna('idle')
        return (None, pyaudio.paContinue)
    except:
        terminateLock.release()
        import traceback
        traceback.print_exc()
        return (None, pyaudio.paAbort)

main()
