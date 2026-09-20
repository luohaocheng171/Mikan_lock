#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mikan Lock v2.3 — 精简稳定版
只保留 7 个有规律的算法，密钥统一由第一层维吉尼亚处理
加密顺序按配置执行，解密反向执行
修复：维吉尼亚密钥强制校验，密钥不同无法解密
"""

import sys
import os
import base64
import hashlib
import binascii
import codecs
import json
import re
from typing import List, Dict
from urllib.parse import quote, unquote

# ==================== 自动补全依赖 ====================
try:
    from cryptography.hazmat.primitives import hashes, padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️ cryptography 未安装，AES 功能不可用")
    print("📦 正在安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography"])
    print("✅ 安装完成，请重新运行")
    sys.exit(0)

# ==================== PySide6 检查 ====================
try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
except ImportError:
    print("📦 正在安装依赖 PySide6...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
    print("✅ 安装完成，请重新运行")
    sys.exit(0)

# ==================== 赛博风主题 ====================
class Theme:
    BG = "#0f0f1a"
    BG2 = "#18182a"
    INPUT_BG = "#1a1a2e"
    INPUT_BORDER = "#334155"
    TEXT = "#ffffff"
    TEXT_DIM = "#94a3b8"
    NEON_PURPLE = "#a855f7"
    NEON_GREEN = "#34d399"
    NEON_CYAN = "#22d3ee"
    NEON_ORANGE = "#f59e0b"
    NEON_PINK = "#ec4899"
    NEON_BLUE = "#3b82f6"
    BORDER = "#334155"
    BTN_BG = "#1e1b4b"
    BTN_HOVER = "#312e81"
    BTN_ACTIVE = "#4f46e5"


def input_style():
    return f"""
        QLineEdit, QTextEdit, QComboBox, QSpinBox {{
            background: {Theme.INPUT_BG};
            color: {Theme.TEXT};
            border: 1px solid {Theme.INPUT_BORDER};
            border-radius: 6px;
            padding: 6px 10px;
            font-family: "Consolas", "Microsoft YaHei", monospace;
            font-size: 10pt;
        }}
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
            border-color: {Theme.NEON_PURPLE};
        }}
        QTextEdit {{
            background: {Theme.INPUT_BG};
            color: {Theme.TEXT};
            border: 1px solid {Theme.INPUT_BORDER};
            border-radius: 6px;
            padding: 8px;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox QAbstractItemView {{
            background: {Theme.INPUT_BG};
            color: {Theme.TEXT};
            selection-background-color: {Theme.BTN_HOVER};
        }}
    """


def btn_style(color):
    return f"""
        QPushButton {{
            background: {Theme.BTN_BG};
            color: {Theme.TEXT};
            border: 1px solid {color};
            border-radius: 6px;
            padding: 6px 16px;
            font-size: 9pt;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {Theme.BTN_HOVER};
            border-color: {Theme.NEON_CYAN};
        }}
        QPushButton:pressed {{
            background: {Theme.BTN_ACTIVE};
        }}
    """


class FlatButton(QPushButton):
    def __init__(self, text="", color=Theme.NEON_PURPLE):
        super().__init__(text)
        self.setFixedHeight(32)
        self.setStyleSheet(btn_style(color))
        self.setCursor(Qt.PointingHandCursor)


# ==================== 核心算法（完整修复版） ====================
class CipherAlgorithms:
    """只保留 7 个有规律、可逆、稳定的算法"""

    # -------- 中文转拼音首字母（简易映射） --------
    _PINYIN_MAP = {
        '床': 'c', '前': 'q', '明': 'm', '月': 'y', '光': 'g',
        '你': 'n', '好': 'h', '世': 's', '界': 'j',
        '中': 'z', '文': 'w', '加': 'j', '密': 'm',
        '测': 'c', '试': 's', '钥': 'y', '键': 'j',
        '安': 'a', '全': 'q', '可': 'k', '靠': 'k',
        '稳': 'w', '定': 'd', '爱': 'a', '国': 'g',
        '人': 'r', '民': 'm', '大': 'd', '小': 'x',
        '上': 's', '下': 'x', '左': 'z', '右': 'y',
        '天': 't', '地': 'd', '水': 's', '火': 'h',
        '风': 'f', '云': 'y', '山': 's', '河': 'h',
        '日': 'r', '星': 'x', '春': 'c', '夏': 'x',
        '秋': 'q', '冬': 'd', '东': 'd', '西': 'x',
        '南': 'n', '北': 'b', '美': 'm', '丽': 'l',
        '强': 'q', '大': 'd', '伟': 'w', '岸': 'a',
    }

    @classmethod
    def _chinese_to_pinyin_first(cls, text: str) -> str:
        """中文 → 拼音首字母"""
        result = ''
        for c in text:
            if c in cls._PINYIN_MAP:
                result += cls._PINYIN_MAP[c]
            elif c.isalpha():
                result += c.upper()
            elif c.isdigit():
                result += chr(ord('A') + int(c))
            else:
                result += c
        return result.upper()

    @classmethod
    def _normalize_vigenere_key(cls, key: str) -> str:
        """将任意密钥转换为字母密钥（A-Z）"""
        if not key:
            raise ValueError("密钥不能为空！")

        # 检查是否包含中文
        if re.search(r'[\u4e00-\u9fff]', key):
            result = cls._chinese_to_pinyin_first(key)
            if not result:
                raise ValueError("无法将中文密钥转换为拼音首字母，请使用英文或数字密钥")
            return result

        # 如果全是数字，映射为字母：0→A, 1→B, ... 9→J
        if key.isdigit():
            return ''.join(chr(ord('A') + int(c)) for c in key)

        # 只保留字母，大写
        result = ''.join(c.upper() for c in key if c.isalpha())
        if not result:
            # 尝试提取数字
            digits = ''.join(c for c in key if c.isdigit())
            if digits:
                return ''.join(chr(ord('A') + int(c)) for c in digits)
            raise ValueError(f"密钥 '{key}' 不包含字母或数字，无法使用")

        return result

    # -------- 维吉尼亚密码（强制密钥校验） --------
    @classmethod
    def vigenere_encrypt(cls, text: str, key: str = "") -> str:
        if not key:
            raise ValueError("❌ 维吉尼亚加密需要密钥！")
        key = cls._normalize_vigenere_key(key)
        result, key_idx = [], 0
        for c in text:
            if c.isupper():
                shift = ord(key[key_idx % len(key)]) - ord('A')
                result.append(chr((ord(c) - ord('A') + shift) % 26 + ord('A')))
                key_idx += 1
            elif c.islower():
                shift = ord(key[key_idx % len(key)]) - ord('A')
                result.append(chr((ord(c) - ord('a') + shift) % 26 + ord('a')))
                key_idx += 1
            else:
                result.append(c)
        return ''.join(result)

    @classmethod
    def vigenere_decrypt(cls, text: str, key: str = "") -> str:
        if not key:
            raise ValueError("❌ 维吉尼亚解密需要密钥！")
        key = cls._normalize_vigenere_key(key)
        result, key_idx = [], 0
        for c in text:
            if c.isupper():
                shift = ord(key[key_idx % len(key)]) - ord('A')
                result.append(chr((ord(c) - ord('A') - shift) % 26 + ord('A')))
                key_idx += 1
            elif c.islower():
                shift = ord(key[key_idx % len(key)]) - ord('A')
                result.append(chr((ord(c) - ord('a') - shift) % 26 + ord('a')))
                key_idx += 1
            else:
                result.append(c)
        return ''.join(result)

    # -------- 凯撒密码 --------
    @staticmethod
    def caesar_encrypt(text: str, key: str = "") -> str:
        shift = 3
        if key:
            digits = ''.join(c for c in key if c.isdigit())
            if digits:
                shift = int(digits) % 26
        result = []
        for c in text:
            if c.isupper():
                result.append(chr((ord(c) - ord('A') + shift) % 26 + ord('A')))
            elif c.islower():
                result.append(chr((ord(c) - ord('a') + shift) % 26 + ord('a')))
            else:
                result.append(c)
        return ''.join(result)

    @staticmethod
    def caesar_decrypt(text: str, key: str = "") -> str:
        shift = 3
        if key:
            digits = ''.join(c for c in key if c.isdigit())
            if digits:
                shift = int(digits) % 26
        return CipherAlgorithms.caesar_encrypt(text, str(-shift))

    # -------- ROT13 --------
    @staticmethod
    def rot13(text: str, key: str = "") -> str:
        result = []
        for c in text:
            if c.isupper():
                result.append(chr((ord(c) - ord('A') + 13) % 26 + ord('A')))
            elif c.islower():
                result.append(chr((ord(c) - ord('a') + 13) % 26 + ord('a')))
            else:
                result.append(c)
        return ''.join(result)

    # -------- Base64 --------
    @staticmethod
    def base64_encode(text: str, key: str = "") -> str:
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')

    @staticmethod
    def base64_decode(text: str, key: str = "") -> str:
        text = text.strip()
        missing_padding = len(text) % 4
        if missing_padding:
            text += '=' * (4 - missing_padding)
        try:
            return base64.b64decode(text.encode('utf-8')).decode('utf-8', errors='ignore')
        except Exception:
            return text

    # -------- Hex --------
    @staticmethod
    def hex_encode(text: str, key: str = "") -> str:
        return binascii.hexlify(text.encode('utf-8')).decode('utf-8')

    @staticmethod
    def hex_decode(text: str, key: str = "") -> str:
        text = text.strip()
        clean = ''.join(c for c in text if c in '0123456789abcdefABCDEF')
        if not clean:
            return text
        if len(clean) % 2 != 0:
            clean = clean[:-1]
        try:
            return binascii.unhexlify(clean).decode('utf-8', errors='ignore')
        except Exception:
            return text

    # -------- URL 编码 --------
    @staticmethod
    def url_encode(text: str, key: str = "") -> str:
        return quote(text, safe='')

    @staticmethod
    def url_decode(text: str, key: str = "") -> str:
        try:
            return unquote(text)
        except Exception:
            return text

    # -------- 倒序 --------
    @staticmethod
    def reverse(text: str, key: str = "") -> str:
        return text[::-1]


# ==================== 算法注册表 ====================
ALGORITHMS = {
    "维吉尼亚": {
        "encrypt": CipherAlgorithms.vigenere_encrypt,
        "decrypt": CipherAlgorithms.vigenere_decrypt,
        "need_key": True,
        "desc": "维吉尼亚密码（数字→A-J）"
    },
    "凯撒": {
        "encrypt": CipherAlgorithms.caesar_encrypt,
        "decrypt": CipherAlgorithms.caesar_decrypt,
        "need_key": True,
        "desc": "凯撒密码（数字偏移）"
    },
    "ROT13": {
        "encrypt": CipherAlgorithms.rot13,
        "decrypt": CipherAlgorithms.rot13,
        "need_key": False,
        "desc": "ROT13（偏移13）"
    },
    "Base64": {
        "encrypt": CipherAlgorithms.base64_encode,
        "decrypt": CipherAlgorithms.base64_decode,
        "need_key": False,
        "desc": "Base64 编码"
    },
    "Hex": {
        "encrypt": CipherAlgorithms.hex_encode,
        "decrypt": CipherAlgorithms.hex_decode,
        "need_key": False,
        "desc": "十六进制编码"
    },
    "URL编码": {
        "encrypt": CipherAlgorithms.url_encode,
        "decrypt": CipherAlgorithms.url_decode,
        "need_key": False,
        "desc": "URL 百分号编码"
    },
    "倒序": {
        "encrypt": CipherAlgorithms.reverse,
        "decrypt": CipherAlgorithms.reverse,
        "need_key": False,
        "desc": "字符串倒序"
    },
}


# ==================== 配置管理器 ====================
class ConfigManager:
    @staticmethod
    def export_config(layer_names: List[str], key: str, layer_count: int) -> str:
        config = {
            "version": "2.3",
            "layer_count": layer_count,
            "layers": layer_names,
            "key": key
        }
        json_str = json.dumps(config, ensure_ascii=False)
        return base64.b64encode(json_str.encode('utf-8')).decode('utf-8')

    @staticmethod
    def import_config(b64_str: str) -> Dict:
        try:
            b64_str = b64_str.strip()
            json_str = base64.b64decode(b64_str.encode('utf-8')).decode('utf-8')
            return json.loads(json_str)
        except Exception as e:
            return {"error": str(e)}


# ==================== 主窗口 ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧩 Mikan Lock v2.3 — 密钥强制校验版")
        self.setMinimumSize(900, 750)
        self.resize(1000, 780)
        self.setStyleSheet(f"background: {Theme.BG};")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 标题
        title = QLabel("🧩 Mikan Lock")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {Theme.NEON_PURPLE}; font-size: 20pt; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("加密顺序 1→2→3 · 解密顺序 3→2→1 · 密钥不同无法解密")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {Theme.TEXT_DIM}; font-size: 11pt;")
        layout.addWidget(subtitle)

        # ===== 配置导入/导出 =====
        config_toolbar = QHBoxLayout()
        self.export_btn = FlatButton("📤 导出配置", Theme.NEON_GREEN)
        self.export_btn.clicked.connect(self.export_config)
        config_toolbar.addWidget(self.export_btn)

        self.import_btn = FlatButton("📥 导入配置", Theme.NEON_CYAN)
        self.import_btn.clicked.connect(self.import_config)
        config_toolbar.addWidget(self.import_btn)

        self.import_from_text_btn = FlatButton("📋 从剪贴板导入", Theme.NEON_ORANGE)
        self.import_from_text_btn.clicked.connect(self.import_from_clipboard)
        config_toolbar.addWidget(self.import_from_text_btn)

        config_toolbar.addStretch()
        layout.addLayout(config_toolbar)

        # ===== 层数 + 密钥 =====
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("层数:"))
        self.layer_spin = QSpinBox()
        self.layer_spin.setRange(2, 6)
        self.layer_spin.setValue(2)
        self.layer_spin.setStyleSheet(input_style())
        self.layer_spin.valueChanged.connect(self.update_layers)
        control_layout.addWidget(self.layer_spin)

        control_layout.addSpacing(20)

        control_layout.addWidget(QLabel("全局密钥:"))
        self.global_key = QLineEdit()
        self.global_key.setStyleSheet(input_style())
        self.global_key.setPlaceholderText("中文/英文/数字（维吉尼亚/凯撒使用）")
        self.global_key.textChanged.connect(self.on_key_changed)
        control_layout.addWidget(self.global_key, 1)

        layout.addLayout(control_layout)

        # ===== 算法选择列表 =====
        self.layer_container = QWidget()
        self.layer_layout = QVBoxLayout(self.layer_container)
        self.layer_layout.setSpacing(4)
        layout.addWidget(QLabel("算法顺序（从上到下执行）:"))
        layout.addWidget(self.layer_container)

        # ===== 内容输入 =====
        self.content_input = QTextEdit()
        self.content_input.setStyleSheet(input_style())
        self.content_input.setMaximumHeight(120)
        self.content_input.setPlaceholderText("输入要加密/解密的内容")
        layout.addWidget(QLabel("内容:"))
        layout.addWidget(self.content_input)

        # ===== 按钮 =====
        btn_layout = QHBoxLayout()
        self.encrypt_btn = FlatButton("🔒 加密", Theme.NEON_GREEN)
        self.encrypt_btn.clicked.connect(self.encrypt)
        btn_layout.addWidget(self.encrypt_btn)

        self.decrypt_btn = FlatButton("🔓 解密", Theme.NEON_CYAN)
        self.decrypt_btn.clicked.connect(self.decrypt)
        btn_layout.addWidget(self.decrypt_btn)

        self.clear_btn = FlatButton("🗑️ 清空", Theme.NEON_ORANGE)
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.clear_btn)

        self.copy_btn = FlatButton("📋 复制结果", Theme.NEON_PINK)
        self.copy_btn.clicked.connect(self.copy_result)
        btn_layout.addWidget(self.copy_btn)

        self.copy_all_btn = FlatButton("📋 复制完整日志", Theme.NEON_BLUE)
        self.copy_all_btn.clicked.connect(self.copy_full_log)
        btn_layout.addWidget(self.copy_all_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # ===== 输出 =====
        self.result_output = QTextEdit()
        self.result_output.setStyleSheet(input_style())
        self.result_output.setMaximumHeight(120)
        self.result_output.setReadOnly(True)
        layout.addWidget(QLabel("结果:"))
        layout.addWidget(self.result_output)

        # ===== 调试日志 =====
        self.debug_output = QTextEdit()
        self.debug_output.setStyleSheet(input_style())
        self.debug_output.setMaximumHeight(100)
        self.debug_output.setReadOnly(True)
        self.debug_output.setPlaceholderText("加密/解密每一步的中间结果")
        layout.addWidget(QLabel("🔍 调试日志:"))
        layout.addWidget(self.debug_output)

        # ===== 状态 + 提示 =====
        self.status_label = QLabel("就绪 · 维吉尼亚/凯撒需要密钥")
        self.status_label.setStyleSheet(f"color: {Theme.TEXT_DIM}; font-size: 10pt;")
        layout.addWidget(self.status_label)

        hint = QLabel("💡 第一层建议用维吉尼亚 · 解密自动反向执行 · 共7种稳定算法")
        hint.setStyleSheet(f"color: {Theme.TEXT_DIM}; font-size: 9pt;")
        layout.addWidget(hint)

        self.layer_widgets = []
        self.last_log = []
        self.update_layers()

    def on_key_changed(self, text):
        key = text.strip()
        if key:
            self.status_label.setText(f"🔑 密钥已输入: {key[:10]}{'...' if len(key) > 10 else ''}")
        else:
            self.status_label.setText("⚠️ 请输入密钥（维吉尼亚/凯撒需要密钥）")

    def update_layers(self):
        for w in self.layer_widgets:
            self.layer_layout.removeWidget(w)
            w.deleteLater()
        self.layer_widgets.clear()

        count = self.layer_spin.value()
        algos = list(ALGORITHMS.keys())

        for i in range(count):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)

            label = QLabel(f"第{i+1}层:")
            label.setStyleSheet(f"color: {Theme.TEXT}; font-size: 10pt;")
            label.setFixedWidth(50)
            row_layout.addWidget(label)

            combo = QComboBox()
            combo.addItems(algos)
            combo.setStyleSheet(input_style())
            combo.currentTextChanged.connect(lambda text, idx=i: self.check_key_need(text, idx))
            row_layout.addWidget(combo, 1)

            info_label = QLabel("")
            info_label.setStyleSheet(f"color: {Theme.TEXT_DIM}; font-size: 8pt;")
            info_label.setFixedWidth(120)
            combo.currentTextChanged.connect(lambda text, lbl=info_label: self.update_info(text, lbl))
            row_layout.addWidget(info_label)

            self.layer_layout.addWidget(row)
            self.layer_widgets.append(row)
            self.update_info(combo.currentText(), info_label)

    def check_key_need(self, text, idx):
        if text in ALGORITHMS and ALGORITHMS[text]["need_key"]:
            if not self.global_key.text().strip():
                self.status_label.setText(f"⚠️ 第{idx+1}层 [{text}] 需要密钥，请先输入全局密钥")

    def update_info(self, text, label):
        if text in ALGORITHMS:
            desc = ALGORITHMS[text]["desc"]
            need_key = ALGORITHMS[text]["need_key"]
            label.setText(f"{desc}" + (" 🔑" if need_key else ""))

    def get_layer_config(self) -> List[Dict]:
        configs = []
        for row in self.layer_widgets:
            combo = row.findChild(QComboBox)
            if combo:
                algo_name = combo.currentText()
                if algo_name in ALGORITHMS:
                    configs.append({
                        "name": algo_name,
                        "encrypt": ALGORITHMS[algo_name]["encrypt"],
                        "decrypt": ALGORITHMS[algo_name]["decrypt"],
                        "need_key": ALGORITHMS[algo_name]["need_key"],
                    })
        return configs

    def get_layer_names(self) -> List[str]:
        names = []
        for row in self.layer_widgets:
            combo = row.findChild(QComboBox)
            if combo:
                names.append(combo.currentText())
        return names

    def log_debug(self, msg: str):
        self.last_log.append(msg)
        self.debug_output.append(msg)
        self.debug_output.verticalScrollBar().setValue(
            self.debug_output.verticalScrollBar().maximum()
        )

    def clear_debug(self):
        self.last_log.clear()
        self.debug_output.clear()

    def encrypt(self):
        text = self.content_input.toPlainText()
        if not text:
            self.result_output.setText("⚠️ 请先输入内容")
            return

        key = self.global_key.text().strip()
        configs = self.get_layer_config()

        if len(configs) < 2:
            self.result_output.setText("⚠️ 至少需要2层加密")
            return

        # 检查需要密钥的算法
        for i, cfg in enumerate(configs):
            if cfg["need_key"] and not key:
                self.result_output.setText(f"⚠️ 第{i+1}层 [{cfg['name']}] 需要密钥，请先输入全局密钥")
                self.status_label.setText("❌ 密钥缺失")
                return

        self.clear_debug()
        self.log_debug("🔒 ===== 开始加密 =====")
        self.log_debug(f"明文: {text[:50]}{'...' if len(text) > 50 else ''}")
        self.log_debug(f"密钥: {key if key else '(无)'}")

        result = text
        for i, cfg in enumerate(configs):
            try:
                if cfg["need_key"]:
                    result = cfg["encrypt"](result, key)
                else:
                    result = cfg["encrypt"](result)
                self.log_debug(f"第{i+1}层 [{cfg['name']}] → {result[:50]}{'...' if len(result) > 50 else ''}")
            except ValueError as e:
                self.result_output.setText(f"❌ 第{i+1}层 [{cfg['name']}] {e}")
                self.log_debug(f"❌ 加密失败: {e}")
                return
            except Exception as e:
                self.result_output.setText(f"❌ 第{i+1}层 [{cfg['name']}] 加密失败: {e}")
                self.log_debug(f"❌ 加密失败: {e}")
                return

        self.result_output.setText(result)
        self.status_label.setText(f"✅ 加密完成 · {len(configs)}层")
        self.log_debug(f"✅ 密文: {result[:50]}{'...' if len(result) > 50 else ''}")
        self.log_debug("🔒 ===== 加密完成 =====")

    def decrypt(self):
        text = self.content_input.toPlainText()
        if not text:
            self.result_output.setText("⚠️ 请先输入内容")
            return

        key = self.global_key.text().strip()
        configs = self.get_layer_config()

        if len(configs) < 2:
            self.result_output.setText("⚠️ 至少需要2层加密")
            return

        # 检查需要密钥的算法
        for i, cfg in enumerate(configs):
            if cfg["need_key"] and not key:
                self.result_output.setText(f"⚠️ 第{i+1}层 [{cfg['name']}] 需要密钥，请先输入全局密钥")
                self.status_label.setText("❌ 密钥缺失")
                return

        self.clear_debug()
        self.log_debug("🔓 ===== 开始解密 (反向执行) =====")
        self.log_debug(f"密文: {text[:50]}{'...' if len(text) > 50 else ''}")
        self.log_debug(f"密钥: {key if key else '(无)'}")

        result = text
        for i in range(len(configs) - 1, -1, -1):
            cfg = configs[i]
            try:
                if cfg["need_key"]:
                    result = cfg["decrypt"](result, key)
                else:
                    result = cfg["decrypt"](result)
                self.log_debug(f"第{i+1}层 [{cfg['name']}] → {result[:50]}{'...' if len(result) > 50 else ''}")
            except ValueError as e:
                self.result_output.setText(f"❌ 第{i+1}层 [{cfg['name']}] {e}")
                self.log_debug(f"❌ 解密失败: {e}")
                return
            except Exception as e:
                self.result_output.setText(f"❌ 第{i+1}层 [{cfg['name']}] 解密失败: {e}")
                self.log_debug(f"❌ 解密失败: {e}")
                return

        self.result_output.setText(result)
        self.status_label.setText(f"✅ 解密完成 · {len(configs)}层（反向）")
        self.log_debug(f"✅ 明文: {result[:50]}{'...' if len(result) > 50 else ''}")
        self.log_debug("🔓 ===== 解密完成 =====")

    def export_config(self):
        layer_names = self.get_layer_names()
        key = self.global_key.text().strip()
        layer_count = self.layer_spin.value()

        if not layer_names:
            self.status_label.setText("❌ 没有可导出的配置")
            return

        b64_str = ConfigManager.export_config(layer_names, key, layer_count)

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出配置",
            "cipher_config.txt",
            "配置文件 (*.txt);;所有文件 (*)"
        )

        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(b64_str)
            self.status_label.setText(f"✅ 配置已导出到: {os.path.basename(file_path)}")
            QMessageBox.information(self, "导出成功",
                f"配置已导出到:\n{file_path}\n\nBase64 配置:\n{b64_str[:50]}...")

    def import_config(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入配置",
            "",
            "配置文件 (*.txt);;所有文件 (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                b64_str = f.read().strip()
            self.apply_config(b64_str)
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"读取文件失败: {e}")

    def import_from_clipboard(self):
        clipboard = QApplication.clipboard().text().strip()
        if not clipboard:
            self.status_label.setText("❌ 剪贴板为空")
            return
        self.apply_config(clipboard)

    def apply_config(self, b64_str: str):
        config = ConfigManager.import_config(b64_str)

        if "error" in config:
            QMessageBox.critical(self, "导入失败", f"配置解析失败:\n{config['error']}")
            self.status_label.setText("❌ 配置解析失败")
            return

        layer_count = config.get("layer_count", 2)
        self.layer_spin.setValue(layer_count)

        key = config.get("key", "")
        self.global_key.setText(key)

        layers = config.get("layers", [])
        algos = list(ALGORITHMS.keys())

        QApplication.processEvents()
        self.update_layers()
        QApplication.processEvents()

        for i, layer_name in enumerate(layers):
            if i < len(self.layer_widgets):
                combo = self.layer_widgets[i].findChild(QComboBox)
                if combo and layer_name in algos:
                    combo.setCurrentText(layer_name)

        self.status_label.setText(f"✅ 配置已导入 · {layer_count}层 · 密钥: {key[:10] if key else '无'}")
        QMessageBox.information(self, "导入成功",
            f"配置已应用:\n\n层数: {layer_count}\n密钥: {key}\n算法: {' → '.join(layers)}")

    def clear_all(self):
        self.content_input.clear()
        self.result_output.clear()
        self.global_key.clear()
        self.clear_debug()
        self.status_label.setText("🗑️ 已清空")

    def copy_result(self):
        text = self.result_output.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_label.setText("📋 已复制结果到剪贴板")

    def copy_full_log(self):
        log_text = self.debug_output.toPlainText()
        if log_text:
            QApplication.clipboard().setText(log_text)
            self.status_label.setText("📋 已复制完整日志到剪贴板")


# ==================== 启动 ====================
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()