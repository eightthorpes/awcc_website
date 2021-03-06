import os

TRAIN_SKUS = {'name': "Train Tour", 'skus': ['00164',]}
BRUNCH_SKUS = {'name': "Brunch Tour", 'skus': ['00116', '00118', '00165', '00166', '00169']}
LUNCH_SKUS = {'name': "Lunch Tour", 'skus': ['00167',]}
DINNER_SKUS = {'name': "Dinner Tour", 'skus': ['00168',]}
TOUR_SKUS = {'name': "Regular House Tour", 
        'skus': ['00091', '00093', '00094', '00095', '00096', '00097',
        '00098', '00099', '00100', '00101', '00102', '00103', '00104',
        '00105', '00106', '00107', '00108', '00109', '00110', '00111',
        '00112', '00113', '00114', '00115', '00117',
        '00119', '00120', '00121', '00122', '00123', '00124',
        '00126', '00128', '00129', '00130', '00131', '00132',
        '00133', '00134', '00135', '00136', '00137', '00139',
        '00140', '00141', '00142', '00144', '00145', '00146',
        '00147', '00148', '00149', '00150', '00151', '00152', '00153',
        '00154', '00155', '00156', '00157', '00158', '00159', '00160',
        '00161', '00162', '00163',
        '00170']}
foo = 0
ECWID_SKUS = TRAIN_SKUS['skus'] + BRUNCH_SKUS['skus'] + LUNCH_SKUS['skus'] + DINNER_SKUS['skus'] + TOUR_SKUS['skus']

ECWID_URL = "https://app.ecwid.com/api/v1"
ECWID_STORE_ID = "734045"
ORDER_AUTH_KEY = os.environ['ORDER_AUTH_KEY']
PRODUCT_AUTH_KEY = os.environ['PRODUCT_AUTH_KEY']
ECWID_FROM = "2013-08-01"
ECWID_TO   = "2013-12-31"
