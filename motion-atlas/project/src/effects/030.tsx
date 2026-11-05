import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 百叶窗交错 — 分条揭露新场景。独立图片预算：2。 */
export default function Effect030(props:AtlasAssets){return <EffectPlayer number={30} assets={props}/>;}
export const durationInFrames=180;
