'use strict';
/* Télésiège Escondus V15 (Vars Les Claux, SEM SEDEV, Leitner) — configuration pour le moteur osmrides (moteur chargé par version, jeu.html).
   Données OSM : lieux/ski/vars/escondus.data.js (tools/make_ski.py). Ce qui est ESTIMÉ est signalé « ESTIMÉ ».
   OSM : chair_lift, 4 places (aerialway:occupancy), débrayable, 2000 p/h (capacity), 5,5 min (duration), 1367 m.
   Le moteur 0.0.1 ne connaît que les montagnes russes : le télésiège est un « train » de 4 sièges (1 rangée de 4) sur un circuit fermé, le câble ;
   le garage, la file et l'embarquement ci-dessous sont des PLACEHOLDERS ESTIMÉS pour que le moteur démarre (voir le rapport : besoins du moteur). */
const SITE=(()=>{
  const C=OSM.cps,P=i=>[C[i][0],C[i][2]],top=C.findIndex(c=>c.includes('lift1')),Q=P(top);
  const u=(()=>{const a=P(1),b=P(4),d=Math.hypot(b[0]-a[0],b[1]-a[1]);return [(b[0]-a[0])/d,(b[1]-a[1])/d];})();
  const off=(p,d,e)=>[p[0]+u[0]*d+u[1]*e,p[1]+u[1]*d-u[0]*e];
  // Saison d'affichage des pistes : ?saison=ete | hiver (défaut hiver), bouton « Pistes : hiver / été » en haut à gauche.
  let saison='hiver';try{saison=/[?&]saison=ete/.test(location.search)?'ete':localStorage.getItem('osmrides.saison')==='ete'&&!/[?&]saison=hiver/.test(location.search)?'ete':'hiver';}catch(e){}
  const bouton=document.createElement('button');
  bouton.style.cssText='position:fixed;right:8px;top:56px;z-index:20;font-size:12px;padding:3px 8px;opacity:.9';
  const maj=()=>{bouton.textContent='Pistes : '+(saison==='ete'?'été':'hiver');};maj();
  bouton.onclick=()=>{saison=saison==='ete'?'hiver':'ete';maj();try{localStorage.setItem('osmrides.saison',saison);}catch(e){}};
  addEventListener('DOMContentLoaded',()=>document.body.appendChild(bouton));if(document.body)document.body.appendChild(bouton);
  // Pistes : largeur ESTIMÉE (OSM n'en donne pas) ; couleurs de difficulté françaises (vert, bleu, rouge, noir) sourdes.
  const DIFF={novice:'#6f8f68',easy:'#5f7f9c',intermediate:'#9c5a52',advanced:'#3c3f45',expert:'#3c3f45',freeride:'#7a6a8a'},LARG={downhill:16,nordic:4,sled:6,snow_park:20,skitour:3,connection:6,hike:2};
  const path=p=>{const o=new Path2D;p.forEach((q,i)=>i?o.lineTo(q[0],q[1]):o.moveTo(q[0],q[1]));return o;};
  const PI=OSM.pistes.map(f=>({f,p:path(f.p),w:LARG[f.t]||6,col:DIFF[f.d]||'#8a8f96'})),LI=OSM.lifts.map(f=>({f,p:path(f.p)})),LL=path(C.slice(0,top+1).map(c=>[c[0],c[2]]));
  const PY=OSM.pylons;
  return {id:'escondus',title:'Télésiège Escondus V15',kind:'steel',goal:400,lap:150,
    // ESTIMÉ : 4 places côte à côte par siège, pas de 12 m entre sièges, soit 5 sièges par km de câble par brin (2000 p/h : 500 sièges/h, vitesse du câble ≈ 1367 m / 5,5 min = 4,1 m/s)
    car:{len:2,n:4,seats:4},trains:[{name:'Câble',col:'#4d5a66',col2:'#c9ced4',wear:20}],
    // PLACEHOLDER : le moteur exige un garage ; ici un tronçon sans sens à côté de la gare aval (ESTIMÉ, hors OSM)
    yard:{at:'station',device:'switch',a:.8,b:6.4,slide:3.4,side:-1,len:8.6,lanes:[{name:'Garage',pts:[off(P(1),30,-8),off(P(1),60,-8)]}],move:{v:2.4,t:3}},
    plat:{load:7.9,exit:3,back:.1,front:1.6},board:{via:[[-3.9,7.9],[-4,6.9]],walk:5.25},
    exit:{door:[-.7,-3],path:[[-.7,-3],[-.7,-4.1],[-11.1,-4.1]],tails:[[[-11.1,-4.1],[-20,-6]]]},approach:[],
    stationPoly:OSM.polys.station,stationAt:[0,5,30],
    queue:{entry0:[10,-10],ways:[[[10,-10],[0,0]]],parts:[{pts:[[10,-10],[0,0]]}]},
    view:{x:-10,z:30,w:220,h:165,bounds:[-900,320,-230,1340]},
    cams:{aval:{label:'Gare aval',x:0,z:5,s:14},amont:{label:'Gare amont',x:Q[0],z:Q[1],s:14},ligne:{label:'Ligne',x:Q[0]/2,z:Q[1]/2,s:.7}},
    labels:()=>[['Gare aval',-20,-8],['Gare amont',Q[0]-30,Q[1]+14],['Escondus V15',Q[0]/2+20,Q[1]/2]],
    draw:{
      // Sol : pistes, autres remontées, pylônes (crochet « shadows » du moteur 0.0.1, appelé après le sol et avant la voie ; besoin : un crochet « sol » dédié)
      shadows(ctx,dry,{lw}){
        ctx.save();ctx.lineCap='round';ctx.lineJoin='round';
        const hiv=saison==='hiver';
        for(const o of PI){
          if(o.f.t==='sled'||o.f.t==='nordic'||o.f.t==='downhill'||o.f.t==='snow_park'||o.f.t==='skitour'){
            ctx.lineWidth=o.w+(hiv?2.4:1.6);ctx.strokeStyle=hiv?o.col:'rgba(70,64,52,.35)';ctx.globalAlpha=hiv?.7:1;if(o.f.c)ctx.fill(o.p);else ctx.stroke(o.p);
            ctx.lineWidth=o.w;ctx.strokeStyle=hiv?'#e9edf0':'#a9a27a';ctx.globalAlpha=hiv?.92:.55;ctx.fillStyle=ctx.strokeStyle;if(o.f.c)ctx.fill(o.p);else ctx.stroke(o.p);}
        }
        ctx.globalAlpha=1;ctx.strokeStyle='#4d525a';lw(.5,1);for(const o of LI)ctx.stroke(o.p);ctx.stroke(LL);
        ctx.fillStyle='#3c4047';for(const q of PY){ctx.beginPath();ctx.arc(q[0],q[1],1.4,0,7);ctx.fill();}
        ctx.restore();
      }}
  };
})();
