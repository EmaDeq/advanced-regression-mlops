# Dataset provenance and ethics

The canonical Boston Housing dataset is fetched from OpenML dataset **531**.
The original `sklearn.datasets.load_boston` helper was removed after the maintainers
highlighted severe ethical problems, including a racially constructed `B` variable.

For this educational project:

1. **Exclude `B` from model features and API schema** by default.
2. Keep the original dataset outside Git; downloaded to `data/raw/boston.csv`.
3. Don't interpret feature effects causally. Other socioeconomic/geographic predictors
   may still encode discriminatory patterns. Dropping `B` does not make the data fair.
4. Use the trained model for historical software-engineering demonstrations only,
   not for lending, pricing, actual housing decisions or policy.
5. Benchmark results are based on a tiny historical sample; do not generalize claims.

Alternative future exercise: California Housing, which is included in scikit-learn
as a supported regression benchmark (still requires documentation of limitations).
