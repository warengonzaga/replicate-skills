import copy
import unittest
from support import module

gate = module('diff', 'acceptance_gate')


def criterion(key='save', required=True, state='pass', evidence=None):
    return {'id': key, 'required': required, 'state': state,
            'evidence': [{'kind': 'test', 'ref': 'results/save.txt'}] if evidence is None else evidence}


def ledger(*items):
    return {'schema_version': 1, 'criteria': list(items)}


class Acceptance(unittest.TestCase):
    def test_required_pass_is_ready(self):
        self.assertTrue(gate.evaluate(ledger(criterion()))['ready'])

    def test_required_failure_blocks_despite_many_optional_passes(self):
        result = gate.evaluate(ledger(criterion(state='fail'), *[criterion(str(i), False) for i in range(30)]))
        self.assertFalse(result['ready'])
        self.assertEqual(result['blockers'], ['save'])

    def test_no_evidence_does_not_verify_pass(self):
        result = gate.evaluate(ledger(criterion(evidence=[])))
        self.assertFalse(result['criteria'][0]['verified'])
        self.assertFalse(result['ready'])

    def test_blocked_and_unknown_required_are_not_ready(self):
        for state in ('blocked', 'unknown'):
            with self.subTest(state=state):
                self.assertFalse(gate.evaluate(ledger(criterion(state=state)))['ready'])

    def test_optional_failure_does_not_block_required_pass(self):
        self.assertTrue(gate.evaluate(ledger(criterion(), criterion('extra', False, 'fail')))['ready'])

    def test_no_required_criteria_cannot_establish_readiness(self):
        self.assertFalse(gate.evaluate(ledger(criterion(required=False)))['ready'])

    def test_counts_are_not_percentages(self):
        result = gate.evaluate(ledger(criterion(), criterion('two', False, 'blocked', [])))
        self.assertEqual(result['counts'], {'pass': 1, 'fail': 0, 'blocked': 1, 'unknown': 0})

    def test_evaluation_does_not_mutate_ledger(self):
        document = ledger(criterion())
        original = copy.deepcopy(document)
        gate.evaluate(document)
        self.assertEqual(document, original)

    def test_invalid_documents(self):
        for document in (None, [], {}, ledger(), {'schema_version': True, 'criteria': [criterion()]}):
            with self.subTest(document=document), self.assertRaises(ValueError):
                gate.evaluate(document)

    def test_invalid_criteria(self):
        for field, value in [('id', ''), ('required', 1), ('state', 'complete'), ('evidence', {})]:
            item = criterion()
            item[field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                gate.evaluate(ledger(item))

    def test_duplicate_ids(self):
        with self.assertRaises(ValueError):
            gate.evaluate(ledger(criterion(), criterion()))

    def test_invalid_evidence(self):
        for evidence in ([None], [{'kind': 'guess', 'ref': 'x'}], [{'kind': 'test', 'ref': ''}]):
            with self.subTest(evidence=evidence), self.assertRaises(ValueError):
                gate.evaluate(ledger(criterion(evidence=evidence)))
