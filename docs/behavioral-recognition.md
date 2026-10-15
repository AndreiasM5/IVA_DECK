# Behavioral recognition

[← Overview](../README.md)

The original thesis reports five participants and approximately 70% recognition in its experiment. This result has not been independently reproduced during this documentation update.

[`recunoastere_comportament.py`](../SOFTWARE/APP/v4/recunoastere_comportament.py) parses timestamped UART logs, builds features per key event, labels them, and trains a `RandomForestClassifier` with **50 trees** and `random_state=42`.

| Input feature | Meaning |
| --- | --- |
| `key` | Device key value |
| `delta` | Seconds since previous key event |
| `distance` | Latest observed proximity |
| `vol_value` | Latest observed volume value |

`vol_key` is recorded but is not a classifier input. Prediction aggregates the last **20 actions** by majority vote.

```text
[2025-06-01 12:00:00.000] UART: {'type': 'key', 'key': 'pressed', 'value': '49'}
```

## Local workflow

From the repository root, with `.venv` created:

```powershell
.\.venv\Scripts\python.exe -m pip install -r SOFTWARE/APP/v4/requirements-ai.txt
cd SOFTWARE/APP/v4
..\..\..\.venv\Scripts\python.exe recunoastere_comportament.py label my_session_log.txt USER_A
..\..\..\.venv\Scripts\python.exe recunoastere_comportament.py train labeled.csv
..\..\..\.venv\Scripts\python.exe recunoastere_comportament.py predict another_session_log.txt
```

Collect separate labeled sessions per participant. `label` appends to `labeled.csv` beside the script; `train` writes `ai_rf_model.pkl` there. Keep new participant data local.

The GUI's `ai_labeled_data.csv` has a different schema (`timestamp,tasta,user`) and cannot directly replace this four-feature labeled table.

## Evaluation limits

- `stats`, `acc`, and `dist` use the saved model on the supplied table. A training table gives in-sample results.
- `splitstats` fits a separate model on a stratified random 80/20 split and does not save it to the normal model file.
- Neighboring events from one session may appear in both halves of a row split. Use session-separated evaluation for stronger claims.
- `disttest` gives predicted-class frequencies, which are not automatically classification accuracy.
- This is an experimental classifier, not validated biometric authentication.

The archived `.pkl` has no pinned historical environment. Prefer retraining and load pickle/joblib artifacts only from trusted sources.
