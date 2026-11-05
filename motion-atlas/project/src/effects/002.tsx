import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 沿线追踪 — 追查线索，依次找到人物或地点。独立图片预算：3。 */
export default function Effect002(props:AtlasAssets){return <EffectPlayer number={2} assets={props}/>;}
export const durationInFrames=210;
