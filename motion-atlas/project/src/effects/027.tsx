import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 三维卡片绕行 — 从不同深度依次访问三张照片。独立图片预算：3。 */
export default function Effect027(props:AtlasAssets){return <EffectPlayer number={27} assets={props}/>;}
export const durationInFrames=180;
