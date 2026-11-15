import React from 'react';
import {AbsoluteFill,Img,OffthreadVideo,Sequence,staticFile,useVideoConfig} from 'remotion';

export const paperEdge='polygon(0% 4%,8% 1%,29% 3%,52% 0%,78% 2%,100% 1%,98% 38%,100% 70%,98% 98%,76% 100%,49% 97%,22% 100%,1% 96%,3% 62%)';
const media=(src:string)=>src.startsWith('data:')||src.startsWith('http')?src:staticFile(src);
export const finite=(frame:number,start:number,frames:number)=>{const x=Math.max(0,Math.min(1,(frame-start)/Math.max(1,frames)));return x*x*(3-2*x)};

export const PaperBackground:React.FC<{color?:string;seed?:number}>=({color='#e3d4b7',seed=19})=><AbsoluteFill style={{background:`radial-gradient(ellipse at 46% 40%,${color},#c9b691)`}}><svg width="100%" height="100%" style={{opacity:.16,mixBlendMode:'multiply'}}><defs><filter id="fixed-paper-fibre"><feTurbulence type="fractalNoise" baseFrequency=".72" numOctaves="3" seed={seed}/><feColorMatrix type="saturate" values="0"/></filter></defs><rect width="100%" height="100%" filter="url(#fixed-paper-fibre)"/></svg></AbsoluteFill>;

export const CutoutLayer:React.FC<{src:string;sourceWidth:number;sourceHeight:number;x:number;y:number;height:number;maxWidth?:number;moveX?:number;opacity?:number}>=({src,sourceWidth,sourceHeight,x,y,height,maxWidth=1800,moveX=0,opacity=1})=>{
 const scale=Math.min(height/sourceHeight,maxWidth/sourceWidth),w=sourceWidth*scale,h=sourceHeight*scale;
 return <Img src={media(src)} style={{position:'absolute',left:x+moveX,top:y+height-h,width:w,height:h,maxWidth:'none',opacity,filter:'drop-shadow(1px 0 1px #f6ead3) drop-shadow(-1px 0 1px #f6ead3) drop-shadow(8px 12px 8px #14271e44)'}}/>;
};

export const PhotoCrop:React.FC<{src:string;sourceWidth:number;sourceHeight:number;x:number;y:number;width:number;height:number;roi?:[number,number,number,number]}>=({src,sourceWidth,sourceHeight,x,y,width,height,roi=[0,0,1,1]})=>{
 const [rx,ry,rw,rh]=roi,scale=Math.max(width/(rw*sourceWidth),height/(rh*sourceHeight));
 return <div style={{position:'absolute',left:x,top:y,width,height,clipPath:paperEdge,overflow:'hidden',filter:'drop-shadow(5px 9px 8px #16271d44)'}}><Img src={media(src)} style={{position:'absolute',maxWidth:'none',width:sourceWidth*scale,height:sourceHeight*scale,left:width/2-(rx+rw/2)*sourceWidth*scale,top:height/2-(ry+rh/2)*sourceHeight*scale}}/></div>;
};

export const Reveal:React.FC<{globalFrame:number;atFrame:number;fadeFrames?:number;children:React.ReactNode}>=({globalFrame,atFrame,fadeFrames=18,children})=>globalFrame<atFrame?null:<div style={{opacity:finite(globalFrame,atFrame,fadeFrames)}}>{children}</div>;

export const NativeVideoWindow:React.FC<{src:string;startGlobalFrame:number;offsetFrame:number;actualSeconds:number;x:number;y:number;width:number;height:number}>=({src,startGlobalFrame,offsetFrame,actualSeconds,x,y,width,height})=>{
 const {fps}=useVideoConfig();
 return <Sequence from={startGlobalFrame-offsetFrame} durationInFrames={Math.round(actualSeconds*fps)} layout="none"><div style={{position:'absolute',left:x,top:y,width,height,overflow:'hidden',clipPath:paperEdge}}><OffthreadVideo src={media(src)} muted style={{width:'100%',height:'100%',objectFit:'contain'}}/></div></Sequence>;
};
