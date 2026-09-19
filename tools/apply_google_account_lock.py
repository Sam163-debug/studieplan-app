from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
p = root / 'cloud-sync.js'
s = p.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'{label} anchor not found')
    s = s.replace(old, new, 1)

replace_once(
"const GOOGLE_PRESENTATION_VERSION=2;\n",
"const GOOGLE_PRESENTATION_VERSION=2;\nconst GOOGLE_SYNC_ACCOUNT_KEY='studieplan-google-sync-account';\n",
"constants"
)

replace_once(
"  lastMessage:'', conflictCount:0, calendarVerifiedId:'', reconnectTried:false\n",
"  lastMessage:'', conflictCount:0, calendarVerifiedId:'', reconnectTried:false, oauthPromise:null\n",
"runtime"
)

auth_old = """function initTokenClient(){if(cloudRuntime.tokenClient)return;const scope=window.STUDIEPLAN_VIEW_MODE?'https://www.googleapis.com/auth/drive.appdata':GOOGLE_SCOPES;cloudRuntime.tokenClient=google.accounts.oauth2.initTokenClient({client_id:GOOGLE_CLIENT_ID,scope,include_granted_scopes:true,callback:()=>{}})}
async function requestAccessToken(interactive=true,promptOverride=null){
  await loadGoogleIdentity();initTokenClient();
  const c=ensureCloudState();
  const ask=(prompt)=>new Promise((resolve,reject)=>{cloudRuntime.tokenClient.callback=resp=>{if(resp.error)return reject(Object.assign(new Error(resp.error_description||resp.error),{oauthError:resp.error}));cloudRuntime.token=resp.access_token;cloudRuntime.tokenExpiry=Date.now()+(Number(resp.expires_in)||3600)*1000-60000;c.authorizedOnce=true;cloudRuntime.suppressDirty=true;try{baseSave()}finally{cloudRuntime.suppressDirty=false}updateCloudUI();resolve(resp)};cloudRuntime.tokenClient.error_callback=err=>reject(Object.assign(new Error(err?.message||err?.type||'Google-inloggningen avbröts.'),{oauthError:err?.type||'popup_error'}));cloudRuntime.tokenClient.requestAccessToken({prompt})});
  const firstPrompt=promptOverride!==null?promptOverride:(interactive?(c.authorizedOnce?'':'consent'):'none');
  try{return await ask(firstPrompt)}catch(err){if(interactive&&firstPrompt!=='consent')return ask('consent');throw err}
}
async function ensureToken(interactive=false){if(cloudRuntime.token&&Date.now()<cloudRuntime.tokenExpiry)return cloudRuntime.token;if(!navigator.onLine)throw new Error('Ingen internetanslutning. Ändringarna ligger kvar lokalt.');try{await requestAccessToken(interactive)}catch(err){if(!interactive)throw Object.assign(new Error('Google-sessionen behöver återanslutas. Klicka Synka nu eller Återanslut Google.'),{oauthError:err.oauthError||'interaction_required'});throw err}return cloudRuntime.token}
"""
auth_new = """function getSyncAccountEmail(){try{return (localStorage.getItem(GOOGLE_SYNC_ACCOUNT_KEY)||'').trim()}catch{return ''}}
function setSyncAccountEmail(email){try{email=String(email||'').trim();if(email)localStorage.setItem(GOOGLE_SYNC_ACCOUNT_KEY,email);else localStorage.removeItem(GOOGLE_SYNC_ACCOUNT_KEY)}catch{}renderSyncAccountControl()}
function tokenIsValid(){return !!cloudRuntime.token&&Date.now()<cloudRuntime.tokenExpiry}
function renderSyncAccountControl(){
  const detail=$('cloudDetail');if(!detail)return;
  let row=$('cloudAccountRow');
  if(!row){row=document.createElement('div');row.id='cloudAccountRow';row.style.cssText='margin-top:7px;font-size:12px;color:var(--muted);display:flex;gap:7px;align-items:center;flex-wrap:wrap';detail.insertAdjacentElement('afterend',row)}
  const email=getSyncAccountEmail();
  row.replaceChildren();
  const text=document.createElement('span');text.textContent=email?'Synkkonto: '+email:'Synkkonto: väljs vid nästa anslutning';row.appendChild(text);
  if(email){const b=document.createElement('button');b.type='button';b.id='changeGoogleAccountBtn';b.textContent='Byt konto';b.style.cssText='padding:3px 7px;font-size:11px';b.onclick=()=>connectGoogle(true);row.appendChild(b)}
}
function initTokenClient(){if(cloudRuntime.tokenClient)return;const driveScope=window.STUDIEPLAN_VIEW_MODE?'https://www.googleapis.com/auth/drive.appdata':GOOGLE_SCOPES;const scope=driveScope+' openid email';cloudRuntime.tokenClient=google.accounts.oauth2.initTokenClient({client_id:GOOGLE_CLIENT_ID,scope,include_granted_scopes:true,callback:()=>{}})}
async function fetchGoogleIdentity(accessToken){
  const res=await fetch('https://openidconnect.googleapis.com/v1/userinfo',{headers:{Authorization:'Bearer '+accessToken}});
  if(!res.ok)throw new Error('Kunde inte verifiera vilket Google-konto som anslöts.');
  const user=await res.json();if(!user.email)throw new Error('Google returnerade ingen e-postadress för det anslutna kontot.');return user;
}
async function requestAccessToken(interactive=true,promptOverride=null,changeAccount=false){
  if(!interactive)throw Object.assign(new Error('Google-sessionen behöver återanslutas med ett klick.'),{oauthError:'interaction_required'});
  if(cloudRuntime.oauthPromise)return cloudRuntime.oauthPromise;
  cloudRuntime.oauthPromise=(async()=>{
    await loadGoogleIdentity();initTokenClient();
    const c=ensureCloudState(),fixedEmail=getSyncAccountEmail();
    const prompt=promptOverride!==null?promptOverride:(fixedEmail?'':'select_account');
    return new Promise((resolve,reject)=>{
      cloudRuntime.tokenClient.callback=async resp=>{
        if(resp.error)return reject(Object.assign(new Error(resp.error_description||resp.error),{oauthError:resp.error}));
        try{
          const nextToken=resp.access_token,user=await fetchGoogleIdentity(nextToken),email=String(user.email||'').trim();
          if(fixedEmail&&!changeAccount&&email.toLowerCase()!==fixedEmail.toLowerCase())throw Object.assign(new Error('Fel Google-konto valdes. Synken är låst till '+fixedEmail+'. Klicka ”Byt konto” om du vill ändra synkkonto.'),{oauthError:'account_mismatch'});
          cloudRuntime.token=nextToken;cloudRuntime.tokenExpiry=Date.now()+(Number(resp.expires_in)||3600)*1000-60000;
          if(!fixedEmail||changeAccount)setSyncAccountEmail(email);
          c.authorizedOnce=true;cloudRuntime.suppressDirty=true;try{baseSave()}finally{cloudRuntime.suppressDirty=false}
          updateCloudUI();renderSyncAccountControl();resolve(resp);
        }catch(err){cloudRuntime.token='';cloudRuntime.tokenExpiry=0;updateCloudUI();reject(err)}
      };
      cloudRuntime.tokenClient.error_callback=err=>reject(Object.assign(new Error(err?.message||err?.type||'Google-inloggningen avbröts.'),{oauthError:err?.type||'popup_error'}));
      const req={prompt};if(fixedEmail&&!changeAccount)req.login_hint=fixedEmail;
      cloudRuntime.tokenClient.requestAccessToken(req);
    });
  })();
  try{return await cloudRuntime.oauthPromise}finally{cloudRuntime.oauthPromise=null}
}
async function ensureToken(interactive=false){if(tokenIsValid())return cloudRuntime.token;if(!navigator.onLine)throw new Error('Ingen internetanslutning. Ändringarna ligger kvar lokalt.');if(!interactive)throw Object.assign(new Error('Google-sessionen behöver återanslutas. Klicka Återanslut Google eller Synka nu.'),{oauthError:'interaction_required'});await requestAccessToken(true);return cloudRuntime.token}
"""
replace_once(auth_old, auth_new, "oauth functions")

