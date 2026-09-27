# 本轮验证记录

此文件记录第一轮49页版本。当前新版为14页独立版 / 56页完整版，导航与媒体验收见同目录 `slides-v2-check.json`，计划与交接见根目录 `handoff.md`。

日期：2026-09-27。操作系统 Windows；Python 3.12.7；Node v22.14.0。演示全部使用离线夹具或已存在的上游轨迹，未调用模型 API。

## 原仓库构建及测试

fast-jev-compaction，运行 `npm ci --ignore-scripts --no-audit --no-fund`、`npm run build`、`npm test`：

```text
added 50 packages in 8s
> fast-jev-compaction@0.2.0 build
> tsc
Test Files  2 passed (2)
     Tests  29 passed (29)
```

JEVfire，运行 `python -m pytest tests/test_parallel_decoding.py -q`。第一次缺少 pytest-asyncio，结果为 15 passed / 7 skipped；补齐插件后：

```text
......................                                                   [100%]
22 passed in 1.44s
```

awesome-jev，运行 `python -m unittest discover -s scripts/tests -q`。第一次本地假服务器经代理出现 HTTP 503，26 项中 4 项失败。终端设置 `NO_PROXY=127.0.0.1,localhost` 后：

```text
Ran 26 tests in 1.057s
OK
```

上游实现及测试未为通过测试而改写。总计 29 + 22 + 26 = 77 项测试通过，不含真实模型集成测试、Android 测试或 NanoJev 训练测试。

## 本项目案例

运行 `python experiment/jev_practice/run_offline.py`：

```text
messagesBefore=9, messagesAfter=7
charsBefore=8144, charsAfter=316
calls=4, kept=1, resultsDropped=1, callsDropped=1, pinned=1
reduction_ratio=0.9611984282907662
PASS: compaction, JEVfire decoding/abstention, Jarvis question construction, NanoJev recording audit
```

脚本断言覆盖：结果与调用不孤立、用户约束不变、错误证据保留、缺失回答抛错；JEVfire 缺失 logprob 抛错、高分通过 / 低分拒答；Jarvis 最近 10 条截断与恰好 3 候选。

## 浏览器验证

`verify_browser.py` 启动临时本地 HTTP 服务，以本机 Chrome 逐页导航并截图。检查 demo 裁剪前后、0.70 拒答、0.30 接受、7 题展示、iframe 回放；访问 NanoJev 迷宫第 225 帧及贪吃蛇第 50 帧。实际快照见 `browser-check.json`。

```text
slides: 49
console_errors: []
http_errors: []
overflow: []
```

已查看全页 contact sheet、新增 7 页预览及交互页面截图。新增页未出现裁切或文字溢出。所有原有页面均保留；原 deck 的技术结论不在本轮重新验证范围内。
