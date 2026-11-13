"""Predict the time to a volcano's next eruption from seismic segments."""

from ingv_eruption.features import FEATURE_COLUMNS, build_feature_table
from ingv_eruption.model import DEFAULT_PARAMS, predict, train_model

__all__ = ['build_feature_table', 'train_model', 'predict',
           'FEATURE_COLUMNS', 'DEFAULT_PARAMS']
