const demo=document.getElementById('layer-demo');
document.querySelectorAll('.demo-buttons [data-state]').forEach(button=>button.addEventListener('click',()=>{
  demo.dataset.state=button.dataset.state;
  document.querySelectorAll('.demo-buttons button').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
}));
document.getElementById('copy-brief').addEventListener('click',async()=>{
 const status=document.getElementById('copy-status');
 try{const r=await fetch('director-brief.txt');if(!r.ok)throw Error('download');await navigator.clipboard.writeText(await r.text());status.textContent='已复制，可连同本篇小说和新参考图交接。';}
 catch{status.textContent='请使用旁边的下载执行入口。';}
});
