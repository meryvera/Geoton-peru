/* ───────────────────────────────────────────────────────────
   Índice de Vulnerabilidad Digital Compuesta — Perú 2025
   Geotón Perú 2026 · Prototipo de alta fidelidad
   Todos los valores provienen de data.json (objeto kpis + array departamentos)
   ─────────────────────────────────────────────────────────── */

const TOPO_URL = "https://cdn.jsdelivr.net/npm/pe-atlas@0.0.1/departments-100k.json";

/* Palette ----------------------------------------------------- */
const V = { v1:"#E2E8F0", v2:"#93C5FD", v3:"#CA8A04", v4:"#EA580C", v5:"#DC2626" };
const GOLD = "#F59E0B";
const SECTORS = [
  { key:"s1", name:"Educación",  tag:"S1", col:"#2563EB", natl:66.2 },
  { key:"s2", name:"Salud",      tag:"S2", col:"#059669", natl:65.5 },
  { key:"s3", name:"Municipio",  tag:"S3", col:"#D97706", natl:27.9 },
  { key:"s4", name:"Seguridad",  tag:"S4", col:"#DC2626", natl:89.0 },
];
const VARS = [
  { key:"ivdc", label:"IVDC Compuesto", short:"Índice de Vulnerabilidad Digital Compuesta" },
  { key:"s1",   label:"S1 Educación",   short:"Brecha de conectividad en educación" },
  { key:"s2",   label:"S2 Salud",       short:"Brecha de conectividad en salud" },
  { key:"s3",   label:"S3 Municipio",   short:"Brecha de capacidad municipal" },
  { key:"s4",   label:"S4 Seguridad",   short:"Brecha de cobertura en seguridad" },
];

/* Region grouping (for scatter color) ------------------------- */
const COSTA = new Set(["LIMA","CALLAO","ICA","LA LIBERTAD","LAMBAYEQUE","PIURA","TUMBES","MOQUEGUA","TACNA","AREQUIPA"]);
const SIERRA = new Set(["ANCASH","APURIMAC","AYACUCHO","CAJAMARCA","CUSCO","HUANCAVELICA","HUANUCO","JUNIN","PASCO","PUNO"]);
const REGION_COL = { Costa:"#2563EB", Sierra:"#059669", Selva:"#D97706" };
const regionOf = d => COSTA.has(d) ? "Costa" : SIERRA.has(d) ? "Sierra" : "Selva";

/* Color bucket by value -------------------------------------- */
function bucket(v){
  if(v < 0.20) return V.v1;
  if(v < 0.40) return V.v2;
  if(v < 0.55) return V.v3;
  if(v < 0.65) return V.v4;
  return V.v5;
}
const LEGEND = [
  { c:V.v1, lab:"Mínima",  rng:"0.00–0.20" },
  { c:V.v2, lab:"Baja",    rng:"0.20–0.40" },
  { c:V.v3, lab:"Media",   rng:"0.40–0.55" },
  { c:V.v4, lab:"Alta",    rng:"0.55–0.65" },
  { c:V.v5, lab:"Crítica", rng:"0.65 +" },
];

/* Distritos: el array completo (1 874 registros) se lee de
   data.json → distritos. Cada fila: dp (departamento), pr
   (provincia), di (distrito), iv (IVDC), s1–s4 (brechas).   */
function dotColor(v){ return v < 0.3 ? "#16A34A" : v < 0.7 ? "#EAB308" : "#DC2626"; }

/* State ------------------------------------------------------- */
const state = { variable:"ivdc", selected:null };
let KPI, DEPS, DIST, byName, topo, feats, path;
const $ = s => document.querySelector(s);
const tip = $("#tip");
const fmt2 = d3.format(".2f");
const fmt3 = d3.format(".3f");
const fmtN = d3.format(",");

/* ───────────────────────── BOOT ───────────────────────────── */
(async function boot(){
  const data = await d3.json("data.json");
  KPI = data.kpis;
  DIST = data.distritos || [];
  DEPS = data.departamentos.slice().sort((a,b)=>b.ivdc-a.ivdc);
  byName = new Map(DEPS.map(d=>[d.dpto, d]));

  buildPills();
  buildDeptSelect();
  try {
    topo = await d3.json(TOPO_URL);
    feats = topojson.feature(topo, topo.objects.departments).features;
    drawMap();
  } catch(e){
    $("#mapWrap").innerHTML = '<div style="display:flex;height:100%;align-items:center;justify-content:center;color:#94A3B8;font-size:12px;padding:20px;text-align:center">No se pudo cargar la geometría del mapa.</div>';
  }
  buildLegend();
  drawScatter();
  drawRanking();
  renderAll();

  $("#deptSel").addEventListener("change", e=>{
    selectDept(e.target.value === "__nac" ? null : e.target.value);
  });
  $("#resetBtn").addEventListener("click", ()=>selectDept(null));
  window.addEventListener("resize", ()=>{ scaleStage(); redrawResponsive(); });
  scaleStage();
})();

