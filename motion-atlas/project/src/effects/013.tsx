import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 时间回拨 — 交代三个关键时间点或倒叙。独立图片预算：3。 */
export default function Effect013(props:AtlasAssets){return <EffectPlayer number={13} assets={props}/>;}
export const durationInFrames=210;
