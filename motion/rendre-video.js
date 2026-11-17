const {chromium}=require('playwright'); const {spawn}=require('child_process');
const FPS=+(process.argv[2]||30), OUT=process.argv[3]||'out.mp4', DUR=40;
(async()=>{
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
  await p.goto('file:///home/user/Nathan/motion/kit-premier-stage-40s.html');
  await p.evaluate(()=>document.fonts.ready);
  console.log('fonts', await p.evaluate(()=>[document.fonts.check('200 100px Sora'),document.fonts.check('400 20px Inter'),document.fonts.check('400 20px "JetBrains Mono"')]));
  await p.click('#play'); // pause
  await p.addStyleTag({content:`body{padding:0!important;margin:0;overflow:hidden;background:#07080C}.wrap>*:not(#stageWrap){display:none!important}.wrap{max-width:none!important}#stageWrap{position:fixed!important;inset:0;width:1920px!important;height:1080px!important;border-radius:0!important;box-shadow:none!important}`});
  await p.waitForTimeout(500);
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-c:v','png','-i','-',
    '-i','/home/user/Nathan/motion/voix-off-musique.wav','-map','0:v','-map','1:a',
    '-c:v','libx264','-preset','slow','-crf','16','-pix_fmt','yuv420p','-tune','film',
    '-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart','-t','40',OUT],{stdio:['pipe','inherit','inherit']});
  const total=FPS*DUR;
  for(let i=0;i<total;i++){
    const ms=Math.round(i*1000/FPS);
    await p.evaluate(v=>{const s=document.getElementById('scrub');s.value=v;s.dispatchEvent(new Event('input'))},ms);
    const buf=await p.screenshot({type:'png'});
    if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
    if(i%120===0) console.log('frame',i,'/',total);
  }
  ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('done');
})();
