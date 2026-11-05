import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 放大镜取证 — 发现签名、眼神、门牌等微小证据。独立图片预算：1。 */
export default function Effect021(props:AtlasAssets){return <EffectPlayer number={21} assets={props}/>;}
export const durationInFrames=180;
