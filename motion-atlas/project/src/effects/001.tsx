import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 局部揭全景 — 先讲信物或局部，再交代人物和现场。独立图片预算：1。 */
export default function Effect001(props:AtlasAssets){return <EffectPlayer number={1} assets={props}/>;}
export const durationInFrames=210;