/* ─────────────────────── SCALING ──────────────────────────── */
function scaleStage(){
  const s = Math.min(window.innerWidth/1440, window.innerHeight/900);
  $("#stage").style.transform = `scale(${s})`;
}
function redrawResponsive(){ if(feats) drawMap(); drawScatter(); drawRanking(); paintMap(); paintScatter(); paintRanking(); }

/* ─────────────────────── TOP BAR ──────────────────────────── */
function buildPills(){
  const row = $("#pillrow");
  row.innerHTML = "";
  VARS.forEach(v=>{
    const b = document.createElement("button");
    b.className = "pill" + (v.key===state.variable ? " active":"");
    b.dataset.k = v.key;
    const sec = SECTORS.find(s=>s.key===v.key);
    b.innerHTML = (sec ? `<span class="swatch" style="background:${sec.col}"></span>`:"") + v.label;
    b.onclick = ()=>setVariable(v.key);
    row.appendChild(b);
  });
}
function buildDeptSelect(){
  const sel = $("#deptSel");
  sel.innerHTML = '<option value="__nac">Nacional (todos)</option>' +
    DEPS.slice().sort((a,b)=>a.dpto.localeCompare(b.dpto))
        .map(d=>`<option value="${d.dpto}">${cap(d.dpto)}</option>`).join("");
}
function cap(s){ return s.split(" ").map(w=>w[0]+w.slice(1).toLowerCase()).join(" "); }

function setVariable(k){
  state.variable = k;
  document.querySelectorAll(".pill").forEach(p=>p.classList.toggle("active", p.dataset.k===k));
  const v = VARS.find(x=>x.key===k);
  $("#mapTitle").textContent = v.short;
  $("#mapSub").textContent = `25 departamentos · ${k==="ivdc"?"índice compuesto":"brecha sectorial"} (0–1)`;
  paintMap(); updateLegendTitle(); renderSector();
}

function selectDept(name){
  state.selected = name;
  $("#deptSel").value = name || "__nac";
  $("#resetBtn").style.display = name ? "block" : "none";
  renderAll(); paintMap(); paintScatter(); paintRanking();
}

/* ─────────────────────── MAP ──────────────────────────────── */
function valOf(d){ return d[state.variable]; }

function drawMap(){
  const wrap = $("#mapWrap");
  const w = wrap.clientWidth, h = wrap.clientHeight;
  const svg = d3.select("#mapSvg").attr("viewBox",`0 0 ${w} ${h}`);
  svg.selectAll("*").remove();
  const proj = d3.geoIdentity().reflectY(true).fitExtent([[12,10],[w-12,h-10]], {type:"FeatureCollection",features:feats});
  path = d3.geoPath(proj);
  const g = svg.append("g");
  g.selectAll("path.dept").data(feats).join("path")
    .attr("class","dept").attr("d", path)
    .attr("data-n", d=>d.properties.name)
    .attr("fill", f=>{ const d=byName.get(f.properties.name); return d?bucket(valOf(d)):"#EEF2F6"; })
    .on("mousemove", (e,f)=>{
      const d = byName.get(f.properties.name); if(!d) return;
      const v = valOf(d);
      showTip(e, `<div class="tt"><span class="sw" style="background:${bucket(v)}"></span>${cap(d.dpto)}</div>
        <div class="row"><span>${VARS.find(x=>x.key===state.variable).label}</span><b>${fmt2(v)}</b></div>
        <div class="row"><span>Distritos en Q5</span><b>${d.q5}</b></div>`);
    })
    .on("mouseleave", hideTip)
    .on("click", (e,f)=>selectDept(f.properties.name));
  paintMap();
}
function paintMap(){
  d3.selectAll("path.dept")
    .classed("sel", f=>f.properties.name===state.selected)
    .transition().duration(200)
    .attr("fill", f=>{ const d=byName.get(f.properties.name); return d?bucket(valOf(d)):"#EEF2F6"; });
  // raise selected for crisp gold border
  d3.selectAll("path.dept").filter(f=>f.properties.name===state.selected).raise();
}

