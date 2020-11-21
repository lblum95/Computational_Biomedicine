# RA, 2020-11-14

import typing
import pandas
import numpy
import idiva.io
from joblib import Parallel, delayed

dtype_v0 = {'CHROM': str, 'POS': int, 'ID': str, 'ALT0': float, 'ALT1': float, 'ALT2': float}


def join(*, case: pandas.DataFrame, ctrl: pandas.DataFrame) -> pandas.DataFrame:
    """
    Outer-join two dataframes on the columns CHROM, POS, ID.
    Use the suffixes _case and _ctrl for the other ambiguous columns.
    Uses sort=False in pandas.merge_ordered.
    """

    df = pandas.merge_ordered(
        left=case, right=ctrl,
        suffixes=['_case', '_ctrl'],
        on=['CHROM', 'POS', 'ID'],
        how="outer",
    )

    return df


def v0_datalines(vcf: idiva.io.ReadVCF) -> typing.Iterable[dict]:
    from idiva.io.vcf import parse_gt, is_genomic_string

    # special = sorted({F"<{k}>" for k in vcf.meta['ALT'].keys()})

    for dataline in vcf:
        samples = [parse_gt(gt) for gt in dataline.samples]

        # SIMPLIFICATION

        samples = (numpy.array(samples, dtype=int) != 0).sum(axis=1)

        line = {
            'CHROM': dataline.chrom,
            'POS': dataline.pos,
            'ID': dataline.id,
            'ALT0': (samples == 0).sum(),
            'ALT1': (samples == 1).sum(),
            'ALT2': (samples == 2).sum(),
        }

        yield line


def v0_df(vcf: idiva.io.ReadVCF) -> pandas.DataFrame:
    """
    Make a dataframe from the VCF datalines.
    Only counts the presence of alternative variants.
    Returns a dataframe like

        ID          CHROM   POS  ALT0  ALT1  ALT2
        rs556541063    17    52   500     0     0
        ...           ...   ...   ...   ...   ...
        rs191439637    17  2833   495     5     0
        rs149757548    17  2837   498     2     0

    ID is not guaranteed to be unique.

    Int64 data type is used for the ALT columns.
    """

    return pandas.DataFrame(data=v0_datalines(vcf)).astype(dtype_v0)


if __name__ == '__main__':
    URLS = {
        'ctrl': "https://public.bmi.inf.ethz.ch/eth_intern/teaching/cbm_2020/cbm_2020_project2/control_v2.vcf.gz",
        'case': "https://public.bmi.inf.ethz.ch/eth_intern/teaching/cbm_2020/cbm_2020_project2/case_processed_v2.vcf.gz",
    }

    from tcga.utils import download
    from idiva.utils import at_most_n
    from pathlib import Path
    from contexttimer import Timer

    cache = (Path(__file__).parent.parent.parent.parent / "input/download_cache").resolve()
    assert cache.is_dir()
    download = download.to(abs_path=cache)

    with download(URLS['ctrl']).now.open() as fd:
        with Timer() as timer:
            df = v0_df(idiva.io.ReadVCF(fd))

        print(F"This took {timer.elapsed} seconds")
