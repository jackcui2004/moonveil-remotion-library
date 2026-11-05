import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 手风琴折页 — 打开折叠照片，强调一张关键照片。独立图片预算：1。 */
export default function Effect018(props:AtlasAssets){return <EffectPlayer number={18} assets={props}/>;}
export const durationInFrames=180;
