# Moonveil 65项运镜与分镜效果工程

## 本地预览

```sh
npm install --no-audit --no-fund
npm start
```

Remotion Studio可选 `Effect-001` 至 `Effect-065`，或 `Atlas-All-65`。

- 1920×1080，30fps。
- 单项各6/7秒；完整合集405秒。
- 入口文件在src/effects，完整实现共享于CameraAtlas*.tsx。
- photos/people可传参，其他剧情数据按planning.md配置。

## 批量渲染

需要Python3、ffmpeg/ffprobe、Node、Chrome。macOS默认原生Chrome路径写在scripts/render_catalog.py，可按系统修改。

```sh
npm run render:all
```

6个独立worker，各1路并发；一次bundle后复用。中间画面静音，独立MP4按原时间窗合音频，最后从有序原始视频和完整音轨总装合集。不会重跑已通过帧数核验的独立片段。输出在工程上一级videos/posters目录。
