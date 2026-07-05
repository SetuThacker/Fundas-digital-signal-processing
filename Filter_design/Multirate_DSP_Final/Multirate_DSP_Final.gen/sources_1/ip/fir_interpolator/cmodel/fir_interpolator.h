
//------------------------------------------------------------------------------
// (c) Copyright 2014 Xilinx, Inc. All rights reserved.
//
// This file contains confidential and proprietary information
// of Xilinx, Inc. and is protected under U.S. and
// international copyright and other intellectual property
// laws.
//
// DISCLAIMER
// This disclaimer is not a license and does not grant any
// rights to the materials distributed herewith. Except as
// otherwise provided in a valid license issued to you by
// Xilinx, and to the maximum extent permitted by applicable
// law: (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND
// WITH ALL FAULTS, AND XILINX HEREBY DISCLAIMS ALL WARRANTIES
// AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, INCLUDING
// BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-
// INFRINGEMENT, OR FITNESS FOR ANY PARTICULAR PURPOSE; and
// (2) Xilinx shall not be liable (whether in contract or tort,
// including negligence, or under any other theory of
// liability) for any loss or damage of any kind or nature
// related to, arising under or in connection with these
// materials, including for any direct, or any indirect,
// special, incidental, or consequential loss or damage
// (including loss of data, profits, goodwill, or any type of
// loss or damage suffered as a result of any action brought
// by a third party) even if such damage or loss was
// reasonably foreseeable or Xilinx had been advised of the
// possibility of the same.
//
// CRITICAL APPLICATIONS
// Xilinx products are not designed or intended to be fail-
// safe, or for use in any application requiring fail-safe
// performance, such as life-support or safety devices or
// systems, Class III medical devices, nuclear facilities,
// applications related to the deployment of airbags, or any
// other applications that could lead to death, personal
// injury, or severe property or environmental damage
// (individually and collectively, "Critical
// Applications"). Customer assumes the sole risk and
// liability of any use of Xilinx products in Critical
// Applications, subject only to applicable laws and
// regulations governing limitations on product liability.
//
// THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS
// PART OF THIS FILE AT ALL TIMES.
//------------------------------------------------------------------------------ 
//
// C Model configuration for the "fir_interpolator" instance.
//
//------------------------------------------------------------------------------
//
// coefficients: -0.0121432091,-0.0134817437,-0.0155835231,-0.0182470587,-0.0209718474,-0.0229610400,-0.0231557321,-0.0202999706,-0.0130326754,0.0000000000,0.0200205391,0.0479943452,0.0845132797,0.1296990384,0.1831357491,0.2438391279,0.3102667825,0.3803710299,0.4516921614,0.5214867360,0.5868824966,0.6450491484,0.6933727145,0.7296206454,0.7520853499,0.7596953122,0.7520853499,0.7296206454,0.6933727145,0.6450491484,0.5868824966,0.5214867360,0.4516921614,0.3803710299,0.3102667825,0.2438391279,0.1831357491,0.1296990384,0.0845132797,0.0479943452,0.0200205391,0.0000000000,-0.0130326754,-0.0202999706,-0.0231557321,-0.0229610400,-0.0209718474,-0.0182470587,-0.0155835231,-0.0134817437,-0.0121432091
// chanpats: 173
// name: fir_interpolator
// filter_type: 1
// rate_change: 0
// interp_rate: 12
// decim_rate: 1
// zero_pack_factor: 1
// coeff_padding: 0
// num_coeffs: 51
// coeff_sets: 1
// reloadable: 0
// is_halfband: 0
// quantization: 1
// coeff_width: 16
// coeff_fract_width: 15
// chan_seq: 0
// num_channels: 1
// num_paths: 1
// data_width: 16
// data_fract_width: 0
// output_rounding_mode: 1
// output_width: 16
// output_fract_width: 0
// config_method: 0

const double fir_interpolator_coefficients[51] = {-0.0121432091,-0.0134817437,-0.0155835231,-0.0182470587,-0.0209718474,-0.0229610400,-0.0231557321,-0.0202999706,-0.0130326754,0.0000000000,0.0200205391,0.0479943452,0.0845132797,0.1296990384,0.1831357491,0.2438391279,0.3102667825,0.3803710299,0.4516921614,0.5214867360,0.5868824966,0.6450491484,0.6933727145,0.7296206454,0.7520853499,0.7596953122,0.7520853499,0.7296206454,0.6933727145,0.6450491484,0.5868824966,0.5214867360,0.4516921614,0.3803710299,0.3102667825,0.2438391279,0.1831357491,0.1296990384,0.0845132797,0.0479943452,0.0200205391,0.0000000000,-0.0130326754,-0.0202999706,-0.0231557321,-0.0229610400,-0.0209718474,-0.0182470587,-0.0155835231,-0.0134817437,-0.0121432091};

const xip_fir_v7_2_pattern fir_interpolator_chanpats[1] = {P_BASIC};

static xip_fir_v7_2_config gen_fir_interpolator_config() {
  xip_fir_v7_2_config config;
  config.name                = "fir_interpolator";
  config.filter_type         = 1;
  config.rate_change         = XIP_FIR_INTEGER_RATE;
  config.interp_rate         = 12;
  config.decim_rate          = 1;
  config.zero_pack_factor    = 1;
  config.coeff               = &fir_interpolator_coefficients[0];
  config.coeff_padding       = 0;
  config.num_coeffs          = 51;
  config.coeff_sets          = 1;
  config.reloadable          = 0;
  config.is_halfband         = 0;
  config.quantization        = XIP_FIR_QUANTIZED_ONLY;
  config.coeff_width         = 16;
  config.coeff_fract_width   = 15;
  config.chan_seq            = XIP_FIR_BASIC_CHAN_SEQ;
  config.num_channels        = 1;
  config.init_pattern        = fir_interpolator_chanpats[0];
  config.num_paths           = 1;
  config.data_width          = 16;
  config.data_fract_width    = 0;
  config.output_rounding_mode= XIP_FIR_TRUNCATE_LSBS;
  config.output_width        = 16;
  config.output_fract_width  = 0,
  config.config_method       = XIP_FIR_CONFIG_SINGLE;
  return config;
}

const xip_fir_v7_2_config fir_interpolator_config = gen_fir_interpolator_config();

