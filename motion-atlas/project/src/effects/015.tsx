import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 物件串场 — 信件或物件从一个场景来到另一个。独立图片预算：2。 */
export default function Effect015(props:AtlasAssets){return <EffectPlayer number={15} assets={props}/>;}
export const durationInFrames=210;
