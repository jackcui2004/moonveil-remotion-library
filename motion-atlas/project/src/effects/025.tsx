import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 斜向跨页 — 从一个空间跨页访问另一处。独立图片预算：2。 */
export default function Effect025(props:AtlasAssets){return <EffectPlayer number={25} assets={props}/>;}
export const durationInFrames=180;
