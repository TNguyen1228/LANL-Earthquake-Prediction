# Volcanic Eruption Prediction (INGV)

Predict the time remaining until a volcano's next eruption from ten minutes of
seismic sensor readings, using frequency-band features and LightGBM.

> The repository is still named `LANL-Earthquake-Prediction`. Its code, report
> and slides have always been about the volcanic eruption problem below.

## Problem

Scientists often estimate "time to eruption" by surveying volcanic tremors in
seismic signals. In very active volcanoes, current approaches predict eruptions
some minutes in advance, but they usually fail at longer-term predictions.

Italy's Istituto Nazionale di Geofisica e Vulcanologia (INGV) monitors
seismicity and volcanic activity around the clock and looks for the earliest
detectable precursors of an eruption. In the Kaggle competition
[INGV - Volcanic Eruption Prediction](https://www.kaggle.com/c/predict-volcanic-eruptions-ingv-oe)
the task is to predict when a volcano's next eruption will occur from data
collected by sensors deployed on active volcanoes.

## Data

The data set is not part of this repository; it is available on Kaggle as
`predict-volcanic-eruptions-ingv-oe`.

- `train.csv`: `segment_id` and `time_to_eruption` for 4431 training segments.
- `sample_submission.csv`: the 4520 test segments to predict.
- `train/<segment_id>.csv`, `test/<segment_id>.csv`: one segment each, ten
  minutes of readings from ten sensors (`sensor_1` … `sensor_10`).

The domain terms used in the code are defined in [GLOSSARY.md](GLOSSARY.md).

## Approach

For each sensor of a segment, the short-time Fourier transform is thresholded
at its mean magnitude. The surviving magnitude and the number of surviving
cells are summed inside five volcanic frequency bands (A, BH, BL, C, D), giving
10 features per sensor and 100 per segment. A LightGBM regressor is trained on
these features with a random 80/20 split and early stopping.

## Repository layout

| Path | Contents |
| --- | --- |
| `src/ingv_eruption/` | The package: `build_feature_table`, `train_model`, `predict` |
| `tests/` | Tests on synthetic segments; no Kaggle data needed |
| `tests/reference/features_2023.csv` | Feature rows displayed by the 2023 run, for checking a new run |
| `notebooks/predict-volcano-eruption.ipynb` | Notebook that calls the package and draws the charts |
| `report/` | The original 2023 notebook, its printed PDF and the slides |

## Running

On Kaggle: add the competition data to a notebook, switch Internet on, upload
`notebooks/predict-volcano-eruption.ipynb` and run it. Its first cell clones
this repository and installs the package.

Locally, with the data set unpacked into `notebooks/predict-volcanic-eruptions-ingv-oe/`:

```bash
pip install -e ".[notebook]"
```

Then set `KAGGLE = False` in the notebook's first cell.

Tests:

```bash
pip install -e ".[test]"
pytest
```

## Recorded results

Both runs were made on Kaggle in December 2023. Errors are root mean squared
errors in the unit of `time_to_eruption` (1/100 s).

| Run | Parameters | Best iteration | Training error | Validation error |
| --- | --- | --- | --- | --- |
| `report/ingv-volcanic-basic-solution.ipynb` | depth 14, min leaf 5, 127 leaves, rate 0.05, L1 80 | 764 | 107,377 | 3,529,360 |
| `report/Notebook_….pdf` | depth 15, min leaf 6, 128 leaves, rate 0.025, L1 75 | 1214 | 69,869.6 | 3,442,370 |

The parameters of the second run are the package defaults. The gap between
training and validation error shows the model overfits.

## Status of the package

The package is a move of the 2023 notebook code into importable functions for
current library versions (NumPy 2, LightGBM 4). The feature computation is
unchanged, with one exception: segments are no longer truncated to the length
of a previously plotted sample segment, which has no effect when all segments
have the same length.

The package has only been run on synthetic segments so far. The notebook
compares its features with `tests/reference/features_2023.csv` when run on the
real data.

Known oddities kept as they were:

- Band C is computed from 0.6 Hz, while its definition starts at 0.5 Hz. At the
  default frequency resolution the band is a single bin.
- The feature columns and the columns dropped before training are chosen in
  separate places.

## Credits

The 2023 notebook started from the public Kaggle notebook
[INGV Volcanic : Basic_solution (STFT)](https://www.kaggle.com/amanooo/ingv-volcanic-basic-solution-stft)
by amanooo, which provides the frequency-band features and the modelling
steps. The changes made here are the title and the LightGBM parameters.
