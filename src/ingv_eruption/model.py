"""LightGBM model of time to eruption."""

import lightgbm as lgb
import pandas as pd

DEFAULT_PARAMS = {'objective': 'rmse',
                  'metric': 'rmse',
                  'max_depth': 15,
                  'min_data_in_leaf': 6,         # = min_child_samples
                  'num_leaves': 2**7,
                  'learning_rate': 0.025,
                  'feature_fraction': 0.7,      # = colsample_bytree
                  'bagging_fraction': 0.5,      # = subsample
                  'bagging_freq': 5,
                  'lambda_l1': 75,              # = reg_alpha
                  'num_iterations': 10000,      # = n_estimators
                  'seed': 42,
                  'verbose': 1
                  }


def train_model(X_train, y_train, X_val, y_val, params=None, *,
                early_stopping_rounds=200, log_period=100):
    """Train a booster on the training rows, early-stopped on the validation rows.

    ``params`` replaces ``DEFAULT_PARAMS`` entirely when given. The validation
    error is logged every ``log_period`` rounds; the returned booster predicts
    with its best iteration.
    """
    params = dict(DEFAULT_PARAMS if params is None else params)
    features = X_train.columns.tolist()

    lgb_train = lgb.Dataset(X_train, y_train, feature_name=features, categorical_feature=[])
    lgb_eval = lgb.Dataset(X_val, y_val, reference=lgb_train)

    evals_result = {}
    model = lgb.train(
        params,
        lgb_train,
        valid_sets=[lgb_train, lgb_eval],
        callbacks=[lgb.early_stopping(early_stopping_rounds),
                   lgb.log_evaluation(log_period),
                   lgb.record_evaluation(evals_result)])

    return model


def predict(model, feature_table):
    """Predict time to eruption for every row of a feature table.

    ``feature_table`` is what ``build_feature_table`` returns. The result has
    the submission layout: ``segment_id`` and ``time_to_eruption``.
    """
    preds = model.predict(feature_table.drop(['segment_id'], axis=1))
    return pd.DataFrame({'segment_id': feature_table['segment_id'].values,
                         'time_to_eruption': preds})
