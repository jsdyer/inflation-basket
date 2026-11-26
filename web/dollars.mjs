import {convertDollars} from './model.mjs';
const $=id=>document.getElementById(id);
const currency=value=>new Intl.NumberFormat('en-CA',{style:'currency',currency:'CAD',maximumFractionDigits:2}).format(value);
let history;
function endpoint(region,value){return value==='latest'?{label:history.latest_month[region].date+' monthly CPI',index:history.latest_month[region].index}: {label:value+' full-year average',index:history.annual[region][value]?.index};}
function choices(){const region=$('dollar-geo').value,years=Object.keys(history.annual[region]).sort(),oldFrom=$('dollar-from').value,oldTo=$('dollar-to').value;
 for(const id of ['dollar-from','dollar-to']){const list=$(id);list.replaceChildren(...years.map(y=>new Option(y+' · full year',y)));}
 $('dollar-to').append(new Option('Latest published month · '+history.latest_month[region].date,'latest'));
 $('dollar-from').value=years.includes(oldFrom)?oldFrom:years.includes('1962')?'1962':years[0];
 $('dollar-to').value=oldTo==='latest'||years.includes(oldTo)?oldTo:'latest';calculate();
}
function calculate(){const region=$('dollar-geo').value,a=endpoint(region,$('dollar-from').value),b=endpoint(region,$('dollar-to').value),amount=$('dollar-amount').valueAsNumber;
 try{const r=convertDollars(amount,a.index,b.index);$('dollar-result').textContent=currency(r.amount);$('dollar-explanation').textContent=currency(amount)+' in '+a.label+' corresponds to '+currency(r.amount)+' using '+b.label+' for '+region+'. CPI change: '+r.change.toLocaleString('en-CA',{maximumFractionDigits:2})+'%.';
 $('dollar-indexes').textContent='Calculation: '+amount.toLocaleString('en-CA')+' × '+b.index.toFixed(4)+' ÷ '+a.index.toFixed(4)+'. '+history.coverage[region].first_complete_year+'–'+history.coverage[region].last_complete_year+' complete annual averages available.';
 $('dollar-export').disabled=false;
 }catch(err){$('dollar-result').textContent='—';$('dollar-explanation').textContent=err.message;$('dollar-indexes').textContent='';$('dollar-export').disabled=true;}
}
async function start(){try{const response=await fetch('./data/dollars.json');if(!response.ok)throw new Error('missing');history=await response.json();if(history.schema!=='coolcode.dollar-history.v1'||!history.regions.includes('Canada'))throw new Error('schema');
 $('dollar-geo').replaceChildren(...history.regions.map(g=>new Option(g,g)));$('dollar-geo').value='Canada';$('dollar-status').textContent='Canada annual history begins in '+history.coverage.Canada.first_complete_year+'. Source checked '+history.checked_at.slice(0,10)+'. Latest published month: '+history.latest_month.Canada.date+'.';choices();$('dollar-geo').onchange=choices;
 for(const id of ['dollar-amount','dollar-from','dollar-to'])$(id).addEventListener('input',calculate);
 $('dollar-export').onclick=()=>{const region=$('dollar-geo').value,a=endpoint(region,$('dollar-from').value),b=endpoint(region,$('dollar-to').value),amount=$('dollar-amount').valueAsNumber,r=convertDollars(amount,a.index,b.index);
 const obj={geography:region,amount,from:a,to:b,result:r.amount,cpi_change_percent:r.change,source:history.source,source_checked_at:history.checked_at,method:history.method};const url=URL.createObjectURL(new Blob([JSON.stringify(obj,null,2)],{type:'application/json'})),link=document.createElement('a');link.href=url;link.download='historical-dollar-comparison.json';link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
 }catch{$('dollar-status').textContent='The historical-dollar snapshot could not be read. The spending-basket calculator remains available.';$('dollar-controls').hidden=true;}}
start();
