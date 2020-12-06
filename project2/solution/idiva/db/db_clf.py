# HK, 2020-12-05

import idiva.io
from idiva import log


def db_classifier(*, case: idiva.io.ReadVCF, ctrl: idiva.io.ReadVCF) -> object:
    """
    Classifies the case-control df by querying the clinvar and dbSNP data.
    """
    from idiva.clf.df import c5_df
    from idiva.db import db

    log.info("Running the database classifier.")
    case_control = c5_df(case)

    db_PosRefAlt = db.get_db_label_df(which_dbSNP=int(case_control.iloc[0]['CHROM']))

    merge_on_PosRefAlt = case_control.merge(db_PosRefAlt, left_on=['POS', 'REF', 'ALT'], right_on=['pos', 'ref', 'alt'],
                                            how='left')
    merge_on_PosRefAlt['class'] = merge_on_PosRefAlt['class'].fillna(2)
    log.info(
        f"Found {len(merge_on_PosRefAlt) - merge_on_PosRefAlt.loc[merge_on_PosRefAlt['class'] == 2, 'class'].count()} "
        f"labels in databases.")

    result = merge_on_PosRefAlt[['CHROM', 'POS', 'ID', 'REF', 'ALT', 'class']]

    class response:
        id_cols = ['CHROM', 'POS', 'ID', 'REF', 'ALT']

        info = {
            'class': {'Number': '.',
                      'Type': 'Integer',
                      'Description': '"Number indicating to which class the variant belongs. '
                                     '0 - Benign, 1 - Pathogenic, 2 - Unknown"'
                      },
        }

        df = result

    assert set(response.id_cols).issubset(set(response.df.columns))
    assert set(response.info.keys()).issubset(set(response.df.columns))

    return response
