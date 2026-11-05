import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 照片堆栈回溯 — 抽走最新照片，露出更早记忆。独立图片预算：3–5。 */
export default function Effect038(props:AtlasAssets){return <EffectPlayer number={38} assets={props}/>;}
export const durationInFrames=180;
