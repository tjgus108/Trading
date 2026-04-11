#!/usr/bin/env python3
import csv
import statistics

csv_path = '/home/user/Trading/.claude-state/QUALITY_AUDIT.csv'

strategies = []
with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        strategies.append({
            'name': row['name'],
            'sharpe': float(row['sharpe']),
            'win_rate': float(row['win_rate']),
            'profit_factor': float(row['profit_factor']),
            'max_dd': float(row['max_dd']),
            'trades': int(row['trades']),
            'total_return': float(row['total_return']),
            'passed': row['passed'] == 'True'
        })

# Summary stats
passed_count = sum(1 for s in strategies if s['passed'])
failed_count = len(strategies) - passed_count
avg_sharpe = statistics.mean(s['sharpe'] for s in strategies)
avg_win_rate = statistics.mean(s['win_rate'] for s in strategies)
avg_profit_factor = statistics.mean(s['profit_factor'] for s in strategies)
avg_max_dd = statistics.mean(s['max_dd'] for s in strategies)

# Top 5 by Sharpe
top_5 = sorted(strategies, key=lambda x: x['sharpe'], reverse=True)[:5]

print("=" * 60)
print("QUALITY AUDIT SUMMARY")
print("=" * 60)
print(f"\nTotal Strategies: {len(strategies)}")
print(f"Passed: {passed_count} | Failed: {failed_count}")
print(f"Pass Rate: {100*passed_count/len(strategies):.1f}%")
print(f"\nAverage Metrics:")
print(f"  Sharpe Ratio: {avg_sharpe:.3f}")
print(f"  Win Rate: {100*avg_win_rate:.1f}%")
print(f"  Profit Factor: {avg_profit_factor:.3f}")
print(f"  Max Drawdown: {100*avg_max_dd:.1f}%")
print(f"\nTop 5 Strategies (by Sharpe):")
for i, s in enumerate(top_5, 1):
    status = "✓" if s['passed'] else "✗"
    print(f"{i}. {s['name']:30} {s['sharpe']:6.3f} {status}")
print("=" * 60)
