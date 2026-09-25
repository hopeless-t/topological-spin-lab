# EXP004-C02 — GitHub Actions evidence-check correction

**STATUS:** CORRECTIVE CHECKPOINT / NO SCIENTIFIC CHANGE

The first public Actions run of `exp004-contract-research` reached the hosted
runner successfully but failed the evidence comparison.

Root cause:

```text
scientific / Monte Carlo values: unchanged
comparison method: too strict
```

The checker compared raw JSON text while the generator emits canonical
`sort_keys=True` text and the committed evidence used a different harmless key
order.

Correction:

- parse the committed JSON;
- compare the JSON object against a freshly recomputed result;
- keep all seed, priors, trial count, and winner shares unchanged.

This is a reproducibility-harness bug, not a physics or Monte Carlo failure.
