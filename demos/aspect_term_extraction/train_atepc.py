# -*- coding: utf-8 -*-
# file: train_atepc.py
# time: 2021/5/21 0021
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.


########################################################################################################################
#                                               ATEPC training script                                                  #
########################################################################################################################
from pyabsa.functional import ATEPCModelList
from pyabsa.functional import Trainer, ATEPCTrainer
from pyabsa.functional import ABSADatasetList
from pyabsa.functional import ATEPCConfigManager

atepc_config_english = ATEPCConfigManager.get_atepc_config_english()
atepc_config_english.num_epoch = 10
atepc_config_english.evaluate_begin = 4
atepc_config_english.log_step = 50
atepc_config_english.pretrained_bert = 'bert-base-multilingual-uncased'
atepc_config_english.model = ATEPCModelList.LCF_ATEPC

dataset_path = ABSADatasetList.Multilingual
# or your local dataset: dataset_path = 'your local dataset path'

aspect_extractor = ATEPCTrainer(config=atepc_config_english,
                                dataset=dataset_path,
                                from_checkpoint='',  # set checkpoint to train on the checkpoint.
                                checkpoint_save_mode=1,
                                auto_device=True
                                )
