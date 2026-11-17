'use strict';
// Keyboard preferences belong to this browser; adventure/profile formats stay unchanged.
const INPUT_STORAGE_KEY='royaumes-input-v1';
const INPUT_ACTIONS={
 forward:{label:'Avancer',keys:['z','w','arrowup'],hint:'Z / W / ↑'},back:{label:'Reculer',keys:['s','arrowdown'],hint:'S / ↓'},left:{label:'Gauche',keys:['q','a','arrowleft'],hint:'Q / A / ←'},right:{label:'Droite',keys:['d','arrowright'],hint:'D / →'},
 attack:{label:'Attaquer au clavier',keys:[],hint:'Clic gauche'},dodge:{label:'Esquiver',keys:[' '],hint:'Espace'},power:{label:'Pouvoir',keys:['e'],hint:'E'},interact:{label:'Interagir / maintenir',keys:['f'],hint:'F'},map:{label:'Carte',keys:['m'],hint:'M'},guide:{label:'Repères',keys:['g'],hint:'G'},extra:{label:'Pouvoir supplémentaire',keys:['r'],hint:'R'}
};
const INPUT_CODE_PATTERN=/^(Key[A-Z]|Digit[0-9]|Numpad[0-9]|Arrow(Up|Down|Left|Right)|Space|Shift(Left|Right)|Enter|Bracket(Left|Right)|Minus|Equal|Semicolon|Quote|Backslash|Comma|Period|Slash|Backquote)$/;
function readInputBindings(){try{const data=JSON.parse(localStorage.getItem(INPUT_STORAGE_KEY)||'{}'),result={},codes=new Set();if(!data||typeof data!=='object'||Array.isArray(data))return{};for(const [action,value]of Object.entries(data)){if(!INPUT_ACTIONS[action]||!value||!INPUT_CODE_PATTERN.test(value.code)||typeof value.label!=='string'||!value.label||value.label.length>20||codes.has(value.code))return{};result[action]={code:value.code,label:value.label};codes.add(value.code);}return result;}catch(_){return{};}}
let inputBindings=readInputBindings(),inputHeldCodes=new Set(),inputKeyboardAttack=false,inputCapture=null,inputSuppressedCodes=new Set(),inputReturnState='menu',inputReturnFocus=null;
function inputSolo(){return selectedMode()==='solo';}
function inputActionLabel(action){if(!inputSolo())return({forward:'Z / W',back:'S',left:'Q / A',right:'D'})[action]||INPUT_ACTIONS[action].hint;return inputBindings[action]?inputBindings[action].label:INPUT_ACTIONS[action].hint;}
function clearRemappedInput(){inputHeldCodes.clear();inputKeyboardAttack=false;}
function inputAttackHeld(){return inputSolo()&&inputKeyboardAttack;}
function inputMovementKeys(){const active=action=>inputSolo()&&inputBindings[action]?inputHeldCodes.has(inputBindings[action].code):INPUT_ACTIONS[action].keys.some(key=>keys.has(key)&&(inputSolo()||!key.startsWith('arrow')));return{x:Number(active('right'))-Number(active('left')),z:Number(active('back'))-Number(active('forward'))};}
function inputKeyLabel(event){return ({' ':'Espace',ArrowUp:'↑',ArrowDown:'↓',ArrowLeft:'←',ArrowRight:'→',Enter:'Entrée',Shift:event.code==='ShiftRight'?'Maj droite':'Maj gauche'})[event.key]||event.key.toLocaleUpperCase().slice(0,20);}
function inputActionForEvent(event){for(const [action,binding]of Object.entries(inputBindings))if(binding.code===event.code)return action;const key=event.key.toLowerCase();return Object.keys(INPUT_ACTIONS).find(action=>!inputBindings[action]&&INPUT_ACTIONS[action].keys.includes(key));}
function persistInputBindings(){try{localStorage.setItem(INPUT_STORAGE_KEY,JSON.stringify(inputBindings));}catch(_){$('#inputFeedback').textContent='Les touches sont actives, mais ce navigateur ne permet pas leur enregistrement.';}}
function inputEditable(target){return target?.isContentEditable||['INPUT','SELECT','TEXTAREA'].includes(target?.tagName);}
function inputMapShortcut(event){
 // Checkboxes own Space/Enter; text fields and selects own their typing keys.
 // A letter assigned to the map may still close it from a non-text form control.
 if(state!=='map'||inputActionForEvent(event)!=='map'||event.ctrlKey||event.metaKey||event.altKey||event.isComposing)return false;
 const target=event.target,key=event.key;
 if(target?.isContentEditable||target?.tagName==='TEXTAREA'||target?.tagName==='SELECT')return false;
 if(target?.tagName==='INPUT')return ['checkbox','radio','range','color','file','button','submit','reset'].includes(target.type)&&![' ','Enter','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(key);
 return true;
}
function cancelInputCapture(message='Modification annulée.'){inputCapture=null;$('#inputCancelCapture').hidden=true;$('#inputFeedback').textContent=message;renderInputRows();}
function assignInputBinding(action,event){
 const code=event.code,key=event.key.toLowerCase();if(!INPUT_CODE_PATTERN.test(code)){ $('#inputFeedback').textContent='Cette touche est réservée au navigateur. Choisissez une lettre, une flèche, un chiffre, Maj, Espace ou Entrée.';return false;}
 const conflict=Object.keys(INPUT_ACTIONS).find(other=>other!==action&&(inputBindings[other]?inputBindings[other].code===code:INPUT_ACTIONS[other].keys.includes(key)));
 if(conflict){$('#inputFeedback').textContent='Cette touche sert déjà à « '+INPUT_ACTIONS[conflict].label+' ». Modifiez d’abord cette action.';return false;}
 inputBindings[action]={code,label:inputKeyLabel(event)};inputCapture=null;inputSuppressedCodes.add(code);clearInputs();persistInputBindings();$('#inputCancelCapture').hidden=true;$('#inputFeedback').textContent=INPUT_ACTIONS[action].label+' : '+inputBindings[action].label+'.';renderInputRows();refreshInputHints();return true;
}
function handleConfiguredKeyDown(event){
 if(inputCapture){event.preventDefault();event.stopImmediatePropagation();if(event.repeat)return true;if(event.key==='Escape'){inputSuppressedCodes.add(event.code);cancelInputCapture();return true;}assignInputBinding(inputCapture,event);return true;}
 if(inputSuppressedCodes.has(event.code)){event.preventDefault();event.stopImmediatePropagation();return true;}
 // Text entry and browser shortcuts must never trigger combat or a map behind a form.
 if(inputEditable(event.target)&&!(event.key==='Escape'&&['map','choice'].includes(state))&&!inputMapShortcut(event)){event.stopImmediatePropagation();return true;}
 if(state==='input-settings'){if(event.key==='Escape'){event.preventDefault();event.stopImmediatePropagation();closeInputSettings();}return true;}
 if($('#helpDialog').open){if(event.key==='Escape'){event.preventDefault();event.stopImmediatePropagation();$('#closeHelp').click();}return true;}
 if(!inputSolo())return false;
 if(event.ctrlKey||event.metaKey||event.altKey||event.isComposing){if(state==='playing')event.stopImmediatePropagation();return true;}
 const action=inputActionForEvent(event),key=event.key.toLowerCase(),masked=Object.keys(inputBindings).some(a=>INPUT_ACTIONS[a].keys.includes(key));
 if(state==='map'&&action==='map'){event.preventDefault();event.stopImmediatePropagation();if(!event.repeat)toggleMap();return true;}
 if(state!=='playing'||(!action&&!masked))return false;
 event.preventDefault();event.stopImmediatePropagation();
 if(!action)return true;inputHeldCodes.add(event.code);if(!inputBindings[action])keys.add(key);
 if(['forward','back','left','right'].includes(action))return true;
 if(action==='attack'){inputKeyboardAttack=true;if(!event.repeat)requestAttack();return true;}
 if(event.repeat)return true;
 if(action==='dodge')requestDodge();else if(action==='power')power();else if(action==='interact')interact();else if(action==='map')toggleMap();else if(action==='guide')revealGuide();else if(action==='extra')activateIncarnation();return true;
}
function handleConfiguredKeyUp(event){
 inputHeldCodes.delete(event.code);keys.delete(event.key.toLowerCase());if(inputBindings.attack?.code===event.code)inputKeyboardAttack=false;if(inputBindings.interact?.code===event.code||!inputBindings.interact&&event.key.toLowerCase()==='f')observing=false;
 if(inputSuppressedCodes.delete(event.code)){event.preventDefault();event.stopImmediatePropagation();return;}
 if(inputEditable(event.target))return;
 if(inputSolo()&&['playing','map'].includes(state)&&(inputActionForEvent(event)||Object.keys(inputBindings).some(a=>INPUT_ACTIONS[a].keys.includes(event.key.toLowerCase())))){event.preventDefault();event.stopImmediatePropagation();}
}
function openInputSettings(){
 if(!['menu','playing','paused'].includes(state)||$('#helpDialog').open)return;inputReturnState=state;inputReturnFocus=document.activeElement;clearInputs();state='input-settings';updateSoundscape(0);$('#mobile').classList.remove('playing');$('#inputSettings').hidden=false;cancelInputCapture('');renderInputRows();$('#inputSettingsClose').focus();updateInputLayout();
}
function closeInputSettings(){if(state!=='input-settings')return;cancelInputCapture('');$('#inputSettings').hidden=true;state=inputReturnState;clearInputs();last=performance.now();accumulator=0;if(state==='playing')$('#mobile').classList.add('playing');inputReturnFocus?.focus();updateInputLayout();}
function renderInputRows(){
 const solo=inputSolo(),container=$('#inputRows');container.replaceChildren();$('#inputScope').textContent=solo?'Clavier J1 en solo. Cliquez sur une touche, puis appuyez sur celle qui doit la remplacer. Échap annule ; la souris reste disponible pour viser et attaquer.':'En coopération et en battle, les commandes fixes restent actives pour protéger le clavier du joueur 2. Vos touches personnalisées seront rétablies en solo.';
 for(const [action,definition]of Object.entries(INPUT_ACTIONS)){const row=document.createElement('div');row.className='input-row';const label=document.createElement('span');label.textContent=definition.label;const button=document.createElement('button');button.type='button';button.dataset.inputAction=action;button.disabled=!solo;button.textContent=inputCapture===action?'Appuyez sur une touche…':inputActionLabel(action);button.setAttribute('aria-label',definition.label+' : '+inputActionLabel(action)+' ; modifier');button.onclick=()=>{clearInputs();inputCapture=action;$('#inputCancelCapture').hidden=false;$('#inputFeedback').textContent='Nouvelle touche pour « '+definition.label+' ». Échap ou Annuler pour revenir.';renderInputRows();container.querySelector('[data-input-action="'+action+'"]').focus();};row.append(label,button);container.append(row);}
 $('#inputReset').disabled=!solo;$('#inputCoop').hidden=solo;
}
function refreshInputHints(){
 if(!$('#inputSettings'))return;const label=inputActionLabel;$('#mapButton').title='Carte · '+label('map');$('#guidePing').title='Repères · '+label('guide');$('#extraPower').setAttribute('aria-label','Pouvoir supplémentaire · '+label('extra'));
 $('#controls').textContent='Déplacer : '+(inputSolo()&&['forward','back','left','right'].some(a=>inputBindings[a])?['forward','left','back','right'].map(label).join(' / '):inputSolo()?'ZQSD / WASD / flèches':'ZQSD / WASD')+' · Attaquer : clic'+(inputSolo()&&inputBindings.attack?' / '+label('attack'):'')+' · Esquiver : '+label('dodge')+' · Pouvoir : '+label('power')+' · Interagir : '+label('interact');
 const menuLine=[...$('#menu').querySelectorAll('p.fine')].map(p=>p.firstChild).find(node=>node?.nodeType===Node.TEXT_NODE&&node.nodeValue.trimStart().startsWith('PC :'));if(menuLine)menuLine.nodeValue='PC : '+$('#controls').textContent+' · Carte : '+label('map')+' · Repères : '+label('guide')+' · Pouvoir supplémentaire : '+label('extra')+' · Échap : pause.';const guidanceText=[...$('#guidanceToggle').parentNode.childNodes].find(node=>node.nodeType===Node.TEXT_NODE);if(guidanceText)guidanceText.nodeValue=' Guidage discret · repères avec '+label('guide')+' / Repère';
 const help=$('#inputHelpSummary');help.textContent='Touches actives : esquive '+label('dodge')+' · pouvoir '+label('power')+' · interaction '+label('interact')+' · carte '+label('map')+' · repères '+label('guide')+'. Les boutons Commandes permettent de les revoir.';
 const instructions=[...$('#helpDialog').querySelectorAll('p')].filter(p=>p.id!=='inputHelpSummary');instructions[0].textContent='Marchez avec '+(inputSolo()&&['forward','back','left','right'].some(a=>inputBindings[a])?['forward','left','back','right'].map(label).join(' / '):inputSolo()?'ZQSD / WASD / les flèches':'ZQSD / WASD')+' ou le joystick. Visez et attaquez avec la souris. Esquivez avec '+label('dodge')+' ; utilisez votre pouvoir avec '+label('power')+'. Sur téléphone, la cible visible la plus proche est choisie.';instructions[1].textContent='Approchez les objets et utilisez '+label('interact')+' / le bouton contextuel. La carte ('+label('map')+') présente les objectifs ; les repères ('+label('guide')+') indiquent un chemin praticable. Aux ancres, la santé et la reprise sont enregistrées.'+(inputSolo()?'':' En coopération, maintenez l’interaction près d’un compagnon à terre pour le relever.');instructions[2].textContent='Manette : stick gauche pour marcher, droit pour viser, X/gâchette pour attaquer, A pour esquiver, Y pour le pouvoir, B pour interagir. Pouvoir supplémentaire : '+label('extra')+(inputSolo()?' au clavier ou RB à la manette.':' pour J1 solo, U pour J2 clavier ou RB à la manette.');
}
function updateInputLayout(){
 const overlay=[...document.querySelectorAll('.screen')].some(panel=>!panel.hidden)||$('#helpDialog').open;document.body.classList.toggle('ui-overlay-open',overlay);
 if(innerWidth>900){const rect=$('.hudButtons').getBoundingClientRect();$('#miniMap').style.setProperty('--minimap-top',Math.max(82,rect.bottom+14)+'px');}
}
function initInputSettings(){
 const style=document.createElement('style');style.textContent=`
 .mapDrawing #largeMap{position:static;inset:auto;display:block;width:100%;height:auto;touch-action:auto}
 body.ui-overlay-open #hud,body.ui-overlay-open #miniMap,body.ui-overlay-open #controls,body.ui-overlay-open #bossHUD,body.ui-overlay-open #interact,body.ui-overlay-open #notice,body.ui-overlay-open #zoneBanner,body.ui-overlay-open #partyStatus{visibility:hidden}
 #inputSettings{z-index:45;justify-content:center;background:#100d16ed;padding:20px}
 .input-panel{width:min(100%,720px);max-height:90dvh;overflow:auto;background:#17131c;border:1px solid #9c7954;border-radius:10px;padding:clamp(18px,3vw,34px)}
 .input-panel h2{font:32px Georgia;margin:18px 0}.input-panel p{font-size:14px;max-width:none}.input-row{display:grid;grid-template-columns:1fr minmax(120px,230px);gap:16px;align-items:center;border-top:1px solid #4a3a32;padding:9px 0;font-size:14px}.input-row button,.input-panel .secondary{border:1px solid #876848;background:#28202c;color:#f7eadb;border-radius:5px;padding:10px;font:inherit}.input-row button:disabled{opacity:.55;cursor:default}#inputFeedback{min-height:24px;color:#ffd28d}#inputHelpSummary{border-left:2px solid #d89c5d;padding-left:14px;color:#ffdbac}#inputReset,#inputCancelCapture{margin:8px 8px 0 0}.input-entry{margin:10px 10px 10px 0}
 @media(min-width:901px){#miniMap{top:var(--minimap-top,154px)}}
 @media(min-width:901px) and (pointer:fine){.hudButtons{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));width:300px;max-width:300px;gap:6px}.hudButtons button{min-width:0;min-height:36px;font-size:12px;padding:8px}.hud .plate,body.immersive .hud .plate{max-width:min(350px,calc(100vw - 370px))}#miniMap{position:fixed;inset:auto 20px auto auto;top:var(--minimap-top,154px);width:120px;height:133px}#controls{display:block;left:50%;right:auto;transform:translateX(-50%);width:max-content;max-width:calc(100vw - 48px);bottom:12px;background:#121019e6;border:1px solid #70523c;border-radius:6px;padding:8px 12px;font-size:11px;line-height:1.5}}
 @media(max-width:600px){.input-row{grid-template-columns:minmax(90px,1fr) minmax(120px,1fr);gap:10px;font-size:13px}.input-panel h2{font-size:28px}#inputSettings{padding:12px}}
 `;document.head.append(style);
 const screen=document.createElement('section');screen.id='inputSettings';screen.className='screen';screen.hidden=true;screen.setAttribute('role','dialog');screen.setAttribute('aria-modal','true');screen.setAttribute('aria-labelledby','inputTitle');screen.innerHTML='<article class="input-panel"><button class="secondary" id="inputSettingsClose">Fermer les commandes</button><h2 id="inputTitle">Vos commandes</h2><p id="inputScope"></p><p>Souris : viser et clic gauche pour attaquer. Échap : pause / retour. Les touches sont enregistrées dans ce navigateur.</p><div id="inputRows"></div><p id="inputFeedback" role="status" aria-live="polite"></p><button id="inputCancelCapture" class="secondary" hidden>Annuler la modification</button><button id="inputReset" class="secondary">Rétablir les touches d’origine</button><p id="inputCoop" hidden>J2 clavier : flèches · J pour attaquer · Maj droite pour esquiver · Ctrl droite pour le pouvoir · Entrée pour interagir ou relever · U pour le pouvoir supplémentaire.</p><p>Téléphone : joystick à gauche, attaque, esquive et pouvoir à droite. Utilisez le bouton contextuel près des objets. Manette : sticks pour marcher / viser, X ou gâchette pour attaquer, A pour esquiver, Y pour le pouvoir, B pour interagir.</p></article>';document.body.append(screen);
 for(const [parent,where,id]of [[$('#helpButton'),'after','inputSettingsButton'],[$('#start'),'before','inputSettingsMenuButton'],[$('#resume'),'after','inputSettingsPauseButton']]){const button=document.createElement('button');button.type='button';button.id=id;button.textContent='Commandes';button.className=where==='after'&&parent.id==='helpButton'?'':'secondary input-entry';button.onclick=openInputSettings;parent[where](button);}
 const summary=document.createElement('p');summary.id='inputHelpSummary';$('#helpDialog h2').after(summary);
 $('#inputSettingsClose').onclick=closeInputSettings;$('#inputCancelCapture').onclick=()=>cancelInputCapture();$('#inputReset').onclick=()=>{inputBindings={};clearInputs();inputCapture=null;inputSuppressedCodes.clear();persistInputBindings();renderInputRows();refreshInputHints();$('#inputCancelCapture').hidden=true;$('#inputFeedback').textContent='Touches d’origine rétablies.';};
 addEventListener('keydown',event=>{if(state==='input-settings'&&event.key==='Tab'&&!inputCapture){const buttons=[...screen.querySelectorAll('button:not(:disabled)')].filter(b=>!b.hidden),first=buttons[0],last=buttons.at(-1);if(event.shiftKey&&document.activeElement===first){event.preventDefault();last.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}}handleConfiguredKeyDown(event);},true);addEventListener('keyup',handleConfiguredKeyUp,true);addEventListener('blur',clearRemappedInput);
 $('#playMode').addEventListener('change',()=>{clearRemappedInput();refreshInputHints();});addEventListener('resize',updateInputLayout);
 const observer=new MutationObserver(()=>queueMicrotask(updateInputLayout));for(const panel of document.querySelectorAll('.screen,#helpDialog,#hud'))observer.observe(panel,{attributes:true,attributeFilter:['hidden','open']});if(typeof ResizeObserver!=='undefined'){const resizeObserver=new ResizeObserver(updateInputLayout);resizeObserver.observe($('.hudButtons'));}
 renderInputRows();refreshInputHints();updateInputLayout();
}
