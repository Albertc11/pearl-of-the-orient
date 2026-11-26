import xlrd,json,datetime,collections
def num(v):
    try: return float(v)
    except: return None
def rows(f,idx):
    return xlrd.open_workbook('data/raw/'+f+'.xls').sheet_by_index(idx)
# PPI all classes
sh=rows('his_data_4',2); PPI={}
for r in range(10,56):
    y=num(sh.cell_value(r,2)); v=num(sh.cell_value(r,26))
    if y and v: PPI[int(y)]=v
old={1970:6,1971:6.5,1972:9,1973:9.5,1974:8,1975:8.5,1976:10,1977:12,1978:16,1979:25,1980:33}
for y in range(1970,1980): PPI[y]=round(old[y]*PPI[1980]/old[1980],1)
# Regional class B avg price & rent per m2
def reg(f):
    out={'HK':{},'KL':{},'NT':{}}
    a=rows(f,3)
    for r in range(11,a.nrows):
        y=num(a.cell_value(r,2))
        if not y or y>1998: continue
        hk,kl,nk,nt=[num(a.cell_value(r,c)) for c in (18,21,24,27)]
        out['HK'][int(y)]=hk; out['KL'][int(y)]=(kl+nk)/2 if kl and nk else (kl or nk); out['NT'][int(y)]=nt
    b=rows(f,4)
    for r in range(11,b.nrows):
        y=num(b.cell_value(r,2))
        if not y: continue
        for k,c in zip(('HK','KL','NT'),(14,17,20)): out[k][int(y)]=num(b.cell_value(r,c))
    return out
P=reg('his_data_2'); R=reg('his_data_1')
YLD={k:{y:round(R[k][y]*12/P[k][y],4) for y in P[k] if R[k].get(y) and P[k][y]} for k in P}
PSQFT={k:{y:round(P[k][y]/10.764) for y in P[k] if P[k][y]} for k in P}
# CPI
ds=json.load(open('data/raw/cpi.json'))['dataSet']
cc={int(r['period']):r['figure'] for r in ds if r['freq']=='Y' and r['sv']=='CC_CM_1920' and r['svDesc']=='Index' and r['figure']!=''}
ca={int(r['period']):r['figure'] for r in ds if r['freq']=='Y' and r['sv']=='A_CM_1920' and r['svDesc']=='Index' and r['figure']!=''}
cpi={y:v for y,v in cc.items() if y<=2025}
for y in range(1975,1981): cpi[y]=ca[y]*cc[1981]/ca[1981]
infl={1974:.027,1973:.15,1972:.18,1971:.06,1970:.03}  # estimated inflation into the following year
for y in (1974,1973,1972,1971,1970): cpi[y]=cpi[y+1]/(1+infl[y])
CPI={y:round(cpi[y]/cpi[1970],3) for y in sorted(cpi)}
# Best lending rate: time-weighted annual avg from effective dates (1971-79), monthly avgs from 1980
eff=sorted((r['effect_date'],r['best_lending_rate']) for r in json.load(open('data/raw/blr_eff.json'))['result']['records'] if r['best_lending_rate'] is not None)
BLR={}
for y in range(1971,1980):
    tot=0
    for d in range(365):
        day=(datetime.date(y,1,1)+datetime.timedelta(d)).isoformat()
        cur=[v for e,v in eff if e<=day]; tot+=cur[-1] if cur else eff[0][1]
    BLR[y]=round(tot/365,2)
BLR[1970]=eff[0][1]
by=collections.defaultdict(list)
for x in json.load(open('data/raw/blr_avg.json'))['result']['records']:
    if x.get('best_lending_rate') is not None: by[int(x['end_of_month'][:4])].append(x['best_lending_rate'])
for y,v in by.items():
    if y<=2025: BLR[y]=round(sum(v)/len(v),2)
BLR=dict(sorted(BLR.items()))
print('first eff',eff[:3])
for n,d in [('PPI',PPI),('CPI',CPI),('BLR',BLR)]: print(n,json.dumps({str(k):d[k] for k in sorted(d)}).replace('"','').replace(' ',''))
print('YLD',json.dumps(YLD).replace('"','').replace(' ',''))
print('PSQFT',json.dumps(PSQFT).replace('"','').replace(' ',''))
import csv
HSI={1970:211.64,1971:341.36,1972:843.40,1973:433.68,1974:171.11,1975:350.00,1976:447.67,1977:404.02,1978:495.51,1979:879.38,1980:1473.59,1981:1405.82,1982:783.82,1983:874.94,1984:1200.38,1985:1752.45}
import json as _j
yh=_j.load(open('data/raw/hsi_yahoo.json'))['chart']['result'][0]
for ts,v in zip(yh['timestamp'],yh['indicators']['quote'][0]['close']):
    if v: 
        yy=datetime.datetime.utcfromtimestamp(ts+28800).year
        if 1986<=yy<=2025: HSI[yy]=round(v,2)
out=r'hk-market-data.csv'
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['year','rvd_price_index_1999_100','hsi_year_end','best_lending_rate_pct','cpi_1970_1','psf_HK_island','psf_kowloon','psf_NT','yield_HK_island','yield_kowloon','yield_NT','estimated'])
    for y in range(1970,2026):
        est=[]
        if y<1980: est.append('price index')
        if y<1975: est.append('cpi')
        if y==1970: est.append('lending rate')
        if y<1986: est.append('psf/yield (not published)')
        w.writerow([y,PPI[y],HSI[y],BLR[y],CPI[y]]+[PSQFT[r].get(y,'') for r in('HK','KL','NT')]+[YLD[r].get(y,'') for r in('HK','KL','NT')]+['; '.join(est)])
