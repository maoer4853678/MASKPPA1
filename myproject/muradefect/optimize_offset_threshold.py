# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s 

Authenticated by Sherk
Any question please refer to:
    sherkfung@gmail.com
"""
import numpy as np
import pandas as pd
import itertools
import datetime

# Define optimizing functions
# %%
# Define optimizing functions
'''
    offset = (OFFSET_X, OFFSET_Y, THETA), example: (0, 1, 20)
'''
OFFSETS = np.vstack(
    map(
        np.ravel,
        np.meshgrid(
            np.arange(-8, 8.5, .5),
            np.arange(-8, 8.5, .5),
            np.arange(-25, 26)
        )
    )
).T

# THRESHOLD = 6.5
WEIGHT = 1


def cal_offseted(data, off=np.zeros(3)):
    data_offseted = data[:, [1, 0]] * [-1, 1] * \
                    off[2] * np.pi / 180 / 100 + off[[0, 1]] + \
                    data[:, 2:]

    return data_offseted


'''
    Below, is the first version of offset optimization algorithm
    Which, consider even importance of PPA_X, PPA_Y
    However, we usually face the fact that improving PPA_X 
        while PPA_Y is detiriated, which is unacceptable.


def cal_offseted_count(data, off=np.zeros(3)):
    # count the panels that exceed the threshold
    rst = np.sum(np.abs( cal_offseted(data, off) ) < 6.5) +\
        WEIGHT * np.sum(np.abs( cal_offseted(data, off) ) < 4)
    return  rst
'''


def cal_offseted_count(data, off=np.zeros(3)):
    '''
        This is the improved version of optimiziation method
        Which increases the weight of PPA_Y
    '''
    # count the panels that exceed the threshold
    data_offseted = np.abs(cal_offseted(data, off))
    rst = np.sum(data_offseted < 6.5) + WEIGHT * np.sum(data_offseted < 4)

    #    data_abs = np.abs(cal_offseted(data))
    #
    #    rst_a = np.mean(data_offseted < 4, axis=0)
    #    rst_b = np.mean(data_abs < 4, axis=0)
    #
    #    rst_c = np.mean(data_offseted < 6.5, axis=0)
    #    rst_d = np.mean(data_abs < 6.5, axis=0)
    #
    #    if any(rst_a < rst_b) | any(rst_c < rst_d):
    #        rst = np.mean(WEIGHT * rst_b + rst_d)
    #    else:
    #        rst = np.mean(WEIGHT * rst_a + rst_c)

    return rst


def optimize_offset(dataset):
    '''
    '''
    time_start = datetime.datetime.now()

    datasets = itertools.repeat(dataset, OFFSETS.shape[0])

    rst = np.fromiter(
        map(cal_offseted_count, datasets, OFFSETS), dtype=np.float)

    time_end = datetime.datetime.now()
    print('Time consumed: %.2f s.' % (time_end - time_start).total_seconds())

    return rst


print('Optimization functions are loaded!')


# %%
# p3 = p2[p2.EVA_CHAMBER == 'B']

def cal_ratio_bna(p3, off=np.zeros(3)):
    p3 = p3[['POS_X', 'POS_Y', 'PPA_X', 'PPA_Y']]

    def cal_ratio(p3, threshold):
        b1 = (p3[['PPA_X', 'PPA_Y']].abs() < threshold).mean()
        b1['PPA_T'] = (p3[['PPA_X', 'PPA_Y']].abs().max(axis=1) < threshold). \
            mean()

        b1.index = [x + str(threshold) for x in b1.index]

        return round(b1, 4)

    b = pd.concat([cal_ratio(p3, 4), cal_ratio(p3, 6.5)])
    b.index = ['b_' + x for x in b.index]

    p3_offseted = p3.copy()

    p3_offseted[['PPA_X', 'PPA_Y']] = cal_offseted(p3.values, off)

    a = pd.concat([cal_ratio(p3_offseted, 4), cal_ratio(p3_offseted, 6.5)])
    a.index = ['a_' + x for x in a.index]

    return pd.concat([b, a])


# %%
# p2 = p2[(p2.GLASS_ID == 'L2E9206A4191') & (p2.EVA_CHAMBER == 'B')]
# rst = optimize_offset(p2[['POS_X', 'POS_Y', 'PPA_X', 'PPA_Y']].values)

# %%
def cal_optimized_offset(p2):
    rst = optimize_offset(p2[['POS_X', 'POS_Y', 'PPA_X', 'PPA_Y']].values)

    r1 = pd.DataFrame(OFFSETS)
    r1.columns = ['OFFSET_X', 'OFFSET_Y', 'OFFSET_T']
    r1['PPA'] = rst

    r0 = r1[r1.PPA.isin(r1.PPA.nlargest(10))]

    r2 = r0.mean()
    r2['PPA'] = round(r2['PPA'])
    r2['PPA_BEFORE'] = \
        cal_offseted_count(p2[['POS_X', 'POS_Y', 'PPA_X', 'PPA_Y']].values)

    r2['EVENTTIME'] = p2['EVENTTIME'].max()

    r2[['OFFSET_X', 'OFFSET_Y']] = (r2[['OFFSET_X', 'OFFSET_Y']] * 2). \
                                       apply(round) / 2
    r2[['OFFSET_T']] = r2[['OFFSET_T']].apply(round)

    r2['X'] = p2['X'].mean()
    r2['Y'] = p2['Y'].mean()
    r2['T'] = p2['T'].mean()

    r2['AFTER_X'] = r2['X'] + r2['OFFSET_Y']
    r2['AFTER_Y'] = r2['Y'] + r2['OFFSET_X']
    r2['AFTER_T'] = r2['T'] - r2['OFFSET_T']

    off = r2[['OFFSET_X', 'OFFSET_Y', 'OFFSET_T']].values

    # r3 = cal_ratio_bna(p2, off)
    return pd.concat([r2, cal_ratio_bna(p2, off)])


# %%
# print('Optimization starts:....................')
# r4 = p2.groupby(['RECIPE', 'exp_label', 'prd_label', 'grp_label',
#                  'EVA_CHAMBER', 'MASK_ID', 'line']). \
#     apply(cal_optimized_offset).reset_index()
#
# r4.EVENTTIME = pd.to_datetime(r4.EVENTTIME)
#
# r4 = r4.groupby(['RECIPE', 'exp_label', 'prd_label', 'grp_label',
#                  'MASK_ID', 'line']).\
#     apply(lambda x: x.sort_values('EVENTTIME')).\
#         reset_index(drop=True)
#
# r4.to_sql('OFFSET', con=db, if_exists='replace')

def plot_data(p1, glass, chamber):
    p5 = p1[(p1.GLASS_ID == glass) & (p1.EVA_CHAMBER == chamber)]
    p5 = p5.sort_values(['POS_Y', 'POS_X'])

    ppa_teg = []
    ppa_val = []

    if p5.shape[0]:
        ppa_teg = p5[['POS_X', 'POS_Y']].values.tolist()

        p5.PPA_X = p5.POS_X + 10 * p5.PPA_X
        p5.PPA_Y = p5.POS_Y + 10 * p5.PPA_Y

        for i in p5.POS_X.unique():
            ppa_val += p5[p5.POS_X == i][['PPA_X', 'PPA_Y']].values.tolist()
            ppa_val.append([])

    return ppa_teg, ppa_val
