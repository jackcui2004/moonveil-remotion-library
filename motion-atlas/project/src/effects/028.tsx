import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 双面档案翻转 — 人物照片背面露出身份档案。独立图片预算：1。 */
export default function Effect028(props:AtlasAssets){return <EffectPlayer number={28} assets={props}/>;}
export const durationInFrames=180;
