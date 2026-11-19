
export const el = id => document.getElementById(id);
export function node(tag,text,css){
  const obj=document.createElement(tag);
  if(text!==undefined)obj.textContent=text;
  if(css)obj.className=css;
  return obj;
}
export async function edition(){
  const files=await Promise.all(['edition','status'].map(async name=>{
    const response=await fetch('./data/'+name+'.json');
    if(!response.ok)throw new Error('Missing source snapshot');
    return response.json();
  }));
  return files;
}
export function choices(id,items,preferred){
  const input=el(id);
  input.replaceChildren(...items.map(item=>Array.isArray(item)?new Option(item[1],item[0]):new Option(item,item)));
  if([...input.options].some(o=>o.value===preferred))input.value=preferred;
}
export function cards(items){
  el('cards').replaceChildren(...items.map(([name,value,d])=>{
    const card=node('article',undefined,'kpi');card.append(node('h3',name),node('p',value,'big'),node('p',d,'fine'));return card;
  }));
}
export function table(id,head,rows){
  const grid=el(id),thead=node('thead'),tr=node('tr'),tb=node('tbody');
  for(const col of head)tr.append(node('th',col));
  thead.append(tr);
  for(const data of rows){
    const line=node('tr');
    data.forEach((entry,i)=>line.append(node(i?'td':'th',entry)));
    tb.append(line);
  }
  grid.replaceChildren(thead,tb);
}
export function exportCsv(headers,rows,name){
  const quote=v=>'"'+String(v??'').replaceAll('"','""')+'"';
  const data=[headers,...rows].map(row=>row.map(quote).join(',')).join('\r\n');
  const url=URL.createObjectURL(new Blob([data],{type:'text/csv;charset=utf-8'}));
  const a=node('a');a.href=url;a.download=name+'.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1200);
}
function svg(tag,attrs,text){
  const e=document.createElementNS('http://www.w3.org/2000/svg',tag);
  Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,v));
  if(text!==undefined)e.textContent=text;return e;
}
export function chart(dates,series,labels){
  const plot=svg('svg',{viewBox:'0 0 760 210',role:'img','aria-label':labels.join(' and ')+' over time. The values are available in the history table.'});
  const values=series.flat().filter(v=>Number.isFinite(v));
  if(!values.length){el('chart').replaceChildren(node('p','No comparable values in this window.'));return;}
  const min=Math.floor(Math.min(...values)),max=Math.max(min+1,Math.ceil(Math.max(...values)));
  const x=i=>70+672*i/Math.max(1,dates.length-1),y=v=>165-149*(v-min)/(max-min);
  for(const v of [min,(min+max)/2,max]){
    plot.append(svg('line',{x1:70,x2:742,y1:y(v),y2:y(v),stroke:'#d4d9d1'}),svg('text',{x:62,y:y(v)+4,'text-anchor':'end',fill:'#36483d','font-size':14},Intl.NumberFormat('en-CA',{maximumFractionDigits:1,notation:'compact'}).format(v)));
  }
  series.forEach((vals,k)=>{
    let path='',live=false;const stroke=k?'var(--second)':'var(--accent)';
    vals.forEach((v,i)=>{
      if(!Number.isFinite(v)){live=false;return;}
      path+=(live?'L':'M')+x(i)+' '+y(v)+' ';live=true;
      const point=svg('circle',{cx:x(i),cy:y(v),r:1.8,fill:stroke});point.append(svg('title',{},dates[i]+' · '+labels[k]+' · '+v.toLocaleString('en-CA')));plot.append(point);
    });
    plot.append(svg('path',{d:path,fill:'none',stroke,'stroke-width':2.4,'stroke-dasharray':k?'6 3':'none'}));
  });
  plot.append(svg('text',{x:70,y:196},dates[0]),svg('text',{x:742,y:196,'text-anchor':'end'},dates.at(-1)));
  el('legend').replaceChildren(...labels.map(s=>node('span',s)));el('chart').replaceChildren(plot);
}
export const pretty=(v,unit='')=> v==null?'Unavailable':new Intl.NumberFormat('en-CA',{maximumFractionDigits:2}).format(v)+(unit==='%'?'%':unit?' '+unit:'');
export function fail(){el('status').textContent='The published snapshot could not be read. Reload or open the source linked below.';el('content').hidden=true;}
