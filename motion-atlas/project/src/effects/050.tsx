import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 缩略图按线索归组 — 把人物、地点、档案归组梳理。独立图片预算：3–9。 */
export default function Effect050(props:AtlasAssets){return <EffectPlayer number={50} assets={props}/>;}
export const durationInFrames=180;
