import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 放射式人物板 — 交代中心人物与周围人的关系。独立图片预算：4–5。 */
export default function Effect042(props:AtlasAssets){return <EffectPlayer number={42} assets={props}/>;}
export const durationInFrames=180;
