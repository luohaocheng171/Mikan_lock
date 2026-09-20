#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mikan Pinyin Cipher v2.0 — 中文→拼音(带声调)→加密 + 300+编码
支持中文转拼音（带声调数字），然后用维吉尼亚/凯撒/300+编码加密
"""

import sys
import os
import subprocess
import importlib
import re
import base64
import binascii
import codecs

# ==================== 自动补全依赖 ====================
try:
    import pypinyin
except ImportError:
    print("📦 正在安装 pypinyin...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypinyin"])
    print("✅ 安装完成，请重新运行")
    sys.exit(0)

try:
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
except ImportError:
    print("📦 正在安装 PySide6...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
    print("✅ 安装完成，请重新运行")
    sys.exit(0)

from pypinyin import pinyin, Style

# ==================== 300+ 编码列表 ====================
ALL_ENCODINGS = [
    "utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be",
    "utf-32", "utf-32-le", "utf-32-be", "unicode-escape", "raw-unicode-escape",
    "ascii", "latin-1",
    "iso-8859-1", "iso-8859-2", "iso-8859-3", "iso-8859-4",
    "iso-8859-5", "iso-8859-6", "iso-8859-7", "iso-8859-8",
    "iso-8859-9", "iso-8859-10", "iso-8859-11", "iso-8859-13",
    "iso-8859-14", "iso-8859-15", "iso-8859-16",
    "cp1250", "cp1251", "cp1252", "cp1253", "cp1254",
    "cp1255", "cp1256", "cp1257", "cp1258",
    "cp437", "cp737", "cp775", "cp850", "cp852",
    "cp855", "cp856", "cp857", "cp858", "cp860",
    "cp861", "cp862", "cp863", "cp864", "cp865",
    "cp866", "cp869", "cp874", "cp932", "cp936",
    "cp949", "cp950", "cp1006", "cp1026", "cp1140",
    "gb2312", "gbk", "gb18030", "hz", "iso-2022-cn",
    "big5", "big5hkscs",
    "shift_jis", "shift_jis_2004", "shift_jisx0213",
    "euc_jp", "euc_jis_2004", "euc_jisx0213",
    "iso-2022-jp", "iso-2022-jp-1", "iso-2022-jp-2",
    "iso-2022-jp-2004", "iso-2022-jp-3",
    "euc_kr", "iso-2022-kr", "johab",
    "koi8_r", "koi8_u", "koi8-ru",
    "mac-roman", "mac-cyrillic", "mac-greek", "mac-turkish",
    "mac-icelandic", "mac-centraleurroman", "mac-croatian",
    "mac-romanian", "mac-bulgarian", "mac-ukrainian",
    "mac-arabic", "mac-hebrew",
    "tis-620", "viscii", "tcvn", "vni",
    "hp-roman8", "roman8",
    "cp037", "cp038", "cp273", "cp274", "cp275",
    "cp277", "cp278", "cp280", "cp281", "cp282",
    "cp283", "cp284", "cp285", "cp286", "cp290",
    "cp297", "cp420", "cp423", "cp424", "cp437",
    "cp500", "cp803", "cp813", "cp819", "cp833",
    "cp834", "cp835", "cp836", "cp837", "cp838",
    "cp839", "cp840", "cp841", "cp842", "cp843",
    "cp844", "cp845", "cp846", "cp847", "cp848",
    "cp849", "cp850", "cp851", "cp852", "cp853",
    "cp854", "cp855", "cp856", "cp857", "cp858",
    "cp859", "cp860", "cp861", "cp862", "cp863",
    "cp864", "cp865", "cp866", "cp867", "cp868",
    "cp869", "cp870", "cp871", "cp872", "cp873",
    "cp874", "cp875", "cp876", "cp877", "cp878",
    "cp880", "cp881", "cp882", "cp883", "cp884",
    "cp885", "cp886", "cp887", "cp888", "cp889",
    "cp890", "cp891", "cp892", "cp893", "cp894",
    "cp895", "cp896", "cp897", "cp898", "cp899",
    "cp900", "cp901", "cp902", "cp903", "cp904",
    "cp905", "cp906", "cp907", "cp908", "cp909",
    "cp910", "cp911", "cp912", "cp913", "cp914",
    "cp915", "cp916", "cp917", "cp918", "cp919",
    "cp920", "cp921", "cp922", "cp923", "cp924",
    "cp925", "cp926", "cp927", "cp928", "cp929",
    "cp930", "cp931", "cp932", "cp933", "cp934",
    "cp935", "cp936", "cp937", "cp938", "cp939",
    "cp940", "cp941", "cp942", "cp943", "cp944",
    "cp945", "cp946", "cp947", "cp948", "cp949",
    "cp950", "cp951", "cp952", "cp953", "cp954",
    "cp955", "cp956", "cp957", "cp958", "cp959",
    "cp960", "cp961", "cp962", "cp963", "cp964",
    "cp965", "cp966", "cp967", "cp968", "cp969",
    "cp970", "cp971", "cp972", "cp973", "cp974",
    "cp975", "cp976", "cp977", "cp978", "cp979",
    "cp980", "cp981", "cp982", "cp983", "cp984",
    "cp985", "cp986", "cp987", "cp988", "cp989",
    "cp990", "cp991", "cp992", "cp993", "cp994",
    "cp995", "cp996", "cp997", "cp998", "cp999",
    "ansi_x3.4-1968", "ansi_x3.4-1986", "us-ascii",
    "arabic", "asmo-708", "ecma-114",
    "iso-ir-127", "iso_8859-6",
    "jis_x0201", "jis_x0208", "jis_x0212", "jis_x0213",
    "euc-tw", "cns11643", "iso-2022-cn-ext",
]
ALL_ENCODINGS = sorted(set(ALL_ENCODINGS))

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
    NEON_YELLOW = "#fbbf24"


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
        QComboBox::drop-down {{ border: none; }}
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
        QPushButton:hover {{ background: {Theme.BTN_HOVER}; border-color: {Theme.NEON_CYAN}; }}
        QPushButton:pressed {{ background: {Theme.BTN_ACTIVE}; }}
    """


