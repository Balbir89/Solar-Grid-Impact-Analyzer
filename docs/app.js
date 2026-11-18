"use strict";
const money = x => new Intl.NumberFormat("en-IE",{style:"currency",currency:"EUR",maximumFractionDigits:0}).format(x);
const number = (x,d=0) => new Intl.NumberFormat("en-GB",{maximumFractionDigits:d}).format(x);
const el = id => document.getElementById(id);
const set = (id,value) => {el(id).textContent=value;};
const ns="http://www.w3.org/2000/svg";
function node(tag,attrs={},text=""){const n=document.createElementNS(ns,tag);for(const[k,v]of Object.entries(attrs))n.setAttribute(k,v);if(text)n.textContent=text;return n;}
function lines(id,rows,keys,colors){
 const svg=el(id);svg.replaceChildren();const W=760,H=280,p={l:50,r:15,t:18,b:35};
 const values=rows.flatMap(r=>keys.map(k=>r[k]));const lo=Math.floor(Math.min(...values)/100)*100,hi=Math.ceil(Math.max(...values)/100)*100||100;
 const x=i=>p.l+i*(W-p.l-p.r)/Math.max(1,rows.length-1),y=v=>H-p.b-(v-lo)/(hi-lo)*(H-p.t-p.b);
 for(let j=0;j<5;j++){let v=lo+(hi-lo)*j/4;svg.append(node("line",{x1:p.l,y1:y(v),x2:W-p.r,y2:y(v),class:"gridline"}),node("text",{x:p.l-9,y:y(v)+4,"text-anchor":"end"},number(v)));}
 keys.forEach((key,i)=>svg.append(node("polyline",{points:rows.map((r,j)=>x(j)+","+y(r[key])).join(" "),fill:"none",stroke:colors[i],"stroke-width":2.3})));
 for(const i of [0,Math.floor(rows.length/3),Math.floor(rows.length*2/3),rows.length-1])svg.append(node("text",{x:x(i),y:H-8,"text-anchor":i===0?"start":i===rows.length-1?"end":"middle"},rows[i].date.slice(5)));
 svg.append(node("text",{x:6,y:12},"kW"));
}
function bars(rows){
 const svg=el("savings-chart");svg.replaceChildren();const W=760,H=250,left=55,bottom=35,top=15;
 const max=Math.max(1,...rows.map(x=>Math.abs(x.operating_savings_eur)));
 const y=v=>H-bottom-v/max*(H-bottom-top);
 for(let j=0;j<4;j++){let v=max*j/3;svg.append(node("line",{x1:left,y1:y(v),x2:W-10,y2:y(v),class:"gridline"}),node("text",{x:left-9,y:y(v)+4,"text-anchor":"end"},number(v)));}
 const width=(W-left-10)/rows.length;
 rows.forEach((r,i)=>{const v=r.operating_savings_eur;const rect=node("rect",{x:left+i*width+width*.15,y:y(Math.max(v,0)),width:width*.7,height:Math.abs(y(v)-y(0)),rx:3,fill:v>=0?"#68e0c1":"#ff9c9c"});rect.append(node("title",{},r.month+": "+money(v)));svg.append(rect,node("text",{x:left+(i+.5)*width,y:H-10,"text-anchor":"middle"},r.month.slice(5)));});
 svg.append(node("text",{x:8,y:12},"EUR"));
}
async function main(){
 const response=await fetch("./data.json");if(!response.ok)throw Error("Data could not be loaded.");
 const d=await response.json(),e=d.economics,m=d.forecast.test_metrics;
 const best=Math.min(m.previous_hour.mae_kw,m.previous_day.mae_kw,m.previous_week.mae_kw);
 set("rows",number(d.input_rows));set("mae",number(m.random_forest.mae_kw,1)+" kW");set("improvement",number((1-m.random_forest.mae_kw/best)*100,1)+"%");
 set("cash",money(e.annual_net_savings_eur));set("hero-npv",money(e.npv_eur));
 set("decision-title",e.npv_eur<0?"Positive cash flow. Unattractive payback.":"Positive modeled investment value.");
 set("decision-copy",money(e.capex_eur)+" initial battery cost. "+(e.simple_payback_years?number(e.simple_payback_years,1)+"-year simple payback. ":"No positive simple payback. ")+"Reassess capital cost and dispatch strategy before investment.");
 lines("forecast-chart",d.daily_forecast,["target_kw","random_forest_kw"],["#68e0c1","#f5c581"]);
 const labels={random_forest:"Random Forest",previous_hour:"Previous hour",previous_day:"Same hour yesterday",previous_week:"Same hour last week"};
 const max=Math.max(...Object.values(m).map(x=>x.mae_kw));
 for(const[k,v]of Object.entries(m)){
   const row=document.createElement("div");row.className="bar-row"+(k==="random_forest"?"":" baseline");
   const head=document.createElement("div");head.className="bar-head";
   const label=document.createElement("span");label.textContent=labels[k];const score=document.createElement("strong");score.textContent=number(v.mae_kw,1)+" kW";head.append(label,score);
   const track=document.createElement("div");track.className="track";const fill=document.createElement("div");fill.className="fill";fill.style.width=v.mae_kw/max*100+"%";track.append(fill);row.append(head,track);el("model-bars").append(row);
 }
 for(const row of d.monthly_dispatch){const opt=document.createElement("option");opt.value=row.month;opt.textContent=row.month;el("month").append(opt);}
 function updateMonth(){const rows=el("month").value==="all"?d.monthly_dispatch:d.monthly_dispatch.filter(r=>r.month===el("month").value);
 set("baseline-bill",money(rows.reduce((s,r)=>s+r.baseline_cost_eur,0)));set("battery-bill",money(rows.reduce((s,r)=>s+r.energy_cost_eur+r.wear_cost_eur,0)));bars(rows);}
 function updateScenario(){const scenario=d.sensitivity.find(s=>s.capacity_kwh===Number(el("capacity").value)&&s.capex_eur_kwh===Number(el("capex").value));set("scenario-npv",money(scenario.npv_eur));set("scenario-net",money(scenario.annual_net_savings_eur)+" annual net benefit · "+(scenario.simple_payback_years?number(scenario.simple_payback_years,1)+"-year simple payback":"no positive payback / no investment"));}
 el("month").addEventListener("change",updateMonth);el("capacity").addEventListener("change",updateScenario);el("capex").addEventListener("change",updateScenario);updateMonth();updateScenario();
 set("charge",number(e.charge_kwh/1000,1)+" MWh");set("discharge",number(e.discharge_kwh/1000,1)+" MWh");set("loss",number(e.loss_kwh/1000,1)+" MWh");set("carbon",number(e.net_emissions_reduction_with_export_credit_tonnes,1)+" t CO₂");
 set("hash","INPUT SHA256 · "+d.input_sha256.slice(0,24)+"…");document.documentElement.dataset.ready="true";
}
main().catch(error=>{el("error").hidden=false;el("error").textContent="Unable to load the demo. Run python simple_server.py from the repository, then open http://localhost:8000. "+error.message;});
