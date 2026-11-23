'use strict';
/* Catalogue du jeu : type -> lieu -> éléments. Chargé par jeu.html. Les fichiers d'un élément : lieux/<type>/<lieu>/<el>.data.js | .js | .game.js. */
const TYPES=[{id:'ski',nom:'Domaines skiables'}];
const LIEUX=[{type:'ski',id:'vars',nom:'Vars Les Claux',elements:[{id:'escondus',nom:'Télésiège Escondus V15'}]}];
const lieuDir=(t,l)=>'lieux/'+t+'/'+l+'/';
const cleSauvegarde=(t,l,el,mode)=>'t2z.save.'+t+'.'+l+'.'+el+'.'+mode; // clés t2z.* : ancien nom du jeu, comme osmrides