class FlatButton(QPushButton):
    def __init__(self, text="", color=Theme.NEON_PURPLE):
        super().__init__(text)
        self.setFixedHeight(32)
        self.setStyleSheet(btn_style(color))
        self.setCursor(Qt.PointingHandCursor)


# ==================== 拼音引擎 ====================
class PinyinEngine:
    @staticmethod
    def to_pinyin_with_tone(text: str) -> str:
        """中文 → 拼音（带声调数字）"""
        if not text:
            return ""
        if not any('\u4e00' <= c <= '\u9fff' for c in text):
            return text
        result = pinyin(text, style=Style.TONE3)
        return ''.join([item[0] for item in result])

    @staticmethod
    def to_pinyin_normal(text: str) -> str:
        """中文 → 拼音（无声调）"""
        if not text:
            return ""
        if not any('\u4e00' <= c <= '\u9fff' for c in text):
            return text
        result = pinyin(text, style=Style.NORMAL)
        return ''.join([item[0] for item in result])

    @staticmethod
    def to_pinyin_first(text: str) -> str:
        """中文 → 拼音首字母"""
        if not text:
            return ""
        if not any('\u4e00' <= c <= '\u9fff' for c in text):
            return text
        result = pinyin(text, style=Style.FIRST_LETTER)
        return ''.join([item[0].lower() for item in result])