connect_old = "async function connectGoogle(){try{await requestAccessToken(true);updateCloudUI();"
connect_new = "async function connectGoogle(changeAccount=false){try{await requestAccessToken(true,changeAccount?'select_account':null,changeAccount);updateCloudUI();"
replace_once(connect_old, connect_new, "connectGoogle")

handlers_old = """$('googleConnectBtn').onclick=()=>{if(cloudRuntime.token&&Date.now()<cloudRuntime.tokenExpiry)disconnectSession();else connectGoogle()};if($('mobileGoogleBtn'))$('mobileGoogleBtn').onclick=()=>{if(cloudRuntime.token&&Date.now()<cloudRuntime.tokenExpiry)disconnectSession();else connectGoogle()};if($('mobileRefreshBtn'))$('mobileRefreshBtn').onclick=()=>syncViewFromDrive(true);
$('syncNowBtn').onclick=()=>syncNow(true);$('driveBackupBtn').onclick=()=>writeDriveBackup(true).catch(err=>alert('Drive-backup misslyckades:\\n'+err.message));$('driveRestoreBtn').onclick=()=>restoreFromDrive().catch(err=>alert('Återställning från Drive misslyckades:\\n'+err.message));
window.addEventListener('online',()=>{updateCloudUI();if(cloudRuntime.token)scheduleCloudSync(500);else tryAutoReconnect()});window.addEventListener('offline',()=>updateCloudUI());
async function tryAutoReconnect(){const c=ensureCloudState();if(cloudRuntime.reconnectTried||!c.authorizedOnce||!navigator.onLine||cloudRuntime.token)return;cloudRuntime.reconnectTried=true;try{await requestAccessToken(false,'none');toast('Google återansluten automatiskt.');if(window.STUDIEPLAN_VIEW_MODE)await syncViewFromDrive(false);else await syncNow(false)}catch(err){console.info('Automatisk Google-återanslutning kräver användarklick:',err?.oauthError||err?.message);updateCloudUI()}}
"""
handlers_new = """$('googleConnectBtn').onclick=()=>{if(tokenIsValid())disconnectSession();else connectGoogle()};if($('mobileGoogleBtn'))$('mobileGoogleBtn').onclick=()=>{if(tokenIsValid())disconnectSession();else connectGoogle()};if($('mobileRefreshBtn'))$('mobileRefreshBtn').onclick=async()=>{if(!tokenIsValid())return connectGoogle();return syncViewFromDrive(true)};
$('syncNowBtn').onclick=async()=>{if(!tokenIsValid())return connectGoogle();return window.STUDIEPLAN_VIEW_MODE?syncViewFromDrive(true):syncNow(true)};$('driveBackupBtn').onclick=async()=>{if(!tokenIsValid())return connectGoogle();return writeDriveBackup(true).catch(err=>alert('Drive-backup misslyckades:\\n'+err.message))};$('driveRestoreBtn').onclick=async()=>{if(!tokenIsValid())return connectGoogle();return restoreFromDrive().catch(err=>alert('Återställning från Drive misslyckades:\\n'+err.message))};
window.addEventListener('online',()=>{updateCloudUI();if(tokenIsValid())scheduleCloudSync(500)});window.addEventListener('offline',()=>updateCloudUI());
function tryAutoReconnect(){const c=ensureCloudState();if(!tokenIsValid()&&c.authorizedOnce){setCloudStatus('',window.STUDIEPLAN_VIEW_MODE?'View mode · Återanslut Google':'Återanslut Google','Automatisk inloggnings-popup är avstängd. Klicka Återanslut Google eller Synka nu.');updateCloudUI()}return false}
"""
replace_once(handlers_old, handlers_new, "handlers")

replace_once(
"updateCloudUI();setTimeout(tryAutoReconnect,350);",
"updateCloudUI();renderSyncAccountControl();",
"startup reconnect"
)

p.write_text(s, encoding='utf-8')
print('Fixed Google sync account and click-only OAuth applied')
