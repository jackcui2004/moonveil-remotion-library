import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 撕纸揭幕 — 旧记忆被撕开，露出下一场。独立图片预算：2。 */
export default function Effect017(props:AtlasAssets){return <EffectPlayer number={17} assets={props}/>;}
export const durationInFrames=180;
