import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 匹配接镜 — 相同物件、门窗或姿态衔接两幕。独立图片预算：2。 */
export default function Effect005(props:AtlasAssets){return <EffectPlayer number={5} assets={props}/>;}
export const durationInFrames=210;
