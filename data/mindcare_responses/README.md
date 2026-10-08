# MindCare 50K Response Dataset

Verified requirements:
- 50,000 unique normalized messages
- 10,000+ varied response texts
- 20 balanced intents, 2,500 each
- 40,000 train / 5,000 validation / 5,000 test
- English + Hinglish
- zero normalized message duplicates
- zero cross-split message leakage
- explicit greeting examples including hi/hii/hello/hey
- natural distress, loneliness, uncertainty, sleep, study and work messages
- high-risk examples are kept in a dedicated intent and use safety-oriented responses
- columns compatible with the existing MindCare response-model trainer

Files:
- `mindcare_50000_message_response.csv`: exactly message,response
- `train.csv`: 40,000 rows
- `validation.csv`: 5,000 rows
- `test.csv`: 5,000 rows
- `dataset_audit.json`

Train from the MindCare project root:

```bash
source .venv/bin/activate

cp -R models/response_model models/response_model_backup_before_50k_final

cp /path/to/mindcare_50000_final/train.csv data/mindcare_responses/train.csv
cp /path/to/mindcare_50000_final/validation.csv data/mindcare_responses/validation.csv
cp /path/to/mindcare_50000_final/test.csv data/mindcare_responses/test.csv

python scripts/train_response_model.py
```

Keep the existing deterministic safety routing authoritative. This dataset is synthetic training/development data, not a clinical dataset. Validate on separate human-written messages before deployment.
