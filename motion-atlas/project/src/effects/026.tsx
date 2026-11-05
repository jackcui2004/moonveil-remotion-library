import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 倾斜失衡后归正 — 失衡、惊慌后重新镇定。独立图片预算：1。 */
export default function Effect026(props:AtlasAssets){return <EffectPlayer number={26} assets={props}/>;}
export const durationInFrames=180;
