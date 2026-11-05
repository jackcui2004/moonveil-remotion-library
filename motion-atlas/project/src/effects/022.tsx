import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 前后景移焦 — 注意力从环境转到人物。独立图片预算：1–2。 */
export default function Effect022(props:AtlasAssets){return <EffectPlayer number={22} assets={props}/>;}
export const durationInFrames=180;
