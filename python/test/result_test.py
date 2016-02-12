from asset import Asset
import config
from result import Result
from vmaf_quality_runner import VmafQualityRunner

__copyright__ = "Copyright 2016, Netflix, Inc."
__license__ = "Apache, Version 2.0"

import unittest

class ResultTest(unittest.TestCase):

    def setUp(self):
        ref_path = config.ROOT + "/resource/yuv/checkerboard_1920_1080_10_3_0_0.yuv"
        dis_path = config.ROOT + "/resource/yuv/checkerboard_1920_1080_10_3_1_0.yuv"
        asset = Asset(dataset="test", content_id=0, asset_id=0,
                      workdir_root=config.ROOT + "/workspace/workdir",
                      ref_path=ref_path,
                      dis_path=dis_path,
                      asset_dict={'width':1920, 'height':1080})

        self.runner = VmafQualityRunner(
            [asset], None, fifo_mode=True,
            log_file_dir=config.ROOT + "/workspace/log_file_dir")
        self.runner.run()
        self.result = self.runner.results[0]

    def tearDown(self):
        if hasattr(self, 'runner'): self.runner.remove_logs()
        pass

    def test_todataframe_fromdataframe(self):
        import numpy as np
        print 'test on result to/from dataframe...'
        df = self.result.to_dataframe()
        df_vmaf = df.loc[df['scores_key'] == 'VMAF_scores']
        df_adm = df.loc[df['scores_key'] == 'VMAF_adm_scores']
        df_vif = df.loc[df['scores_key'] == 'VMAF_vif_scores']
        df_ansnr = df.loc[df['scores_key'] == 'VMAF_ansnr_scores']
        df_motion = df.loc[df['scores_key'] == 'VMAF_motion_scores']
        self.assertEquals(len(df), 5)
        self.assertEquals(len(df_vmaf), 1)
        self.assertEquals(len(df_adm), 1)
        self.assertEquals(len(df_vif), 1)
        self.assertEquals(len(df_ansnr), 1)
        self.assertEquals(len(df_motion), 1)
        self.assertEquals(np.mean(df_vmaf.iloc[0]['scores']), 43.46099858503333)
        self.assertEquals(np.mean(df_adm.iloc[0]['scores']), 0.81386)
        self.assertEquals(np.mean(df_vif.iloc[0]['scores']), 0.15612933333333334)
        self.assertEquals(np.mean(df_ansnr.iloc[0]['scores']), 12.418291000000002)
        self.assertEquals(np.mean(df_motion.iloc[0]['scores']), 12.343795333333333)
        self.assertEquals(df.iloc[0]['dataset'], 'test')
        self.assertEquals(df.iloc[0]['content_id'], 0)
        self.assertEquals(df.iloc[0]['asset_id'], 0)
        self.assertEquals(df.iloc[0]['ref_name'], 'checkerboard_1920_1080_10_3_0_0.yuv')
        self.assertEquals(df.iloc[0]['dis_name'], 'checkerboard_1920_1080_10_3_1_0.yuv')
        self.assertEquals(
            df.iloc[0]['asset'],
            '{"asset_dict": {"height": 1080, "width": 1920}, "asset_id": 0, "content_id": 0, "dataset": "test", "dis_path": "checkerboard_1920_1080_10_3_1_0.yuv", "ref_path": "checkerboard_1920_1080_10_3_0_0.yuv", "workdir": ""}')
        self.assertEquals(df.iloc[0]['executor_id'], 'VMAF_V0.1')

        Result._assert_assert_dataframe(df)

        recon_result = Result.from_dataframe(df)
        self.assertEquals(self.result, recon_result)
        self.assertTrue(self.result == recon_result)
        self.assertFalse(self.result != recon_result)

    def test_to_score_str(self):
        print 'test on result aggregate scores...'
        self.assertEquals(self.result.get_score('VMAF_score'),
                          43.46099858503333)
        self.assertEquals(self.result.get_score('VMAF_adm_score'),
                          0.81386)
        self.assertEquals(self.result.get_score('VMAF_vif_score'),
                          0.15612933333333334)
        self.assertEquals(self.result.get_score('VMAF_motion_score'),
                          12.343795333333333)
        self.assertEquals(self.result.get_score('VMAF_ansnr_score'),
                          12.418291000000002)

        with self.assertRaises(KeyError):
            self.result.get_score('VVMAF_score')
        with self.assertRaises(KeyError):
            self.result.get_score('VMAF_motion_scor')

        self.assertEquals(
            self.result._get_perframe_score_str(),
            'Frame 0: VMAF_adm_score:0.799, VMAF_ansnr_score:12.421, VMAF_motion_score:0.000, VMAF_score:42.112, VMAF_vif_score:0.156\n'
            'Frame 1: VMAF_adm_score:0.843, VMAF_ansnr_score:12.418, VMAF_motion_score:18.489, VMAF_score:47.654, VMAF_vif_score:0.156\n'
            'Frame 2: VMAF_adm_score:0.800, VMAF_ansnr_score:12.416, VMAF_motion_score:18.542, VMAF_score:40.617, VMAF_vif_score:0.156\n'
        )

        self.assertEquals(
            self.result._get_aggregate_score_str(),
            'Aggregate: VMAF_adm_score:0.814, VMAF_ansnr_score:12.418, VMAF_motion_score:12.344, VMAF_score:43.461, VMAF_vif_score:0.156'
        )
