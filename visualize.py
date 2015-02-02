from lsltools.vis import Grapher
from midas.node import lsl


def visualize_ecg():
    stream_ptr = lsl.resolve_byprop('name', 'ecg_data')[0]
    if stream_ptr:
        g = Grapher(stream_ptr, 256 * 5, 'c')
    else:
        print("Stream not found!")

if __name__ == "__main__":
    visualize_ecg()
