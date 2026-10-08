import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_report import build_report, report_rows, validate
from openpyxl import load_workbook


def sample():
    return json.loads((Path(__file__).resolve().parents[1] / 'examples/findings.json').read_text(encoding='utf-8'))


class ReportTests(unittest.TestCase):
    def test_all_pass_has_no_issue_sheet(self):
        data = sample()
        for c in data['checks']:
            c.update(result='√', evidence_state='available', issues=[])
        self.assertEqual(list(report_rows(data)), ['Checklist'])

    def test_all_x_have_detail(self):
        data = sample()
        issue = data['checks'][1]['issues'][0]
        for c in data['checks']:
            c.update(result='X', evidence_state='available', issues=[copy.deepcopy(issue)])
        self.assertEqual(len(report_rows(data)['15. HREFLANG']), 4)

    def test_missing_results_are_disclosed(self):
        data = sample()
        row = report_rows(data)['Checklist'][3]
        self.assertIn('尚未取得', row[3])
        self.assertIn('Not fully verified', row[4])
        del data['checks'][2]['missing_evidence_note']
        with self.assertRaises(ValueError):
            validate(data)

    def test_invalid_status_issue_and_id(self):
        for mutate in [lambda d: d['checks'][1].update(issues=[]),
                       lambda d: d['checks'][0].update(id='15.2'),
                       lambda d: d['checks'][0].update(result='Y'),
                       lambda d: d['checks'][0].update(evidence_state='unavailable')]:
            data = sample()
            mutate(data)
            with self.assertRaises(ValueError):
                validate(data)

    def test_single_language_and_explicit_skip(self):
        data = sample()
        for c in data['checks']:
            c.update(result='N/A', evidence_state='not_applicable', issues=[], finding='确认单语言；15.3 用户明确跳过。')
        self.assertEqual(list(report_rows(data)), ['Checklist'])

    def test_literal_text_roundtrip_and_no_overwrite(self):
        data = sample()
        data['checks'][0]['finding'] = '=HYPERLINK("bad","中文")'
        run_root = Path(__file__).resolve().parents[1] / 'runs'
        run_root.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=run_root) as directory:
            path = build_report(data, directory)
            wb = load_workbook(path)
            self.assertEqual(wb['Checklist']['D2'].value, data['checks'][0]['finding'])
            self.assertEqual(wb['Checklist']['D2'].data_type, 's')
            self.assertEqual(wb.sheetnames, ['Checklist', '15. HREFLANG'])
            wb.close()
            with self.assertRaises(FileExistsError):
                build_report(data, directory)


if __name__ == '__main__':
    unittest.main()
