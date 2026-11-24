'use strict';
const heroPreviewRuntime={panel:null,frame:null,selected:null,readyHero:null,inView:false,active:false,supported:false,message:'',timeout:null,observer:null};
function heroPreviewAllowed(id){return typeof id==='string'&&Object.hasOwn(HERO_DEFS,id)&&(!HERO_DEFS[id].secret||secretUnlocked());}
function heroPreviewActive(){const view=heroPreviewRuntime;return !!(view.frame&&view.inView&&state==='menu'&&!$('#menu').hidden&&!document.hidden);}
function heroPreviewPost(message,frame=heroPreviewRuntime.frame){if(frame?.contentWindow)frame.contentWindow.postMessage(message,location.origin);}
function heroPreviewFeedback(){if(!heroPreviewRuntime.panel)return;$('#heroPreviewFeedback').textContent=$('#menuFeedback')?.textContent.trim()||heroPreviewRuntime.message;}
function heroPreviewPlayState(){if(!heroPreviewRuntime.panel)return;const start=$('#start'),button=$('#heroPreviewPlay');button.disabled=start.disabled||!heroPreviewAllowed(heroPreviewRuntime.selected);button.textContent=start.disabled?'Préparation du personnage…':'Jouer avec ce personnage';}
function heroPreviewDispose(){
 const view=heroPreviewRuntime,frame=view.frame;clearTimeout(view.timeout);view.timeout=null;view.frame=null;view.readyHero=null;view.active=false;
 if(frame){heroPreviewPost({type:'review-active',active:false},frame);heroPreviewPost({type:'review-dispose'},frame);frame.hidden=true;setTimeout(()=>{frame.src='about:blank';frame.remove();},50);}
 if(view.panel){$('#heroPreviewPlaceholder').hidden=false;view.message='L’aperçu se recharge lorsque vous revenez à la sélection.';heroPreviewFeedback();}
}
function heroPreviewWatchLoading(){
 const view=heroPreviewRuntime;clearTimeout(view.timeout);const frame=view.frame,id=view.selected;view.timeout=setTimeout(()=>{if(view.frame!==frame||view.selected!==id||view.readyHero===id)return;view.message='L’aperçu met du temps à charger. Vous pouvez lancer le jeu dès que le personnage est prêt.';heroPreviewFeedback();},20000);
}
function heroPreviewCreate(){
 const view=heroPreviewRuntime;if(view.frame||!view.supported||!heroPreviewAllowed(view.selected)||state!=='menu'||$('#menu').hidden||!view.inView)return;
 const frame=document.createElement('iframe'),url=new URL('./atelier-lame.html',location.href);url.searchParams.set('embedded','1');url.searchParams.set('hero',view.selected);url.searchParams.set('v',ROYAUMES_VERSION);frame.title='Aperçu 3D : '+HERO_DEFS[view.selected].name;frame.className='hero-preview-frame';frame.setAttribute('loading','lazy');frame.setAttribute('allow','fullscreen');frame.src=url.href;view.frame=frame;view.readyHero=null;view.message='Chargement de l’aperçu 3D…';$('#heroPreviewPlaceholder').hidden=true;$('#heroPreviewStage').append(frame);
 frame.addEventListener('load',()=>{if(view.frame!==frame)return;heroPreviewPost({type:'review-hero',hero:view.selected});heroPreviewPost({type:'review-active',active:heroPreviewActive()});});frame.addEventListener('error',()=>{if(view.frame!==frame)return;view.message='L’aperçu est indisponible. La sélection et le lancement du jeu restent accessibles.';heroPreviewFeedback();});heroPreviewWatchLoading();heroPreviewFeedback();
}
function heroPreviewSyncActivity(){
 const view=heroPreviewRuntime;if(!view.panel)return;
 if($('#menu').hidden||state==='playing'){heroPreviewDispose();return;}
 if(view.inView&&state==='menu'&&!document.hidden)heroPreviewCreate();
 const active=heroPreviewActive();if(active!==view.active){view.active=active;heroPreviewPost({type:'review-active',active});}
 heroPreviewPlayState();
}
function heroPreviewSelect(id){
 const view=heroPreviewRuntime;if(!heroPreviewAllowed(id))return;const changed=id!==view.selected;view.selected=id;const definition=HERO_DEFS[id];$('#heroPreviewName').textContent=definition.name;$('#heroPreviewKit').textContent=definition.weapon+' · '+definition.description;$('#heroPreviewTruth').textContent=id==='lame'?'Étude 3D en cours : proportions, matières et animations restent à revoir.':'Personnage retravaillé : silhouette, matières et mouvements propres à son équipement. La finition reste à éprouver en jeu.';
 if(changed){view.readyHero=null;view.message=view.supported?'Chargement de l’aperçu 3D…':'L’aperçu 3D intégré est disponible depuis la page en ligne. Vous pouvez toujours choisir un personnage et lancer le jeu ici.';if(view.frame){view.frame.title='Aperçu 3D : '+definition.name;heroPreviewPost({type:'review-hero',hero:id});heroPreviewWatchLoading();}}
 heroPreviewPlayState();heroPreviewFeedback();heroPreviewSyncActivity();
}
function handleHeroPreviewMessage(event){
 const view=heroPreviewRuntime;if(!view.frame||event.origin!==location.origin||event.source!==view.frame.contentWindow||!heroPreviewAllowed(event.data?.hero))return;
 const type=event.data?.type;if(type!=='review-ready'&&type!=='review-error')return;
 if(event.data.hero!==view.selected){if(type==='review-ready')heroPreviewPost({type:'review-hero',hero:view.selected});return;}
 clearTimeout(view.timeout);view.timeout=null;
 if(type==='review-error'){view.readyHero=null;view.message='L’aperçu n’a pas pu être chargé. Vous pouvez lancer le jeu si le personnage est prêt.';heroPreviewFeedback();return;}
 view.readyHero=event.data.hero;view.message='Tournez le modèle et choisissez un geste pour l’observer.';heroPreviewFeedback();heroPreviewPost({type:'review-active',active:heroPreviewActive()});
}
function initHeroPreview(){
 const view=heroPreviewRuntime,gallery=$('.heroChoices');if(view.panel||!gallery)return;view.supported=['http:','https:'].includes(location.protocol);
 const style=document.createElement('style');style.textContent=`
 #menu .panel{max-width:1150px}.hero-selection{display:grid;grid-template-columns:minmax(230px,.85fr) minmax(300px,1.15fr);gap:20px;align-items:start;margin:18px 0}.hero-selection .heroChoices{grid-template-columns:1fr;max-height:490px;overflow-y:auto;overscroll-behavior:contain;margin:0;padding:4px;min-width:0}.hero-selection .heroCard{width:100%}.hero-preview{min-width:0;padding:16px;border:1px solid #78593e;border-radius:10px;background:#131019ee}.hero-preview h2{font:clamp(24px,2.6vw,35px) Georgia;margin:3px 0 8px;color:#ffcf91}.hero-preview p{max-width:none;margin:9px 0;font-size:12px;line-height:1.55}.hero-preview-stage{position:relative;height:clamp(420px,42vw,520px);background:radial-gradient(ellipse at 50% 70%,#463124,#121018 68%);border:1px solid #4c3a30;border-radius:7px;overflow:hidden}.hero-preview-frame{position:static;display:block;width:100%;height:100%;border:0;background:#100e13}.hero-preview-placeholder{display:flex;align-items:center;justify-content:center;height:100%;padding:24px;text-align:center;color:#cbb49a;font-size:13px}.hero-preview-truth{color:#bca58c!important}.hero-preview-feedback{min-height:20px;color:#ffdb9d!important}#heroPreviewPlay{width:100%;margin-top:7px}.hero-preview .eyebrow{font-size:9px}#menu #menuFeedback{color:#ffdc9d}
 @media(max-width:700px){.hero-selection{grid-template-columns:1fr;gap:12px}.hero-selection .heroChoices{grid-template-columns:1fr 1fr;max-height:240px;order:2}.hero-selection .hero-preview{order:1;padding:12px}.hero-preview-stage{height:420px}.hero-preview h2{font-size:27px}.hero-selection .heroCard strong{font-size:17px}}
 @media(max-height:500px) and (min-width:701px){.hero-selection .heroChoices{max-height:360px}.hero-preview-stage{height:280px}}
 `;document.head.append(style);
 const layout=document.createElement('div');layout.className='hero-selection';gallery.before(layout);layout.append(gallery);const panel=document.createElement('aside');panel.className='hero-preview';panel.setAttribute('aria-label','Aperçu du personnage sélectionné');panel.innerHTML='<span class="eyebrow">Personnage sélectionné · aperçu 3D</span><h2 id="heroPreviewName"></h2><p id="heroPreviewKit"></p><div id="heroPreviewStage" class="hero-preview-stage"><div id="heroPreviewPlaceholder" class="hero-preview-placeholder">Approchez cette zone pour charger l’aperçu 3D.</div></div><p id="heroPreviewTruth" class="hero-preview-truth"></p><p id="heroPreviewFeedback" class="hero-preview-feedback" role="status" aria-live="polite"></p><button id="heroPreviewPlay" type="button" class="primary">Jouer avec ce personnage</button>';layout.append(panel);view.panel=panel;
 $('#heroPreviewPlay').onclick=()=>{if(state!=='menu'||$('#start').disabled||!heroPreviewAllowed(view.selected))return;beginCompleteRun();releaseMenuFocus();heroPreviewFeedback();heroPreviewSyncActivity();};
 gallery.addEventListener('click',event=>{const button=event.target.closest('[data-hero]');if(state==='menu'&&button&&!button.disabled&&gallery.contains(button)&&heroPreviewAllowed(button.dataset.hero))heroPreviewSelect(button.dataset.hero);});
 const selectionObserver=new MutationObserver(()=>{if(state==='menu'&&heroPreviewAllowed(hero))heroPreviewSelect(hero);});selectionObserver.observe(gallery,{attributes:true,attributeFilter:['aria-pressed','disabled'],childList:true,subtree:true});
 const menuObserver=new MutationObserver(()=>{if(!$('#menu').hidden&&heroPreviewAllowed(hero))heroPreviewSelect(hero);heroPreviewSyncActivity();});menuObserver.observe($('#menu'),{attributes:true,attributeFilter:['hidden']});for(const screen of document.querySelectorAll('.screen'))if(screen!==$('#menu'))menuObserver.observe(screen,{attributes:true,attributeFilter:['hidden']});
 const startObserver=new MutationObserver(heroPreviewPlayState);startObserver.observe($('#start'),{attributes:true,attributeFilter:['disabled']});const feedbackObserver=new MutationObserver(heroPreviewFeedback);feedbackObserver.observe($('#menuFeedback'),{childList:true,subtree:true,characterData:true});
 addEventListener('message',handleHeroPreviewMessage);
 addEventListener('visibilitychange',heroPreviewSyncActivity);addEventListener('pagehide',heroPreviewDispose);
 if(view.supported){if(typeof IntersectionObserver!=='undefined'){view.observer=new IntersectionObserver(entries=>{for(const entry of entries)if(entry.target===$('#heroPreviewStage')){view.inView=entry.isIntersecting&&entry.intersectionRatio>0;heroPreviewSyncActivity();}},{root:$('#menu'),threshold:[0,.01]});view.observer.observe($('#heroPreviewStage'));}else{const measure=()=>{const r=$('#heroPreviewStage').getBoundingClientRect(),m=$('#menu').getBoundingClientRect();view.inView=r.bottom>Math.max(0,m.top)&&r.top<Math.min(innerHeight,m.bottom);heroPreviewSyncActivity();};$('#menu').addEventListener('scroll',measure,{passive:true});addEventListener('resize',measure);queueMicrotask(measure);}}
 heroPreviewSelect(heroPreviewAllowed(hero)?hero:'rempart');if(!view.supported)$('#heroPreviewPlaceholder').textContent='Aperçu 3D disponible sur la page en ligne. La sélection et le jeu restent utilisables ici.';
}
