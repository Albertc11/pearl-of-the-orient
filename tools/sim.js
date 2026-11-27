// Headless balance simulator: runs the game's own script with bot strategies.
// Usage: node tools/sim.js [runs]   (from the project folder)
const fs = require('fs'), vm = require('vm');
const html = fs.readFileSync('hk-tycoon.html', 'utf8');
// run every inline script in page order (map data first, then the game)
const code = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(m => m[1]).join('\n;\n');
const el = () => ({ innerHTML: '', textContent: '', style: {}, value: '', disabled: false });
const els = {};
const ctx = {
  console, setTimeout: () => 0, clearTimeout: () => 0, innerWidth: 1000,
  localStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {}, clear: () => {} },
  document: { querySelector: q => els[q] || (els[q] = { ...el(), setAttribute() {} }), querySelectorAll: () => [],
              body: { classList: { contains: () => false, add() {}, toggle: () => false } } },
};
ctx.window = ctx;
vm.createContext(ctx);
vm.runInContext(code, ctx);
vm.runInContext(`
var __ev=[]; var __modal=null; showModal=function(h){__modal=h}; closeModal=function(){__modal=null}; render=function(){};
const GOOD=/concession|10% stake|Relocate|60% of cash|Hold your nerve|retention|Inject/;
function choosePolicy(e){
  const ok=c=>!c.ok||c.ok();
  if(!(e.choices&&(!e.cond||e.cond()))) return -1;
  const i=e.choices.findIndex(c=>ok(c)&&GOOD.test(c.l)); if(i>=0) return i;
  for(let j=e.choices.length-1;j>=0;j--) if(ok(e.choices[j])) return j;
  return -1;
}
function playYear(){
  A.advance();
  let guard=0;
  while(guard++<50 && queueHasEvent()){ A.choose(choosePolicy(A._cur)); }
}
function queueHasEvent(){ return __modal && !/ANNUAL REPORT|FINAL RECKONING/.test(__modal); }
const interest=()=>s.props.reduce((a,p)=>a+p.loan,0)*mortRate(s.year)+s.devs.reduce((a,d)=>a+d.loan,0)*mortRate(s.year);
function cautious(){
  for(let j=0;j<4;j++){const k=pick(D).k,t=pick(['flat','shop','building']),c=buyCost(k,t);if(s.cash-c.need>interest()*1.5+c.loan*mortRate(s.year))A.buyProp(k,t);}
  if(s.auctions[0]&&s.cash>s.auctions[0].land*.5+s.auctions[0].build+interest()*2)A.bidSite(s.auctions[0].id,1);
  for(const k of ['trading','food','port','retail','bank','broker']){const b=BZ[k];if(!s.biz[k]&&s.year>=b.from&&s.cash>b.cost*CPI(s.year)*3&&(!b.req||(face()>=b.req.face&&netWorth()>=b.req.nw*CPI(s.year))))A.buyBiz(k);}
}
function aggressive(){
  // recycle equity: remortgage everything to the max loan-to-value, then redeploy the cash
  s.props.forEach(p=>A.remortgage(p.id));
  const buffer=()=>interest()*1.2;
  for(const a of [...s.auctions]) if(s.cash-a.land*.75>a.build+buffer()) A.bidSite(a.id,2);
  for(const k of ['trading','port','retail','bank','broker','junket']){const b=BZ[k];if(!s.biz[k]&&s.year>=b.from&&(!b.to||s.year<b.to)&&s.cash>b.cost*CPI(s.year)*2+buffer()&&(!b.req||(face()>=b.req.face&&netWorth()>=b.req.nw*CPI(s.year))))A.buyBiz(k);}
  let n=0; while(n++<400){const k=pick(D).k,t=pick(['building','office','shop']),c=buyCost(k,t);if(PT[t].only&&!PT[t].only.includes(k))continue;if(s.cash-c.need>buffer()+c.loan*mortRate(s.year))A.buyProp(k,t);else break;}
}
// moderate: like aggressive, but never remortgages and keeps three years' interest in cash
function moderate(){
  const buffer=()=>interest()*3;
  for(const a of [...s.auctions]) if(s.cash-a.land*.5>a.build+buffer()) A.bidSite(a.id,1);
  for(const k of ['trading','port','retail','bank','broker','junket']){const b=BZ[k];if(!s.biz[k]&&s.year>=b.from&&(!b.to||s.year<b.to)&&s.cash>b.cost*CPI(s.year)*2+buffer()&&(!b.req||(face()>=b.req.face&&netWorth()>=b.req.nw*CPI(s.year))))A.buyBiz(k);}
  let n=0; while(n++<400){const k=pick(D).k,t=pick(['building','office','shop']),c=buyCost(k,t);if(PT[t].only&&!PT[t].only.includes(k))continue;if(s.cash-c.need>buffer()+c.loan*mortRate(s.year))A.buyProp(k,t);else break;}
}
function tycoon(){
  // list in hot markets, sell more stock while hot, buy back cheaply after crashes
  const mood=hsiMood(s.year);
  if(!s.ipo&&mood>1.1&&ipoOk()){A.ipo();__ev.push(s.year+'IPO');}
  else if(s.ipo&&mood>1.2&&s.ipo.own>=.45){A.placement();__ev.push(s.year+'+10%');}
  else if(s.ipo&&mood<.55&&s.cash>privCost()*1.5){A.privatise();__ev.push(s.year+'priv');}
  aggressive();
}
function runGame(strategy){
  localStorage.clear(); A.start(START); s.diff=SIMDIFF; A.useLoan=true; const path=[]; __ev=[];
  for(let i=0;i<60&&!s.over;i++){ if(s.year>=2025){A.advance();break;} strategy(); playYear();
    if(s.pendingDeath){ if(s.kids){A.chooseHeir(0);__ev.push(s.year+'heir');} else successionModal('death'); }
    if(s.year%10==0) path.push(s.year+':'+money(netWorth())); }
  return {nw:netWorth(),over:s.over,path:path.join(' '),props:s.props.length,casino:!!s.biz.casino,ipo:__ev.join(',')+(s.ipo?' own='+Math.round(s.ipo.own*100)+'%':'')};
}
`, ctx);
vm.runInContext('var START='+JSON.stringify(process.argv[4]||'chiu'),ctx);
vm.runInContext('var SIMDIFF='+JSON.stringify(process.argv[5]||'easy'),ctx);
const runs = +process.argv[2] || 5;
const only = process.argv[3];  // optional: run one strategy, e.g. node tools/sim.js 5 tycoon
for (const name of ['cautious', 'moderate', 'aggressive', 'tycoon'].filter(n => !only || n === only)) {
  const res = [];
  for (let i = 0; i < runs; i++) res.push(vm.runInContext(`runGame(${name})`, ctx));
  res.sort((a, b) => a.nw - b.nw);
  console.log(`\n== ${name} (${runs} runs)`);
  res.forEach(r => console.log(`${vm.runInContext(`money(${r.nw})`, ctx).padStart(12)} ${r.over || ''} props=${r.props} casino=${r.casino} ${r.ipo ? 'listing=' + r.ipo : ''} | ${r.path}`));
}
