import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PLUGIN = Path(__file__).resolve().parents[1] / 'plugins/sdlc'
SCRIPT = PLUGIN / 'scripts/bands.py'
spec = importlib.util.spec_from_file_location('bands', SCRIPT)
bands = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bands)

BASE = [9, 11] * 7  # mean 10, sample sigma ~1.04
QUIET = [9, 11, 9, 11, 9, 11, 9, 11]


def run(recent):
    return bands.evaluate(BASE + recent, 8, 20)


class BandsTests(unittest.TestCase):
    def test_spike(self):
        result = run(QUIET[:7] + [15])
        self.assertEqual((result['tier'], result['rule']), ('propose', 'rule1'))
        self.assertAlmostEqual(result['mean'], 10)

    def test_drift(self):
        result = run([10.5] * 8)
        self.assertEqual((result['tier'], result['rule']), ('diagnose', 'rule4'))

    def test_two_of_three_beyond_two_sigma(self):
        result = run([9, 11, 9, 11, 9, 12.5, 10, 12.5])
        self.assertEqual((result['tier'], result['rule']), ('diagnose', 'rule2'))

    def test_four_of_five_beyond_one_sigma(self):
        result = run([9, 11, 9, 11.5, 11.5, 11.5, 11.5, 9])
        self.assertEqual((result['tier'], result['rule']), ('diagnose', 'rule3'))

    def test_low_side_detected(self):
        self.assertEqual(run(QUIET[:7] + [5])['rule'], 'rule1')

    def test_noise(self):
        result = run(QUIET)
        self.assertEqual((result['tier'], result['rule']), ('none', 'none'))

    def test_single_one_sigma_point(self):
        result = run([9, 11, 9, 11, 9, 11, 9, 11.5])
        self.assertEqual((result['tier'], result['rule']), ('log', '1sigma'))

    def test_short_series(self):
        result = bands.evaluate([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 8, 20)
        self.assertEqual((result['tier'], result['rule']), ('log', 'insufficient-baseline'))

    def test_zero_sigma(self):
        result = bands.evaluate([5] * 30, 8, 20)
        self.assertEqual(result['rule'], 'insufficient-baseline')

    def cli(self, series):
        with tempfile.TemporaryDirectory() as temp:
            config = Path(temp) / 'bands.json'
            metric = Path(temp) / 'metric.json'
            config.write_text((PLUGIN / 'ci/bands.json').read_text())
            metric.write_text(series)
            return subprocess.run([sys.executable, str(SCRIPT), '--config', str(config), '--series', str(metric)],
                                  capture_output=True, text=True)

    def test_cli_round_trip(self):
        result = self.cli(json.dumps(BASE + QUIET[:7] + [15]))
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual((data['metric'], data['tier'], data['rule']), ('ci_test_failure_rate', 'propose', 'rule1'))
        self.assertIn('pull_request', data['action']['routes'])

    def test_cli_malformed_series(self):
        for text in ('{"a": 1}', '["x"]', 'not json', '[]'):
            result = self.cli(text)
            self.assertEqual(result.returncode, 1, text)
            self.assertTrue(result.stderr.startswith('BANDS:'), text)


if __name__ == '__main__':
    unittest.main()
