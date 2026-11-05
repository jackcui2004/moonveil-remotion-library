import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 钟面倒计时 — 危急时刻强调剩余时间。独立图片预算：0–1。 */
export default function Effect052(props:AtlasAssets){return <EffectPlayer number={52} assets={props}/>;}
export const durationInFrames=180;
