'use strict';
(() => {
 const lang=document.documentElement.lang, fr=lang==='fr', config=window.NIORO_CONFIG||{};
 const toggle=document.querySelector('.menu-toggle'),nav=document.getElementById('main-nav');
 const close=()=>{nav?.classList.remove('is-open');toggle?.setAttribute('aria-expanded','false');};
 toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('is-open',open);});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&toggle?.getAttribute('aria-expanded')==='true'){close();toggle.focus();}});
 document.addEventListener('click',e=>{if(!e.target.closest('.header'))close();});
 matchMedia('(min-width:821px)').addEventListener('change',e=>{if(e.matches)close();});
 document.querySelector('[data-language]')?.addEventListener('click',e=>{const query=new URLSearchParams(location.search);const cat=query.get('category');if(cat&&/^[0-9]$/.test(cat))e.currentTarget.href+='?category='+cat;});
 const network=document.querySelector('[data-network]');
 if(network){
  const choose=id=>{
   network.querySelectorAll('[data-country-panel]').forEach(panel=>{panel.hidden=panel.dataset.countryPanel!==id;});
   network.querySelectorAll('[data-map-country]').forEach(control=>{const active=control.dataset.mapCountry===id;control.setAttribute('aria-current',active?'true':'false');});
   network.querySelectorAll('[data-country-shape]').forEach(shape=>shape.classList.toggle('selected',shape.dataset.countryShape===id));
  };
  network.querySelectorAll('[data-map-country]').forEach(control=>control.addEventListener('click',e=>{e.preventDefault();choose(control.dataset.mapCountry);}));
  const initial=location.hash.replace('#country-','');
  choose(['us','sn','fr','it','tr','cn'].includes(initial)?initial:'us');
 }
 const form=document.querySelector('[data-inquiry]');if(!form)return;
 const category=new URLSearchParams(location.search).get('category');
 if(category&&/^[0-9]$/.test(category))form.elements.category.value=category;
 const result=form.querySelector('.form-result'),submit=form.querySelector('[type=submit]'),note=document.getElementById('form-note');
 const endpoint=config.formEndpoint||'';const direct=endpoint.startsWith('https://');
 if(direct){note.textContent=note.dataset.directNote;submit.textContent=submit.dataset.send;}
 let downloadURL;
 const add=(tag,text,parent=result)=>{const e=document.createElement(tag);e.textContent=text;parent.append(e);return e;};
 const show=()=>{result.replaceChildren();result.hidden=false;result.focus();};
 const draft=(subject,body)=>{
  show();add('h3',fr?'Votre brouillon est prêt. Rien n’a été envoyé.':'Your draft is ready. Nothing has been sent.');
  add('p',fr?'Ouvrez votre messagerie pour vérifier et envoyer la demande, ou téléchargez le texte et envoyez-le à '+config.email+'.':'Open your email app to review and send, or download the text and email it to '+config.email+'.');
  const actions=add('div','');actions.className='actions';
  const mail=add('a',fr?'Ouvrir la messagerie':'Open email app',actions);mail.className='button';mail.href='mailto:'+config.email+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
  if(downloadURL)URL.revokeObjectURL(downloadURL);
  downloadURL=URL.createObjectURL(new Blob(['To: '+config.email+'\nSubject: '+subject+'\n\n'+body],{type:'text/plain;charset=utf-8'}));
  const download=add('a',fr?'Télécharger la demande':'Download inquiry',actions);download.href=downloadURL;download.download='nioro-inquiry.txt';download.className='text-link';
  const details=add('details','');add('summary',fr?'Relire le message':'Review message',details);add('pre',body,details);
 };
 form.addEventListener('submit',async e=>{
  e.preventDefault();
  if(!form.reportValidity()||form.elements.fax.value)return;
  for(const key of ['name','organization','country','message']){
   const input=form.elements[key];input.setCustomValidity(input.value.trim().length<(key==='message'?20:2)?(fr?'Veuillez renseigner ce champ.':'Please complete this field.'): '');
   if(!input.reportValidity())return;
  }
  const data=Object.fromEntries(new FormData(form));delete data.fax;
  data.category=form.elements.category.selectedOptions[0].textContent;data.language=lang;data.source=location.pathname;
  const subject='Nioro Resources — '+data.category;
  const labels=fr?['Nom','E-mail','Organisation','Pays / marché','Site web','Type de demande','Besoin']:['Name','Email','Organization','Country / market','Website','Inquiry type','Requirements'];
  const body=['name','email','organization','country','website','category','message'].map((k,i)=>labels[i]+': '+(data[k]||'—')).join('\n\n');
  if(!direct){draft(subject,body);return;}
  submit.disabled=true;submit.textContent=fr?'Envoi en cours…':'Sending…';
  try{
   const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({...data,subject}),signal:AbortSignal.timeout(15000)});
   if(!response.ok)throw new Error('Submission rejected');
   show();add('h3',fr?'Demande acceptée.':'Inquiry accepted.');add('p',fr?'Le service de formulaire a accepté votre demande. Cela ne confirme pas la lecture par notre équipe.':'The form service accepted your inquiry. This does not confirm it has been read by our team.');form.reset();
  }catch{
   draft(subject,body);result.querySelector('h3').textContent=fr?'L’envoi n’a pas pu être confirmé.':'Submission could not be confirmed.';
   result.querySelector('p').textContent=fr?'Vérifiez une éventuelle confirmation avant de réessayer. Vous pouvez aussi envoyer ce brouillon par e-mail.':'Check for a confirmation before retrying. You can also send this draft by email.';
  }finally{submit.disabled=false;submit.textContent=submit.dataset.send;}
 });
 form.addEventListener('input',e=>{if(e.target.setCustomValidity)e.target.setCustomValidity('');});
 form.addEventListener('input',()=>{if(!result.hidden){result.hidden=true;if(downloadURL){URL.revokeObjectURL(downloadURL);downloadURL=undefined;}}});
})();
