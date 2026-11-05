import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 双线并行 — 两个人在同一时间做不同的事。独立图片预算：2。 */
export default function Effect012(props:AtlasAssets){return <EffectPlayer number={12} assets={props}/>;}
export const durationInFrames=210;
