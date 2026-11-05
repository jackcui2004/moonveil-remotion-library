import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 多层视差 — 人物决定、内心独白或人物亮相。独立图片预算：1–2。 */
export default function Effect004(props:AtlasAssets){return <EffectPlayer number={4} assets={props}/>;}
export const durationInFrames=210;
