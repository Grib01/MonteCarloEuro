import numpy as np
from scipy.stats import norm
import pandas as pd
import time

# Paramètres de l'option
S0 = 100   # Prix initial
K = 105    # Strike
r = 0.05   # Taux sans risque
sigma = 0.2  # Volatilité
T = 0.25   # Maturité


def prix_bs(S0: float, K: float, r: float, sigma: float, T: float, option: str = 'call') -> float:
    """Calcul du prix exact via Black–Scholes"""
    d1 = (np.log(S0/K) + (r + 0.5*sigma**2)*T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    if option == 'call':
        return S0 * norm.cdf(d1) - K * np.exp(-r*T) * norm.cdf(d2)
    else:
        return K * np.exp(-r*T) * norm.cdf(-d2) - S0 * norm.cdf(-d1)


def mc_classique(n: int) -> dict:
    """Monte Carlo standard"""
    Z = np.random.randn(n)
    ST = S0 * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z)
    pay = np.maximum(ST - K, 0)
    Dpay = np.exp(-r*T) * pay
    mean = Dpay.mean()
    var = Dpay.var(ddof=1)
    se = np.sqrt(var / n)
    ic = 1.96 * se
    return {'prix': mean, 'se': se, 'ic_inf': mean-ic, 'ic_sup': mean+ic, 'var': var}


def mc_antithetique(n: int) -> dict:
    """Monte Carlo antithétique"""
    m = n // 2
    Z = np.random.randn(m)
    STp = S0 * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z)
    STm = S0 * np.exp((r - 0.5*sigma**2)*T - sigma*np.sqrt(T)*Z)
    payp = np.maximum(STp - K, 0)
    paym = np.maximum(STm - K, 0)
    avg_pay = 0.5 * (payp + paym)
    Dpay = np.exp(-r*T) * avg_pay
    mean = Dpay.mean()
    var = Dpay.var(ddof=1)
    se = np.sqrt(var / m)
    ic = 1.96 * se
    corr = np.corrcoef(payp, paym)[0,1]
    return {'prix': mean, 'se': se, 'ic_inf': mean-ic, 'ic_sup': mean+ic, 'var': var, 'corr': corr}


def mc_controle(n: int) -> dict:
    """Monte Carlo avec variable de contrôle"""
    Z = np.random.randn(n)
    ST = S0 * np.exp((r - 0.5*sigma**2)*T + sigma*np.sqrt(T)*Z)
    pay = np.maximum(ST - K, 0)
    Dpay = np.exp(-r*T) * pay
    mu = S0 * np.exp(r*T)
    cov = np.cov(Dpay, ST)
    b = cov[0,1] / cov[1,1]
    payc = Dpay - b * (ST - mu)
    mean = payc.mean()
    var = payc.var(ddof=1)
    se = np.sqrt(var / n)
    ic = 1.96 * se
    rho = cov[0,1] / np.sqrt(cov[0,0]*cov[1,1])
    return {'prix': mean, 'se': se, 'ic_inf': mean-ic, 'ic_sup': mean+ic, 'var': var, 'b': b, 'rho': rho}


def comparer(n: int = 100000) -> pd.DataFrame:
    """Compare Classique, Antithétique et Contrôle"""
    # prix de référence
    ref = prix_bs(S0, K, r, sigma, T)
    result = {}
    # Méthode classique
    t0 = time.perf_counter()
    c = mc_classique(n)
    t_mc = time.perf_counter() - t0
    result['MC Classique'] = {
        'Prix estimé': c['prix'],
        'Prix Black-Scholes': ref,
        'Erreur absolue': abs(c['prix'] - ref),
        'Erreur Std': c['se'],
        'Temps (s)': t_mc,
        'Efficacité relative': 1.0,
        'Corrélation': np.nan,
        'b*': np.nan
    }
    # Antithétique
    t0 = time.perf_counter()
    a = mc_antithetique(n)
    t_a = time.perf_counter() - t0
    t_a = max(t_a, 1e-12)
    eff_a = (c['var'] * t_mc) / (a['var'] * t_a)
    result['Antithétique'] = {
        'Prix estimé': a['prix'],
        'Prix Black-Scholes': ref,
        'Erreur absolue': abs(a['prix'] - ref),
        'Erreur Std': a['se'],
        'Temps (s)': t_a,
        'Efficacité relative': eff_a,
        'Corrélation': a['corr'],
        'b*': np.nan
    }
    # Contrôle
    t0 = time.perf_counter()
    v = mc_controle(n)
    t_v = time.perf_counter() - t0
    t_v = max(t_v, 1e-12)
    eff_v = (c['var'] * t_mc) / (v['var'] * t_v)
    result['Contrôle'] = {
        'Prix estimé': v['prix'],
        'Prix Black-Scholes': ref,
        'Erreur absolue': abs(v['prix'] - ref),
        'Erreur Std': v['se'],
        'Temps (s)': t_v,
        'Efficacité relative': eff_v,
        'Corrélation': np.nan,
        'b*': v['b']
    }
    # Black-Scholes exact
    result['Black-Scholes (exact)'] = {
        'Prix estimé': ref,
        'Prix Black-Scholes': ref,
        'Erreur absolue': 0.0,
        'Erreur Std': 0.0,
        'Temps (s)': 0.0,
        'Efficacité relative': float('inf'),
        'Corrélation': np.nan,
        'b*': np.nan
    }
    df = pd.DataFrame(result).T
    print("Comparaison des différentes méthodes de Monte Carlo")
    print("-"*70)
    return df.round(6)

if __name__ == '__main__':
    df = comparer()
    print(df)
