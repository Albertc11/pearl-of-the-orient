# Official C&SD district populations. 1981: domestic-household persons from 1981 District Board Tabulations,
# scaled to census whole-territory 5,109,812; Mong Kok+Yau Ma Tei -> YTM; Tsuen Wan split into TW/Kwai Tsing by 1991 ratio.
K=['CW','WC','EA','SO','YT','SS','KC','WT','KT','KW','TW','TM','YL','NO','TP','ST','SK','IS']
c81={'CW':277520,'WC':228414,'EA':468540,'SO':228868,'KC':482213,'KT':611179,'YT':240442+179750,'SS':455640,'WT':489003,
     'IS':50649,'NO':114644,'SK':44682,'ST':115888,'TP':75129,'TWall':610355,'TM':126883,'YL':186761}
f81=5109812/4986560
c91=dict(zip(K,[253383,180309,560200,257101,282060,380615,402934,386572,578502,440807,271576,380683,229724,165666,202117,506368,130418,47459]))
c96=dict(zip(K,[259224,171656,594087,287670,260573,365927,378205,396220,587071,470726,270801,463703,341030,231907,284640,582993,197876,63057]))
c01=dict(zip(K,[262300,167600,617100,290800,282400,354100,381900,444700,562700,476900,275800,489300,449600,298900,311100,629200,327900,86800]))
c11=dict(zip(K,[251519,152608,588094,278655,307878,380855,377351,420183,622152,511167,304637,487546,578529,304134,296853,630273,436627,141327]))
c16=dict(zip(K,[243266,180123,555034,274994,342970,405869,418732,425235,648541,520572,318916,489299,614178,315270,303926,659794,461864,156801]))
c21=dict(zip(K,[235953,166695,529603,263278,310647,431090,410634,406802,673166,495798,320094,506879,668080,309631,316470,692806,489037,185282]))
r=c91['KW']/(c91['KW']+c91['TW'])
c81['KW']=c81['TWall']*r; c81['TW']=c81['TWall']*(1-r)
print('1981 total',round(sum(c81[k] for k in K)*f81), ' 2021 total',sum(c21.values()))
for k in K:
    v=[round(c81[k]*f81),c91[k],c96[k],c01[k],c11[k],c16[k],c21[k]]
    print(k, v)
old={'CW':(300,280),'WC':(240,200),'EA':(370,520),'SO':(120,220),'YT':(420,340),'SS':(480,420),'KC':(450,420),'WT':(400,460),'KT':(450,590),'KW':(150,420),'TW':(250,300),'TM':(30,130),'YL':(120,140),'NO':(100,110),'TP':(50,60),'ST':(30,100),'SK':(20,30),'IS':(40,40)}
e71={k:c81[k]*f81*old[k][0]/old[k][1] for k in K}; sc=3936630/sum(e71.values())
print('JS:')
for k in K:
    v=[round(e71[k]*sc/1000,1),round(c81[k]*f81/1000,1),c91[k]/1000,c96[k]/1000,c01[k]/1000,c11[k]/1000,c16[k]/1000,c21[k]/1000]
    print(f"{k}:[{','.join(str(round(x,1)) for x in v)}],")
import csv
names=dict(CW='Central and Western',WC='Wan Chai',EA='Eastern',SO='Southern',YT='Yau Tsim Mong',SS='Sham Shui Po',KC='Kowloon City',WT='Wong Tai Sin',KT='Kwun Tong',KW='Kwai Tsing',TW='Tsuen Wan',TM='Tuen Mun',YL='Yuen Long',NO='North',TP='Tai Po',ST='Sha Tin',SK='Sai Kung',IS='Islands')
out=r'hk-district-population.csv'
with open(out,'w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['district','1971_estimated','1981','1991','1996','2001','2011','2016','2021','note'])
    for k in K:
        note='1981 derived: Tsuen Wan split by 1991 ratio' if k in('KW','TW') else ('1981 = Mong Kok + Yau Ma Tei' if k=='YT' else '')
        w.writerow([names[k],round(e71[k]*sc),round(c81[k]*f81),c91[k],c96[k],c01[k],c11[k],c16[k],c21[k],note])
