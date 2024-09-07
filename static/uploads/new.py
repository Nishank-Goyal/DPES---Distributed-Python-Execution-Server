#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import math
import warnings
warnings.filterwarnings('ignore')

xls = pd.ExcelFile('C:/Users/Nishank/OneDrive/Desktop/Network Planning Tool_V6.xlsm')
df = pd.read_excel(xls, 'c-M data')

cols = df.columns.tolist()

mmfc = df
plan = df[df['NBR Plan'] != 'Yes']
final = pd.DataFrame(columns=cols)
result = pd.DataFrame()

df3 = pd.DataFrame()  # Initialize an empty DataFrame
for index, row in plan.iterrows():
    Cell_id = row["Cell ID"]
    Site_id = row["Site ID"]
    long_a = row["Long(in decimal)"]
    lat_a = row["Lat(in decimal)"]
    azi_a = row["AZIMUTH"]

    Dist = []
    for long_b, lat_b in zip(mmfc["Long(in decimal)"], mmfc["Lat(in decimal)"]):
        d = 108 * (math.sqrt((long_a - long_b) * (long_a - long_b) + (lat_a - lat_b) * (lat_a - lat_b)))
        Dist.append(d)
    mmfc["Distance"] = Dist

    mmfc = mmfc.sort_values(by=['Distance'])

    StoS = []
    StoS_final = []
    StoA = []
    StoA_final = []
    StoB = []
    StoB_final = []
    Azi = []
    Grade = []
    for long_b, lat_b, azi_b in zip(mmfc["Long(in decimal)"], mmfc["Lat(in decimal)"], mmfc["AZIMUTH"]):
        n = math.degrees(math.atan2(lat_b - lat_a, long_b - long_a))
        StoS.append(n)

        m = -90 - int(n) if n <= -90 else 270 - int(n)
        StoS_final.append(m)

        p = 360 + (azi_b - m) if m > azi_b else azi_b - m
        StoA.append(p)

        q = 360 - p if p > 180 else p
        StoA_final.append(q)

        r = 360 + (azi_a - m) if m > azi_a else azi_a - m
        StoB.append(r)

        s = r - 180 if r > 180 else 180 - r
        StoB_final.append(s)

        t = 10 if (s + q) < 10 else s + q
        Azi.append(t)

        x = d * t
        Grade.append(x)

    mmfc["S to S"] = StoS
    mmfc["S to S Final"] = StoS_final
    mmfc["S to A"] = StoA
    mmfc["S to A Final"] = StoA_final
    mmfc["S to B"] = StoB
    mmfc["S to B Final"] = StoB_final
    mmfc["Azi"] = Azi
    mmfc["Grade"] = Grade

    StoS = []
    StoS_final = []
    StoA = []
    StoA_final = []
    StoB = []
    StoB_final = []
    Azi = []
    Grade = []

    mmfc = mmfc.sort_values(by=['Grade'])

    df2 = pd.DataFrame()
    df2 = mmfc[['Cell ID', 'Site ID', 'Distance', 'Azi', 'Grade']].copy().iloc[:25]
    df2["Cell ID(Plan)"] = Cell_id
    df2["Site ID(Plan)"] = Site_id
    df3 = pd.concat([df3, df2])  # Concatenate DataFrames

# Print the final result
print(df3)
