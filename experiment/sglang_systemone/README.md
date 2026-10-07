# SGLang System One 部署记录

更新：2026-10-05。教学与接口验证用途；不是 Jev 权重，也不是模型校准或性能结论。

## 当前实例

- SSH：`root@120.209.70.195:30113`。密码不保存在本项目。
- GPU：NVIDIA A100-SXM4-80GB × 1；数据盘 `/root/gpufree-data` 约 147GB。
- 模型：官方 `Qwen/Qwen3.8-27B` BF16，33 个文件，合计 55,586,114,768 字节。下载器逐文件校验 SHA-256。
- SGLang：0.5.21；PyTorch：2.13.0；Transformers：5.12.1；TypeSafe SDK：0.7.2。
- 模型目录：`/root/gpufree-data/systemone/models/Qwen3.8-27B`。
- Python 环境：`/root/systemone-venv`。
- 启动脚本：`/root/gpufree-data/systemone/scripts/start_systemone.sh`。
- 测试脚本：`/root/gpufree-data/systemone/scripts/smoke_test.py`。
- 服务日志：`/root/gpufree-data/systemone/logs/server.log`。
- 服务：`127.0.0.1:30000`，模型名 `Qwen3.8-27B-SystemOne`；`context-length=8192`，`max-running-requests=4`，`mem-fraction-static=0.85`，`mamba-full-memory-ratio=0.6`。
- Supervisor 配置：`/.gpufree/supervisord/conf.d/systemone.conf`，供实例下一次启动时自动运行；尚未通过重启验证。

## 下载来源测速

在服务器上对同一模型分片读取前 16MiB：ModelScope 约 19.5 MB/s；hf-mirror 约 11.4 MB/s；Hugging Face 主站不可达。选择 ModelScope 下载。测速只是当时的小样本，不能代表持续吞吐。ModelScope 文件列表报告模型总量约 55.59GB；最终下载日志显示 `COMPLETE`。

## 验证

`GET /ready` 返回 200；`GET /v1/models` 返回模型名。`POST /v1/systemone` 同时提交 `choice`、`noul`、`score` 三种问题返回 200，`usage.output_tokens=0`；官方 TypeSafe Python SDK 也成功返回三个答案。以上只证明接口运行，不证明概率已校准或业务准确率。

服务仅监听服务器本机。客户端可通过 SSH 隧道连接：

```bash
ssh -N -L 30000:127.0.0.1:30000 -p 30113 root@120.209.70.195
```

随后在客户端请求 `http://127.0.0.1:30000/v1/systemone`，或使用 `TypeSafeClient(base_url="http://127.0.0.1:30000", api_key="unused")`。没有启用公网 API 端口。

## 来源及边界

- [SGLang Decision models / System One compatible API](https://docs.sglang.io/docs/supported-models/decision_models#system-one-compatible-api)
- [SGLang 安装说明](https://docs.sglang.io/docs/get-started/install)
- [Qwen3.8-27B 模型页](https://huggingface.co/Qwen/Qwen3.8-27B)

SGLang 文档验证过 Qwen3.8-27B 在 H200 上的 BF16 部署；本次 A100 实例通过了实际接口请求，但尚未做负载、长文本、重启恢复或准确率评测。
