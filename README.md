# fishingTB

在终端里刷贴吧的 Textual TUI —— 键盘/鼠标都能用，窗口标题可伪装成 `npm run dev`，一键老板键切走。

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Textual](https://img.shields.io/badge/UI-Textual-41a4a9.svg)](https://textual.textualize.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 特性

| | |
|---|---|
| **登录** | 终端扫码登录（百度 App），凭证写入本地 `config.yaml` |
| **浏览** | 关注动态、已关注吧、搜索进吧；帖列表与楼层阅读 |
| **图片** | 帖内 `[图N]` 弹窗预览；Windows Terminal 下优先 Sixel，否则回退字符渲染 |
| **摸鱼** | 可配置窗口标题；`` ` `` 老板键秒切伪装屏 |
| **性能** | 图片 HTTP 复用、磁盘/内存缓存（启动时清空图片磁盘缓存） |

## 环境要求

- **Python 3.11+**（本机验证：Python 3.14 / macOS arm64）
- 推荐 **[Windows Terminal](https://github.com/microsoft/terminal)**（Sixel 彩色图预览体验最好）
- 贴吧账号（扫码登录）

## 快速开始

macOS / Linux 在项目目录运行：

```bash
./start.sh
# 仅扫码登录
./start.sh login
```

macOS 和 Linux 均直接在当前终端会话中启动，不会打开额外的终端窗口或标签页，也无需安装 iTerm。可以在 Codex 的终端中直接运行 `./start.sh`。

脚本会自动切换到项目目录并启用 `.venv`。首次运行自动创建虚拟环境、安装依赖，需要系统已安装 Python 3.11+；之后复用该环境。依赖安装失败时，下次启动会自动重试。

进入登录页后点击「扫码登录」，用百度 App 扫描并确认。二维码使用黑白块渲染；扫码前建议放大终端窗口。

本次检查、修复和验证范围见 [本地检查报告](docs/LOCAL_REVIEW.md)。
`config.yaml` 包含账号登录凭证，以权限 `600` 保存在本地，未加密，请勿分享。
当前项目为 `aiotieba==4.8.2` 增加了 HTTPS 与证书校验适配，升级该依赖时必须重新验证适配和安全测试。

`requirements.lock` 锁定本机验证的 30 个依赖及 macOS arm64 / Python 3.14 wheel 的 SHA-256。
同平台重新安装时使用：

```bash
python -m pip install --index-url https://pypi.org/simple --only-binary=:all: --require-hashes -r requirements.lock
```

其他系统使用下方 `requirements.txt` 安装流程，再运行测试；锁文件不保证跨平台可用。

```bash
git clone https://github.com/andrewtarget/fishingTB.git
cd fishingTB
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
copy config.example.yaml config.yaml   # Windows
# cp config.example.yaml config.yaml   # Unix
```

**方式 A — 进 TUI 再扫码**

```bash
python main.py
```

**方式 B — 仅登录（不进界面）**

```bash
python main.py login
```

首次使用把 `config.example.yaml` 拷成 `config.yaml`；登录成功后不要提交 `config.yaml`（已在 `.gitignore`）。

## 配置

`config.yaml`（项目根目录，见 `config.example.yaml`）：

| 键 | 说明 |
|----|------|
| `bduss` / `stoken` | 登录后自动写入 |
| `terminal_title` | 终端标题，默认 `npm run dev` |
| `theme` | 默认 `ansi-light`，使用终端本身的底色、文字色和 ANSI 调色板；深色终端可选 `ansi-dark` |
| `recent_forums` | 最近访问的吧 |
| `image_renderer` | `auto` \| `sixel` \| `braille` \| `halfblock` |

`auto`：Windows Terminal 用 Sixel，其它终端用 braille 回退。

## 常用操作

| 场景 | 操作 |
|------|------|
| 退出 | `q` |
| 老板键 | `` ` `` |
| 帖内图片 | 点 `[图N]` 或快捷键（见界面提示） |
| 预览内浏览器打开 | `o` |
| 登出 / 返回 | 登录页按钮 |

## 项目结构

```
fishingTB/
├── main.py                 # 入口：tui | login
├── config.example.yaml
├── fishingtb/
│   ├── ui/                 # Textual 界面
│   ├── feeds/              # 吧列表、动态
│   ├── media/              # 图片下载与终端渲染
│   └── auth/               # 扫码登录
├── scripts/                # smoke / pilot 测试
└── docs/screenshots/       # README 截图
```

## 开发

```bash
python -m scripts.smoke_test
python -m scripts.pilot_test
python -m scripts.security_test
python -m scripts.workflow_test
# 联网公开数据测试，无需账号
python -m scripts.api_smoke
```

## 截图

> 以下为界面示意（终端主题与字体因环境而异）。

### 主页 · 动态 / 吧列表

![主页 — 动态与关注吧](docs/screenshots/fishingtb-home.png)

### 帖子阅读

![帖子楼层与图片链接](docs/screenshots/fishingtb-thread.png)

### 图片预览

![弹窗 Sixel 预览](docs/screenshots/fishingtb-preview.png)

---

## 免责声明

本项目仅供学习与个人使用。请遵守百度贴吧服务条款与当地法律法规；勿用于未授权爬取、传播或商用。使用本软件产生的风险由使用者自行承担。

## License

MIT — 见 [LICENSE](LICENSE)。
