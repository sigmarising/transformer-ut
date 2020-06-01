import random
import numpy as np

import torch
import copy
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

from modules.layers import TransformerDecoderLayer
from modules.layers import _gen_position_signal
from .Act import ACT

import warnings
warnings.filterwarnings("ignore")


class Decoder(nn.Module):

	""" transformer decoder """

	def __init__(self,
		dim_model = 200,
		dim_feedforward=512,
		num_heads = 8,
		num_layers = 6,
		act=False,
		dropout=0.2,
		transformer_type='standard'
		):

		super(Decoder, self).__init__()

		upperbound_seq_len = 200
		self.layer_signal = _gen_position_signal(num_layers, dim_model) # layer
		self.time_signal = _gen_position_signal(upperbound_seq_len, dim_model) # time

		self.dim_model = dim_model
		self.dim_feedforward = dim_feedforward
		self.d_k = int(dim_model / num_heads)
		self.d_v = int(dim_model / num_heads)
		self.num_heads = num_heads
		self.num_layers = num_layers
		self.act = act
		self.transformer_type = transformer_type

		self.dec = TransformerDecoderLayer(self.dim_model, self.num_heads,
			self.dim_feedforward, self.d_k, self.d_v, dropout)
		if self.transformer_type == 'universal':
			self.dec_layers = nn.ModuleList([self.dec for _ in range(num_layers)])
			if self.act:
				self.act_fn = ACT(self.dim_model)
		elif self.transformer_type == 'standard':
			self.dec_layers = _get_clones(self.dec, num_layers) # deep copy
		else: assert False, 'not implemented transformer type'

		self.norm = nn.LayerNorm(self.dim_model)


	def forward(self, tgt, memory,
		tgt_mask=None, src_mask=None):

		"""
			add time/layer positional encoding; then run decoding
			Args:
				tgt: [b x seq_len x dim_model]
				memory: encoder outputs
		"""

		# import pdb; pdb.set_trace()

		x = tgt
		if not self.act:
			for layer in range(self.num_layers):
				x = x + self.time_signal[:, :tgt.shape[1], :].type_as(
					tgt.data).clone().detach()
				if self.transformer_type == 'universal':
					x = x + self.layer_signal[:, layer, :].unsqueeze(1).repeat(
						1,tgt.shape[1],1).type_as(tgt.data).clone().detach()
				x, att_decslf, att_encdec = self.dec_layers[layer](x, memory,
					decslf_attn_mask=tgt_mask, encdec_attn_mask=src_mask)
			x = self.norm(x)
			return x, att_decslf, att_encdec
		else:
			x, layer_map = self.act_fn.forward_dec(x, memory, tgt_mask, src_mask,
				self.dec, self.time_signal, self.layer_signal, self.num_layers)
			x = self.norm(x)
			return x, layer_map


def _get_clones(module, N):
	
	return nn.ModuleList([copy.deepcopy(module) for i in range(N)])