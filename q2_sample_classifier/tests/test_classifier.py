# ----------------------------------------------------------------------------
# Copyright (c) 2017--, q2-sample-classifier development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import qiime2
import pandas as pd
from os import mkdir
from os.path import join
from warnings import filterwarnings
from sklearn.exceptions import ConvergenceWarning
from q2_sample_classifier.visuals import (
    _two_way_anova, _pairwise_stats, _linear_regress)
from q2_sample_classifier.classify import (
    classify_samples, regress_samples,
    maturity_index, detect_outliers, predict_coordinates)

from . import SampleClassifierTestPluginBase


filterwarnings("ignore", category=UserWarning)
filterwarnings("ignore", category=ConvergenceWarning)


class VisualsTests(SampleClassifierTestPluginBase):

    def test_two_way_anova(self):
        aov, mod_sum = _two_way_anova(tab1, md, 'Value', 'Time', 'Group')
        self.assertAlmostEqual(aov['PR(>F)']['Group'], 0.00013294988301061492)
        self.assertAlmostEqual(aov['PR(>F)']['Time'], 4.1672315658105502e-07)
        self.assertAlmostEqual(aov['PR(>F)']['Time:Group'], 0.0020603144625217)

    def test_pairwise_tests(self):
        res = _pairwise_stats(tab1, md, 'Value', 'Time', 'Group')
        self.assertAlmostEqual(
            res['q-value'][(1, 'a')][(1, 'b')], 0.066766544811987918)
        self.assertAlmostEqual(
            res['q-value'][(1, 'a')][(2, 'b')], 0.00039505928148818022)

    def test_linear_regress(self):
        res = _linear_regress(md['Value'], md['Time'])
        self.assertAlmostEqual(res.iloc[0]['Mean squared error'], 1.9413916666)
        self.assertAlmostEqual(res.iloc[0]['R'], 0.86414956372460128)
        self.assertAlmostEqual(res.iloc[0]['P-value'], 0.00028880275858705694)


# This test class really just makes sure that each plugin runs without error.
# Currently it does not test for a "right" answer. There is no "right" answer,
# though we could set a random seed to make sure the test always produces the
# same result.
class EstimatorsTests(SampleClassifierTestPluginBase):

    def setUp(self):
        super().setUp()

        def _load_df(table_fp):
            table_fp = self.get_data_path(table_fp)
            table = qiime2.Artifact.load(table_fp)
            table = table.view(pd.DataFrame)
            return table

        def _load_md(md_fp):
            md_fp = self.get_data_path(md_fp)
            md = pd.DataFrame.from_csv(md_fp, sep='\t')
            md = qiime2.Metadata(md)
            return md

        self.table_chard_fp = _load_df('chardonnay.table.qza')
        self.md_chard_fp = _load_md('chardonnay.map.txt')
        self.table_ecam_fp = _load_df('ecam-table-maturity.qza')
        self.md_ecam_fp = _load_md('ecam_map_maturity.txt')

    def test_classify_samples(self):
        for classifier in ['RandomForestClassifier', 'ExtraTreesClassifier',
                           'GradientBoostingClassifier', 'AdaBoostClassifier',
                           'KNeighborsClassifier', 'LinearSVC', 'SVC']:
            tmpd = join(self.temp_dir.name, classifier)
            mkdir(tmpd)
            classify_samples(tmpd, self.table_chard_fp, self.md_chard_fp,
                             category='Vineyard', test_size=0.5, cv=3,
                             n_estimators=2, n_jobs=-1, estimator=classifier)

    def test_regress_samples(self):
        for regressor in ['RandomForestClassifier', 'ExtraTreesClassifier',
                           'GradientBoostingClassifier', 'AdaBoostClassifier',
                           'KNeighborsClassifier', 'LinearSVC', 'SVC']:
            tmpd = join(self.temp_dir.name, regressor)
            mkdir(tmpd)
            classify_samples(tmpd, self.table_chard_fp, self.md_chard_fp,
                             category='Vineyard', test_size=0.5, cv=3,
                             n_estimators=2, n_jobs=-1, estimator=regressor)

    def test_maturity_index(self):
        maturity_index(self.temp_dir.name, self.table_ecam_fp, self.md_ecam_fp,
                       category='month', group_by='delivery', n_jobs=-1,
                       control='Vaginal', test_size=0.4)

    def test_detect_outliers(self):
        outliers = detect_outliers(self.table_chard_fp, self.md_chard_fp,
                                   n_jobs=-1, contamination=0.05)

    def test_predict_coordinates(self):
        pred, coords = predict_coordinates(
            self.table_chard_fp, self.md_chard_fp,
            latitude='latitude', longitude='longitude', n_jobs=-1)


md = pd.DataFrame([(1, 'a', 0.11), (1, 'a', 0.12), (1, 'a', 0.13),
                   (2, 'a', 0.19), (2, 'a', 0.18), (2, 'a', 0.21),
                   (1, 'b', 0.14), (1, 'b', 0.13), (1, 'b', 0.14),
                   (2, 'b', 0.26), (2, 'b', 0.27), (2, 'b', 0.29)],
                  columns=['Time', 'Group', 'Value'])

tab1 = pd.DataFrame([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], columns=['Junk'])