function buildLegend(){
  const el = $("#legend"); el.innerHTML = "";
  LEGEND.forEach(l=>{
    const d = document.createElement("div"); d.className="lg";
    d.innerHTML = `<div class="bar" style="background:${l.c}"></div><div class="lab">${l.lab}</div><div class="rng">${l.rng}</div>`;
    el.appendChild(d);
  });
}
function updateLegendTitle(){ /* legend ranges identical across variables (all 0–1) */ }

/* ─────────────────────── KPI CARDS ────────────────────────── */
function renderKPI(){
  const grid = $("#kpiGrid");
  let cards;
  if(!state.selected){
    $("#kpiHead").textContent = "Indicadores nacionales";
    cards = [
      { num:fmtN(KPI.q5_distritos), lab:"Distritos más vulnerables (Q5)" },
      { num:fmtN(KPI.cuadruple_brecha), lab:"Con brecha en los 4 sectores" },
      { num:fmtN(KPI.municipios_precarios), lab:"Municipios sin internet o conexión precaria" },
      { num:fmtN(KPI.desincronizados), lab:"Con señal pero sin servicios conectados" },
    ];
  } else {
    const d = byName.get(state.selected);
    $("#kpiHead").innerHTML = `Indicadores · <span style="color:#0F172A">${cap(d.dpto)}</span>`;
    cards = [
      { num:fmtN(d.q5), lab:"Distritos en quintil crítico (Q5)" },
      { num:fmt2(d.ivdc), lab:"IVDC promedio departamental" },
      { num:fmt3(d.idh), lab:"IDH promedio departamental" },
      { num:d.pct_q5.toFixed(1), u:"%", lab:"% distritos en quintil crítico" },
    ];
  }
  grid.innerHTML = cards.map(c=>`
    <div class="kpi"><div class="num">${c.num}${c.u?`<span class="u">${c.u}</span>`:""}</div>
    <div class="lab">${c.lab}</div></div>`).join("");
}

/* ─────────────────── SECTOR PROFILE ───────────────────────── */
function renderSector(){
  const list = $("#secList");
  const isNat = !state.selected;
  const d = isNat ? null : byName.get(state.selected);
  $("#secHead").innerHTML = `Perfil sectorial — <span class="em">${isNat?"Nacional":cap(d.dpto)}</span>`;
  list.innerHTML = "";
  SECTORS.forEach(s=>{
    const pct = isNat ? s.natl : (d[s.key]*100);
    const hot = (state.variable===s.key);
    const dim = (state.variable!=="ivdc" && !hot);
    const wpct = Math.max(0,Math.min(100,pct));
    const row = document.createElement("div");
    row.className = "sec" + (hot?" hot":"") + (dim?" dim":"");
    row.innerHTML = `
      <div class="nm"><span class="sw" style="background:${s.col}"></span>${s.tag} ${s.name}</div>
      <div class="track">
        <div class="fill" style="background:${s.col};width:${wpct}%"></div>
        <div class="avg" style="left:${s.natl}%" title="Promedio nacional ${s.natl}%"></div>
      </div>
      <div class="val">${pct.toFixed(1)}%</div>`;
    list.appendChild(row);
  });
}

/* ─────────────────── DISTRICTS TABLE ──────────────────────── */
function topDistricts(filterFn){
  return DIST.filter(filterFn).sort((a,b)=>b.iv-a.iv).slice(0,5);
}
function renderDist(){
  const body = $("#distBody");
  const isNat = !state.selected;
  $("#distHead").innerHTML = `Distritos prioritarios — <span class="em">${isNat?"Nacional":cap(state.selected)}</span>`;
  const raw = isNat
    ? topDistricts(()=>true)
    : topDistricts(d=>d.dp===state.selected);
  if(!raw.length){
    body.innerHTML = `<div id="distMsg">Sin distritos registrados para este departamento.</div>`;
    return;
  }
  const rows = raw.map(r=>({
    d: cap(r.di),
    sub: cap(isNat ? r.dp : r.pr),
    ivdc: r.iv, s1:r.s1, s2:r.s2, s3:r.s3, s4:r.s4
  }));
  const cell = v=>`<td class="c"><span class="dotc" style="background:${dotColor(v)}"></span></td>`;
  body.innerHTML = `<table class="dist">
    <thead><tr><th>Distrito</th><th class="r">IVDC</th><th class="c">S1</th><th class="c">S2</th><th class="c">S3</th><th class="c">S4</th></tr></thead>
    <tbody>${rows.map(r=>`
      <tr><td class="nm">${r.d}${r.sub?` <small>· ${r.sub}</small>`:""}</td>
      <td class="iv">${fmt2(r.ivdc)}</td>${cell(r.s1)}${cell(r.s2)}${cell(r.s3)}${cell(r.s4)}</tr>`).join("")}
    </tbody></table>`;
}

