import itertools
from pathlib import Path

from flights.config import DATA_DIR, DATETIME_NOW, DATETIME_NOW_STR

SITE = 'rair'

DATA_FPATH = Path(DATA_DIR / f'{SITE}.joblib')
DATA_FPATH_HISTORY = Path(DATA_DIR / 'history' /
                          f'{SITE}_{DATETIME_NOW_STR}.joblib')

src_dsts = [
    {
        'srcs': ['OTP'],  # ,'BCM','CND','TGM']
        'dsts': [
            'VIE',
            'CRL',
            'ZAD',
            'PFO',
            'MRS',
            'BER',
            'CHQ', 'CFU', 'JSI', 'SKG',
            # 'DUB',
            'GOA', 'SUF', 'PSR', 'TSF', 'PSA', 'NAP', 'FCO', 'CIA',  # 'PMO','PEG','CTA','BGY',
            'MAD', 'AGP', 'PMI',
            # 'LIS','TFS'-nuE, #'LPA'-nonExistent,
            'MLA',  # 'LCA'-nuE,'AHO'-nonExistent,
            # 'BRS','EDI', # UK
            'JSI', 'CFU',  # 'ZTH','JMK','JTR','HER','PVK',, # 'ATH',
            # 'BLL','CPH', 'AAR', # DK -nonExistent
            # 'BUD','DTM','CAM', -nonExistent
        ]
    },
]

src_dst_pairs = list(itertools.chain.from_iterable(
    [list(itertools.product(comb['srcs'], comb['dsts'])) for comb in src_dsts]))
src_dst_pairs += [(dst, src) for src, dst in src_dst_pairs]

DBG = 0

CONFIG = {
    'days_to_query': range(7, 1*30, 30),  # 1 month
    'src_dst_pairs': src_dst_pairs,
    'src_dsts': src_dsts,
}
