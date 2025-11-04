#%% 
'''
Code Purpose: 
Author(s): Code created by Leo Rizk (leo.rizk@mail.utoronto.ca) and modified by Owen A. Johnson (ojohnson@tcd.ie)
Last Major Update: 2023-11-01
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import scienceplots; plt.style.use('science')
from astropy import units as u
from astropy.constants import G, R_sun, M_sun, R_earth, M_earth, R_jup, M_jup, L_sun, m_e, m_p, c, k_B, h, e, sigma_sb

# data dictionary 
# name: [log(EIRP), log(transmitter rate), [frequency range], sky coverage, minimum detectable flux, \
# marker shape, Drake figure of merit]

data = {}

data['Price 2020 (GBT L)'] = [12.32, -2.67, [1100, 1900], None, 6.82, '^', 993]
data['Price 2020 (GBT S)'] = [12.32, -2.64, [1800, 2800], None, 6.82, 's', 1240]
data['Price 2020 (GBT L & S)'] = [None, None, None, 22.1, 6.82, '^', None]
data['Price 2020 (Parkes)'] = [12.96, -1.73, None, 22.1, 23.18, 'p', 170]
data['Price 2020 (GBT & Parkes)'] = [None, None, [1100, 3450], 22.1, None, '^', None]
data['Parkes (2019-2020)'] = [None, None, [2600, 3450], 23.116789567277724 / 2, None, '^', None]
data['Enriquez 2017 (GBT L)'] = [12.72, -2.48, [1100, 1900], 10.6, 17.68, '^', 94.1]
data['Gray 2017 (JVLA 1.4GHz)'] = [21.30, -8.85, [1399, 1401], 22.7, 28.41, '^', 0.150]
data['Gray 2017 (JVLA 8.4GHz)'] = [21.15, -7.17, [8400, 8400], 22.7, 20.12, 's', 0.0314]
data['Harp 2016 (ATA) 1'] = [16.94, -2.02, None, None, None, '^', 358]
data['Harp 2016 (ATA) 2'] = [16.74, -2.90, None, None, None, 's', 91.4]
data['Harp 2016 (ATA) 3'] = [14.58, -2.28, None, None, None, 'p', 15.1]
data['Harp 2016 (ATA) 4'] = [15.04, -2.60, None, None, None, 'h', 12.0]
data['Harp 2016 (ATA)'] = [None, None, [1000, 9000], 193, 265, '^', None]
data['Siemion 2013 (GBT L)'] = [15.15, -1.58, [1100, 1900], 1.3, 10.21, '^', 26.7]
data['Project Phoenix (Parkes L)'] = [14.74, -1.88, None, None, 100, '^', 9.9]
data['Project Phoenix (Parkes S)'] = [14.74, -1.74, None, None, 100, 's', 22.5]
data['Project Phoenix (Parkes & NRAO)'] = [None, None, None, 18, 100, '^', None]
data['Project Phoenix (Arecibo L)'] = [13.94, -1.85, None, None, 16, 'p', 104]
data['Project Phoenix (Arecibo S)'] = [13.94, -2.29, None, None, 16, 'h', 352]
data['Project Phoenix (Arecibo)'] = [None, None, None, 18, 16, 's', None]
data['Project Phoenix (NRAO 43m)'] = [14.74, -2.22, None, None, 100, 'o', 32.4]
data['Project Phoenix (1995-2004)'] = [None, None, [1200, 3000], 18, None, '^', None]
data['Horowitz 1993 (Harvard-Smithsonian)'] = [18.04, -3.93, [1419.8, 1420.2], 28052, 938, '^', 1.17]
data['Valdes 1986 (HCRO) 1'] = [13.26, 1.36, None, 14.7, 2815, '^', 1.23e-4]
data['Valdes 1986 (HCRO) 2'] = [12.34, 3.21, None, 14.7, 351, 's', 1.74e-4]
data['Valdes 1986 (HCRO)'] = [None, None, [1516, 1517.4], 14.7, None, '^', None]
data['Tarter 1980 (NRAO 91m)'] = [13.04, 0.77, [1665.7, 1667.1], 3, 151, '^', 2.26e-3]
data['Verschuur 1973 (NRAO 91m)'] = [11.75, 2.90, None, 1.6, 188, '^', 3.73e-4]
data['Verschuur 1973 (NRAO 43m)'] = [12.58, 0.95, None, 1.6, 1289, 's', 6.92e-4]
data['Verschuur 1973 (NRAO)'] = [None, None, [1416, 1436], 1.6, None, '^', None]
data['JVLA (coherent)'] = [15.80, -7.90, None, 12500, 35, '^', 121]
data['JVLA (incoherent)'] = [17.07, -8.70, None, None, 179, 's', None]
data['MeerKAT'] = [14.62, -5.88, [544, 1712], 15240, 3.51, '^', 1.78e6]
data['LOFAR'] = [16.81, -5.90, [110, 190], 230.12, 5774, '^', None]
data['LOFTS'] = [16.81, -5.90, [110, 190], 10460.12, 5774, '^', None]
data['NenuFAR'] = [None, None, [10, 85], 258.52, None, '^', None]
data['MWA'] = [20.00, -7.00, None, None, None, '^', None]
data['SKA1 (low)'] = [14.16, -6.36, None, None, 0.808, '^', None]
data['SKA1 (mid)'] = [13.95, -5.66, None, None, 0.491, 's', None]
data['ngVLA'] = [13.89, -5.98, None, 4042.2670446847505, 0.85, '^', None]
data['CHIME'] = [None, None, [400, 800], 11663.16273, 4.98, '^', None]
data['CHORD'] = [None, None, [300, 1500], 5831.581363, 2.60, '^', None]
data['HIRAX'] = [None, None, [400, 800], 15000, 2.75, '^', None]

# JVLA: [[frequency ranges], sky coverage, minimum detectable flux]
JVLA_data = [ [[58, 84], [230, 472], [1000, 50000]] , 12500, 35]
# GBT: [[frequency ranges], [sky coverages]]
GBT_data = [
    [[1100, 1750], [1680, 2650], [3900, 6180], [7900, 11600], [11800, 15600], [18000, 27500]], 
    [9.69147842e+01, 6.36052476e+01, 9.99227761e+00, 2.73070545e+00, 2.39221129e-03, 3.47006699e-03]
]
# JVLA: [[frequency ranges], [sky coverages]]
full_JVLA_data = [
    [[230, 472], [1000, 2030], [2000, 4000], [4000, 8000], [8000, 12000], 
     [12000, 18000], [18000, 26500], [26500, 40000], [40000, 50000]], 
    [1605.78018068971, 2549.21207277804, 15735.3333728496, 316.230023973661, 32.0402215639876, 
     10.8262080145674, 2.77720312338184, 2.11383792527063, 4.9751108669488]
]
# JVLA: [[frequency ranges], [sky coverages]]
JVLA_data_2020 = [
    [[230, 472], [1000, 2030], [2000, 4000], [4000, 8000], [8000, 12000], 
     [12000, 18000], [18000, 26500], [26500, 40000], [40000, 50000]], 
    [125.591745975732, 160.349002688918, 6048.11219287954, 12.587186042345, 3.43722280317317, 
     0.503487441693812, 0.321476888880218, 0.0874726027246096, 0.0783202687079259]
]
# ngVLA: [[frequency ranges], [sky coverages]]
ngVLA_data = [
    [[1200, 3500], [3500, 12300], [12300, 20500], [20500, 34000], [30500, 50500], [70000, 116000]],
    [15735.3333728496, 316.230023973661, 10.8262080145674, 2.77720312338184, 4.9751108669488, 0.0001232498529125791]
]
# ngVLA: [[frequency ranges], [sky coverages]]
ngVLA_data_est = [
    [[1200, 3500], [3500, 12300], [12300, 20500], [20500, 34000], [30500, 50500], [70000, 116000]],
    [20733.15250119847, 1383.990928833395, 64.55933287868221, 26.124197250397962, 13.185691255853653,
     2.2493098156545686]
]
# ngVLA: [[frequency ranges], [sky coverages]]
new_ngVLA_data = [
    [[1200, 3500], [3500, 12300], [12300, 20500], [20500, 34000], [30500, 50500], [70000, 116000]],
    [4042.2670446847505, 268.7980148145315, 162.00459359782886, 99.13576047526033, 26.73741978100996,
     9.085366435827604]
]


A, B, C, D = 10 ** 0.08, 10 ** 0.002, 10 ** -0.04, 10 ** 0.05
E = A ** -2

line_pts_x_future = [full_JVLA_data[0][0][0], 
                     full_JVLA_data[0][0][0],
                     full_JVLA_data[0][0][1],
                     full_JVLA_data[0][0][1],
                     data['MeerKAT'][2][0],
                     data['MeerKAT'][2][0],
                     data['Horowitz 1993 (Harvard-Smithsonian)'][2][0],
                     data['Horowitz 1993 (Harvard-Smithsonian)'][2][0],
                     data['Horowitz 1993 (Harvard-Smithsonian)'][2][1],
                     data['Horowitz 1993 (Harvard-Smithsonian)'][2][1],
                     data['MeerKAT'][2][1],
                     data['MeerKAT'][2][1],
                     full_JVLA_data[0][2][0],
                     full_JVLA_data[0][2][0],
                     full_JVLA_data[0][2][1],
                     full_JVLA_data[0][2][1],
                     full_JVLA_data[0][3][1],
                     full_JVLA_data[0][3][1],
                     new_ngVLA_data[0][1][1],
                     new_ngVLA_data[0][1][1],
                     new_ngVLA_data[0][2][1],
                     new_ngVLA_data[0][2][1],
                     new_ngVLA_data[0][3][1],
                     new_ngVLA_data[0][3][1],
                     new_ngVLA_data[0][4][1],
                     new_ngVLA_data[0][4][1],
                     new_ngVLA_data[0][5][0],
                     new_ngVLA_data[0][5][0],
                     new_ngVLA_data[0][5][1],
                     new_ngVLA_data[0][5][1]]
                 
line_pts_y_future = [0,
                     full_JVLA_data[1][0],
                     full_JVLA_data[1][0],
                     0,
                     0,
                     data['MeerKAT'][3],
                     data['MeerKAT'][3],
                     data['Horowitz 1993 (Harvard-Smithsonian)'][3],
                     data['Horowitz 1993 (Harvard-Smithsonian)'][3],
                     data['MeerKAT'][3],
                     data['MeerKAT'][3],
                     new_ngVLA_data[1][0],
                     new_ngVLA_data[1][0],
                     full_JVLA_data[1][2],
                     full_JVLA_data[1][2],
                     full_JVLA_data[1][3],
                     full_JVLA_data[1][3],
                     new_ngVLA_data[1][1],
                     new_ngVLA_data[1][1],
                     new_ngVLA_data[1][2],
                     new_ngVLA_data[1][2],
                     new_ngVLA_data[1][3],
                     new_ngVLA_data[1][3],
                     new_ngVLA_data[1][4],
                     new_ngVLA_data[1][4],
                     0,
                     0,
                     new_ngVLA_data[1][5],
                     new_ngVLA_data[1][5],
                     0]

lines_low_frequency_x = [data['LOFAR'][2][0], data['LOFAR'][2][0], data['LOFAR'][2][1], data['LOFAR'][2][1]]
lines_low_frequency_y = [0, data['LOFTS'][3], data['LOFTS'][3], 0]

nenuFAR_x = [data['NenuFAR'][2][0], data['NenuFAR'][2][0], data['NenuFAR'][2][1], data['NenuFAR'][2][1]]
nenuFAR_y = [0, data['NenuFAR'][3], data['NenuFAR'][3], 0]

plt.figure(figsize=(15,12), dpi=200)
plt.plot(line_pts_x_future, line_pts_y_future, color='black')
plt.plot(lines_low_frequency_x, lines_low_frequency_y, color='black')
plt.plot(nenuFAR_x, nenuFAR_y, color='black')

clr = '#F07B3F'
clr2 = '#F07B3F'



for i in [1]:
    plt.gca().add_patch(patches.Polygon(
        [(new_ngVLA_data[0][i][0], new_ngVLA_data[1][i] * E), (new_ngVLA_data[0][i][1], new_ngVLA_data[1][i] * E), 
         (new_ngVLA_data[0][i][1], new_ngVLA_data[1][i]), (new_ngVLA_data[0][i][0], new_ngVLA_data[1][i])], 
        facecolor=clr, label='Very high sensitivity', zorder = 3))

for i in [0]:
    plt.gca().add_patch(patches.Polygon(
        [(new_ngVLA_data[0][i][0], new_ngVLA_data[1][i] * E), (new_ngVLA_data[0][i][1], new_ngVLA_data[1][i] * E), 
         (new_ngVLA_data[0][i][1], new_ngVLA_data[1][i]), (new_ngVLA_data[0][i][0], new_ngVLA_data[1][i])], 
        facecolor=clr, hatch = '//'))

for i in range(2, len(new_ngVLA_data[0])):
    plt.gca().add_patch(patches.Polygon(
        [(new_ngVLA_data[0][i][0], new_ngVLA_data[1][i] * E), (new_ngVLA_data[0][i][1], new_ngVLA_data[1][i] * E), 
         (new_ngVLA_data[0][i][1], new_ngVLA_data[1][i]), (new_ngVLA_data[0][i][0], new_ngVLA_data[1][i])], 
        facecolor=clr, hatch = '//'))
    
for i in [0, 2, 3, 4, 5]:
    plt.text(new_ngVLA_data[0][i][1] * D, new_ngVLA_data[1][i] * C / A, 
             'ngVLA', color=clr2, size=11, fontweight='bold')

for i in [1]:
    plt.text(new_ngVLA_data[0][i][1] * D, new_ngVLA_data[1][i] / A, 
             'ngVLA', color=clr2, size=11, fontweight='bold')


clr = '#EA5455'
clr2 = '#EA5455'

key = 'MeerKAT'
plt.gca().add_patch(patches.Polygon(
    [(data[key][2][0], data[key][3] * E), (data[key][2][1], data[key][3] * E), 
     (data[key][2][1], data[key][3]), (data[key][2][0], data[key][3])], facecolor=clr,
    label=r'High sensitivity'))
plt.text(data[key][2][0] * 10 ** -0.3, data[key][3] * C / A, key, color=clr2, size=11, fontweight='bold')

for i in range(len(GBT_data[0])):
    plt.gca().add_patch(patches.Polygon(
        [(GBT_data[0][i][0], GBT_data[1][i] * E), (GBT_data[0][i][1], GBT_data[1][i] * E), 
         (GBT_data[0][i][1], GBT_data[1][i]), (GBT_data[0][i][0], GBT_data[1][i])], 
        facecolor=clr))
    
for i in [0, 1, 5]:
    plt.text(GBT_data[0][i][1] * D, GBT_data[1][i] * C / A, 
             'GBT (2015-2021)', color=clr2, size=11, fontweight='bold')
for i in [2]:
    plt.text(GBT_data[0][i][0] * 10 ** 0.02, GBT_data[1][i] * 10 ** -0.25 / A, 
             'GBT (2015-2021)', color=clr2, size=11, fontweight='bold')
for i in [3]:
    plt.text(GBT_data[0][i][0] * 10 ** -0.53, GBT_data[1][i] * C / A, 
             'GBT (2015-2021)', color=clr2, size=11, fontweight='bold')
for i in [4]:
    plt.text(GBT_data[0][i][1] * D, GBT_data[1][i] * 10 ** -0.1 / A, 
             'GBT (2015-2021)', color=clr2, size=11, fontweight='bold')
    

clr = '#40679E'
clr2 = '#40679E'

key = 'Project Phoenix (1995-2004)'
plt.gca().add_patch(patches.Polygon(
    [(data[key][2][0], data[key][3] * E), (data[key][2][1], data[key][3] * E), 
     (data[key][2][1], data[key][3]), (data[key][2][0], data[key][3])], facecolor=clr,
    label='Mid sensitivity'))
plt.text(data[key][2][0] * 10 ** -0.7, data[key][3] * B / A, key, color=clr2, size=11, fontweight='bold')

key = 'Parkes (2019-2020)'
plt.gca().add_patch(patches.Polygon(
    [(data[key][2][0], data[key][3] * E), (data[key][2][1], data[key][3] * E), 
     (data[key][2][1], data[key][3]), (data[key][2][0], data[key][3])], facecolor=clr))
plt.text(data[key][2][0] * 10 ** -0.48, data[key][3] * 10 ** -0.25 / A, key, color=clr2, size=11, fontweight='bold')

for i in range(len(full_JVLA_data[0])):
    plt.gca().add_patch(patches.Polygon(
        [(full_JVLA_data[0][i][0], full_JVLA_data[1][i] * E), (full_JVLA_data[0][i][1], full_JVLA_data[1][i] * E), 
         (full_JVLA_data[0][i][1], full_JVLA_data[1][i]), (full_JVLA_data[0][i][0], full_JVLA_data[1][i])], 
        facecolor=clr, hatch='//'))

for i in [1, 2, 5, 8, 7]:
    plt.text(full_JVLA_data[0][i][1] * D, full_JVLA_data[1][i] * C / A, 
             'JVLA', color=clr2, size=11, fontweight='bold')

for i in [3, 6]:
    plt.text(full_JVLA_data[0][i][1] * 10 ** -0.52, full_JVLA_data[1][i] * 10 ** 0.15 / A, 
             'JVLA', color=clr2, size=11, fontweight='bold')

for i in [0, 4]:
    plt.text(full_JVLA_data[0][i][0] * 10 ** -0.15, full_JVLA_data[1][i] * C / A, 
             'JVLA', color=clr2, size=11, fontweight='bold')


clr = '#2D4059'
clr2 = '#2D4059'

key = 'Harp 2016 (ATA)'
plt.gca().add_patch(patches.Polygon(
    [(data[key][2][0], data[key][3] * E), (data[key][2][1], data[key][3] * E), 
     (data[key][2][1], data[key][3]), (data[key][2][0], data[key][3])], facecolor=clr,
    label='Low sensitivity'))
plt.text(data[key][2][0] * 10 ** -0.42, data[key][3] * C / A, key, color=clr2, size=11, fontweight='bold')

key = 'Verschuur 1973 (NRAO)'
plt.gca().add_patch(patches.Polygon(
    [(data[key][2][0], data[key][3] * E), (data[key][2][1], data[key][3] * E), 
     (data[key][2][1], data[key][3]), (data[key][2][0], data[key][3])], facecolor=clr))
plt.text(data[key][2][1] * 10 ** -0.58, data[key][3] * C / A, key, color=clr2, size=11, fontweight='bold')

key = 'Horowitz 1993 (Harvard-Smithsonian)'
plt.plot(np.mean(data[key][2]), data[key][3] / A, '|', color=clr, ms=15)
plt.text(data[key][2][1] * D, data[key][3] * C / A, key, color=clr2, size=11, fontweight='bold')

key = 'Valdes 1986 (HCRO)'
plt.plot(np.mean(data[key][2]), data[key][3] / A, '|', color=clr, ms=15)
plt.text(data[key][2][1] * 10 ** -0.5, data[key][3] * 10 ** -0.1 / A, key, color=clr2, size=11, fontweight='bold')

key = 'Tarter 1980 (NRAO 91m)'
plt.plot(np.mean(data[key][2]), data[key][3] / A, '|', color=clr, ms=15)
plt.text(data[key][2][1] * 10 ** -0.61, data[key][3] * C / A, key, color=clr2, size=11, fontweight='bold')

clr = '#40679E'
clr2 = '#40679E'


key = 'LOFAR'
plt.gca().add_patch(patches.Polygon(
    [(data[key][2][0], data[key][3] * E), (data[key][2][1], data[key][3] * E), 
     (data[key][2][1], data[key][3]), (data[key][2][0], data[key][3])], facecolor=clr))
plt.text(data[key][2][1] * 10 ** -0.22, data[key][3] * C*1.4 / A, key, color=clr2, size=11, fontweight='bold')

key = 'LOFTS'
plt.gca().add_patch(patches.Polygon(
    [(data[key][2][0], data[key][3] * E), (data[key][2][1], data[key][3] * E), 
     (data[key][2][1], data[key][3]), (data[key][2][0], data[key][3])], facecolor=clr, hatch='//'))
plt.text(data[key][2][1] * 10 ** -0.45, data[key][3] * C / A, key, color=clr2, size=11, fontweight='bold')

key = 'NenuFAR'
plt.gca().add_patch(patches.Polygon(
    [(data[key][2][0], data[key][3] * E), (data[key][2][1], data[key][3] * E),
        (data[key][2][1], data[key][3]), (data[key][2][0], data[key][3])], facecolor=clr, hatch='//'))
plt.text(data[key][2][1] * 10 ** -0.3, data[key][3] * C*1.5 / A, key, color=clr2, size=11, fontweight='bold')

# plt.axvspan(0, 550, color='#EA5455', alpha=0.5)

clr = '#F07B3F'
clr2 = '#F07B3F'



plt.xscale('log')
plt.yscale('log')
plt.xlim(10 ** 1.6, 10 ** 5.6)
plt.ylim(10 ** -3, 10 ** 4.75)

plt.xticks(ticks=[100, 1000, 10000, 100000], labels=['0.1', '1', '10', '100'], fontsize=17)
plt.yticks(ticks=[0.01, 0.1, 1, 10, 100, 1000, 10000], labels=['0.01', '0.1', '1', '10', '100', '1000', '10000'], fontsize=17)

plt.xlabel('Observing frequency  (GHz)', fontsize=22)
plt.ylabel(r'Sky coverage  (deg$^2$)', fontsize=22)
#plt.title('Extent of SETI projects in parameter space', fontsize=18)

# plt.gcf().set_size_inches(15, 12)
# plt.rc('font', size=15)
plt.legend(fontsize=17, loc='upper right')
plt.grid()
plt.savefig('SETI-Frequency-Parameter-Space.pdf', bbox_inches='tight')
plt.show()