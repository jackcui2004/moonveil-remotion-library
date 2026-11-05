const {bundle}=require('@remotion/bundler');const path=require('path');
bundle({entryPoint:path.resolve('src/index.ts'),outDir:path.resolve('.render/bundle'),publicDir:path.resolve('public')}).then(x=>console.log(x)).catch(e=>{console.error(e);process.exit(1)});
