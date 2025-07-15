# Pricing d'Options Européennes par Méthodes de Monte Carlo

## Vue d'ensemble du projet

Ce projet implémente différentes méthodes de Monte Carlo pour estimer le prix d'options européennes. J'utilise Black-Scholes pour fournir le prix exact qui sert de référence pour évaluer la précision de nos estimations.

## Ce qu'on cherche à calculer

**Objectif** : Estimer $p^G_0$, le prix d'une option européenne G 

**Formule théorique du prix** 

$$p^G_t = e^{-r(T-t)}\mathbb{E}^{Q^*} [G|F_t]$$


Où :
- r = taux sans risque
- T = maturité  
- Q* = mesure de probabilité neutre au risque
- G = $(S_T - K)^+$ le payoff d'un call
- G = $(K - S_T)^+$ le payoff d'un put

Le but étant de simuler à l'aide de méthode de Monte Carlo $$\delta:=e^{-rT}\mathbb{E}^{Q^*} [G]$$

## Méthode

### Étape 1 : Modélisation du prix de l'actif

Le prix $S_t$ de l'actif suis sous $\mathbb{P}$ l'EDS suivante:

$$dS_t = μS_t dt + σS_t dB_t$$

où $B_t$ est un mouvement brownien standard.


Sous la mesure risque-neutre Q* (d'après le théorème de Girsanov) :

$$dS_t = rS_t dt + σS_t dB^*_t$$


où 

$$B^*_t:=B_t+\frac{\mu - r}{\sigma}t$$

est un mouvement brownien sous Q*.

La solution de cette EDS étant:

$$S_t = S_0\exp{((r-\frac{σ^2}{2})t + σB^*_t)}$$


### Étape 2 : Estimation par méthodes de Monte Carlo

### Monte Carlo Classique

Puisqu'on ne peut pas calculer $$e^{-rT}E^{Q^*}[G]$$ analytiquement (sauf cas simples), on l'approxime par 

$$\hat{\delta}_n = e^{-rT}\frac{1}{n}\sum_{i=1}^n G(S_T^{(i)})$$


où $S_T^{(1)},...S_T^{(n)}$ sont n simulations indépendantes sous Q*.


**Algorithme** :
1. Pour $i = 1$ à $n$ :
   - Générer $Z_i$ ~ $\mathcal{N}(0,1)$
   - Calculer $S_T^{(i)} = S_0\exp{((r - \frac{\sigma^2}{2})T + σ\sqrt{T}  Zᵢ)}$
   - Calculer $G^{(i)} = (S_T^{(i)} - K)^+$

2. Estimer le prix :
$$
\hat{\delta}_n = e^{-rT} × \frac{1}{n}\sum_{i=1}^n G(S_T^{(i)})
$$

**Variance et intervalle de confiance** :
$$
\begin{align*}
\mathbb{V}(\hat{\delta}_n) &= e^{-2rT}\frac{\mathbb{V}(G)}{n}\\
\text{Erreur standard} &= \sqrt{\mathbb{V}(\hat{\delta}_n)}\\
\text{IC 95\%} &= \hat{\delta}_n ± 1.96 × \text{Erreur standard}
\end{align*}
$$

### Variables Antithétiques

**Principe** : Pour chaque $Z$, on utilise son antithétique $-Z$. Cela crée une corrélation négative.

**Algorithme** :
1. Pour $i = 1$ à $n/2$ :
   - Générer $Z_i$ ~ $\mathcal{N}(0,1)$
   - Calculer $S_T^+ = S_0\exp{((r - \frac{\sigma^2}{n})T + σ\sqrt{T}Z_i)}$
   - Calculer $S_T^- = S_0\exp{((r - \frac{\sigma^2}{n})T - σ\sqrt{T}Z_i)}$
   - $G^+_i = (S_T^+ - K)^+$
   - $G^-_i = (S_T^- - K)^+$
   - $G_{\text{moyen}}^{i}=\frac{G^+_i+G^-_i}{2}$

2. Estimer le prix :
$$
\hat{\delta}^A_n = e^{-rT} \frac{2}{n}\sum_{i=1}^{n/2} G_{\text{moyen}}^i
$$

**Réduction de variance**
$$
\mathbb{V}(G_{moyen}) = \frac{1}{2}[\mathbb{V}(G⁺) + \mathbb{V}(G⁻) + 2Cov(G⁺, G⁻)]
$$
Si $Cov(G⁺, G⁻) < 0$, alors $\mathbb{V}(p̂^{G^A}_0) < \mathbb{V}(p̂^G_0)$

### Variable de Contrôle

**Principe** : Utiliser $S_T$ comme variable de contrôle car $\mathbb{E}^{Q^*}[S_T] = S_0e^{rT}$ est connu.

utiliser directement $S_T$ comme variable de contrôle, car on connaît
$$
\mathbb{E}[S_T] = S_0 e^{rT} = m.
$$

On note pour chaque simulation :
- $S_T^{(i)}$ le prix simulé
- $G^{(i)} = (S_T^{(i)} - K)^+$ le payoff

On définit :
$$\begin{align*}
\bar{G}_n &= \frac{1}{n}\sum_{i=1}^n G^{(i)},\\
\bar{S}_n &= \frac{1}{n}\sum_{i=1}^n S_T^{(i)},\\
\end{align*}
$$

Le coefficient optimal s'écrit :
$$
b^* = \frac{\operatorname{Cov}(G,S_T)}{\operatorname{Var}(S_T)},
$$

calculé empiriquement sur l'échantillon. L'estimateur par variable de contrôle est alors :

$$
G^{\mathrm{ctrl},(i)} = G^{(i)} - b^* \bigl(S_T^{(i)} - m\bigr).
$$

Le prix estimé devient :
$$

\hat{\delta}^{ctrl}_n = e^{-rT} \cdot \frac{1}{n} \sum_{i=1}^n G^{\mathrm{ctrl},(i)}.

$$


