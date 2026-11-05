import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 连续深入 — 从大场景进入档案，再发现隐藏细节。独立图片预算：2。 */
export default function Effect010(props:AtlasAssets){return <EffectPlayer number={10} assets={props}/>;}
export const durationInFrames=210;
