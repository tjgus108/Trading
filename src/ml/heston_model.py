"""
F2. HestonVolatilityModel: Heston 확률 변동성 파라미터 추정.

Heston 모델 파라미터:
  - kappa: 평균 회귀 속도
  - theta: 장기 변동성 (분산)
  - sigma: 변동성의 변동성 (vol-of-vol)
  - rho: 가격-변동성 상관관계
  - v0: 현재 분산

외부 의존성 없는 순수 numpy 구현:
  - Realized variance: (log return)^2 rolling 20
  - kappa: mean-reversion 속도 (AR(1) 계수 역수)
  - theta: rolling var의 장기 평균
  - sigma: rolling var의 표준편차
  - rho: log_return과 d(variance)의 상관계수
  - v0: 최근 realized variance
"""

import numpy as np
import pandas as pd

_DEFAULT_PARAMS = {
    "kappa": 1.0,
    "theta": 0.04,
    "sigma": 0.2,
    "rho": -0.5,
    "v0": 0.04,
}


class HestonVolatilityModel:
    def __init__(self, window: int = 20):
        self.window = window

    def estimate(self, df: pd.DataFrame) -> dict:
        """
        OHLCV df → Heston 파라미터 dict
        keys: kappa, theta, sigma, rho, v0
        데이터 부족 시 기본값 반환
        """
        if len(df) < self.window + 2:
            return dict(_DEFAULT_PARAMS)

        close = df["close"].values
        log_ret = np.log(close[1:] / close[:-1])

        # Realized variance: (log return)^2 rolling window
        sq_ret = log_ret ** 2
        if len(sq_ret) < self.window:
            return dict(_DEFAULT_PARAMS)

        # Rolling realized variance using the last `window` values
        n = len(sq_ret)
        rv_list = []
        for i in range(self.window - 1, n):
            rv_list.append(np.mean(sq_ret[i - self.window + 1: i + 1]))
        rv = np.array(rv_list)

        if len(rv) < 2:
            return dict(_DEFAULT_PARAMS)

        # v0: most recent realized variance
        v0 = float(max(rv[-1], 0.0))

        # theta: long-run mean of realized variance
        theta = float(np.mean(rv))

        # sigma: vol-of-vol = std of realized variance
        sigma = float(np.std(rv))
        if sigma < 1e-10:
            sigma = 1e-4

        # kappa: mean-reversion speed via AR(1)
        # v_{t+1} - theta ≈ (1 - kappa*dt) * (v_t - theta) → AR coef = 1 - kappa
        v_demeaned = rv - theta
        if len(v_demeaned) >= 2 and np.std(v_demeaned[:-1]) > 1e-12:
            ar_coef = float(np.corrcoef(v_demeaned[:-1], v_demeaned[1:])[0, 1])
            ar_coef = np.clip(ar_coef, -0.9999, 0.9999)
            kappa = float(max(1.0 - ar_coef, 1e-4))
        else:
            kappa = 1.0

        # rho: correlation between log_return and change in realized variance
        # align lengths: rv corresponds to windows ending at indices window-1..n-1
        # log_ret indices 0..n-1; take log_ret from index window-1 onward
        ret_aligned = log_ret[self.window - 1:]
        dv = np.diff(rv)  # length = len(rv) - 1
        ret_for_rho = ret_aligned[:len(dv)]
        if len(ret_for_rho) >= 2 and np.std(ret_for_rho) > 1e-12 and np.std(dv) > 1e-12:
            rho = float(np.corrcoef(ret_for_rho, dv)[0, 1])
            rho = float(np.clip(rho, -0.9999, 0.9999))
        else:
            rho = -0.5

        return {
            "kappa": kappa,
            "theta": theta,
            "sigma": sigma,
            "rho": rho,
            "v0": v0,
        }

    def build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Heston 파라미터를 rolling window로 계산 → DataFrame 반환
        columns: heston_kappa, heston_theta, heston_sigma, heston_rho, heston_v0
        len(result) == len(df) (NaN 허용)
        """
        cols = ["heston_kappa", "heston_theta", "heston_sigma", "heston_rho", "heston_v0"]
        result = pd.DataFrame(index=df.index, columns=cols, dtype=float)

        min_rows = self.window + 2
        for i in range(len(df)):
            if i + 1 < min_rows:
                continue
            sub = df.iloc[: i + 1]
            params = self.estimate(sub)
            result.iloc[i] = [
                params["kappa"],
                params["theta"],
                params["sigma"],
                params["rho"],
                params["v0"],
            ]

        return result