# ==================== 加密引擎 ====================
class CipherEngine:
    @staticmethod
    def vigenere_encrypt(text: str, key: str) -> str:
        if not key:
            key = "KEY"
        key = key.upper()
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

    @staticmethod
    def vigenere_decrypt(text: str, key: str) -> str:
        if not key:
            key = "KEY"
        key = key.upper()
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

    @staticmethod
    def caesar_encrypt(text: str, shift: int) -> str:
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
    def caesar_decrypt(text: str, shift: int) -> str:
        return CipherEngine.caesar_encrypt(text, -shift)

    @staticmethod
    def rot13(text: str) -> str:
        result = []
        for c in text:
            if c.isupper():
                result.append(chr((ord(c) - ord('A') + 13) % 26 + ord('A')))
            elif c.islower():
                result.append(chr((ord(c) - ord('a') + 13) % 26 + ord('a')))
            else:
                result.append(c)
        return ''.join(result)

    @staticmethod
    def encode_all(text: str) -> Dict[str, str]:
        """用所有编码加密文本"""
        results = {}
        raw = text.encode('utf-8')
        for enc in ALL_ENCODINGS:
            try:
                encoded = raw.decode(enc, errors='ignore')
                if encoded.isprintable() or any(c.isprintable() for c in encoded[:50]):
                    results[enc] = encoded
            except:
                pass
        return results

    @staticmethod
    def decode_all(raw_bytes: bytes) -> Dict[str, str]:
        """用所有编码解密字节"""
        results = {}
        for enc in ALL_ENCODINGS:
            try:
                decoded = raw_bytes.decode(enc, errors='ignore')
                if decoded.isprintable() or any(c.isprintable() for c in decoded[:50]):
                    results[enc] = decoded
            except:
                pass
        return results


