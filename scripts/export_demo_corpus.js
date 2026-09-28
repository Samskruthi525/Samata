#!/usr/bin/env node
// Extract the demo corpus embedded in prototype/ambedkar_kiosk.html into data/demo_corpus.json.
// Usage: node scripts/export_demo_corpus.js [path/to/ambedkar_kiosk.html]
const fs=require('fs');
const html=fs.readFileSync(process.argv[2]||'prototype/ambedkar_kiosk.html','utf8');
const b=html.indexOf('<body');const js=html.slice(html.indexOf('<script',b));
function grab(name){const i=js.indexOf('const '+name+' =');let k=js.indexOf('=',i)+1;while(js[k]==' ')k++;const open=js[k],close=open=='['?']':'}';let d=0,q=null;for(let p=k;p<js.length;p++){const c=js[p];if(q){if(c=='\\'){p++;continue}if(c==q)q=null;continue}if(c=="'"||c=='"'||c=='`'){q=c;continue}if(c==open)d++;else if(c==close){d--;if(!d)return eval('('+js.slice(k,p+1)+')')}}}
const out={_note:"Extracted from prototype/ambedkar_kiosk.html by scripts/export_demo_corpus.js. DEMO CORPUS: placeholder transcriptions and sample records for the prototype build; not a verified archive. Replace with curator-verified material before public use.",
items:grab('ITEMS'),events:grab('EVENTS'),eras:grab('ERAS'),km_nodes:grab('KM_NODES').map(n=>({id:n.id,type:n.type,x:n.x,y:n.y,r:n.r,lines:n.lines,sub:n.sub})),km_edges:grab('KM_EDGES'),
stories:grab('STORIES').map(s=>({id:s.id,title:s.title,sub:s.sub,stops:s.stops.map(t=>({date:t.date,title:t.title,item:t.item||t.ev||null}))})),
tests:grab('TESTS').map(t=>({id:t[0],procedure:t[1],pass:t[2],mode:t[3]})),ask_set:grab('ASK_SET'),suggested:grab('SUGGESTED_QS'),admin_ids:grab('ADMIN_IDS'),
image_credits:Object.entries(grab('IMG')).map(([k,v])=>({key:k,alt:v.alt,credit:v.credit,w:v.w,h:v.h}))};
fs.writeFileSync('data/demo_corpus.json',JSON.stringify(out,null,1));
// interface strings: base dictionary + later part dictionaries, merged per language
const i18n={};for(const n of ['I18N','PART5_I18N','PART6_I18N']){const d=grab(n);if(!d)continue;for(const [lang,kv] of Object.entries(d)){i18n[lang]=Object.assign(i18n[lang]||{},kv)}}
fs.writeFileSync('data/i18n_strings.json',JSON.stringify(i18n,null,1));
console.log('i18n:'+Object.entries(i18n).map(([l,kv])=>l+'='+Object.keys(kv).length).join(','));
console.log(Object.keys(out).map(k=>k+':'+(Array.isArray(out[k])?out[k].length:'')).join(' '));
