'use strict';
// Published 1.4 focuses on adventure. The complete local modes remain in
// local-party.js and immutable 1.3 archives, without entering this live bundle.
let localParty=[],partyKeys=new Set(),battle=null,partyLoading=false;
function selectedMode(){return'solo';}
function clearLocalParty(){localParty.length=0;partyKeys.clear();partyLoading=false;}
function updateLocalParty(){}
function resetLocalPartyAtLeader(){}
function applyPartyPact(){}
function hitPartyProjectile(){return false;}
function hurtPartyFromHazard(){}
function renderPartyStatus(){const panel=$('#partyStatus');if(panel){panel.hidden=true;panel.textContent='';}}
