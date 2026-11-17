'use strict';
// Focus is owned only while one of these game dialogs is the active screen.
const modalFocusRuntime={initialized:false,active:null,entries:new Map(),inerted:new Map(),observer:null,redirecting:false};
const MANAGED_MODAL_IDS=['mapPanel','choicePanel','journeyChoice'];
function modalFocusVisible(element){
 if(!element?.isConnected||element.closest('[hidden]'))return false;
 const style=getComputedStyle(element);
 return style.display!=='none'&&style.visibility!=='hidden'&&element.getClientRects().length>0;
}
function modalFocusEnabled(element){
 return !!element&&modalFocusVisible(element)&&!element.closest('[inert]')&&!element.matches(':disabled,[aria-disabled="true"]');
}
function modalFocusItems(panel){
 return [...panel.querySelectorAll('button,a[href],input,select,textarea,summary,[tabindex],[contenteditable="true"]')].filter(element=>element.tabIndex>=0&&modalFocusEnabled(element));
}
function selectedFocusModal(){
 // Native dialogs own their top layer and focus themselves.
 if(document.querySelector('dialog[open]'))return null;
 const expected=typeof state==='string'?state:'';
 const ids=expected==='map'?['mapPanel']:expected==='choice'?['choicePanel','journeyChoice']:[];
 return ids.map(id=>document.getElementById(id)).filter(modalFocusVisible).sort((a,b)=>(Number(getComputedStyle(a).zIndex)||0)-(Number(getComputedStyle(b).zIndex)||0)).at(-1)||null;
}
function releaseModalInert(){
 for(const [element,wasInert]of modalFocusRuntime.inerted)if(element.inert!==wasInert)element.inert=wasInert;
 modalFocusRuntime.inerted.clear();
}
function applyModalInert(panel){
 for(const element of document.body.children){
  if(element===panel||element.contains(panel)||['SCRIPT','STYLE','LINK','DIALOG'].includes(element.tagName))continue;
  if(!modalFocusRuntime.inerted.has(element))modalFocusRuntime.inerted.set(element,element.inert);
  if(!element.inert)element.inert=true;
 }
}
function focusModalElement(panel,preferred=null){
 const runtime=modalFocusRuntime;if(runtime.redirecting)return;
 const target=preferred&&panel.contains(preferred)&&modalFocusEnabled(preferred)?preferred:modalFocusItems(panel)[0]||panel;
 if(target===panel&&!panel.hasAttribute('tabindex')){panel.tabIndex=-1;runtime.entries.get(panel).temporaryTabindex=true;}
 runtime.redirecting=true;
 try{target.focus();}finally{runtime.redirecting=false;}
}
function syncModalFocus(){
 const runtime=modalFocusRuntime;if(!runtime.initialized)return;
 const next=selectedFocusModal(),previous=runtime.active;
 if(next===previous){
  if(next){applyModalInert(next);const focused=document.activeElement;if(!next.contains(focused)||!modalFocusEnabled(focused))focusModalElement(next,runtime.entries.get(next)?.lastInside);}
  return;
 }
 const focused=document.activeElement,oldEntry=runtime.entries.get(previous),closed=previous&&!modalFocusVisible(previous);
 if(oldEntry&&previous.contains(focused))oldEntry.lastInside=focused;
 releaseModalInert();runtime.active=next;
 if(next){
  let entry=runtime.entries.get(next);
  if(!entry){
   const opener=focused&&focused!==document.body&&!previous?.contains(focused)?focused:oldEntry?.returnFocus;
   entry={returnFocus:opener||null,lastInside:null,temporaryTabindex:false};runtime.entries.set(next,entry);
  }
  applyModalInert(next);
  const returning=closed&&oldEntry?.returnFocus&&next.contains(oldEntry.returnFocus)?oldEntry.returnFocus:entry.lastInside;
  focusModalElement(next,returning);
 }else if(closed){
  // A completed world interaction may hide its trigger. Never invent a canvas
  // focus target or leave a hidden choice button receiving gameplay keys.
  const opener=oldEntry?.returnFocus,otherDialog=document.querySelector('dialog[open]');
  if(!otherDialog&&['playing','menu','paused'].includes(typeof state==='string'?state:'')&&modalFocusEnabled(opener)&&opener.tagName!=='CANVAS')opener.focus({preventScroll:true});
  else if(previous.contains(document.activeElement))document.activeElement.blur();
 }
 for(const [panel,entry]of runtime.entries)if(!modalFocusVisible(panel)){
  if(entry.temporaryTabindex)panel.removeAttribute('tabindex');runtime.entries.delete(panel);
 }
}
function initModalFocus(){
 const runtime=modalFocusRuntime;if(runtime.initialized)return;
 const panels=MANAGED_MODAL_IDS.map(id=>document.getElementById(id)).filter(Boolean);if(!panels.length)return;
 runtime.initialized=true;
 const style=document.createElement('style');style.textContent=MANAGED_MODAL_IDS.map(id=>'#'+id+':focus-visible,#'+id+' :focus-visible').join(',')+'{outline:2px solid #ffdf9f;outline-offset:3px}';document.head.append(style);
 // Register before the input-settings capture listener so Tab from checkboxes
 // can wrap here without becoming a gameplay key or leaving the dialog.
 addEventListener('keydown',event=>{
  if(event.key!=='Tab'||event.ctrlKey||event.metaKey||event.altKey)return;
  syncModalFocus();const panel=runtime.active;if(!panel)return;
  const items=modalFocusItems(panel),first=items[0],last=items.at(-1),focused=document.activeElement;
  if(!items.length||!panel.contains(focused)||event.shiftKey&&(focused===first||focused===panel)||!event.shiftKey&&(focused===last||focused===panel)){
   event.preventDefault();event.stopImmediatePropagation();focusModalElement(panel,event.shiftKey?last:first);
  }
 },true);
 document.addEventListener('focusin',event=>{
  if(runtime.redirecting)return;
  if(selectedFocusModal()!==runtime.active){syncModalFocus();return;}
  const panel=runtime.active;if(!panel)return;
  if(panel.contains(event.target))runtime.entries.get(panel).lastInside=event.target;
  else focusModalElement(panel,runtime.entries.get(panel).lastInside);
 },true);
 const observer=new MutationObserver(syncModalFocus);runtime.observer=observer;
 const observeScreen=screen=>observer.observe(screen,{attributes:true,attributeFilter:['hidden','open']});
 for(const screen of document.querySelectorAll('.screen,dialog'))observeScreen(screen);
 for(const panel of panels)observer.observe(panel,{attributes:true,attributeFilter:['hidden','disabled','inert','aria-disabled'],childList:true,subtree:true});
 // Controls/chronicle are created during startup. Observe only new body roots,
 // not per-frame game transforms or health-bar style updates.
 const roots=new MutationObserver(records=>{for(const record of records)for(const node of record.addedNodes)if(node.nodeType===1&&node.matches('.screen,dialog'))observeScreen(node);syncModalFocus();});
 roots.observe(document.body,{childList:true});runtime.rootsObserver=roots;syncModalFocus();
}
