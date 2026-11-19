import {el,node,edition,choices,cards,table,chart,pretty,exportCsv,fail} from './ui.mjs';
import {basket,official} from './model.mjs';
let data,rows=[];
const heads=['Month','Your basket index','Published all-items index'];
const inputs=()=>[...el('weights').querySelectorAll('input')];
function preset(equal=false){
  const allot=data.weights[el('geo').value];
  inputs().forEach((item,i)=>item.value=equal?'1':allot.values[i]);
  el('weightnote').textContent=equal?'Each category has the same starting share.':allot.year+' published reference-period weights for '+el('geo').value+'.';
  update();
}
function update(){
  const geo=el('geo').value,from=el('from').value,to=el('to').value,w=inputs().map(n=>n.value===''?0:n.valueAsNumber);
  const months=data.months.filter(m=>m>=from&&m<=to);
  const series=data.series[geo],base=series[from];
  const selected=basket(base,series[to],w),all=official(base,series[to]);
  const valid=months.length && selected?.change!=null;
  el('download').disabled=!valid;
  cards([['Your basket',valid?pretty(selected.change,'%'):'Unavailable',from+' to '+to],
         ['Official all-items CPI',months.length&&all!==null?pretty(all-100,'%'):'Unavailable',geo]]);
  if(!valid){
    el('summary').textContent=from>to?'Choose an ending month on or after the starting month.':!selected?'Enter at least one positive amount and use non-negative amounts.':'A selected category has no published value at one of the endpoints.';
    ['parts','chart','legend','table'].forEach(k=>el(k).replaceChildren()); rows=[];return;
  }
  const categories=data.categories.slice(0,8),parts=selected.contributions.map((v,i)=>[categories[i],selected.shares[i],v]).sort((a,b)=>Math.abs(b[2])-Math.abs(a[2]));
  el('summary').textContent='The largest contribution by magnitude came from '+parts[0][0].toLowerCase()+' ('+pretty(parts[0][2])+' percentage points).';
  table('parts',['Category','Starting share','Contribution'],parts.map(([n,s,v])=>[n,pretty(s,'%'),pretty(v)+' pp']));
  rows=months.map(m=>{const val=basket(base,series[m],w)?.change;return [m,val==null?null:100+val,official(base,series[m])];});
  chart(months,[rows.map(r=>r[1]),rows.map(r=>r[2])],['Your basket','Published all-items CPI']);
  table('table',heads,[...rows].reverse().map(([m,a,b])=>[m,pretty(a),pretty(b)]));
}
async function start(){
  let status;[data,status]=await edition();
  el('status').textContent=status.count.toLocaleString('en-CA')+' published index observations · '+status.start+' to '+status.end+' · Retrieved '+status.retrieved;
  choices('geo',data.regions,'British Columbia');choices('from',data.months,data.months.at(-13));choices('to',data.months,data.months.at(-1));
  data.categories.slice(0,8).forEach((c,i)=>{
    const label=node('label',c),input=node('input');input.id='weight-'+i;input.type='number';input.min=0;input.step='any';input.inputMode='decimal';label.append(input);el('weights').append(label);
  });
  el('geo').onchange=()=>{if(el('weights').dataset.mode==='custom'){update();}else preset(el('weights').dataset.mode==='equal');};
  el('published').onclick=()=>{el('weights').dataset.mode='published';preset();};
  el('equal').onclick=()=>{el('weights').dataset.mode='equal';preset(true);};
  el('weights').oninput=()=>{el('weights').dataset.mode='custom';el('weightnote').textContent='Using your spending mix.';update();};
  el('from').onchange=el('to').onchange=update;
  el('download').onclick=()=>exportCsv(heads,rows,'inflation-basket-'+el('geo').value+'-'+el('to').value);
  el('content').hidden=false;preset();
}
start().catch(fail);
