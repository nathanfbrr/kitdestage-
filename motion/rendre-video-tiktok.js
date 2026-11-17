const {chromium}=require('playwright'); const {spawn}=require('child_process');
const FPS=+(process.argv[2]||30), OUT=process.argv[3]||'out.mp4', DUR=40;
(async()=>{
  const b=await chromium.launch();const p=await b.newPage({viewport:process.env.VERT?{width:1080,height:1920}:{width:1920,height:1080},deviceScaleFactor:1});
  await p.goto('file://'+process.env.HTML+(process.env.HASH||''));
  await p.evaluate(()=>document.fonts.ready);
  console.log('fonts', await p.evaluate(()=>[document.fonts.check('200 100px Sora'),document.fonts.check('400 20px Inter'),document.fonts.check('400 20px "JetBrains Mono"')]));
  await p.click('#play'); // pause
  await p.addStyleTag({content:`body{padding:0!important;margin:0;overflow:hidden;background:#07080C}.wrap>*:not(#stageWrap){display:none!important}.wrap{max-width:none!important}#stageWrap{position:fixed!important;inset:0;width:100vw!important;height:100vh!important;max-width:none!important;margin:0!important;border-radius:0!important;box-shadow:none!important}`});
  await p.waitForTimeout(500);
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-c:v','png','-i','-',
    '-i',process.env.AUDIO,'-map','0:v','-map','1:a',
    '-c:v','libx264','-preset','slow','-crf','17','-profile:v','high','-level','4.2','-maxrate','15M','-bufsize','30M','-pix_fmt','yuv420p','-r','30','-g','60',
    '-c:a','aac','-b:a','192k','-ar','44100','-movflags','+faststart','-t','40',OUT],{stdio:['pipe','inherit','inherit']});
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
