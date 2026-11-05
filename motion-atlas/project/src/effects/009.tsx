import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 同画面对位切换 — 过去与现在的身份、环境形成对照。独立图片预算：2。 */
export default function Effect009(props:AtlasAssets){return <EffectPlayer number={9} assets={props}/>;}
export const durationInFrames=210;
