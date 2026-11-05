import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 图钉落位连线 — 照片落桌后建立三方关联。独立图片预算：3。 */
export default function Effect041(props:AtlasAssets){return <EffectPlayer number={41} assets={props}/>;}
export const durationInFrames=180;
