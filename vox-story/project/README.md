# 剧情驱动Vox：两分钟独立Remotion示例

这是用户于2026-11-07观看后认可的制作方向：先读小说、确定叙事落点，再设计镜头、底板和组件变体。该工程直接编写17个剧情阶段，不依次调用65个效果编号。

## 本地运行

需要Node.js及npm；在这个project目录中执行：

```sh
npm install --no-audit --no-fund
npm start
```

选择 `Cage-Opening-Director-V1`。渲染示例：

```sh
npm run render
```

输出120秒、1920×1080、30fps，含现有旁白片段和轻雨声纹理。系统Chrome或不同渲染环境的配置可按本库高速渲染说明适配；不承诺所有机器达到相同速度。

## 文件与设计

- `src/Root.tsx`：17个阶段及对应Scene分支；stages记录起止时间、剧情理由、引用素材。
- `src/captions.json`：仅本样片的句级字幕；来自本地ASR并修正名字和拼写，非人工逐词强制对齐。
- `src/waveform.json`：从本样片旁白提取的音量数据，用于语音备忘录画面。
- `public/images/`：6张已有素材；没有新增生图。
- `public/opening.m4a`：仅获授权展示的开头118.16秒旁白，组件延后55帧开始播放；不包含整篇有声书。
- `public/rain-texture.m4a`、`public/paper.svg`：程序生成的轻雨纹理与纸张纹理。

人物纸片通过SVG轮廓裁口和层级运动呈现，属于有限平移、分离、前后遮挡，不是自动骨骼绑定或新姿势生成。图板裁口、镜形边框、手写标注和底板都可以修改。不同小说要重新阅读并重写stages及对应镜头，不要只换图片继续使用本片时间表。

根目录策略：[`../story-driven-vox.md`](../story-driven-vox.md)。来源与许可范围：[`../NOTICE.md`](../NOTICE.md)。