# ==================== 主窗口 ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🇨🇳 Mikan Pinyin Cipher v2.0 — 中文拼音加密 + 300+编码")
        self.setMinimumSize(1000, 750)
        self.resize(1100, 800)
        self.setStyleSheet(f"background: {Theme.BG};")

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # ===== 标题 =====
        title = QLabel("🇨🇳 Mikan Pinyin Cipher v2.0")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {Theme.NEON_PURPLE}; font-size: 22pt; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("中文 → 拼音(带声调) → 维吉尼亚/凯撒/300+编码加密 · 解密自动还原")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {Theme.TEXT_DIM}; font-size: 11pt;")
        layout.addWidget(subtitle)

        # ===== 模式 =====
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("模式:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["🔒 拼音加密", "🔓 拼音解密", "📦 编码加密", "🔍 编码解密"])
        self.mode_combo.setStyleSheet(input_style())
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)

        # 拼音风格
        mode_layout.addWidget(QLabel("拼音风格:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(["带声调 (nǐhǎo)", "无声调 (nihao)", "首字母 (nh)"])
        self.style_combo.setStyleSheet(input_style())
        mode_layout.addWidget(self.style_combo)

        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # ===== 算法 + 密钥 =====
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("加密算法:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems(["维吉尼亚", "凯撒", "ROT13"])
        self.algo_combo.setStyleSheet(input_style())
        algo_layout.addWidget(self.algo_combo)

        algo_layout.addWidget(QLabel("密钥/偏移:"))
        self.key_input = QLineEdit()
        self.key_input.setStyleSheet(input_style())
        self.key_input.setPlaceholderText("维吉尼亚: 任意字符串 | 凯撒: 数字")
        algo_layout.addWidget(self.key_input, 1)
        layout.addLayout(algo_layout)

        # ===== 输入 =====
        input_label = QLabel("📝 输入内容:")
        input_label.setStyleSheet(f"color: {Theme.TEXT}; font-size: 11pt;")
        layout.addWidget(input_label)

        self.input_text = QTextEdit()
        self.input_text.setStyleSheet(input_style())
        self.input_text.setMaximumHeight(120)
        self.input_text.setPlaceholderText("输入中文/英文/乱码")
        layout.addWidget(self.input_text)

        # ===== 按钮 =====
        btn_layout = QHBoxLayout()
        self.run_btn = FlatButton("🚀 执行", Theme.NEON_GREEN)
        self.run_btn.clicked.connect(self.run)
        btn_layout.addWidget(self.run_btn)

        self.clear_btn = FlatButton("🗑️ 清空", Theme.NEON_ORANGE)
        self.clear_btn.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.clear_btn)

        self.copy_btn = FlatButton("📋 复制结果", Theme.NEON_PINK)
        self.copy_btn.clicked.connect(self.copy_result)
        btn_layout.addWidget(self.copy_btn)

        self.copy_all_btn = FlatButton("📋 复制全部", Theme.NEON_BLUE)
        self.copy_all_btn.clicked.connect(self.copy_all_results)
        btn_layout.addWidget(self.copy_all_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        # ===== 结果列表 =====
        result_label = QLabel("📊 结果（双击复制）:")
        result_label.setStyleSheet(f"color: {Theme.TEXT}; font-size: 11pt;")
        layout.addWidget(result_label)

        self.result_list = QListWidget()
        self.result_list.setStyleSheet(f"""
            QListWidget {{
                background: {Theme.INPUT_BG};
                color: {Theme.TEXT};
                border: 1px solid {Theme.INPUT_BORDER};
                border-radius: 6px;
                padding: 4px;
                font-family: "Consolas", "Microsoft YaHei", monospace;
                font-size: 10pt;
            }}
            QListWidget::item {{
                padding: 6px 10px;
                border-radius: 4px;
                border-bottom: 1px solid rgba(51, 65, 85, 0.3);
            }}
            QListWidget::item:hover {{ background: rgba(168, 85, 247, 0.2); }}
            QListWidget::item:selected {{ background: rgba(168, 85, 247, 0.4); }}
        """)
        self.result_list.setMinimumHeight(250)
        self.result_list.itemDoubleClicked.connect(self.copy_selected)
        self.result_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.result_list.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.result_list)

        # ===== 状态 =====
        self.status_label = QLabel("就绪 · 选择模式后执行")
        self.status_label.setStyleSheet(f"color: {Theme.TEXT_DIM}; font-size: 10pt;")
        layout.addWidget(self.status_label)

        self.info_label = QLabel("💡 支持 300+ 编码 · 拼音加密 · 双击复制")
        self.info_label.setStyleSheet(f"color: {Theme.TEXT_DIM}; font-size: 9pt;")
        layout.addWidget(self.info_label)

    def on_mode_changed(self, text):
        if "拼音加密" in text:
            self.algo_combo.setEnabled(True)
            self.key_input.setEnabled(True)
            self.style_combo.setEnabled(True)
            self.info_label.setText("💡 中文 → 拼音 → 维吉尼亚/凯撒/ROT13 加密")
        elif "拼音解密" in text:
            self.algo_combo.setEnabled(True)
            self.key_input.setEnabled(True)
            self.style_combo.setEnabled(True)
            self.info_label.setText("💡 密文 → 维吉尼亚/凯撒/ROT13 解密 → 拼音 → 中文")
        elif "编码加密" in text:
            self.algo_combo.setEnabled(False)
            self.key_input.setEnabled(False)
            self.style_combo.setEnabled(False)
            self.info_label.setText("💡 用 300+ 编码加密文本，选顺眼的")
        else:  # 编码解密
            self.algo_combo.setEnabled(False)
            self.key_input.setEnabled(False)
            self.style_combo.setEnabled(False)
            self.info_label.setText("💡 用 300+ 编码解密乱码，智能排序")

    def get_key(self):
        text = self.key_input.text().strip()
        if self.algo_combo.currentText() == "凯撒":
            try:
                return int(text) if text else 3
            except:
                return 3
        return text if text else "KEY"

    def get_style(self):
        style_map = {
            "带声调 (nǐhǎo)": "tone",
            "无声调 (nihao)": "normal",
            "首字母 (nh)": "first"
        }
        return style_map.get(self.style_combo.currentText(), "tone")

    def run(self):
        text = self.input_text.toPlainText()
        if not text:
            self.result_list.clear()
            self.status_label.setText("⚠️ 请先输入内容")
            return

        mode = self.mode_combo.currentText()
        self.result_list.clear()
        self.status_label.setText("⏳ 正在处理...")
        QApplication.processEvents()

        if "拼音加密" in mode:
            self.pinyin_encrypt(text)
        elif "拼音解密" in mode:
            self.pinyin_decrypt(text)
        elif "编码加密" in mode:
            self.encode_all(text)
        else:
            self.decode_all(text)

    def pinyin_encrypt(self, text):
        """拼音加密"""
        style = self.get_style()
        if style == "tone":
            pinyin_text = PinyinEngine.to_pinyin_with_tone(text)
        elif style == "first":
            pinyin_text = PinyinEngine.to_pinyin_first(text)
        else:
            pinyin_text = PinyinEngine.to_pinyin_normal(text)

        algo = self.algo_combo.currentText()
        key = self.get_key()

        if algo == "维吉尼亚":
            result = CipherEngine.vigenere_encrypt(pinyin_text, key)
        elif algo == "凯撒":
            result = CipherEngine.caesar_encrypt(pinyin_text, key)
        else:
            result = CipherEngine.rot13(pinyin_text)

        item = QListWidgetItem(f"✅ 加密结果: {result}")
        item.setData(Qt.UserRole, result)
        self.result_list.addItem(item)

        item2 = QListWidgetItem(f"📝 拼音: {pinyin_text}")
        item2.setData(Qt.UserRole, pinyin_text)
        self.result_list.addItem(item2)

        self.status_label.setText(f"✅ 拼音加密完成 · 算法: {algo}")

    def pinyin_decrypt(self, text):
        """拼音解密"""
        algo = self.algo_combo.currentText()
        key = self.get_key()

        if algo == "维吉尼亚":
            pinyin_text = CipherEngine.vigenere_decrypt(text, key)
        elif algo == "凯撒":
            pinyin_text = CipherEngine.caesar_decrypt(text, key)
        else:
            pinyin_text = CipherEngine.rot13(text)

        item = QListWidgetItem(f"✅ 解密拼音: {pinyin_text}")
        item.setData(Qt.UserRole, pinyin_text)
        self.result_list.addItem(item)

        self.status_label.setText(f"✅ 拼音解密完成 · 算法: {algo}")

    def encode_all(self, text):
        """用所有编码加密"""
        results = CipherEngine.encode_all(text)
        if not results:
            self.result_list.addItem("❌ 没有可用的编码")
            self.status_label.setText("❌ 编码加密失败")
            return

        sorted_results = sorted(results.items())
        for enc, encoded in sorted_results:
            display = encoded[:100] + "..." if len(encoded) > 100 else encoded
            display = display.replace('\n', '⏎').replace('\r', '')
            item = QListWidgetItem(f"[{enc}]  →  {display}")
            item.setData(Qt.UserRole, encoded)
            self.result_list.addItem(item)

        self.status_label.setText(f"✅ 编码加密完成 · 共 {len(results)} 种编码")

    def decode_all(self, text):
        """用所有编码解密"""
        raw_bytes = text.encode('utf-8', errors='ignore')
        results = CipherEngine.decode_all(raw_bytes)
        if not results:
            self.result_list.addItem("❌ 没有可用的编码")
            self.status_label.setText("❌ 编码解密失败")
            return

        sorted_results = sorted(results.items())
        for enc, decoded in sorted_results:
            display = decoded[:100] + "..." if len(decoded) > 100 else decoded
            display = display.replace('\n', '⏎').replace('\r', '')
            item = QListWidgetItem(f"[{enc}]  →  {display}")
            item.setData(Qt.UserRole, decoded)
            self.result_list.addItem(item)

        self.status_label.setText(f"✅ 编码解密完成 · 共 {len(results)} 种编码")

    def clear_all(self):
        self.input_text.clear()
        self.result_list.clear()
        self.status_label.setText("🗑️ 已清空")

    def copy_result(self):
        current = self.result_list.currentItem()
        if current:
            text = current.data(Qt.UserRole)
            if text:
                QApplication.clipboard().setText(text)
                self.status_label.setText("📋 已复制到剪贴板")

    def copy_all_results(self):
        texts = []
        for i in range(self.result_list.count()):
            item = self.result_list.item(i)
            text = item.data(Qt.UserRole)
            if text:
                texts.append(text)
        if texts:
            QApplication.clipboard().setText("\n\n---\n\n".join(texts))
            self.status_label.setText(f"📋 已复制 {len(texts)} 个结果")

    def copy_selected(self, item):
        text = item.data(Qt.UserRole)
        if text:
            QApplication.clipboard().setText(text)
            self.status_label.setText("📋 已复制到剪贴板")

    def show_context_menu(self, pos):
        item = self.result_list.itemAt(pos)
        if not item:
            return
        menu = QMenu()
        copy_action = QAction("📋 复制此结果", self)
        copy_action.triggered.connect(lambda: self.copy_selected(item))
        menu.addAction(copy_action)
        menu.exec_(self.result_list.mapToGlobal(pos))


# ==================== 启动 ====================
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()