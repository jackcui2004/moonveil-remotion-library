# 人物剪纸组件起步工程

这是12秒、1080p30的抽象图层示意，静音，不是生产长片，也不含演员或小说素材。它演示有限位移、遮挡、按事件出现和停稳。

```sh
npm install --no-audit --no-fund --prefer-offline --maxsockets=4
npm start
```

选择PaperCutout-Demo。将代码轮廓替换为自己的真实透明PNG，并将sourceWidth/sourceHeight设为裁切后的实际像素尺寸。保留父素材、服装、时空和接触组记录。PhotoCrop按源宽高等比填充ROI，仍需要检查脸、手和物件是否被切掉。

Reveal使用已经对齐到原文的全局帧号；章节工程需自行传入globalFrame。NativeVideoWindow使用global起点减章节offset，并按真实秒数播放一次；输入视频静音，整集原声独立放入Audio。起步工程没有附带旁白，不能将它宣称为有声成片。

当前组件仅提供构图能力。下一篇自行编写语义分镜、人物、素材和时间表；不能自动从小说推断镜头。精确截图复用必须审计新项目的全部时间依赖，不能继承生产案例的截帧阈值。
