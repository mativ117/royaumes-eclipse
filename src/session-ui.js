'use strict';

// The browser's share sheet is opened only after the player chooses Share.
// Invitations remain in memory; no codes, addresses or files enter a save.
const sessionUi={initialized:false,busy:false,outgoing:null,status:'',generation:0,downloadUrl:null};
function sessionElement(tag,text='',className=''){
 const element=document.createElement(tag);if(text)element.textContent=text;if(className)element.className=className;return element;
}
function sessionButton(id,text,action,className='secondary'){
 const button=sessionElement('button',text,className);button.id=id;button.type='button';button.onclick=action;return button;
}
function sessionField(labelText,control){const label=sessionElement('label',labelText);label.htmlFor=control.id;const group=sessionElement('div','','session-field');group.append(label,control);return group;}
function setLanStatus(message){sessionUi.status=String(message||'');const status=$('#lanStatus');if(status)status.textContent=sessionUi.status;}
function clearLanInvitation(){
 sessionUi.outgoing=null;sessionUi.generation++;
 if(sessionUi.downloadUrl){URL.revokeObjectURL(sessionUi.downloadUrl);sessionUi.downloadUrl=null;}
 const code=$('#lanOutgoingCode');if(code)code.value='';const incoming=$('#lanIncomingCode');if(incoming)incoming.value='';
 const file=$('#lanIncomingFile');if(file)file.value='';
}
function sessionHeroOptions(select){
 const previous=select.value;select.replaceChildren();
 for(const [id,definition]of Object.entries(HERO_DEFS)){
  if(definition.secret&&!secretUnlocked())continue;const option=sessionElement('option',definition.name);option.value=id;select.append(option);
 }
 if([...select.options].some(o=>o.value===previous))select.value=previous;else select.value=hero==='rempart'?'lame':'rempart';
}
function sessionLanError(error){
 const protocol=error?.name==='EclipseLanProtocolError',message=protocol?(error.code==='invitation-expirée'?'Cette invitation ou réponse a expiré. Créez une nouvelle connexion.':error.code==='invitation-session'?'Cette réponse appartient à une autre invitation. Ouvrez celle de votre partenaire.':error.code==='sdp-réseau-local'?'Aucune connexion locale utilisable n’a été trouvée. Vérifiez le Wi-Fi et créez une nouvelle invitation.':'Ce fichier ou ce code n’est pas une invitation de jeu valide. Demandez un nouvel échange à votre partenaire.'):(error instanceof Error?error.message:'L’échange n’a pas pu être terminé. Créez une nouvelle invitation.');
 setLanStatus(message);refreshSessionUI();
}
async function sessionLanTask(task){
 if(sessionUi.busy)return;sessionUi.busy=true;refreshSessionUI();
 try{await task();}catch(error){sessionLanError(error);}finally{sessionUi.busy=false;refreshSessionUI();}
}
function sessionKeepOutgoing(envelope){
 sessionUi.outgoing=envelope;$('#lanOutgoingCode').value=JSON.stringify(envelope);refreshSessionUI();
 setLanStatus(envelope.kind==='offer'?'Invitation prête. Envoyez-la à l’autre joueur, puis ouvrez sa réponse ici.':'Réponse prête. Renvoyez-la au créateur de l’invitation. Gardez cette page ouverte.');
}
async function sessionImportLan(raw){
 if(typeof raw!=='string'||new TextEncoder().encode(raw).byteLength>EclipseLanProtocol.MAX_PACKET_BYTES)throw Error('Ce fichier de connexion est trop volumineux.');
 const envelope=EclipseLanProtocol.parsePairEnvelope(raw);
 if(envelope.kind==='offer'){
  if(lanSession.peer?.role==='host'&&!lanSession.peer.closed)throw Error('Vous avez créé une invitation sur cet appareil. Ouvrez la réponse de votre partenaire, ou fermez cette connexion avant de rejoindre une autre invitation.');
  clearLanInvitation();const response=await acceptLanInvitation(raw);sessionKeepOutgoing(response);
 }else{
  await acceptLanAnswer(raw);clearLanInvitation();setLanStatus('Réponse acceptée. Connexion directe en cours…');
 }
}
function sessionOutgoingFile(){
 if(!sessionUi.outgoing)throw Error('Préparez d’abord une invitation ou une réponse.');
 // Revalidate expiry when exporting again; stale files must not look reusable.
 const value=EclipseLanProtocol.parsePairEnvelope(sessionUi.outgoing);
 return new File([JSON.stringify(value)],value.kind==='offer'?'eclipse-invitation.json':'eclipse-reponse.json',{type:'application/json'});
}
function downloadLanInvitation(){
 try{
  const file=sessionOutgoingFile();if(sessionUi.downloadUrl)URL.revokeObjectURL(sessionUi.downloadUrl);
  const url=URL.createObjectURL(file);sessionUi.downloadUrl=url;const link=document.createElement('a');link.href=url;link.download=file.name;link.click();
  setTimeout(()=>{if(sessionUi.downloadUrl===url){URL.revokeObjectURL(url);sessionUi.downloadUrl=null;}},10000);
  setLanStatus('Fichier prêt à être envoyé à votre partenaire. Gardez le jeu ouvert pendant l’échange.');
 }catch(error){sessionLanError(error);}
}
async function shareLanInvitation(){
 try{
  const file=sessionOutgoingFile();
  if(navigator.share&&navigator.canShare?.({files:[file]}))await navigator.share({title:'Les Royaumes de l’Éclipse',files:[file]});
  else{downloadLanInvitation();return;}
  setLanStatus('Partage terminé. Gardez le jeu ouvert et poursuivez l’échange sur l’autre appareil.');
 }catch(error){if(error?.name==='AbortError')setLanStatus('Partage annulé. L’invitation reste disponible.');else sessionLanError(error);}
}
async function copyLanInvitation(){
 try{const file=sessionOutgoingFile(),code=await file.text();if(!navigator.clipboard?.writeText)throw Error('Copie automatique indisponible. Sélectionnez le code dans le champ ci-dessous.');await navigator.clipboard.writeText(code);setLanStatus('Code copié. Envoyez-le à votre partenaire.');}
 catch(error){sessionLanError(error);}
}
function refreshSessionUI(){
 if(!sessionUi.initialized)return;
 const mode=selectedMode(),network=mode==='lan',duel=mode==='duel',peer=lanSession.peer,active=lanActive(),connected=!!peer?.connected,ready=connected&&!!lanSession.remote;
 $('#duelOptions').hidden=!duel;$('#lanPanel').hidden=!network;
 const chapter=$('#chapterSelect'),chapterLabel=document.querySelector('label[for="chapterSelect"]');if(chapter)chapter.hidden=mode!=='solo';if(chapterLabel)chapterLabel.hidden=mode!=='solo';
 $('#modeDescription').textContent=network?'Duel entre deux appareils · même réseau · sans PC obligatoire':duel?'Duel contre un adversaire tactique · calculé sur cet appareil':'Aventure solo · trois chapitres';
 const start=$('#start'),loading=typeof avatarRuntime==='undefined'||avatarRuntime.status!=='ready'||!Object.hasOwn(avatarRuntime.heroes,hero)||partyLoading;
 const disableStart=loading||sessionUi.busy;if(start.disabled!==disableStart)start.disabled=disableStart;
 start.textContent=network?'Préparer le duel réseau →':duel?'Entrer dans le cercle →':'Nouvelle expédition →';
 $('#lanCreate').disabled=sessionUi.busy||active||!EclipseLanPeer.supported();
 $('#lanIncomingFile').disabled=sessionUi.busy||connected;$('#lanImportCode').disabled=sessionUi.busy||connected;$('#lanIncomingCode').disabled=sessionUi.busy||connected;
 for(const id of ['lanDownload','lanShare','lanCopy'])$('#'+id).disabled=sessionUi.busy||!sessionUi.outgoing;
 $('#lanReady').disabled=sessionUi.busy||!ready||lanSession.localReady||lanSession.started;
 $('#lanStart').hidden=peer?.role!=='host';$('#lanStart').disabled=sessionUi.busy||!connected||!lanSession.localReady||!lanSession.remoteReady||lanSession.started||lanSession.starting;
 $('#lanClose').disabled=!peer;
 $('#lanOwnHero').textContent='Votre personnage : '+HERO_DEFS[lanSession.selfHero||hero].name;
 $('#lanPlayers').textContent=connected?(lanSession.remote?(lanSession.remote.name+' · '+HERO_DEFS[lanSession.remote.hero].name+' · '+(peer.role==='host'?(lanSession.remoteReady?'prêt':'se prépare'):'hôte')):'Connexion établie · attente du partenaire…'):'';
 $('#lanLocalReady').textContent=lanSession.localReady?'Votre personnage est prêt.':'';
 for(const button of document.querySelectorAll('[data-hero]'))button.disabled=active||!!HERO_DEFS[button.dataset.hero]?.secret&&!secretUnlocked();
 if((connected||peer?.closed)&&sessionUi.outgoing)clearLanInvitation();
 if(!EclipseLanPeer.supported()&&!sessionUi.status)setLanStatus('La connexion directe n’est pas disponible dans ce navigateur. Utilisez un navigateur récent sur les deux appareils.');
}
function initSessionUI(){
 if(sessionUi.initialized)return;sessionUi.initialized=true;
 const style=sessionElement('style');style.textContent=`.session-options{margin:14px 0;padding:16px;border:1px solid #67523d;border-radius:10px;background:#17141de8}.session-options[hidden]{display:none!important}.session-options h3{font:24px Georgia,serif;margin:0 0 12px;color:#f6d5a7}.session-options p{font-size:13px;line-height:1.6}.session-field{margin:12px 0}.session-field label{display:block;margin-bottom:6px;font-size:14px}.session-field select,.session-field textarea{width:100%;max-width:100%;font:inherit;padding:11px;background:#25212c;color:#f7e8d3;border:1px solid #806447;border-radius:6px}.session-options button{min-height:44px;margin:5px 7px 5px 0}.session-options input[type=file]{display:block;max-width:100%;margin:8px 0}.session-actions{display:flex;gap:7px;flex-wrap:wrap}.session-actions button{margin-right:0}.session-options textarea{min-height:90px;resize:vertical;overflow-wrap:anywhere;font:12px/1.5 ui-monospace,monospace}.session-options details{margin-top:14px}.session-options summary{cursor:pointer}.session-options [role=status]{min-height:24px;color:#ffe0a8}.session-options .session-step{margin:12px 0 5px;color:#ead5b7}.session-mode-label{display:block;margin:12px 0 6px;font-size:14px}#playMode{display:block;width:100%;max-width:100%;padding:11px;font:inherit}#duelBrain{position:fixed;left:10px;right:10px;bottom:29px;text-align:center;pointer-events:none;color:#e8ccaa;font:11px system-ui;z-index:2}@media(max-width:600px){.session-options{padding:13px}.session-actions button{flex:1 1 130px}#duelBrain{bottom:204px;font-size:10px}}`;
 document.head.append(style);
 const select=$('#playMode');select.hidden=false;select.replaceChildren();
 for(const [value,text]of[['solo','Aventure solo'],['duel','Duel contre l’IA'],['lan','Duel en réseau local']]){const option=sessionElement('option',text);option.value=value;select.append(option);}
 const modeLabel=sessionElement('label','Comment voulez-vous jouer ?','session-mode-label');modeLabel.htmlFor='playMode';select.before(modeLabel);
 const panel=sessionElement('section','','session-options');panel.id='duelOptions';panel.setAttribute('aria-labelledby','duelOptionsTitle');const title=sessionElement('h3','Le Cercle des deux lunes');title.id='duelOptionsTitle';panel.append(title,sessionElement('p','Trois manches gagnantes. L’adversaire cherche des ouvertures, contourne les abris et utilise ses pouvoirs. Le duel ne modifie pas votre aventure.'));
 const opponent=sessionElement('select');opponent.id='duelOpponentHero';sessionHeroOptions(opponent);panel.append(sessionField('Personnage adverse',opponent));
 const difficulty=sessionElement('select');difficulty.id='botDifficulty';for(const [value,text]of[['tactician','Stratège'],['veteran','Vétéran']]){const option=sessionElement('option',text);option.value=value;difficulty.append(option);}panel.append(sessionField('Style de l’adversaire',difficulty));
 const lan=sessionElement('section','','session-options');lan.id='lanPanel';lan.setAttribute('aria-labelledby','lanTitle');const lanTitle=sessionElement('h3','Un cercle, deux appareils');lanTitle.id='lanTitle';lan.append(lanTitle,sessionElement('p','Ouvrez ce jeu sur les deux appareils, connectés au même Wi-Fi ou réseau local. Un joueur crée une invitation ; l’autre l’ouvre et lui renvoie une réponse. Aucun PC ni compte n’est nécessaire.'));
 const own=sessionElement('p');own.id='lanOwnHero';lan.append(own);
 lan.append(sessionElement('p','1 · Créer une invitation, ou ouvrir celle du partenaire.','session-step'));
 const create=sessionButton('lanCreate','Créer une invitation',()=>sessionLanTask(async()=>{clearLanInvitation();sessionKeepOutgoing(await createLanInvitation());}),'primary');lan.append(create);
 const incoming=sessionElement('input');incoming.id='lanIncomingFile';incoming.type='file';incoming.accept='.json,application/json';incoming.onchange=()=>sessionLanTask(async()=>{const file=incoming.files?.[0];if(!file)return;if(file.size>EclipseLanProtocol.MAX_PACKET_BYTES)throw Error('Ce fichier de connexion est trop volumineux.');await sessionImportLan(await file.text());incoming.value='';});lan.append(sessionField('Ouvrir une invitation ou une réponse',incoming));
 lan.append(sessionElement('p','2 · Envoyer le fichier préparé. La réponse revient au créateur de l’invitation.','session-step'));
 const exports=sessionElement('div','','session-actions');exports.append(sessionButton('lanShare','Partager le fichier',shareLanInvitation),sessionButton('lanDownload','Télécharger le fichier',downloadLanInvitation));lan.append(exports);
 const details=sessionElement('details');details.append(sessionElement('summary','Échanger un code au lieu d’un fichier'));const outgoing=sessionElement('textarea');outgoing.id='lanOutgoingCode';outgoing.readOnly=true;outgoing.spellcheck=false;outgoing.autocomplete='off';details.append(sessionField('Code à envoyer',outgoing),sessionButton('lanCopy','Copier le code',copyLanInvitation));const code=sessionElement('textarea');code.id='lanIncomingCode';code.maxLength=EclipseLanProtocol.MAX_PACKET_BYTES;code.spellcheck=false;code.autocomplete='off';details.append(sessionField('Coller le code reçu',code),sessionButton('lanImportCode','Ouvrir le code reçu',()=>sessionLanTask(async()=>{const value=code.value.trim();if(!value)throw Error('Collez le code de votre partenaire.');await sessionImportLan(value);code.value='';})));lan.append(details);
 lan.append(sessionElement('p','3 · Quand les deux appareils sont connectés, préparez vos personnages. L’hôte lance ensuite le duel.','session-step'));
 const players=sessionElement('p');players.id='lanPlayers';const ready=sessionElement('p');ready.id='lanLocalReady';lan.append(players,ready);
 const actions=sessionElement('div','','session-actions');actions.append(sessionButton('lanReady','Je suis prêt',()=>sessionLanTask(readyLanPlayer)),sessionButton('lanStart','Lancer le duel',()=>sessionLanTask(startLanDuel),'primary'),sessionButton('lanClose','Fermer la connexion',()=>{closeLanSession();clearLanInvitation();refreshSessionUI();}));lan.append(actions);
 const status=sessionElement('p');status.id='lanStatus';status.setAttribute('role','status');status.setAttribute('aria-live','polite');lan.append(status,sessionElement('p','Les invitations expirent après dix minutes. Partagez-les seulement avec votre partenaire et gardez cette page ouverte. Certains réseaux invités isolent les appareils et empêchent cette connexion directe.'));
 $('#modeDescription').after(panel,lan);
 const brain=sessionElement('div');brain.id='duelBrain';brain.hidden=true;document.body.append(brain);
 select.onchange=()=>{if(lanActive())closeLanSession('manual',true);clearLanInvitation();setLanStatus('');clearInputs();sessionHeroOptions(opponent);refreshSessionUI();};
 $('.heroChoices').addEventListener('click',()=>{queueMicrotask(()=>{sessionHeroOptions(opponent);refreshSessionUI();});});
 const observer=new MutationObserver(()=>refreshSessionUI());observer.observe($('#start'),{attributes:true,attributeFilter:['disabled']});
 const profileObserver=new MutationObserver(()=>sessionHeroOptions(opponent));profileObserver.observe($('.heroChoices'),{childList:true});
 refreshSessionUI();
}
