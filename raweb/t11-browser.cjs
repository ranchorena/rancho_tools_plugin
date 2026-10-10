const {spawn}=require('node:child_process');
const {readFileSync,mkdtempSync,rmSync,writeFileSync}=require('node:fs');
const {tmpdir}=require('node:os');
const {join}=require('node:path');
const assert=require('node:assert/strict');
const phase=process.argv[2]||'green',url='http://192.168.0.102:8080/';
const delay=ms=>new Promise(r=>setTimeout(r,ms));
const profile=mkdtempSync(join(tmpdir(),'raweb-t11-'));
let chrome,ws;const evidence={phase,checks:[],errors:[],requests:[],measurements:[]};
(async()=>{
 chrome=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--no-first-run','--no-default-browser-check','--remote-debugging-port=0',`--user-data-dir=${profile}`,'about:blank'],{stdio:'ignore'});
 let endpoint;for(let i=0;i<100;i++){try{endpoint=readFileSync(join(profile,'DevToolsActivePort'),'utf8').split(/\r?\n/);break;}catch{await delay(100);}}assert(endpoint);
 const tabs=await(await fetch(`http://127.0.0.1:${endpoint[0]}/json/list`)).json();ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 let id=0;const pending=new Map();
 const send=(method,params={})=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params}));});
 ws.onmessage=({data})=>{const m=JSON.parse(data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(m.error):p.resolve(m.result);}else if(m.method==='Fetch.requestPaused'){
  const p=m.params,u=new URL(p.request.url);const local=u.origin===new URL(url).origin;
  evidence.requests.push({method:p.request.method,kind:local?'app':u.pathname.endsWith('/ows')?'WFS':'external',controlled:!local});
  if(local)send('Fetch.continueRequest',{requestId:p.requestId});
  else {const wfs=u.pathname.endsWith('/ows');send('Fetch.fulfillRequest',{requestId:p.requestId,responseCode:200,responseHeaders:[{name:'Access-Control-Allow-Origin',value:'*'},{name:'Content-Type',value:wfs?'application/json':'image/png'}],body:wfs?Buffer.from('{"type":"FeatureCollection","features":[]}').toString('base64'):'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jRZkAAAAASUVORK5CYII='});}
 }else if(m.method==='Runtime.exceptionThrown')evidence.errors.push(m.params.exceptionDetails.text);else if(m.method==='Log.entryAdded'&&m.params.entry.level==='error')evidence.errors.push(m.params.entry.text);};
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});assert(!r.exceptionDetails,JSON.stringify(r.exceptionDetails));return r.result.value;};
 const viewport=async(w,h)=>{await send('Emulation.setDeviceMetricsOverride',{width:w,height:h,deviceScaleFactor:1,mobile:false});await delay(200);};
 const media=async value=>{await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value}]});await delay(150);};
 const key=async(key,code,vk,modifiers=0)=>{await send('Input.dispatchKeyEvent',{type:'keyDown',key,code,windowsVirtualKeyCode:vk,modifiers,...(key==='Enter'?{text:'\r'}:{})});await send('Input.dispatchKeyEvent',{type:'keyUp',key,code,windowsVirtualKeyCode:vk,modifiers});await delay(100);};
 const state=()=>evaluate(`({theme:document.documentElement.dataset.theme,saved:localStorage.getItem('raweb.theme.v1'),values:Array.from(document.querySelectorAll('.theme-selector select'),e=>e.value)})`);
 const choose=async(id,value)=>{await evaluate(`document.getElementById('${id}').focus()`);await key('Home','Home',36);if(value==='dark')await key('ArrowDown','ArrowDown',40);if(value==='system')await key('End','End',35);};
 const reload=async()=>{await send('Page.reload',{ignoreCache:true});await delay(700);};
 const measure=()=>evaluate(`(()=>{const nav=document.querySelector('.navbar'),r=nav.getBoundingClientRect();const rect=e=>{const b=e.getBoundingClientRect(),s=getComputedStyle(e);return {width:b.width,height:b.height,x:b.x,y:b.y,bottom:b.bottom,right:b.right,color:s.color,background:s.backgroundColor,outline:s.outlineStyle,outlineWidth:s.outlineWidth};};return {viewport:[innerWidth,innerHeight],nav:rect(nav),brand:rect(nav.querySelector('h1')),toggle:rect(document.querySelector('.mobile-menu-toggle')),buttons:Array.from(document.querySelectorAll('.nav-buttons button'),rect),selectors:Array.from(document.querySelectorAll('.theme-selector select'),e=>({id:e.id,value:e.value,label:e.labels[0]?.textContent,box:rect(e)})),mobileActions:Array.from(document.querySelectorAll('.mobile-nav-buttons button'),rect)};})()`);
 for(const d of ['Runtime','Log','Page'])await send(d+'.enable');await send('Fetch.enable',{patterns:[{urlPattern:'*'}]});await send('Emulation.setFocusEmulationEnabled',{enabled:true});await viewport(1366,768);await media('light');await send('Page.navigate',{url});await delay(1000);evidence.browser=await send('Browser.getVersion');
 if(phase==='red'){
  for(const [w,h] of [[1366,768],[360,800],[800,360],[768,1024]]){await viewport(w,h);evidence.measurements.push(await measure());}
  assert.equal(await evaluate(`document.querySelectorAll('.theme-selector select').length`),1,'Selector Tema inexistente en App antes de T11');
 }
 await viewport(1366,768);assert.deepEqual(await state(),{theme:'light',saved:null,values:['system']});await media('dark');assert.equal((await state()).theme,'dark');evidence.checks.push('Sin elección: Sistema sigue dispositivo claro/oscuro');
 for(const value of ['light','dark','system']){
  await choose('theme-desktop',value);let s=await state();assert.equal(s.saved,value);assert.equal(s.theme,value==='system'?'dark':value);await reload();s=await state();assert.equal(s.saved,value);assert.deepEqual(s.values,[value]);
  await media('light');assert.equal((await state()).theme,value==='dark'?'dark':'light');await media('dark');assert.equal((await state()).theme,value==='light'?'light':'dark');
  await send('Page.navigate',{url:'about:blank'});await delay(100);await send('Page.navigate',{url});await delay(700);assert.equal((await state()).saved,value);assert.deepEqual((await state()).values,[value]);
 }
 evidence.checks.push('Tres opciones por teclado, persistencia/recarga/reapertura y cambios de dispositivo explícito/Sistema');
 for(const [w,h] of [[1366,768],[360,800],[800,360],[768,1024]]){
  await viewport(w,h);const mobile=w<=768;
  if(mobile)await evaluate(`document.querySelector('.mobile-menu-toggle').click()`);
  for(const theme of ['light','dark']){
   await choose(mobile?'theme-mobile':'theme-desktop',theme);const m=await measure();m.theme=theme;evidence.measurements.push(m);
   assert.equal(m.nav.height,mobile?80:68);assert.equal(m.brand.y>=m.nav.y,true);assert.equal(m.toggle.height>0,mobile);
   const selector=m.selectors.find(s=>s.id===(mobile?'theme-mobile':'theme-desktop'));assert.equal(selector.label,'Tema');assert(selector.box.width>0);assert(selector.box.right<=w);
   if(mobile){assert(selector.box.y>=m.mobileActions.at(-1).bottom);assert.equal(m.selectors[0].box.width,0);}
   else {assert(selector.box.x>=m.buttons.at(-1).right);assert(m.buttons.every(b=>b.y>=m.nav.y&&b.bottom<=m.nav.bottom));}
   assert.equal(selector.box.outline,'solid');assert.equal(selector.box.outlineWidth,'3px');
   const shot=await send('Page.captureScreenshot',{format:'png'});writeFileSync(join(__dirname,`t11-${w}-${h}-${theme}.png`),Buffer.from(shot.data,'base64'));
   for(const sel of [mobile?'.mobile-menu-toggle':'.nav-buttons button',...(mobile?['.mobile-nav-buttons button']:[])]){
    const count=await evaluate(`document.querySelectorAll('${sel}').length`);
    for(let i=0;i<count;i++){await evaluate(`document.querySelectorAll('${sel}')[${i}].focus()`);const f=await evaluate(`(()=>{const s=getComputedStyle(document.activeElement);return {outline:s.outlineStyle,width:s.outlineWidth};})()`);assert.deepEqual(f,{outline:'solid',width:'3px'});}
   }
  }
  if(mobile){
   for(const value of ['light','dark','system']){await choose('theme-mobile',value);assert.deepEqual((await state()).values,[value,value]);await reload();await evaluate(`document.querySelector('.mobile-menu-toggle').click()`);assert.deepEqual((await state()).values,[value,value]);}
   await evaluate(`document.querySelector('.mobile-nav-buttons button:last-child').focus()`);await key('Tab','Tab',9);assert.equal(await evaluate('document.activeElement.id'),'theme-mobile');await key('Tab','Tab',9,8);assert.equal(await evaluate(`document.activeElement===document.querySelector('.mobile-nav-buttons button:last-child')`),true);
   await evaluate(`document.querySelector('.mobile-menu-toggle').click()`);
  }else{await evaluate(`document.querySelector('.nav-buttons button:last-of-type').focus()`);await key('Tab','Tab',9);assert.equal(await evaluate('document.activeElement.id'),'theme-desktop');await key('Tab','Tab',9,8);assert.equal(await evaluate(`document.activeElement===document.querySelector('.nav-buttons button:last-of-type')`),true);}
 }
 evidence.checks.push('Cuatro viewports ambos temas: ubicación, header sin fila nueva, foco 3px, Tab/Mayús+Tab; persistencia móvil tres opciones');
 await viewport(360,800);await evaluate(`document.querySelector('.mobile-menu-toggle').focus()`);await key('Enter','Enter',13);assert.equal(await evaluate(`!!document.getElementById('theme-mobile')`),true);await choose('theme-mobile','system');await media('light');assert.equal((await state()).theme,'light');await media('dark');assert.equal((await state()).theme,'dark');await viewport(1366,768);assert.equal((await state()).values[0],'system');
 const ax=await send('Accessibility.getFullAXTree');evidence.accessibleNames=ax.nodes.filter(n=>['combobox','button'].includes(n.role?.value)).map(n=>({role:n.role.value,name:n.name?.value}));assert(evidence.accessibleNames.some(n=>n.role==='combobox'&&n.name==='Tema'));assert(evidence.accessibleNames.some(n=>n.name.includes('Buscar Dirección')));
 await viewport(360,800);const mobileAX=await send('Accessibility.getFullAXTree');assert(mobileAX.nodes.some(n=>n.role?.value==='button'&&n.name?.value==='Menú'));assert(mobileAX.nodes.some(n=>n.role?.value==='combobox'&&n.name?.value==='Tema'));
 evidence.checks.push('Menú por Enter, Sistema móvil vivo, cambio responsive sincronizado y nombre AX Tema');
 assert.deepEqual(evidence.errors,[]);assert(evidence.requests.every(r=>r.method==='GET'));evidence.checks.push('Consola limpia; solo GET, WFS vacío y cartografía controlados; sin mutaciones');evidence.result='pasa';await send('Browser.close');
})().catch(error=>{evidence.result='falla';evidence.failure=error.message;console.error(error);process.exitCode=1;}).finally(async()=>{writeFileSync(join(__dirname,`t11-${phase}-result.json`),JSON.stringify(evidence,null,2));console.log(JSON.stringify({phase,result:evidence.result,failure:evidence.failure,checks:evidence.checks,measurements:evidence.measurements.map(m=>({viewport:m.viewport,theme:m.theme,header:m.nav.height}))},null,2));if(ws)ws.close();if(chrome&&chrome.exitCode===null){await Promise.race([new Promise(r=>chrome.once('exit',r)),delay(3000)]);if(chrome.exitCode===null)chrome.kill();}for(let i=0;i<10;i++){try{rmSync(profile,{recursive:true,force:true});break;}catch{await delay(200);}}});
