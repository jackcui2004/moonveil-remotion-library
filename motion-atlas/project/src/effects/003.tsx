import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 前景遮挡穿过 — 穿门、越过遮挡进入下一场。独立图片预算：2–3。 */
export default function Effect003(props:AtlasAssets){return <EffectPlayer number={3} assets={props}/>;}
export const durationInFrames=210;
