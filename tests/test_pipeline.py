"""Tests through the three public operations, on synthetic segments."""

import numpy as np
import pandas as pd
import pytest

from ingv_eruption import (DEFAULT_PARAMS, FEATURE_COLUMNS, build_feature_table,
                           predict, train_model)

SAMPLING_RATE = 100
SEGMENT_SAMPLES = 6000      # one minute; real segments are ten minutes


def write_segment(data_dir, split, segment_id, signals):
    """Write a segment CSV with one column per sensor."""
    folder = data_dir / split
    folder.mkdir(exist_ok=True)
    columns = {f'sensor_{i + 1}': signal for i, signal in enumerate(signals)}
    pd.DataFrame(columns).to_csv(folder / f'{segment_id}.csv', index=False)


def sine(frequency_hz):
    t = np.arange(SEGMENT_SAMPLES) / SAMPLING_RATE
    return 1000 * np.sin(2 * np.pi * frequency_hz * t)


def noise(seed):
    return np.random.default_rng(seed).normal(0, 300, SEGMENT_SAMPLES)


def test_feature_table_has_one_row_per_segment_and_the_original_columns(tmp_path):
    for segment_id in (11, 22, 33):
        write_segment(tmp_path, 'train', segment_id, [noise(segment_id + i) for i in range(10)])

    table = build_feature_table(tmp_path, 'train', [11, 22, 33], progress=False)

    assert table['segment_id'].tolist() == [11, 22, 33]
    assert table.columns.tolist() == ['segment_id'] + FEATURE_COLUMNS
    assert len(FEATURE_COLUMNS) == 100
    assert FEATURE_COLUMNS[:3] == ['s1_A_pow', 's1_A_num', 's1_BH_pow']
    assert FEATURE_COLUMNS[-1] == 's10_D_num'
    assert table[FEATURE_COLUMNS].notna().all().all()


@pytest.mark.parametrize('frequency_hz, band', [(12, 'A'), (6, 'BH'), (3, 'D'), (0.78, 'C')])
def test_a_pure_tone_puts_its_energy_in_the_band_that_contains_it(tmp_path, frequency_hz, band):
    # Band C is a single frequency bin (0.78 Hz) at the default resolution of 0.39 Hz.
    write_segment(tmp_path, 'train', 1, [sine(frequency_hz)] + [noise(i) for i in range(9)])

    row = build_feature_table(tmp_path, 'train', [1], progress=False).iloc[0]

    power = {b: row[f's1_{b}_pow'] for b in ('A', 'BH', 'BL', 'C', 'D')}
    assert max(power, key=power.get) == band
    assert power[band] > 10 * sum(v for b, v in power.items() if b != band)


def test_a_sensor_with_too_many_missing_samples_yields_only_missing_features(tmp_path):
    mostly_missing = noise(0)
    mostly_missing[:1001] = np.nan
    few_missing = noise(1)
    few_missing[:1000] = np.nan
    write_segment(tmp_path, 'test', 7, [mostly_missing, few_missing] + [noise(i) for i in range(2, 10)])

    row = build_feature_table(tmp_path, 'test', [7], progress=False).iloc[0]

    sensor_1 = [c for c in FEATURE_COLUMNS if c.startswith('s1_')]
    sensor_2 = [c for c in FEATURE_COLUMNS if c.startswith('s2_')]
    assert len(sensor_1) == 10
    assert row[sensor_1].isna().all()
    assert row[sensor_2].notna().all()


def test_train_then_predict_returns_one_time_to_eruption_per_segment():
    rng = np.random.default_rng(0)
    table = pd.DataFrame(rng.normal(size=(300, 100)), columns=FEATURE_COLUMNS)
    table.insert(0, 'segment_id', np.arange(300))
    target = 1e7 + 1e6 * table['s1_A_pow'] + rng.normal(0, 1e4, 300)
    X, y = table[FEATURE_COLUMNS], target
    params = {**DEFAULT_PARAMS, 'num_iterations': 50, 'verbose': -1}

    model = train_model(X[:240], y[:240], X[240:], y[240:], params, early_stopping_rounds=10)
    result = predict(model, table[240:])

    assert result.columns.tolist() == ['segment_id', 'time_to_eruption']
    assert result['segment_id'].tolist() == list(range(240, 300))
    assert np.corrcoef(result['time_to_eruption'], y[240:])[0, 1] > 0.5
