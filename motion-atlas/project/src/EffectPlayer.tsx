import React from 'react';
import {Sequence} from 'remotion';
import {CameraAtlas, AtlasAssets, AtlasAssetsContext} from './CameraAtlas';
import {CameraAtlasMore} from './CameraAtlasMore';
import {CameraAtlasThird} from './CameraAtlasThird';
export function EffectPlayer({number,assets={}}:{number:number;assets?:AtlasAssets}){
 const Component=number<=15?CameraAtlas:number<=45?CameraAtlasMore:CameraAtlasThird;
 const start=number<=15?(number-1)*210:number<=45?(number-16)*180:(number-46)*180;
 const duration=number<=15?3150:number<=45?5400:3600;
 return <AtlasAssetsContext.Provider value={assets}><Sequence from={-start} durationInFrames={duration}><Component/></Sequence></AtlasAssetsContext.Provider>;
}
