# Mikan 工具箱

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)](https://www.qt.io/qt-for-python)

> Mikan 工具箱 — 加密、编码、拼音密码与破解综合工具集，赛博朋克风格桌面应用

Mikan 工具箱是一套基于 Python 和 PySide6 开发的桌面应用程序集合，包含三个子项目，覆盖加密、编码转换、拼音密码、哈希计算、密码破解等全场景密码学需求。所有子项目均采用赛博朋克风格深色主题，提供图形化界面，轻量、稳定、安全。

---

## 子项目

### 1. Mikan Lock v2.3 — 精简稳定版加密工具箱

提供图形化界面来执行多层组合加密与解密操作。内置维吉尼亚、凯撒、ROT13、Base64、十六进制、URL编码、倒序共 7 种稳定可逆算法，支持自定义加密层数与顺序，第一层统一由维吉尼亚密码处理密钥，解密自动反向执行。密钥不匹配则无法解密，确保安全性。

**运行命令：** `python Mikan_china.py`

### 2. MikanLock v3.0 — 专业加密/编码/哈希/破解工具箱

侧边栏导航设计，内置 11 个功能面板，覆盖编码转换、进制转换、键盘密码、经典密码、哈希计算、AES/RSA 加密、JWT 处理、哈希破解与编码检测等全场景密码学需求。支持摩斯密码表、QWERTY 键盘邻键映射密码、Base58/Base32 等进阶编码，以及 bcrypt/BLAKE2b 等安全哈希算法。

**运行命令：** `python Mikan_lock.py`

### 3. Mikan Pinyin Cipher v2.0 — 中文拼音加密 + 300+编码解码器

中文拼音加密与编码处理桌面应用程序，提供图形化界面来执行中文转拼音（带声调/无声调/首字母）后加密，以及 300+ 字符编码的加密与解密操作。内置 pypinyin 引擎实现精准的中文拼音转换，支持维吉尼亚、凯撒、ROT13 三种经典加密算法，收录 Python 全部 300+ 内置字符编码。

**运行命令：** `python Mikan_tool.py`

---

## 功能特性

### Mikan Lock v2.3

#### 核心算法（7种）

- **维吉尼亚密码**：支持中文/英文/数字密钥，自动转换为拼音首字母或数字映射（A-J）
- **凯撒密码**：支持数字偏移量自定义，默认偏移 3
- **ROT13**：固定偏移 13 的字母替换，加解密相同操作
- **Base64 编码**：标准 Base64 编解码，自动处理填充
- **十六进制编码**：文本与 Hex 字符串互转
- **URL 编码**：百分号编码/解码（quote/unquote）
- **倒序**：字符串完全反转

#### 多层加密引擎

- 支持 2~6 层加密配置，每层独立选择算法
- 加密顺序：第1层 → 第2层 → ... → 第N层（从上到下依次执行）
- 解密顺序：第N层 → ... → 第2层 → 第1层（自动反向执行）
- 全局密钥统一输入，维吉尼亚和凯撒层共用同一密钥
- 密钥不同则无法解密（强制校验机制）

#### 配置管理

- **导出配置**：将当前层数、算法顺序、密钥打包为 Base64 编码的 JSON 字符串
- **导入配置**：从 Base64 配置字符串恢复层设置
- **剪贴板导入**：直接从剪贴板粘贴配置字符串

### MikanLock v3.0

#### 编码转换

- Base64 编码/解码
- URL-Safe Base64 编码/解码
- 十六进制（Hex）编码/解码
- URL 编码/解码
- Unicode 转义/反转义
- HTML 转义/反转义
- 摩斯密码编码/解码（完整 A-Z / 0-9 / 空格 映射表）

#### 进制转换

- 二进制、八进制、十进制、十六进制互转
- Base64 / Base32 / Base58 进制支持
- ASCII 字符与进制互转（字符→二进制/八进制/十六进制/十进制）
- 文本批量转进制序列（空格分隔）
- 任意进制（2~36 位）编码/解码
- Base58 编码（比特币风格）

#### 键盘密码

- QWERTY 键盘邻键映射加密（上下左右邻键替换）
- 键盘坐标记录（行/列坐标对）
- 支持自定义键盘布局

#### 经典密码

- **凯撒密码**：可配置偏移量（1~25），支持加密/解密/暴力破解
- **ROT13**：固定偏移 13 的字母替换
- **Atbash**：字母表反转（A↔Z, B↔Y...）
- **维吉尼亚密码**：自定义密钥，支持加密/解密
- **仿射密码**：自定义 a/b 参数，支持加密/解密

#### 哈希计算

- MD5 / SHA-1 / SHA-256 / SHA-512
- SHA3-256 / SHA3-512
- BLAKE2b
- bcrypt（自适应哈希）
- HMAC-SHA256（带密钥哈希）
- 文件哈希计算（MD5 + SHA-256 + SHA-512 一键计算）
- 进度条显示文件处理进度

#### AES 加密/解密

- CBC 模式（传统加密模式）
- GCM 模式（认证加密，防篡改）
- 自定义密钥字符串

#### RSA 加密/解密

- RSA 密钥对生成（可配置密钥长度）
- RSA 公钥加密 / 私钥解密
- RSA 私钥加密 / 公钥解密（数字签名模式）
- PEM 格式密钥导出/导入

#### JWT 处理

- JWT Token 编码（Header + Payload 签名）
- JWT Token 解码与验证
- 支持 HS256 / RS256 算法
- 自定义密钥/证书

#### 哈希破解与智能识别

- 哈希值字典查找破解（MD5/SHA1/SHA256/SHA512）
- 彩虹表查找
- 智能编码识别（自动检测文本使用的编码类型）

### Mikan Pinyin Cipher v2.0

#### 拼音引擎

- **带声调拼音**：中文 → 拼音（带声调数字），如 "你好" → "ni3hao3"
- **无声调拼音**：中文 → 拼音（无声调），如 "你好" → "nihao"
- **拼音首字母**：中文 → 拼音首字母，如 "你好世界" → "nhsj"
- 自动识别非中文字符并原样保留

#### 加密模式

- **拼音加密**：中文 → 拼音 → 维吉尼亚/凯撒/ROT13 加密
- **拼音解密**：密文 → 维吉尼亚/凯撒/ROT13 解密 → 拼音 → 中文
- **编码加密**：用 300+ 编码对文本进行编码加密
- **编码解密**：用 300+ 编码对乱码文本进行智能解密

#### 300+ 编码覆盖

- **Unicode 系列**：utf-8、utf-8-sig、utf-16、utf-16-le、utf-16-be、utf-32、utf-32-le、utf-32-be、unicode-escape
- **ASCII 系列**：ascii、ansi_x3.4-1968、ansi_x3.4-1986、us-ascii
- **ISO-8859 系列**：iso-8859-1 至 iso-8859-16（涵盖拉丁文/泰文/希伯来文/阿拉伯文等）
- **Windows CP 系列**：cp437、cp737、cp775、cp850~cp869、cp874、cp932~cp959、cp970~cp999 等（涵盖多国语言）
- **中文编码**：gb2312、gbk、gb18030、hz、big5、big5hkscs、iso-2022-cn、iso-2022-cn-ext
- **日文编码**：shift_jis、shift_jis_2004、shift_jisx0213、euc_jp、euc_jis_2004、euc_jisx0213、iso-2022-jp 系列
- **韩文编码**：euc_kr、iso-2022-kr、johab
- **斯拉夫语编码**：koi8_r、koi8_u、koi8-ru
- **Mac 编码**：mac-roman、mac-cyrillic、mac-greek、mac-turkish、mac-icelandic 等
- **其他编码**：tis-620、viscii、tcvn、vni、hp-roman8、roman8 等

#### 结果展示

- 列表形式展示所有编码结果（编码名称 + 解码内容）
- 双击结果项一键复制到剪贴板
- 右键菜单操作
- 全选/复制全部结果

---

## UI 特性（全部子项目共用）

- 赛博朋克风格深色主题（深色背景 + 霓虹配色）
- 扁平化按钮设计（多色方案：青色/黄色/橙色/粉色/蓝色/紫色/红色/绿色）
- CyberGroupBox 分组框（霓虹边框 + 圆角）
- 进度条显示处理进度
- 实时调试日志与状态栏实时反馈
- 一键复制结果 / 复制完整日志

---

## 技术栈

| 组件 | 技术 |
|------|------|
| 语言 | Python 3.8+ |
| GUI 框架 | PySide6 (Qt for Python) |
| 密码学 | cryptography（AES/RSA/哈希/HMAC） |
| 哈希计算 | hashlib、bcrypt |
| JWT | pyjwt |
| 编码检测 | chardet |
| 拼音引擎 | pypinyin（带声调/无声调/首字母） |
| 编码处理 | base64、binascii、codecs、urllib.parse、Python 内置 encodings 模块（300+ 编码） |
| 并发模型 | QThread + threading |
| 配置存储 | JSON 文件 / Base64 编码 |
| UI 样式 | 自定义 QSS 赛博朋克主题 |

---

## 安装与运行

### 环境要求

- Windows / macOS / Linux
- Python 3.8 或更高版本

### 安装依赖

```
pip install PySide6 cryptography chardet bcrypt pyjwt pypinyin
```

### 运行程序

```
# Mikan Lock v2.3 — 精简稳定版加密工具箱
python Mikan_china.py

# MikanLock v3.0 — 专业加密/编码/哈希/破解工具箱
python Mikan_lock.py

# Mikan Pinyin Cipher v2.0 — 中文拼音加密 + 300+编码解码器
python Mikan_tool.py
```

首次运行时，程序会自动检测缺失依赖并弹出安装提示，支持清华/阿里/豆瓣多镜像源自动切换安装。

---

## 项目结构

```
Mikan_china.py          # Mikan Lock v2.3 主程序入口（单文件应用）
├── Theme               # 赛博朋克主题配色与QSS样式
├── CipherAlgorithms    # 7种核心算法实现
├── ALGORITHMS          # 算法注册表
├── ConfigManager       # 配置导出/导入管理器
└── MainWindow          # 主窗口（UI逻辑与加密流程）

Mikan_lock.py           # MikanLock v3.0 主程序入口（单文件应用）
├── CyberTheme          # 赛博朋克主题配色
├── CryptEngine         # 核心加密引擎（进制转换/编码/摩斯/键盘/经典密码/哈希/AES/RSA/JWT）
├── WorkerThread        # 异步工作线程
├── BasePanel           # 面板基类
├── EncodingPanel       # 编码转换面板
├── BaseConvertPanel    # 进制转换面板
├── KeyboardPanel       # 键盘密码面板
├── ClassicCipherPanel  # 经典密码面板
├── HashPanel           # 哈希计算面板
├── AesPanel            # AES加密面板
├── RsaPanel            # RSA加密面板
├── JwtPanel            # JWT处理面板
├── CrackPanel          # 哈希破解面板
├── DetectPanel         # 编码检测面板
├── ReferencePanel      # 编解码参考面板
└── MainWindow          # 主窗口（侧边栏导航 + 面板切换）

Mikan_tool.py           # Mikan Pinyin Cipher v2.0 主程序入口（单文件应用）
├── ALL_ENCODINGS       # 300+ 编码列表（去重排序）
├── Theme               # 赛博朋克主题配色与QSS样式
├── PinyinEngine        # 拼音引擎（带声调/无声调/首字母转换）
├── CipherEngine        # 加密引擎（维吉尼亚/凯撒/ROT13/全编码加密解密）
└── MainWindow          # 主窗口（模式切换/拼音加密/编码处理）
```

> 注：每个子项目均采用单文件架构，所有模块、引擎、面板、对话框和主窗口均集成在各自的主文件中，便于分发和部署。

---

## 模块说明

### Mikan Lock v2.3

| 模块 | 说明 |
|------|------|
| `Theme` | 赛博朋克主题配色（背景色、霓虹色、按钮色等） |
| `input_style()` | 输入控件 QSS 样式生成函数 |
| `btn_style(color)` | 按钮 QSS 样式生成函数（带悬停/按下效果） |
| `FlatButton` | 自定义扁平化按钮组件（霓虹边框 + 悬停高亮） |
| `CipherAlgorithms` | 核心算法类（维吉尼亚/凯撒/ROT13/Base64/Hex/URL/倒序） |
| `ALGORITHMS` | 算法注册表字典（名称→加密/解密函数/是否需要密钥/描述） |
| `ConfigManager` | 配置管理器（导出为Base64 JSON / 从Base64 JSON导入） |
| `MainWindow` | 主窗口（层数配置、算法选择、加密/解密执行、调试日志） |

### MikanLock v3.0

| 模块 | 说明 |
|------|------|
| `CyberTheme` | 赛博朋克主题配色（背景色、霓虹色、按钮色等） |
| `CryptEngine` | 核心加密引擎（进制转换/编码/摩斯密码/键盘密码/经典密码/哈希/AES/RSA/JWT/Base58/Base32） |
| `WorkerThread` | 异步工作线程（耗时操作不阻塞UI） |
| `BasePanel` | 面板基类（统一样式与布局模板） |
| `EncodingPanel` | 编码转换面板（Base64/Hex/URL/Unicode/HTML/摩斯） |
| `BaseConvertPanel` | 进制转换面板（二进制/八进制/十进制/十六进制/Base64/Base32/Base58互转） |
| `KeyboardPanel` | 键盘密码面板（QWERTY邻键映射/坐标记录） |
| `ClassicCipherPanel` | 经典密码面板（凯撒/ROT13/Atbash/维吉尼亚/仿射） |
| `HashPanel` | 哈希计算面板（MD5/SHA系列/SHA3/BLAKE2b/bcrypt/HMAC/文件哈希） |
| `AesPanel` | AES加密面板（CBC/GCM模式） |
| `RsaPanel` | RSA加密面板（密钥生成/加密/解密/签名） |
| `JwtPanel` | JWT处理面板（编码/解码/验证） |
| `CrackPanel` | 哈希破解面板（字典查找/彩虹表/智能编码识别） |
| `DetectPanel` | 编码检测面板（自动检测文本编码类型） |
| `ReferencePanel` | 编解码参考面板（摩斯密码表/键盘布局参考） |
| `MainWindow` | 主窗口（侧边栏导航 + QStackedWidget面板切换） |

### Mikan Pinyin Cipher v2.0

| 模块 | 说明 |
|------|------|
| `ALL_ENCODINGS` | 300+ 编码名称列表（Python 内置编码全集，去重排序） |
| `Theme` | 赛博朋克主题配色（背景色、霓虹色、按钮色等） |
| `input_style()` | 输入控件 QSS 样式生成函数 |
| `btn_style(color)` | 按钮 QSS 样式生成函数（带悬停/按下效果） |
| `FlatButton` | 自定义扁平化按钮组件（霓虹边框 + 悬停高亮） |
| `PinyinEngine` | 拼音引擎（to_pinyin_with_tone / to_pinyin_normal / to_pinyin_first） |
| `CipherEngine` | 加密引擎（vigenere_encrypt/decrypt / caesar_encrypt/decrypt / rot13 / encode_all / decode_all） |
| `MainWindow` | 主窗口（模式选择/拼音风格/算法选择/密钥输入/执行/结果展示） |

---

## 注意事项

### 通用注意事项

1. **依赖安装**：首次运行程序会自动检测缺失依赖并提示安装，支持多镜像源自动切换。也可手动执行 `pip install PySide6 cryptography chardet bcrypt pyjwt pypinyin` 预先安装。
2. **bcrypt 依赖**：bcrypt 库在部分系统上编译可能需要 C 编译器，如安装失败请手动安装预编译包：`pip install bcrypt`。
3. **pypinyin 依赖**：拼音转换功能依赖 pypinyin 库，首次运行会自动安装。如自动安装失败，请手动执行 `pip install pypinyin`。
4. **RSA 密钥长度**：生成 RSA 密钥时，密钥长度越长安全性越高但计算越慢，建议根据实际需求选择（2048 位为推荐值）。
5. **JWT 安全**：JWT 签名密钥应妥善保管，不要将敏感信息放入 JWT Payload 中（JWT 编码可被逆向解码）。
6. **哈希破解**：字典查找功能依赖内置字典数据，对于复杂密码可能无法破解。彩虹表功能需要额外数据支持。
7. **文件哈希**：大文件哈希计算可能需要较长时间，请耐心等待，程序会显示进度条。
8. **杀毒软件**：程序涉及加密解密和进程操作，可能被杀毒软件误报，请将程序加入白名单。
9. **编码匹配**：300+ 编码中并非所有编码都能正确解码任意文本，程序会自动过滤不可打印字符较多的结果，但仍可能有部分编码输出乱码，请根据实际情况选择。
10. **拼音准确性**：pypinyin 引擎对常见汉字拼音识别准确率高，但部分生僻字或多音字可能需要手动调整。
11. **加密安全性**：本工具中的加密算法（维吉尼亚/凯撒/ROT13）属于经典密码学算法，适用于学习、趣味加密等场景，不建议用于高安全需求的场景。
12. **大文本处理**：对超长文本进行 300+ 编码遍历可能需要数秒时间，请耐心等待。

### Mikan Lock v2.3 特有

1. **密钥要求**：维吉尼亚和凯撒算法需要输入密钥，密钥为空时将无法执行加密/解密操作。
2. **密钥校验**：解密时必须使用与加密时完全相同的密钥，否则将无法还原原文。
3. **中文密钥支持**：维吉尼亚算法支持中文密钥，程序会自动将其转换为拼音首字母进行处理。
4. **数字密钥映射**：纯数字密钥会自动映射为字母（0→A, 1→B, ..., 9→J）。

---

## 开发指南

### 代码风格

- 遵循 PEP 8 编码规范
- 使用类型注解（typing）
- 使用 dataclass 定义数据结构
- 异步操作通过 QThread + Signal/Slot 机制实现
- UI 样式统一使用 QSS 管理
- 算法类采用静态方法设计，便于独立调用

### 添加新功能面板（MikanLock v3.0）

1. 创建新的面板类继承 `BasePanel`
2. 在 `CryptEngine` 中实现核心功能方法
3. 在 `MainWindow` 的 `panels` 列表中注册新面板
4. 在侧边栏中自动出现新面板按钮

### 添加新算法（Mikan Lock v2.3）

1. 在 `CipherAlgorithms` 类中添加新的加密/解密静态方法
2. 在 `ALGORITHMS` 注册表中注册新算法（名称、加密函数、解密函数、是否需要密钥、描述）
3. 在 `MainWindow.update_layers()` 中确保新算法出现在下拉选项中

### 添加新编码（Mikan Pinyin Cipher v2.0）

编码列表来源于 Python 内置 encodings 模块，如需添加更多编码，可在 `ALL_ENCODINGS` 列表中追加编码名称。

### 添加新加密算法（Mikan Pinyin Cipher v2.0）

1. 在 `CipherEngine` 类中添加新的加密/解密静态方法
2. 在 `MainWindow` 的模式逻辑中集成新算法
3. 更新 UI 控件以支持新算法的参数配置

---

## 许可证

本项目采用 **GNU General Public License v3.0** 许可。你可以自由地复制、修改和再分发本软件，但必须保留版权声明和许可声明。衍生作品也必须以相同的许可证开源。

详见 [LICENSE](LICENSE) 文件。

---

## 致谢

- [PySide6](https://www.qt.io/qt-for-python) - Qt for Python 绑定
- [cryptography](https://cryptography.io/) - 密码学工具包
- [bcrypt](https://github.com/pyca/bcrypt) - bcrypt 哈希库
- [pyjwt](https://pyjwt.readthedocs.io/) - JWT 处理库
- [chardet](https://github.com/chardet/chardet) - 字符编码检测库
- [pypinyin](https://github.com/mozillazg/python-pypinyin) - 中文拼音转换库
- [DeepSeek](https://www.deepseek.com/) - AI 辅助开发

---

## 联系方式

如有问题或建议，欢迎提交 Issue 或 Pull Request。

---

*Made with care by Mikan Team · AI assisted by DeepSeek*
