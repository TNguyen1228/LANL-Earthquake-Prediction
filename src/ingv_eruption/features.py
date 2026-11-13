"""Frequency-band features of volcanic seismic segments.

Each segment is a ten-minute recording of ten sensors. For every sensor the
short-time Fourier transform is thresholded at its mean magnitude, and the
surviving magnitude ("pow") and the number of surviving cells ("num") are
summed inside five volcanic frequency bands (A, BH, BL, C, D).
"""

import os

import numpy as np
import pandas as pd
import scipy.signal
from tqdm.auto import tqdm

N_SENSORS = 10
MAX_MISSING_SAMPLES = 1000

BAND_FEATURES = ['A_pow', 'A_num', 'BH_pow', 'BH_num', 'BL_pow', 'BL_num',
                 'C_pow', 'C_num', 'D_pow', 'D_num']

FEATURE_COLUMNS = [f's{i + 1}_{j}' for i in range(N_SENSORS) for j in BAND_FEATURES]


def build_feature_table(data_dir, split, segment_ids, *, sampling_rate=100,
                        fft_segment_size=256, max_frequency=20, progress=True):
    """Build one row of band features per segment.

    Reads ``<data_dir>/<split>/<segment_id>.csv`` for every id in
    ``segment_ids`` (``split`` is ``'train'`` or ``'test'``) and returns a
    DataFrame with ``segment_id`` followed by ``FEATURE_COLUMNS``.

    A sensor with more than ``MAX_MISSING_SAMPLES`` missing samples yields
    NaN for all of its features; fewer missing samples are filled with 0.
    """
    fs = sampling_rate
    n = fft_segment_size
    max_f = max_frequency
    delta_f = fs / n

    feature_set = []
    for segment_id in tqdm(segment_ids, disable=not progress):
        segment_df = pd.read_csv(os.path.join(data_dir, f'{split}/{segment_id}.csv'))
        segment = [segment_id]
        for sensor in segment_df.columns:
            x = segment_df[sensor]
            if x.isna().sum() > MAX_MISSING_SAMPLES:
                segment += ([np.nan] * len(BAND_FEATURES))
                continue
            f, t, Z = scipy.signal.stft(x.fillna(0), fs=fs, window='hann', nperseg=n)
            f = f[:round(max_f / delta_f) + 1]
            Z = np.abs(Z[:round(max_f / delta_f) + 1]).T    # up to max_f, row:time, col:freq

            th = Z.mean() * 1
            Z_pow = Z.copy()
            Z_pow[Z < th] = 0
            Z_num = Z_pow.copy()
            Z_num[Z >= th] = 1

            Z_pow_sum = Z_pow.sum(axis=0)
            Z_num_sum = Z_num.sum(axis=0)

            A_pow = Z_pow_sum[round(10 / delta_f):].sum()
            A_num = Z_num_sum[round(10 / delta_f):].sum()
            BH_pow = Z_pow_sum[round(5 / delta_f):round(8 / delta_f)].sum()
            BH_num = Z_num_sum[round(5 / delta_f):round(8 / delta_f)].sum()
            BL_pow = Z_pow_sum[round(1.5 / delta_f):round(2.5 / delta_f)].sum()
            BL_num = Z_num_sum[round(1.5 / delta_f):round(2.5 / delta_f)].sum()
            C_pow = Z_pow_sum[round(0.6 / delta_f):round(1.2 / delta_f)].sum()
            C_num = Z_num_sum[round(0.6 / delta_f):round(1.2 / delta_f)].sum()
            D_pow = Z_pow_sum[round(2 / delta_f):round(4 / delta_f)].sum()
            D_num = Z_num_sum[round(2 / delta_f):round(4 / delta_f)].sum()
            segment += [A_pow, A_num, BH_pow, BH_num, BL_pow, BL_num, C_pow, C_num, D_pow, D_num]

        feature_set.append(segment)

    feature_df = pd.DataFrame(feature_set, columns=['segment_id'] + FEATURE_COLUMNS)
    feature_df['segment_id'] = feature_df['segment_id'].astype('int')
    return feature_df
