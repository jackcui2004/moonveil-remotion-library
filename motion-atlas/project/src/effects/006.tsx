import React from 'react';
import {EffectPlayer} from '../EffectPlayer';
import {AtlasAssets} from '../CameraAtlas';
/** 快速移镜后停稳 — 电话、敲门、突发消息打断平静。独立图片预算：2。 */
export default function Effect006(props:AtlasAssets){return <EffectPlayer number={6} assets={props}/>;}
export const durationInFrames=210;
