// Ouvre jeu.html en file:// avec Playwright et relève les erreurs de page et de console.
// Usage : node tools/test-page.js [moteur] [capture.jpg]   (moteur par défaut : ../osmrides/engine/)
const path=require('path');
let chromium;try{({chromium}=require('playwright'));}catch(e){({chromium}=require('/opt/node22/lib/node_modules/playwright'));}
(async()=>{
  const moteur=process.argv[2]||'../osmrides/engine/',cap=process.argv[3];
  const b=await chromium.launch({executablePath:process.env.CHROME||undefined}),p=await b.newPage({viewport:{width:600,height:450}}),err=[];
  p.on('pageerror',e=>err.push('pageerror: '+e.message+(process.env.STACK?' '+e.stack.split('\n').slice(0,3).join(' | '):'')));
  p.on('console',m=>{if(m.type()==='error'||m.type()==='warning')err.push(m.type()+': '+m.text());});
  await p.goto('file://'+path.resolve(__dirname,'..','jeu.html')+'?moteur='+moteur+(process.env.QS||''));
  await p.waitForTimeout(3000);
  if(cap)await p.screenshot({path:cap,type:'jpeg',quality:70});
  console.log(err.length?err.join('\n'):'aucune erreur');
  await b.close();process.exit(err.length?1:0);
})();
