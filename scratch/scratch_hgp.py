import numpy as np
import scipy.sparse as sp

from ldpc2.bp_decoder import BpDecoder
from ldpc2.bposd_decoder import BpOsdDecoder
from ldpc import bposd_decoder as bposd_decoder_og
from tqdm import tqdm

from ldpc2.noise_models import generate_bsc_error

from bposd.css import css_code
from bposd.hgp import hgp

from ldpc2.monte_carlo_simulation import McSim

h = np.loadtxt("scratch/16_4_6.txt", dtype=int)
qcode = hgp(h,h)

hx = sp.csr_matrix(qcode.hx, dtype=np.uint8)
hz = sp.csr_matrix(qcode.hz, dtype=np.uint8)
lx = sp.csr_matrix(qcode.lx, dtype=np.uint8)
lz = sp.csr_matrix(qcode.lz, dtype=np.uint8)

run_count = 100000
error_rate = 0.001

osd = BpOsdDecoder(hx,error_rate=error_rate, bp_method='ms', schedule="parallel", ms_scaling_factor=0.625, max_iter=50,omp_thread_count=1,osd_order=0,osd_method="osd_e")
osd_og = bposd_decoder_og(hx,error_rate=error_rate, bp_method='ms', ms_scaling_factor=0.625, max_iter=50,osd_order=0,osd_method="osd_e")

# bpd = BpDecoder(hx,error_rate=error_rate, bp_method='ms', schedule="serial", ms_scaling_factor=0.625, max_iter=50,omp_thread_count=1)

# McSim(hx, error_rate=error_rate, Decoder=bpd, target_run_count=run_count,seed=42)

for DECODER in [osd,osd_og]:
    np.random.seed(42)
    fail = 0

    for i in tqdm(range(run_count)):

        error = generate_bsc_error(hx.shape[1], error_rate)
        z = hx@error%2

        decoding = DECODER.decode(z)

        residual = (decoding + error) %2

        if np.any((lx@residual)%2):
            fail+=1

    print(f"ler: {fail/run_count}")






