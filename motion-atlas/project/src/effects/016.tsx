import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 圆孔开场 — 从封闭的局部打开到新场景。独立图片预算：2。 */
export default function Effect016(props:AtlasAssets){return <EffectPlayer number={16} assets={props}/>;}
export const durationInFrames=180;
