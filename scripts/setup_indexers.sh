 #!/bin/sh

. ./scripts/load_python_env.sh

./.venv/bin/python ./app/backend/setup/indexers/cosmos_indexer.py
./.venv/bin/python ./app/backend/setup/indexers/storage_account_indexer.py
