from advanced_regression_mlops.modeling import make_advanced_pipeline, make_baselines


def test_advanced_pipeline_predicts(synthetic_training_set) -> None:
    X, y = synthetic_training_set
    pipeline = make_advanced_pipeline()
    pipeline.fit(X, y)
    preds = pipeline.predict(X.iloc[:3])
    assert len(preds) == 3


def test_baselines_are_trainable(synthetic_training_set) -> None:
    X, y = synthetic_training_set
    for baseline in make_baselines().values():
        baseline.fit(X, y)
        assert len(baseline.predict(X.iloc[:2])) == 2
