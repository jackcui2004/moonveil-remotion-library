import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 对照分界线扫动 — 比较同一地点、人物前后状态。独立图片预算：2。 */
export default function Effect054(props:AtlasAssets){return <EffectPlayer number={54} assets={props}/>;}
export const durationInFrames=180;
