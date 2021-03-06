import sys
import unittest

import numpy as np
import pandas as pd

sys.path.append('../..')

import anduryl

class TestRobustness(unittest.TestCase):

    def test1_compare_item_robustness(self):
        
        item_table = pd.read_csv('data/item_robustness_tobacco.csv', sep=';', index_col=0)
                
        # Show full message if not equal
        # self.maxDiff = None
        
        project = anduryl.Project()
        project.io.load_excalibur(f'../data/tobacco.dtt', f'../data/tobacco.rls')

        project.calculate_item_robustness(
            weight_type='global',
            overshoot=0.1,
            max_exclude=4,
            min_exclude=0,
            calpower=1.0,
            alpha=0.0
        )

        df = pd.DataFrame(
            data=project.main_results.item_robustness.values(),
            index=list(project.main_results.item_robustness.keys()),
            columns=['Info score total' ,'Info score realizations', 'Calibration score']
        )

        for (key1, row1), (key2, row2) in zip(df.round(7).iterrows(), item_table.round(7).iterrows()):
            self.assertDictEqual(row1.to_dict(), row2.to_dict(), msg=f'\nDifferences found for case: {key1}, {key2}')

    def test2_compare_expert_robustness(self):
        
        expert_table = pd.read_csv('data/expert_robustness_tobacco.csv', sep=';', index_col=0).round(7)
                
        # Show full message if not equal
        # self.maxDiff = None
        
        project = anduryl.Project()
        project.io.load_excalibur(f'../data/tobacco.dtt', f'../data/tobacco.rls')

        project.calculate_expert_robustness(
            weight_type='global',
            overshoot=0.1,
            max_exclude=4,
            min_exclude=0,
            calpower=1.0,
            alpha=0.0
        )

        df = pd.DataFrame(
            data=project.main_results.expert_robustness.values(),
            index=list(project.main_results.expert_robustness.keys()),
            columns=['Info score total' ,'Info score realizations', 'Calibration score']
        )

        for (key1, row1), (key2, row2) in zip(df.round(7).iterrows(), expert_table.round(7).iterrows()):
            self.assertDictEqual(row1.to_dict(), row2.to_dict(), msg=f'\nDifferences found for case: {key1}, {key2}')

if __name__ == "__main__":
    unittest.main(verbosity=2)
