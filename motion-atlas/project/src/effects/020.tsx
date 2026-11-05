import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 接触印样选中 — 从许多线索里选中一条。独立图片预算：3–9。 */
export default function Effect020(props:AtlasAssets){return <EffectPlayer number={20} assets={props}/>;}
export const durationInFrames=180;
