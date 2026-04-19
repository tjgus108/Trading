#!/bin/bash
# 3개 심볼 ML 모델 일괄 재학습 스크립트
# 사용법: bash scripts/retrain_all.sh [--triple-barrier]

PYTHON=python3.11
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EXTRA_ARGS="$@"

SYMBOLS=("BTC/USDT" "ETH/USDT" "SOL/USDT")
PASS=0
FAIL=0

echo "=== ML 일괄 재학습 시작 ($(date)) ==="
echo ""

for sym in "${SYMBOLS[@]}"; do
    echo "--- $sym ---"
    $PYTHON "$SCRIPT_DIR/train_ml.py" --bybit --binary --symbol "$sym" $EXTRA_ARGS 2>&1 | \
        grep -E "(train_accuracy|val_accuracy|test_accuracy|verdict|fail_reasons)"

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        ((PASS++))
    else
        ((FAIL++))
    fi
    echo ""
done

echo "=== 완료: PASS=$PASS FAIL=$FAIL ==="