/* ─────────────────────── SCATTER ──────────────────────────── */
let scatScales = null;
function drawScatter(){
  const wrap = $("#scatWrap");
  const w = wrap.clientWidth, h = wrap.clientHeight;
  const m = { t:16, r:16, b:34, l:42 };
  const svg = d3.select("#scatSvg").attr("viewBox",`0 0 ${w} ${h}`);
  svg.selectAll("*").remove();
  const x = d3.scaleLinear().domain([0.1,1.05]).range([m.l, w-m.r]);
  const y = d3.scaleLinear().domain([0.28,0.72]).range([h-m.b, m.t]);
  const r = d3.scaleSqrt().domain(d3.extent(DEPS,d=>d.n)).range([4,15]);
  scatScales = {x,y,r,w,h,m};

  const g = svg.append("g");
  // gridlines + ticks
  [0.2,0.4,0.6,0.8,1.0].forEach(t=>{
    g.append("line").attr("class","gridln").attr("x1",x(t)).attr("x2",x(t)).attr("y1",m.t).attr("y2",h-m.b);
    g.append("text").attr("class","axtick").attr("x",x(t)).attr("y",h-m.b+13).attr("text-anchor","middle").text(d3.format(".1f")(t));
  });
  [0.3,0.4,0.5,0.6,0.7].forEach(t=>{
    g.append("line").attr("class","gridln").attr("x1",m.l).attr("x2",w-m.r).attr("y1",y(t)).attr("y2",y(t));
    g.append("text").attr("class","axtick").attr("x",m.l-6).attr("y",y(t)+3).attr("text-anchor","end").text(d3.format(".1f")(t));
  });
  // axis labels
  g.append("text").attr("class","axlab").attr("x",(m.l+w-m.r)/2).attr("y",h-4).attr("text-anchor","middle").text("Vulnerabilidad digital (IVDC) →");
  g.append("text").attr("class","axlab").attr("transform",`rotate(-90)`).attr("x",-(m.t+h-m.b)/2).attr("y",13).attr("text-anchor","middle").text("Desarrollo humano (IDH) →");

  // quadrant labels
  g.append("text").attr("class","quad").attr("x",x(0.16)).attr("y",y(0.70)).text("Baja vulnerabilidad / alto desarrollo");
  g.append("text").attr("class","quad").attr("x",w-m.r).attr("y",y(0.30)).attr("text-anchor","end").text("Alta vulnerabilidad / bajo desarrollo");

  // trend line (least squares idh ~ ivdc)
  const n=DEPS.length, sx=d3.sum(DEPS,d=>d.ivdc), sy=d3.sum(DEPS,d=>d.idh),
        sxx=d3.sum(DEPS,d=>d.ivdc*d.ivdc), sxy=d3.sum(DEPS,d=>d.ivdc*d.idh);
  const slope=(n*sxy-sx*sy)/(n*sxx-sx*sx), intc=(sy-slope*sx)/n;
  const x0=0.15, x1=1.0;
  g.append("line").attr("class","trend").attr("x1",x(x0)).attr("y1",y(slope*x0+intc)).attr("x2",x(x1)).attr("y2",y(slope*x1+intc));

  const LBL = new Set(["APURIMAC","LORETO","AREQUIPA","CALLAO","CAJAMARCA"]);
  const pts = g.append("g");
  pts.selectAll("circle.pt").data(DEPS).join("circle")
    .attr("class","pt").attr("data-n",d=>d.dpto)
    .attr("cx",d=>x(d.ivdc)).attr("cy",d=>y(d.idh)).attr("r",d=>r(d.n))
    .attr("fill",d=>REGION_COL[regionOf(d.dpto)]).attr("fill-opacity",.78)
    .attr("stroke","#fff").attr("stroke-width",1)
    .on("mousemove",(e,d)=>showTip(e,`<div class="tt"><span class="sw" style="background:${REGION_COL[regionOf(d.dpto)]}"></span>${cap(d.dpto)}</div>
      <div class="row"><span>IVDC</span><b>${fmt2(d.ivdc)}</b></div>
      <div class="row"><span>IDH</span><b>${fmt3(d.idh)}</b></div>
      <div class="row"><span>Distritos</span><b>${d.n}</b></div>`))
    .on("mouseleave",hideTip)
    .on("click",(e,d)=>selectDept(d.dpto));

  pts.selectAll("text.ptlab").data(DEPS.filter(d=>LBL.has(d.dpto))).join("text")
    .attr("class","ptlab")
    .attr("x",d=>x(d.ivdc)+r(d.n)+3).attr("y",d=>y(d.idh)+3)
    .text(d=>cap(d.dpto));
  paintScatter();
}
function paintScatter(){
  if(!scatScales) return;
  const {r}=scatScales;
  d3.selectAll("circle.pt")
    .classed("sel",d=>d.dpto===state.selected)
    .transition().duration(200)
    .attr("r",d=>d.dpto===state.selected ? r(d.n)+4 : r(d.n))
    .attr("fill-opacity",d=> state.selected && d.dpto!==state.selected ? .32 : .82);
  d3.selectAll("circle.pt").filter(d=>d.dpto===state.selected).raise();
}

