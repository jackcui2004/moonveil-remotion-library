import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 聚光灯寻证 — 在暗处找证据，最后落到目标。独立图片预算：1。 */
export default function Effect040(props:AtlasAssets){return <EffectPlayer number={40} assets={props}/>;}
export const durationInFrames=180;
