import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 手机消息进入现场 — 手机收到现场照片，继而进入现场。独立图片预算：1。 */
export default function Effect064(props:AtlasAssets){return <EffectPlayer number={64} assets={props}/>;}
export const durationInFrames=180;
