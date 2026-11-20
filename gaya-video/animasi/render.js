const { chromium } = require('playwright'); const { spawn } = require('child_process'); const fs = require('fs');
(async () => {
  const preview = process.argv.slice(2).map(Number);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await p.goto('file://' + __dirname + '/anim.html'); await p.waitForFunction('window.ready === true');
  const total = await p.evaluate('window.TOTAL'); console.log('total', total);
  const grab = async T => Buffer.from((await p.evaluate(T => { window.render(T); return document.getElementById('c').toDataURL('image/jpeg', 0.93); }, T)).split(',')[1], 'base64');
  if (preview.length) { for (const T of preview) fs.writeFileSync(`pv_${T}.jpg`, await grab(T)); await b.close(); return; }
  const ff = spawn('ffmpeg', ['-loglevel', 'error', '-y', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'mjpeg', '-i', '-', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-shortest',
    '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', 'reel-bentuk-bukan-berat.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  const N = Math.round(total * 30);
  for (let n = 0; n < N; n++) { const buf = await grab(n / 30); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close(); console.log('frames', N);
})();
