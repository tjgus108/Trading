# Cycle 115 Result

## lob_maker Strategy Analysis (FAIL)

**Current Performance**:
- Return: +3.16% (was +8.92%)
- Sharpe: 0.97 (was 2.27)
- PF: 1.17 (was 1.36, need ≥1.5)
- MDD: 8.1% (≤20% ✓)
- Trades: 41 (≥30 ✓)

**Verdict**: FAIL (PF 1.17 < 1.5 required minimum)

## Root Cause
Threshold tightening (OFI 0.36→0.38, VPIN 0.42→0.43, vol 1.25→1.30) reduced trade count without improving win rate or PF. Signal selectivity alone insufficient.

## Why This Strategy Won't Pass
1. **Fundamental architecture issue**: OFI proxy (close-open)/HL range is too noisy on synthetic data
2. **VPIN calculation**: Works better with real order flow depth; insufficient granularity on simulated data
3. **Strategy vs market regime mismatch**: Random walk generation doesn't favor OFI patterns

## Recommendation
**Deprecate lob_maker from consideration**. Current approach unreliable. Focus efforts on Top 10 performers (all PASS except narrow_range/dema_cross which fail on trade count).

## Next Steps
1. Monitor Top 10 strategies for live deployment
2. Archive lob_maker (future R&D: requires real LOB data)
3. Consider replacing with proven order_flow_imbalance_v2 variant
