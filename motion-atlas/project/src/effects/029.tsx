import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 书页翻篇 — 翻过一页，推进到下一个情节。独立图片预算：2。 */
export default function Effect029(props:AtlasAssets){return <EffectPlayer number={29} assets={props}/>;}
export const durationInFrames=180;
