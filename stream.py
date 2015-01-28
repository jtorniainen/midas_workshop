import lsltools.sim as sim  # github.com/bwrc/lsltools


def stream_ecg():
    print("Streaming started...")

    # Start the ECG stream (with default parameters)
    ecg = sim.ECGData('/home/jtorniai/ecgsyn_c/ecgsyn', stream_name='ecg_data')
    ecg.start()

    # Simple UI to change the heart rate
    while True:
        try:
            val = int(input('ecg>'))
            print("***\nSetting average heart rate to %d\n***" % val)

            ecg.set_h(val)
            ecg.reset()

        except ValueError:
            print("Input not integer")


if __name__ == "__main__":
    stream_ecg()
