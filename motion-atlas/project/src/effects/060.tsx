import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 章节索引跳转 — 目录锁定章节，进入对应画面。独立图片预算：1。 */
export default function Effect060(props:AtlasAssets){return <EffectPlayer number={60} assets={props}/>;}
export const durationInFrames=180;
