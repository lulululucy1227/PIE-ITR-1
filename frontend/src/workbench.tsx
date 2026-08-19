import { useEffect, useRef, useState } from "react";

type Case = { id:string; ticket:string; todo:boolean; notes:string; prepared?:any; analysis?:any; translated?:any; customerZh?:string; replyZh?:string; language:"ZH"|"ORIGINAL"; loading?:string; error?:string; diagnostic?:string; freshnessBlocked?:boolean; generations:Record<string,number> };
const api = async (path:string, body:object) => (await fetch(`/api${path}`, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body) })).json();
const fresh = ():Case => ({ id:crypto.randomUUID(), ticket:"", todo:false, notes:"", language:"ORIGINAL", generations:{} });

export function App() {
  const [cases,setCases] = useState<Case[]>([fresh()]);
  const [active,setActive] = useState(0);
  const [tokenOpen,setTokenOpen] = useState(false); const [curl,setCurl] = useState(""); const [tokenMessage,setTokenMessage] = useState(""); const [authConfigured,setAuthConfigured] = useState<boolean|undefined>();
  const casesRef = useRef(cases); casesRef.current = cases;
  const current = cases[active];
  useEffect(()=>{ api("/auth/nextop/status",{}).then(value=>setAuthConfigured(Boolean(value.configured))).catch(()=>setAuthConfigured(false)); },[]);
  const patch = (id:string, data:Partial<Case>) => setCases(items => items.map(item => item.id === id ? {...item,...data} : item));
  const live = (id:string, operation:string, generation:number) => casesRef.current.some(item => item.id === id && item.generations[operation] === generation);
  const run = async (item:Case, operation:string, loading:string, action:()=>Promise<any>, apply:(result:any)=>Partial<Case>) => {
    const generation = (item.generations[operation] || 0) + 1;
    setCases(items => items.map(value => value.id === item.id ? {...value, generations:{...value.generations,[operation]:generation}, loading, error:undefined, diagnostic:undefined} : value));
    try { const result = await action(); if (live(item.id,operation,generation)) patch(item.id,apply(result)); }
    catch { if (live(item.id,operation,generation)) patch(item.id,{loading:undefined,error:"Local API operation failed."}); }
  };
  const analyze = (item=current) => item.prepared && run(item,"analyze","Analyzing...",() => api("/cases/analyze",{case:{...(item.prepared.existing_case || item.prepared.fields),...(item.prepared.analysis || {}),context_pack:item.prepared.context_pack}}), result => ({analysis:result,translated:undefined,language:"ORIGINAL",loading:"Ready for review"}));
  const refresh = () => current.prepared && run(current,"refresh","Refreshing...",() => api("/cases/refresh",{prepared:current.prepared}), result => { if(!result.success){if(String(result.error_type||"").startsWith("NEXTOP_AUTH"))setAuthConfigured(false);return {loading:undefined,error:result.message||"Latest Nextop state could not be verified.",freshnessBlocked:true};} if(result.requires_reanalyze)queueMicrotask(()=>analyze({...current,prepared:result.prepared})); return {prepared:result.prepared,loading:result.message,freshnessBlocked:false}; });
  const load = () => run(current,"prepare","Loading case...",() => api("/cases/prepare",{source:"nextop",ticket_no:current.ticket}), result => {
    if (!result.success) { const diagnostic=`${result.message || "Case could not be loaded."}\n\nStage: ${result.stage || "unknown"}\nError code: ${result.error_type || "unknown"}${result.detail ? `\nSafe detail: ${result.detail}` : ""}\n\nNo credentials are shown here.`; return {loading:undefined,error:result.message || "Case could not be loaded.",diagnostic}; }
    const preparedCase = {...current,prepared:result.prepared};
    queueMicrotask(() => analyze(preparedCase));
    return {prepared:result.prepared,analysis:undefined,translated:undefined,loading:"Building context and analyzing..."};
  });
  const translateText = (kind:"customer"|"reply") => { const text=kind==="customer"?current.analysis?.customer_description:current.analysis?.reply_en; return text && run(current,`${kind}-translation`,"Preparing Chinese review...",() => api("/cases/translate-text",{text}), result => kind==="customer"?{customerZh:result.text,loading:"Ready for review"}:{replyZh:result.text,loading:"Ready for review"}); };
  const commit = () => current.prepared && run(current,"commit","Checking latest Nextop state...",async()=>{const latest=await api("/cases/refresh",{prepared:current.prepared});if(!latest.success||latest.change_type!=="NO_CHANGE")return {...latest,success:false};return api("/cases/commit",{prepared:current.prepared,include_itr_todo:current.todo,todo_dirty:true});}, result => result.success?{loading:"Complete",freshnessBlocked:false}:{prepared:result.prepared||current.prepared,loading:undefined,error:result.message||"Ticket has changed since ITR preparation. Please review the latest messages.",freshnessBlocked:true});
  const close = (id:string) => setCases(items => { const next=items.filter(item=>item.id!==id); setActive(index=>Math.min(index,Math.max(0,next.length-1))); return next.length ? next : [fresh()]; });
  const review = current.language === "ZH" && current.translated ? current.translated : current.analysis;
  const logiqSupported = current.analysis?.capability?.logiq === "supported";
  return <main>
    <header><div className="tabs">{cases.map((item,index)=><button className={index===active?"active":""} onClick={()=>setActive(index)} key={item.id}>{item.ticket || "New Case"}</button>)}<button onClick={()=>{setCases(items=>[...items,fresh()]);setActive(cases.length);}}>+</button></div><button className={authConfigured?"auth-ok":"auth-required"} onClick={()=>setTokenOpen(true)}>{authConfigured?"Nextop ✓":"Nextop Auth Required"}</button></header>
    <section className="status">{current.loading || current.error || "Ready"}{current.diagnostic&&<details className="diagnostic" open><summary>Help diagnose this failure</summary><pre>{current.diagnostic}</pre><button onClick={()=>navigator.clipboard.writeText(current.diagnostic || "")}>Copy diagnostic</button></details>}</section>
    <div className="workbench"><aside><h2>Context</h2><label>Ticket<input value={current.ticket} onChange={event=>patch(current.id,{ticket:event.target.value})} onKeyDown={event=>event.key==="Enter"&&load()}/></label><button onClick={load}>Search / Load</button>{current.prepared&&<><p>Reference: {current.prepared.ticket_no}</p><label className="todo"><input type="checkbox" checked={current.todo} onChange={event=>patch(current.id,{todo:event.target.checked})}/> Add to ITR Todo</label><textarea placeholder="Session notes" value={current.notes} onChange={event=>patch(current.id,{notes:event.target.value})}/><button onClick={()=>close(current.id)}>Close Case</button></>}</aside>
    <article><div className="tools"><h1>Case Review</h1><button disabled={!current.prepared} onClick={refresh}>Refresh Latest</button><button disabled={!current.prepared} onClick={()=>analyze()}>Re-analyze</button><button className="logiq" disabled={!logiqSupported} title={logiqSupported ? "Copies device name and opens LogiQ" : "LogiQ is unavailable until product capability is confirmed"} onClick={()=>{const device=current.prepared?.fields?.["Device name"] || current.prepared?.fields?.device_name;if(device) navigator.clipboard.writeText(device);window.open("https://logiq.cloud-cn.mammotion.com/","_blank")}}>LogiQ · Logs</button></div>
    {current.analysis ? <Review value={current.analysis} customerZh={current.customerZh} onCustomerZh={()=>translateText("customer")}/> : <p className="empty">Load a case to automatically build context and analyze it.</p>}
    <section className="reply"><h3>Email Reply</h3><pre>{current.analysis?.reply_en || "—"}</pre>{current.analysis?.reply_en&&<><button onClick={()=>navigator.clipboard.writeText(current.analysis.reply_en)}>Copy Reply</button><button onClick={()=>translateText("reply")}>查看中文</button>{current.replyZh&&<pre className="translation">{current.replyZh}</pre>}</>}</section>
    <button className="commit" disabled={!current.prepared || current.freshnessBlocked} onClick={commit}>{current.prepared?.can_update?"Update ITR":"Create in ITR"}</button></article></div>
  {tokenOpen&&<div className="token-modal"><section><h2>Update Nextop Token</h2><p>Log in to Nextop, open DevTools → Network, copy an authenticated request as cURL, then paste it here.</p><textarea value={curl} onChange={e=>setCurl(e.target.value)} placeholder="Paste Copy as cURL"/><button onClick={async()=>{try{const r=await api("/auth/nextop/update",{curl});setTokenMessage(r.success?"Token configured. Load the current ticket again.":"Token was not accepted.");if(r.success)setAuthConfigured(true)}catch{setTokenMessage("Token was not accepted.")}}}>Save & Validate</button><button onClick={()=>setTokenOpen(false)}>Close</button><p>{tokenMessage}</p></section></div>}
  </main>;
}

function Review({value,customerZh,onCustomerZh}:{value:any;customerZh?:string;onCustomerZh:()=>void}) {
  const field = (label:string,key:string) => <section><h3>{label}</h3><p>{Array.isArray(value?.[key]) ? value[key].join("\n") : value?.[key] || "—"}</p></section>;
  return <>{value?.information_status === "insufficient" && <section className="insufficient"><h3>信息不足</h3><p>{(value.missing_information || []).join("\n") || "—"}</p><h3>需要原因</h3><p>{(value.reason_for_request || []).join("\n") || "—"}</p></section>}<section><h3>Customer Issue</h3><p>{value.customer_description || "—"}</p><button onClick={onCustomerZh}>中文翻译</button>{customerZh&&<pre className="translation">{customerZh}</pre>}</section>{field("Repair Action","repair_actions")}{field("Blocker","current_blocker")}{field("PIE Guidance","historical_pie_recommendations")}{field("Next Step","ai_suggested_next_step")}{field("Solution","solution")}</>;
}
