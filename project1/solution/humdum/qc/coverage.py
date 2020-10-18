# RA, 2020-09-28

import numpy as np
import re

from pathlib import Path
from humdum.io import from_sam


# On alignment quality

# https://hbctraining.github.io/Intro-to-rnaseq-hpc-O2/lessons/04_alignment_quality.html

# https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5964631/
# Three primary metrics are used to evaluate sequence quality in NGS data:
# depth of coverage (how many sequence reads are present at a given position),
# base quality (have the correct bases been called in sequence reads) and
# mapping quality (have the reads been mapped to the correct position in the genome).

# https://learn.gencore.bio.nyu.edu/alignment/


def coverage_pbp(file, reference_length=None):
    """
    Reads the SAM file and computes the per-based coverage
    from the aligned blocks.
    In particular: if a position in the reference is consistently
    a 'delete' compared to the matched reads, it will be counted as zero.

    The `reference_length` can be inferred from the mapped reads
    but there can be an undetected residual at the 'right' end
    if it is not specified.
    """
    zeros = (lambda n: np.zeros(n, dtype=int))
    counts = zeros(reference_length or 0)
    for read in from_sam(file):
        a = read.pos
        for (n, A) in re.findall(r"([0-9]+)([XIDS=])", read.cigar):
            b = a + int(n)
            if (A == '='):
                assert (a < b)
                if (b > len(counts)):
                    counts = np.concatenate([counts, zeros(b - len(counts))])
                counts[a:b] += 1
            a = b

    return counts



def test_coverage_pbp(file):
    counts = coverage_pbp(file)
    print(*counts)


if (__name__ == '__main__'):
    in_file = list((Path(__file__).parent.parent.parent.parent / "input/data_small/").glob("*.sam")).pop()
    counts = coverage_pbp(in_file)

    print(len(counts))

    from plox import Plox
    with Plox() as px:
        px.a.plot(counts)
        px.show()
