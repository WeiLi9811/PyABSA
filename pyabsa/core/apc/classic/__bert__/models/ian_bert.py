# -*- coding: utf-8 -*-
# file: ian.py
# author: songyouwei <youwei0314@gmail.com>
# Copyright (C) 2018. All Rights Reserved.

import torch
import torch.nn as nn

from ..layers.attention import Attention
from ..layers.dynamic_rnn import DynamicLSTM


class IAN_BERT(nn.Module):
    inputs = ['text_indices', 'aspect_indices']

    def __init__(self, bert, opt):
        super(IAN_BERT, self).__init__()
        self.opt = opt
        self.embed = self.embed = bert
        self.lstm_context = DynamicLSTM(opt.embed_dim, opt.hidden_dim, num_layers=1, batch_first=True)
        self.lstm_aspect = DynamicLSTM(opt.embed_dim, opt.hidden_dim, num_layers=1, batch_first=True)
        self.attention_aspect = Attention(opt.hidden_dim, score_function='bi_linear')
        self.attention_context = Attention(opt.hidden_dim, score_function='bi_linear')
        self.dense = nn.Linear(opt.hidden_dim * 2, opt.polarities_dim)

    def forward(self, inputs):
        text_raw_indices, aspect_indices = inputs['text_indices'], inputs['aspect_indices']
        text_raw_len = torch.sum(text_raw_indices != 0, dim=-1)
        aspect_len = torch.sum(aspect_indices != 0, dim=-1)

        context = self.embed(text_raw_indices)['last_hidden_state']
        aspect = self.embed(aspect_indices)['last_hidden_state']
        context, (_, _) = self.lstm_context(context, text_raw_len)
        aspect, (_, _) = self.lstm_aspect(aspect, aspect_len)

        aspect_len = torch.tensor(aspect_len, dtype=torch.float).to(self.opt.device)
        aspect_pool = torch.sum(aspect, dim=1)
        aspect_pool = torch.div(aspect_pool, aspect_len.view(aspect_len.size(0), 1))

        text_raw_len = text_raw_len.clone().detach()
        context_pool = torch.sum(context, dim=1)
        context_pool = torch.div(context_pool, text_raw_len.view(text_raw_len.size(0), 1))

        aspect_final, _ = self.attention_aspect(aspect, context_pool)
        aspect_final = aspect_final.squeeze(dim=1)
        context_final, _ = self.attention_context(context, aspect_pool)
        context_final = context_final.squeeze(dim=1)

        x = torch.cat((aspect_final, context_final), dim=-1)
        out = self.dense(x)
        return {'logits': out}
