#!/usr/bin/env python3

# This file is part of the MIDAS Workshop
# Jari Torniainen <jari.torniainen@ttl.fi>
# Copyright 2015 Finnish Institute of Occupational Health

import sys
import inspect

from midas.node import BaseNode
import midas.utilities as mu

import scipy
import scipy.signal
import ECGUtilities

import numpy as np


class ECGNode(BaseNode):

    def __init__(self, *args):
        super().__init__(*args)

        # Generate dict for metric descriptions and function pointers
        # these are saved to metric_list and metric_functions dicts
        self.metric_functions = [
            i[1] for i in inspect.getmembers(
                ECGUtilities,
                inspect.isfunction)]

        self.metric_functions.append(self.get_bpm)
        self.process_list.append(self.online_ibi)

    def median_bpm(self, x):
        """ Metric function for calculating median BPM from the IBI-vector. """
        median_ibi = np.median(x['data'][0])
        bpm = 60.0 / (median_ibi * 1e-3)
        return bpm

    # -------------------------------------------------------------------------
    # Online R-peak detection process
    # -------------------------------------------------------------------------
    def online_ibi(self):
        """ Process incoming ECG data: identify R-peaks, calculate the interbeat
            intervals (IBIs) and store these and their times of occurrence in
            arrays shared between the processes.

        Args:
            in_ch: <integer> input channel
            iyt_ch: <integer> output channel
            run_state: <integer> boolean "poison pill" to signal
                        termination to the process

        Returns:
             Nothing. The function only identifies R peaks and stores them in
             the specified secondary data channel.
        """

        print("starting the online ibi detection alg")

        # Set ECG-channel (if there are multiple channels like acc.meters etc)
        in_ch = 0
        out_ch = 0
        # ------------------------------------------------------------
        # Design Filters
        # The energy in the QRS complex is in the range 5 ... 15 Hz
        # ------------------------------------------------------------

        # ------------------------------
        # (1) FIR filter
        # ------------------------------
        lowcut = 2.5
        numtaps = 31
        window = "hamming"

        # band-pass filter for enhancing the QRS complex
        # (as used in the Pan-Tompkins algorithm)
        # taps = signal.firwin(numtaps, [lowcut, highcut], nyq = fs/2,
        #                   pass_zero = False, window = window, scale = False)

        # high-pass filter to remove baseline wander
        b = scipy.signal.firwin(numtaps, lowcut,
                                nyq=self.sampling_rate / 2,
                                pass_zero=False, window=window,
                                scale=False)
        # initial conditions
        zi = scipy.signal.lfiltic(b, 1.0, [0])

        # ------------------------------------------------------------
        # Set up buffers and state variables
        # ------------------------------------------------------------
        buffer_size = 1 * self.sampling_rate
        buffer_size_adap = 3 * self.sampling_rate

        buffer = scipy.zeros(buffer_size)
        buffer_adap = scipy.zeros(buffer_size_adap)

        inside_r = False  # are we "inside" an R-peak
        rr = 0      # the number of samples between two R-peaks
        r_ind_last = 0
        counter_sample = 1      # sample counter

        ind_read = 50  # read at the 50th value to compensate for filtering

        # ------------------------------------------------------------
        # Adaptation phase to determine threshold for peak detection
        # ------------------------------------------------------------
        print('Adaptation started')
        i = 0
        while i < buffer_size_adap:
            buffer_adap[i] = self.get_sample()[in_ch]
            i += 1
        print('\tDone')

        buffer_adap = scipy.signal.filtfilt(b, [1.0], buffer_adap)
        thr = 0.75 * max(buffer_adap)
        thr_max = thr
        vec_thr = [thr] * 5
        thr_max_ind = 0

        print('threshold:%0.2f' % (thr))

        time_tot = 0

        # ------------------------------------------------------------
        # Read data samples and detect R-peaks
        # ------------------------------------------------------------
        while self.run_state.value:
            # read data into the buffer
            smp, zi = scipy.signal.lfilter(b, 1.0, [self.get_sample()[in_ch]],
                                           zi=zi)
            buffer = scipy.concatenate((buffer[1:], smp))

            # RR state-machine
            if (buffer[ind_read] >= thr):
                if not inside_r:
                    inside_r = True
                else:
                    if buffer[ind_read] > thr_max:
                        thr_max = buffer[ind_read]
                        thr_max_ind = counter_sample
            else:
                if inside_r:
                    rr = thr_max_ind - r_ind_last
                    r_ind_last = thr_max_ind
                    inside_r = False
                    vec_thr = vec_thr[1:] + [thr_max]
                    thr = 0.75 * scipy.mean(vec_thr)
                    thr_max = thr

                    # add the detected IBI to the IBI secondary channel
                    rr_tmp = 1000 * (rr / self.sampling_rate)
                    self.push_sample_secondary(out_ch, time_tot, rr_tmp)
                    # print(rr_tmp)
                    time_tot += (rr_tmp / 1000)
                    rr = 0

            # update counters
            counter_sample += 1
            rr += 1

# -----------------------------------------------------------------------------
# Run the node if started from the command line
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    node = mu.midas_parse_config(ECGNode, sys.argv)

    if node is not None:
        node.start()
        node.show_ui()
# -----------------------------------------------------------------------------
# EOF
# -----------------------------------------------------------------------------
