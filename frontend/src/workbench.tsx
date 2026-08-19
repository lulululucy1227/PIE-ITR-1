import { useRef, useState } from "react";

type Case = { id:string; ticket:string; todo:boolean; notes:string; prepared?:any; analysis?:any; translated?:any; language:"ZH"|"ORIGINAL"; loading?:string; error?:string; generations:Record<string,number> };
const api = async (path:string, body:object) => (await fetch(`/api${path}`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body) })).json();
const fresh = ():Case => ({ id:crypto.randomUUID(), ticket:"", todo:false, notes:"", language:"ORIGINAL", generations:{} });

export function App() {
  const [cases,setCases] = useState<Case[]>([fresh()]);
  const [active,setActive] = useState(0);
  const [tokenOpen,setTokenOpen] = useState(false); const [curl,setCurl] = useState(""); const [tokenMessage,setTokenMessage] = useState("");
  const casesRef = useRef(cases); casesRef.current = cases;
  const current = cases[active];
  const patch = (id:string, data:Partial<Case>) => setCases(items => items.map(item => item.id === id ? {...item,...data} : item));
  const live = (id:string, operation:string, generation:number) => casesRef.current.some(item => item.id === id && item.generations[operation] === generation);
  const run = async (item:Case, operation:string, loading:string, action:()=>Promise<any>, apply:(result:any)=>Partial<Case>) => {
    const generation = (item.generations[operation] || 0) + 1;
    setCases(items => items.map(value => value.id === item.id ? {...value, generations:{...value.generations,[operation]:generation}, loading, error:undefined} : value));
    try { const result = await action(); if (live(item.id,operation,generation)) patch(item.id,apply(result)); }
    catch { if (live(item.id,operation,generation)) patch(item.id,{loading:undefined,error:"Local API operation failed."}); }
  };
  const analyze = (item=current) => item.prepared && run(item,"analyze","Analyzing...",() => api("/cases/analyze",{case:{...(item.prepared.existing_case || item.prepared.fields),...(item.prepared.analysis || {}),context_pack:item.prepared.context_pack}}), result => ({analysis:result,translated:undefined,language:"ORIGINAL",loading:"Ready for review"}));
  const load = () => run(current,"prepare","Loading case...",() => api("/cases/prepare",{source:"nextop",ticket_no:current.ticket}), result => {
    if (!result.success) return {loading:undefined,error:result.message || "Case could not be loaded."};
    const preparedCase = {...current,prepared:result.prepared};
    queueMicrotask(() => analyze(preparedCase));
    return {prepared:result.prepared,analysis:undefined,translated:undefined,loading:"Building context and analyzing..."};
  });
  const translate = () => current.analysis && (current.translated ? patch(current.id,{language:"ZH"}) : run(current,"translate","Preparing Chinese review...",() => api("/cases/translate",{analysis:current.analysis}), result => ({translated:result,language:"ZH",loading:"Ready for review"})));
  const commit = () => current.prepared && run(current,"commit","Writing...",() => api("/cases/commit",{prepared:current.prepared,include_itr_todo:current.todo,todo_dirty:true}), result => ({loading:result.success ? "Complete" : undefined,error:result.success ? undefined : result.message}));
  const close = (id:string) => setCases(items => { const next=items.filter(item=>item.id!==id); setActive(index=>Math.min(index,Math.max(0,next.length-1))); return next.length ? next : [fresh()]; });
  const review = current.language === "ZH" && current.translated ? current.translated : current.analysis;
  const logiqSupported = current.analysis?.capability?.logiq === "supported";
  return <main>
    <header><div className="tabs">{cases.map((item,index)=><button className={index===active?"active":""} onClick={()=>setActive(index)} key={item.id}>{item.ticket || "New Case"}</button>)}<button onClick={()=>{setCases(items=>[...items,fresh()]);setActive(cases.length);}}>+</button></div></header>
    <section className="status">{current.loading || current.error || "Ready"}{current.error?.includes("authentication")&&<button onClick={()=>setTokenOpen(true)}>Update Nextop Token</button>}</section>
    <div className="workbench"><aside><h2>Context</h2><label>Ticket<input value={current.ticket} onChange={event=>patch(current.id,{ticket:event.target.value})} onKeyDown={event=>event.key==="Enter"&&load()}/></label><button onClick={load}>Search / Load</button><button onClick={()=>setTokenOpen(true)}>Update Nextop Token</button>{current.prepared&&<><p>Reference: {current.prepared.ticket_no}</p><label className="todo"><input type="checkbox" checked={current.todo} onChange={event=>patch(current.id,{todo:event.target.checked})}/> Add to ITR Todo</label><textarea placeholder="Session notes" value={current.notes} onChange={event=>patch(current.id,{notes:event.target.value})}/><button onClick={()=>close(current.id)}>Close Case</button></>}</aside>
    <article><div className="tools"><h1>Case Review</h1><button disabled={!current.prepared} onClick={()=>analyze()}>Re-analyze</button><button onClick={()=>patch(current.id,{language:"ORIGINAL"})}>Original</button><button disabled={!current.analysis} onClick={translate}>中文</button><button className="logiq" disabled={!logiqSupported} title={logiqSupported ? "Copies device name and opens LogiQ" : "LogiQ is unavailable until product capability is confirmed"} onClick={()=>{const device=current.prepared?.fields?.["Device name"] || current.prepared?.fields?.device_name;if(device) navigator.clipboard.writeText(device);window.open("https://logiq.cloud-cn.mammotion.com/","_blank")}}>LogiQ · Logs</button></div>
    {review ? <Review value={review} original={current.analysis}/> : <p className="empty">Load a case to automatically build context and analyze it.</p>}
    <section className="reply"><h3>Email Reply</h3><pre>{current.analysis?.reply_en || "—"}</pre>{current.analysis?.reply_en&&<button onClick={()=>navigator.clipboard.writeText(current.analysis.reply_en)}>Copy Reply</button>}</section>
    <button className="commit" disabled={!current.prepared} onClick={commit}>{current.prepared?.can_update?"Update ITR":"Create in ITR"}</button></article></div>
  {tokenOpen&&<div className="token-modal"><section><h2>Update Nextop Token</h2><p>Log in to Nextop, open DevTools → Network, copy an authenticated request as cURL, then paste it here.</p><textarea value={curl} onChange={e=>setCurl(e.target.value)} placeholder="Paste Copy as cURL"/><button onClick={async()=>{try{const r=await api("/auth/nextop/update",{curl});setTokenMessage(r.success?"Token configured. Load the current ticket again.":"Token was not accepted.")}catch{setTokenMessage("Token was not accepted.")}}}>Save & Validate</button><button onClick={()=>setTokenOpen(false)}>Close</button><p>{tokenMessage}</p></section></div>}
  </main>;
}

function Review({value,original}:{value:any;original:any}) {
  const field = (label:string,key:string) => <section><h3>{label}</h3><p>{Array.isArray(value?.[key]) ? value[key].join("\n") : value?.[key] || (original?.[key] ? "Translation unavailable." : "—")}</p></section>;
  return <>{value?.information_status === "insufficient" && <section className="insufficient"><h3>Information insufficient</h3><p>{(value.missing_information || original?.missing_information || []).join("\n") || "—"}</p><h3>Why this is needed</h3><p>{(value.reason_for_request || original?.reason_for_request || []).join("\n") || "—"}</p></section>}{field("Customer Issue","customer_description")}{field("Repair Actions","repair_actions")}{field("Current Blocker","current_blocker")}{field("Previous PIE Guidance","historical_pie_recommendations")}{field("Assessment / Next Step","ai_suggested_next_step")}{field("Solution","solution")}</>;
}
