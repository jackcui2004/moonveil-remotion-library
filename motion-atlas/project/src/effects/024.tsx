import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 纵向升降镜头 — 从地面信物移向人物，或反向寻找原因。独立图片预算：1。 */
export default function Effect024(props:AtlasAssets){return <EffectPlayer number={24} assets={props}/>;}
export const durationInFrames=180;