/* ─────────────────────── RANKING ──────────────────────────── */
let rankScales=null;
function drawRanking(){
  const wrap = $("#rankWrap");
  const w = wrap.clientWidth, h = wrap.clientHeight;
  const m={t:4,r:34,b:4,l:80};
  const svg = d3.select("#rankSvg").attr("viewBox",`0 0 ${w} ${h}`);
  svg.selectAll("*").remove();
  const data = DEPS; // already sorted desc
  const yb = d3.scaleBand().domain(data.map(d=>d.dpto)).range([m.t,h-m.b]).padding(0.28);
  const x = d3.scaleLinear().domain([0,d3.max(data,d=>d.ivdc)*1.02]).range([m.l, w-m.r]);
  rankScales={yb,x,w,h,m};

  const g = svg.append("g");
  const rows = g.selectAll("g.rk-row").data(data,d=>d.dpto).join("g")
    .attr("class","rk-row").attr("data-n",d=>d.dpto)
    .on("mousemove",(e,d)=>showTip(e,`<div class="tt"><span class="sw" style="background:${bucket(d.ivdc)}"></span>${cap(d.dpto)}</div>
      <div class="row"><span>IVDC</span><b>${fmt2(d.ivdc)}</b></div>
      <div class="row"><span>Distritos Q5</span><b>${d.q5}</b></div>`))
    .on("mouseleave",hideTip)
    .on("click",(e,d)=>selectDept(d.dpto));

  rows.append("text").attr("class","rk-nm").attr("x",m.l-7).attr("y",d=>yb(d.dpto)+yb.bandwidth()/2).attr("text-anchor","end").text(d=>cap(d.dpto));
  rows.append("rect").attr("class","rk-frame").attr("x",m.l-1).attr("y",d=>yb(d.dpto)-1.5).attr("width",1).attr("height",yb.bandwidth()+3).attr("fill","none").attr("rx",3).style("pointer-events","none");
  rows.append("rect").attr("class","rk-bar").attr("x",m.l).attr("y",d=>yb(d.dpto)).attr("height",yb.bandwidth()).attr("rx",2).attr("width",d=>x(d.ivdc)-m.l).attr("fill",d=>bucket(d.ivdc));
  rows.append("text").attr("class","rk-val").attr("x",d=>x(d.ivdc)+5).attr("y",d=>yb(d.dpto)+yb.bandwidth()/2).text(d=>fmt2(d.ivdc));
  paintRanking();
}
function paintRanking(){
  if(!rankScales) return;
  const {yb,x,m}=rankScales;
  d3.selectAll("g.rk-row").each(function(d){
    const sel = d.dpto===state.selected;
    const g = d3.select(this).classed("rk-sel",sel);
    g.select(".rk-frame")
      .attr("x", sel ? m.l : m.l-1)
      .attr("width", sel ? (x(d.ivdc)-m.l) : 1)
      .attr("y", yb(d.dpto)-1.5).attr("height", yb.bandwidth()+3);
    g.select(".rk-bar").attr("opacity", state.selected && !sel ? .5 : 1);
  });
}

/* ─────────────────────── TOOLTIP ──────────────────────────── */
function showTip(e,html){
  tip.innerHTML = html; tip.style.opacity = 1;
  const pad=14, tw=tip.offsetWidth, th=tip.offsetHeight;
  let x=e.clientX+pad, y=e.clientY+pad;
  if(x+tw>window.innerWidth) x=e.clientX-tw-pad;
  if(y+th>window.innerHeight) y=e.clientY-th-pad;
  tip.style.left=x+"px"; tip.style.top=y+"px";
}
function hideTip(){ tip.style.opacity=0; }

/* ─────────────────────── RENDER ALL ───────────────────────── */
function renderAll(){ renderKPI(); renderSector(); renderDist(); }
