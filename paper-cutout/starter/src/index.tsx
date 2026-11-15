import React from 'react';
import {AbsoluteFill,Composition,registerRoot,useCurrentFrame} from 'remotion';
import {PaperBackground,CutoutLayer,Reveal,finite} from './PaperStage';

// Program-drawn abstract silhouettes only. Replace these with reviewed photographic alpha assets.
const figure=(coat:string)=>'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="360" height="900" viewBox="0 0 360 900"><path d="M146 145L120 126L114 88L123 45L152 20L199 23L230 51L238 94L218 128L197 146L202 177L254 207L280 357L255 422L239 374L218 278L222 493L250 842L205 868L177 637L163 876L115 878L130 505L119 277L98 390L74 418L68 350L94 207L143 178Z" fill="${coat}"/><path d="M146 177L179 257L202 177M179 257V500M131 506L222 493" stroke="#c9b38a" stroke-width="5" fill="none"/></svg>`);
const a=figure('#405d50'),b=figure('#302e2b');
export const Demo=()=>{
 const f=useCurrentFrame(),arrival=finite(f,0,24);
 return <AbsoluteFill style={{overflow:'hidden',color:'#20392f',fontFamily:'Georgia,serif'}}><PaperBackground/><div style={{position:'absolute',top:50,left:90,fontSize:23,letterSpacing:3}}>PAPER CUTOUT · LAYER DEMO</div><CutoutLayer src={a} sourceWidth={360} sourceHeight={900} x={290} y={110} height={760} moveX={(1-arrival)*-45}/><Reveal globalFrame={f} atFrame={90}><CutoutLayer src={b} sourceWidth={360} sourceHeight={900} x={870} y={90} height={780}/></Reveal><svg width="1920" height="1080" style={{position:'absolute'}}><path d="M680 110L820 85L850 920L700 945Z" fill="#654a3b"/><path d="M160 900L1640 875" stroke="#8e7855" strokeWidth="3"/></svg><Reveal globalFrame={f} atFrame={150}><div style={{position:'absolute',left:1280,top:300,width:480,fontSize:42,lineHeight:1.4}}>Reveal on the source phrase.<br/><span style={{fontSize:25}}>Then hold for reading.</span></div></Reveal><div style={{position:'absolute',left:90,bottom:45,fontSize:22}}>Abstract code-only demonstration · no story media or narration included</div></AbsoluteFill>;
};
const Root=()=> <Composition id="PaperCutout-Demo" component={Demo} width={1920} height={1080} fps={30} durationInFrames={360}/>;
registerRoot(Root);
