export function basket(start, current, weights) {
  const sum=weights.reduce((a,b)=>a+b,0);
  if(!(sum>0) || weights.some(v=>!Number.isFinite(v)||v<0)) return null;
  const contributions=weights.map((w,i)=>{
    if(!w)return 0;
    const a=start?.[i],b=current?.[i];
    return a>0 && b>0 ? w/sum*100*(b/a-1) : null;
  });
  const change=contributions.includes(null)?null:contributions.reduce((a,b)=>a+b,0);
  return {change,contributions,shares:weights.map(w=>w/sum*100)};
}
export function official(start,current) {
  return start?.at(-1)>0 && current?.at(-1)>0 ? 100*current.at(-1)/start.at(-1) : null;
}
