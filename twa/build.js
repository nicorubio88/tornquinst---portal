// Genera el proyecto Android (Trusted Web Activity) a partir de twa-manifest.json con Bubblewrap.
const { TwaManifest, TwaGenerator, ConsoleLog } = require('@bubblewrap/core');
const cfg = require('./twa-manifest.json');
(async () => {
  const m = new TwaManifest(cfg);
  const err = m.validate();
  if (err) throw new Error(err);
  await new TwaGenerator().createTwaProject(__dirname + '/android', m, new ConsoleLog('twa'));
  console.log('Proyecto Android generado en twa/android');
})().catch(e => { console.error(e); process.exit(1); });
