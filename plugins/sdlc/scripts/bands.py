"""Deterministic control-band detection for one metric. No model, no network.

Python 3.10+, standard library only. Baseline = every point except the last `window`;
mean and sample standard deviation. Western Electric rules run on the last `window`
points, higher is worse but both sides are detected.
"""
import argparse
import json
from pathlib import Path
import statistics
import sys

TIERS = {'rule1': 'propose', 'rule2': 'diagnose', 'rule3': 'diagnose', 'rule4': 'diagnose',
         '1sigma': 'log', 'insufficient-baseline': 'log', 'none': 'none'}


def side(value, mean, sigma, k):
    """+1 or -1 when value is beyond k sigma from the mean, else 0."""
    z = (value - mean) / sigma
    return (z > k) - (z < -k)


def rule_hit(recent, mean, sigma):
    last = recent[-1]
    if side(last, mean, sigma, 3):
        return 'rule1'
    for k, n, m, rule in ((2, 3, 2, 'rule2'), (1, 5, 4, 'rule3')):
        sides = [side(v, mean, sigma, k) for v in recent[-n:]]
        if any(sides.count(s) >= m for s in (1, -1)):
            return rule
    last8 = recent[-8:]
    if len(last8) == 8 and (all(v > mean for v in last8) or all(v < mean for v in last8)):
        return 'rule4'
    return '1sigma' if side(last, mean, sigma, 1) else 'none'


def evaluate(series, window, min_points):
    if not isinstance(series, list) or not series or not all(
            isinstance(v, (int, float)) and not isinstance(v, bool) for v in series):
        raise ValueError('Series must be a non-empty JSON array of numbers')
    if not isinstance(window, int) or window < 1 or window >= len(series) and len(series) >= min_points:
        raise ValueError('window must be a positive integer smaller than the series length')
    base = series[:-window]
    mean = statistics.fmean(base) if base else None
    sigma = statistics.stdev(base) if len(base) > 1 else 0
    out = {'mean': mean, 'sigma': sigma, 'last': series[-1]}
    if len(series) < min_points or not sigma:
        return {'rule': 'insufficient-baseline', 'tier': 'log', **out}
    rule = rule_hit(series[-window:], mean, sigma)
    return {'rule': rule, 'tier': TIERS[rule], **out}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--config', required=True)
    parser.add_argument('--series', required=True)
    args = parser.parse_args(argv)
    try:
        config = json.loads(Path(args.config).read_text())
        series = json.loads(Path(args.series).read_text())
        result = evaluate(series, config.get('window', 8), config.get('min_points', 20))
    except (OSError, json.JSONDecodeError) as error:
        print(f'BANDS: cannot read input: {error}', file=sys.stderr)
        return 1
    except ValueError as error:
        print(f'BANDS: {error}', file=sys.stderr)
        return 1
    action = config.get('tiers', {}).get(result['tier'], {})
    print(json.dumps({'metric': config.get('metric'), **result, 'action': action}, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
