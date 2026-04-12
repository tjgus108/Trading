"""
test_backtest_report.py

BacktestReport의 from_json 에러 처리 테스트.
"""

import pytest
import json
from src.backtest.report import BacktestReport


class TestBacktestReportFromJson:
    """from_json round-trip 및 에러 처리 테스트"""
    
    def test_from_json_invalid_json_syntax(self):
        """잘못된 JSON 문법: ValueError 발생"""
        invalid_json = '{"total_return": 0.05, "invalid syntax'
        with pytest.raises(ValueError, match="Invalid JSON"):
            BacktestReport.from_json(invalid_json)
    
    def test_from_json_not_dict(self):
        """JSON이 dict가 아닌 경우: ValueError 발생"""
        json_array = json.dumps([1, 2, 3])
        with pytest.raises(ValueError, match="Expected JSON object"):
            BacktestReport.from_json(json_array)
    
    def test_from_json_missing_field(self):
        """필수 필드 누락: ValueError 발생"""
        incomplete = json.dumps({"total_return": 0.05})
        with pytest.raises(ValueError, match="Missing or invalid fields"):
            BacktestReport.from_json(incomplete)
    
    def test_from_json_round_trip(self):
        """to_json -> from_json 왕복: 동일성 보장"""
        report = BacktestReport.from_trades(
            [{"pnl_pct": 0.01}, {"pnl_pct": -0.005}, {"pnl_pct": 0.02}],
            annualization=252
        )
        json_str = report.to_json()
        restored = BacktestReport.from_json(json_str)
        
        assert restored.total_return == report.total_return
        assert restored.sharpe_ratio == report.sharpe_ratio
        assert restored.total_trades == 3
    
    def test_from_json_inf_nan_handling(self):
        """inf/nan 직렬화 및 역직렬화"""
        d = {
            'total_return': 0.1, 'ann_return': 0.05, 'ann_volatility': 0.02,
            'sharpe_ratio': 1.5, 'sortino_ratio': 2.0, 'deflated_sharpe_ratio': 1.4,
            'calmar_ratio': float('inf'), 'recovery_factor': float('nan'),
            'max_drawdown': 0.1,
            'total_trades': 50, 'win_rate': 0.6, 'profit_factor': 2.0,
            'avg_win': 0.015, 'avg_loss': 0.01, 'win_loss_ratio': 1.5,
            'max_consecutive_losses': 3, 'annualization': 252
        }
        
        # 수동으로 JSON 생성 후 복원
        json_str = json.dumps(d, default=lambda x: "inf" if x == float('inf') else "nan")
        report = BacktestReport.from_json(json_str)
        
        assert report.calmar_ratio == float('inf')
        assert str(report.recovery_factor) == 'nan'

