#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MikanLock v3.0 - 专业加密/编码/哈希/破解工具箱
赛博风 · 全功能版
新增：进制转换 (二进制/八进制/十进制/十六进制/ASCII)
"""

import sys
import os
import subprocess
import importlib
import json
import threading
import time
import re
from datetime import datetime
from typing import List, Tuple, Dict, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import Counter
import hashlib
import base64
import binascii
import codecs
from urllib.parse import quote, unquote

# ==================== 自动补全依赖 ====================
REQUIRED_PACKAGES = {
    "PySide6": "PySide6",
    "cryptography": "cryptography",
    "chardet": "chardet",
    "bcrypt": "bcrypt",
    "pyjwt": "jwt",
}

def install_package(pkg: str):
    mirrors = [
        "https://pypi.tuna.tsinghua.edu.cn/simple",
        "https://mirrors.aliyun.com/pypi/simple/",
        "https://pypi.douban.com/simple/",
    ]
    for mirror in mirrors:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg, "-i", mirror],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            return True
        except:
            continue
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        return True
    except:
        return False

def ensure_dependencies():
    missing = []
    for pkg, import_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"📦 正在安装缺失的依赖: {', '.join(missing)}...")
        for pkg in missing:
            if install_package(pkg):
                print(f"✅ {pkg} 安装成功")
            else:
                print(f"❌ {pkg} 安装失败，请手动安装: pip install {pkg}")
                input("按 Enter 键退出...")
                sys.exit(1)
        print("✅ 所有依赖已安装完成")
        print("🔄 正在重启程序...")
        os.execv(sys.executable, [sys.executable] + sys.argv)

ensure_dependencies()

# ==================== 导入 ====================
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives import hmac
from cryptography.hazmat.backends import default_backend
import bcrypt
import jwt
import chardet

# ==================== 常量定义 ====================
# 摩斯密码表
MORSE_MAP = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....', '7': '--...',
    '8': '---..', '9': '----.', ' ': '/'
}
MORSE_REVERSE = {v: k for k, v in MORSE_MAP.items()}

# 键盘布局 - QWERTY
KEYBOARD_ROWS = [
    "1234567890",
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm"
]

# 键盘相邻键映射
KEYBOARD_NEIGHBORS = {}
for row_idx, row in enumerate(KEYBOARD_ROWS):
    for col_idx, char in enumerate(row):
        neighbors = []
        if col_idx > 0:
            neighbors.append(row[col_idx - 1])
        if col_idx < len(row) - 1:
            neighbors.append(row[col_idx + 1])
        if row_idx > 0 and col_idx < len(KEYBOARD_ROWS[row_idx - 1]):
            neighbors.append(KEYBOARD_ROWS[row_idx - 1][col_idx])
        if row_idx < len(KEYBOARD_ROWS) - 1 and col_idx < len(KEYBOARD_ROWS[row_idx + 1]):
            neighbors.append(KEYBOARD_ROWS[row_idx + 1][col_idx])
        KEYBOARD_NEIGHBORS[char] = neighbors

# 键盘坐标
KEYBOARD_COORDS = {}
for row_idx, row in enumerate(KEYBOARD_ROWS):
    for col_idx, char in enumerate(row):
        KEYBOARD_COORDS[char] = (row_idx, col_idx)

# ==================== 赛博风主题 ====================
class CyberTheme:
    BG = "#0f0f1a"
    BG2 = "#18182a"
    BG3 = "#222244"
    BG4 = "#2a2a4a"
    
    NEON_PURPLE = "#a855f7"
    NEON_BLUE = "#3b82f6"
    NEON_CYAN = "#22d3ee"
    NEON_PINK = "#ec4899"
    NEON_GREEN = "#34d399"
    NEON_ORANGE = "#f59e0b"
    NEON_RED = "#ef4444"
    NEON_YELLOW = "#eab308"
    
    TEXT = "#ffffff"
    TEXT_DIM = "#94a3b8"
    
    BORDER = "#334155"
    BORDER_LIGHT = "#475569"
    
    BTN_BG = "#1e1b4b"
    BTN_HOVER = "#312e81"
    BTN_ACTIVE = "#4f46e5"
    
    INPUT_BG = "#1a1a2e"
    INPUT_BORDER = "#334155"

# ==================== 样式函数 ====================
def btn_style(color):
    return f"""
        QPushButton {{
            background: {CyberTheme.BTN_BG};
            color: {CyberTheme.TEXT};
            border: 1px solid {color};
            border-radius: 6px;
            padding: 6px 14px;
            font-size: 9pt;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background: {CyberTheme.BTN_HOVER};
            border-color: {CyberTheme.NEON_CYAN};
        }}
        QPushButton:pressed {{
            background: {CyberTheme.BTN_ACTIVE};
        }}
        QPushButton:disabled {{
            border-color: {CyberTheme.TEXT_DIM};
            color: {CyberTheme.TEXT_DIM};
        }}
    """

def input_style():
    return f"""
        QLineEdit, QTextEdit, QSpinBox, QComboBox {{
            background: {CyberTheme.INPUT_BG};
            color: {CyberTheme.TEXT};
            border: 1px solid {CyberTheme.INPUT_BORDER};
            border-radius: 6px;
            padding: 6px 10px;
            font-family: "Consolas", monospace;
            font-size: 10pt;
        }}
        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
            border-color: {CyberTheme.NEON_PURPLE};
        }}
        QTextEdit {{
            background: {CyberTheme.INPUT_BG};
            color: {CyberTheme.TEXT};
            border: 1px solid {CyberTheme.INPUT_BORDER};
            border-radius: 6px;
            padding: 8px;
        }}
        QSpinBox::up-button, QSpinBox::down-button {{
            background: {CyberTheme.BTN_BG};
            border: none;
            width: 16px;
        }}
        QComboBox::drop-down {{
            background: {CyberTheme.BTN_BG};
            border: none;
            width: 20px;
        }}
        QComboBox QAbstractItemView {{
            background: {CyberTheme.INPUT_BG};
            color: {CyberTheme.TEXT};
            border: 1px solid {CyberTheme.BORDER};
        }}
        QProgressBar {{
            background: {CyberTheme.INPUT_BG};
            border: 1px solid {CyberTheme.BORDER};
            border-radius: 4px;
            text-align: center;
            color: {CyberTheme.TEXT};
        }}
        QProgressBar::chunk {{
            background: {CyberTheme.NEON_PURPLE};
            border-radius: 4px;
        }}
    """

# ==================== 自定义组件 ====================
class FlatButton(QPushButton):
    def __init__(self, text="", parent=None, color=CyberTheme.NEON_PURPLE):
        super().__init__(text, parent)
        self.color = color
        self.setFixedHeight(32)
        self.setStyleSheet(btn_style(color))
        self.setCursor(Qt.PointingHandCursor)

class CyberGroupBox(QGroupBox):
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(f"""
            QGroupBox {{
                color: {CyberTheme.TEXT};
                border: 1px solid {CyberTheme.BORDER};
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
            }}
        """)

# ==================== 核心引擎 ====================
class CryptEngine:
    # ---------- 进制转换 ----------
    @staticmethod
    def bin_to_dec(binary: str) -> str:
        """二进制转十进制"""
        try:
            return str(int(binary, 2))
        except:
            return "❌ 无效的二进制数"
    
    @staticmethod
    def bin_to_hex(binary: str) -> str:
        """二进制转十六进制"""
        try:
            return hex(int(binary, 2))[2:].upper()
        except:
            return "❌ 无效的二进制数"
    
    @staticmethod
    def bin_to_oct(binary: str) -> str:
        """二进制转八进制"""
        try:
            return oct(int(binary, 2))[2:]
        except:
            return "❌ 无效的二进制数"
    
    @staticmethod
    def dec_to_bin(decimal: str) -> str:
        """十进制转二进制"""
        try:
            return bin(int(decimal))[2:]
        except:
            return "❌ 无效的十进制数"
    
    @staticmethod
    def dec_to_hex(decimal: str) -> str:
        """十进制转十六进制"""
        try:
            return hex(int(decimal))[2:].upper()
        except:
            return "❌ 无效的十进制数"
    
    @staticmethod
    def dec_to_oct(decimal: str) -> str:
        """十进制转八进制"""
        try:
            return oct(int(decimal))[2:]
        except:
            return "❌ 无效的十进制数"
    
    @staticmethod
    def hex_to_bin(hex_str: str) -> str:
        """十六进制转二进制"""
        try:
            # 移除0x前缀
            hex_str = hex_str.replace('0x', '').replace('0X', '')
            return bin(int(hex_str, 16))[2:].zfill(len(hex_str) * 4)
        except:
            return "❌ 无效的十六进制数"
    
    @staticmethod
    def hex_to_dec(hex_str: str) -> str:
        """十六进制转十进制"""
        try:
            hex_str = hex_str.replace('0x', '').replace('0X', '')
            return str(int(hex_str, 16))
        except:
            return "❌ 无效的十六进制数"
    
    @staticmethod
    def hex_to_oct(hex_str: str) -> str:
        """十六进制转八进制"""
        try:
            hex_str = hex_str.replace('0x', '').replace('0X', '')
            return oct(int(hex_str, 16))[2:]
        except:
            return "❌ 无效的十六进制数"
    
    @staticmethod
    def oct_to_bin(octal: str) -> str:
        """八进制转二进制"""
        try:
            return bin(int(octal, 8))[2:]
        except:
            return "❌ 无效的八进制数"
    
    @staticmethod
    def oct_to_dec(octal: str) -> str:
        """八进制转十进制"""
        try:
            return str(int(octal, 8))
        except:
            return "❌ 无效的八进制数"
    
    @staticmethod
    def oct_to_hex(octal: str) -> str:
        """八进制转十六进制"""
        try:
            return hex(int(octal, 8))[2:].upper()
        except:
            return "❌ 无效的八进制数"
    
    @staticmethod
    def char_to_hex(char: str) -> str:
        """字符转十六进制 (ASCII)"""
        try:
            return hex(ord(char))[2:].upper().zfill(2)
        except:
            return "❌ 无效的字符"
    
    @staticmethod
    def char_to_bin(char: str) -> str:
        """字符转二进制 (ASCII)"""
        try:
            return bin(ord(char))[2:].zfill(8)
        except:
            return "❌ 无效的字符"
    
    @staticmethod
    def char_to_oct(char: str) -> str:
        """字符转八进制 (ASCII)"""
        try:
            return oct(ord(char))[2:]
        except:
            return "❌ 无效的字符"
    
    @staticmethod
    def hex_to_char(hex_str: str) -> str:
        """十六进制转字符 (ASCII)"""
        try:
            hex_str = hex_str.replace('0x', '').replace('0X', '')
            return chr(int(hex_str, 16))
        except:
            return "❌ 无效的十六进制"
    
    @staticmethod
    def bin_to_char(binary: str) -> str:
        """二进制转字符 (ASCII)"""
        try:
            return chr(int(binary, 2))
        except:
            return "❌ 无效的二进制"
    
    @staticmethod
    def oct_to_char(octal: str) -> str:
        """八进制转字符 (ASCII)"""
        try:
            return chr(int(octal, 8))
        except:
            return "❌ 无效的八进制"
    
    @staticmethod
    def text_to_hex(text: str, separator: str = ' ') -> str:
        """文本转十六进制"""
        return separator.join([hex(ord(c))[2:].upper().zfill(2) for c in text])
    
    @staticmethod
    def text_to_bin(text: str, separator: str = ' ') -> str:
        """文本转二进制"""
        return separator.join([bin(ord(c))[2:].zfill(8) for c in text])
    
    @staticmethod
    def text_to_oct(text: str, separator: str = ' ') -> str:
        """文本转八进制"""
        return separator.join([oct(ord(c))[2:] for c in text])
    
    @staticmethod
    def hex_to_text(hex_str: str) -> str:
        """十六进制转文本"""
        try:
            hex_str = hex_str.replace(' ', '').replace('0x', '').replace('0X', '')
            if len(hex_str) % 2 != 0:
                return "❌ 十六进制长度必须为偶数"
            return ''.join([chr(int(hex_str[i:i+2], 16)) for i in range(0, len(hex_str), 2)])
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    @staticmethod
    def bin_to_text(binary_str: str) -> str:
        """二进制转文本"""
        try:
            binary_str = binary_str.replace(' ', '')
            if len(binary_str) % 8 != 0:
                return "❌ 二进制长度必须为8的倍数"
            return ''.join([chr(int(binary_str[i:i+8], 2)) for i in range(0, len(binary_str), 8)])
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    @staticmethod
    def oct_to_text(octal_str: str) -> str:
        """八进制转文本"""
        try:
            octal_str = octal_str.replace(' ', '')
            # 每3位一组
            if len(octal_str) % 3 != 0:
                return "❌ 八进制长度必须为3的倍数"
            return ''.join([chr(int(octal_str[i:i+3], 8)) for i in range(0, len(octal_str), 3)])
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    @staticmethod
    def decimal_to_text(decimal_str: str, separator: str = ' ') -> str:
        """十进制序列转文本"""
        try:
            nums = decimal_str.split(separator)
            return ''.join([chr(int(n)) for n in nums if n])
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    @staticmethod
    def text_to_decimal(text: str, separator: str = ' ') -> str:
        """文本转十进制序列"""
        return separator.join([str(ord(c)) for c in text])
    
    @staticmethod
    def base_n_encode(text: str, base: int) -> str:
        """任意进制编码 (2-36)"""
        digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if base < 2 or base > 36:
            return "❌ 进制必须在2-36之间"
        try:
            num = int.from_bytes(text.encode('utf-8'), 'big')
            result = ""
            while num > 0:
                result = digits[num % base] + result
                num //= base
            return result if result else "0"
        except Exception as e:
            return f"❌ 转换失败: {e}"
    
    @staticmethod
    def base_n_decode(encoded: str, base: int) -> str:
        """任意进制解码 (2-36)"""
        digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if base < 2 or base > 36:
            return "❌ 进制必须在2-36之间"
        try:
            num = 0
            for c in encoded.upper():
                num = num * base + digits.index(c)
            return num.to_bytes((num.bit_length() + 7) // 8, 'big').decode('utf-8', errors='replace')
        except Exception as e:
            return f"❌ 解码失败: {e}"
    
    @staticmethod
    def base58_encode(text: str) -> str:
        """Base58编码 (比特币风格)"""
        alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        num = int.from_bytes(text.encode('utf-8'), 'big')
        result = ""
        while num > 0:
            result = alphabet[num % 58] + result
            num //= 58
        return result if result else alphabet[0]
    
    @staticmethod
    def base58_decode(encoded: str) -> str:
        """Base58解码"""
        alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        num = 0
        for c in encoded:
            num = num * 58 + alphabet.index(c)
        return num.to_bytes((num.bit_length() + 7) // 8, 'big').decode('utf-8', errors='replace')
    
    @staticmethod
    def base32_encode(text: str) -> str:
        """Base32编码"""
        return base64.b32encode(text.encode('utf-8')).decode('utf-8').rstrip('=')
    
    @staticmethod
    def base32_decode(encoded: str) -> str:
        """Base32解码"""
        try:
            # 补齐padding
            encoded = encoded.strip()
            if len(encoded) % 8:
                encoded += '=' * (8 - len(encoded) % 8)
            return base64.b32decode(encoded.encode('utf-8')).decode('utf-8', errors='replace')
        except Exception as e:
            return f"❌ Base32解码失败: {e}"

    # ---------- 编码 ----------
    @staticmethod
    def base64_encode(text: str) -> str:
        return base64.b64encode(text.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def base64_decode(text: str) -> str:
        try:
            text = text.strip()
            if len(text) % 4:
                text += '=' * (4 - len(text) % 4)
            return base64.b64decode(text.encode('utf-8')).decode('utf-8', errors='replace')
        except Exception as e:
            return f"❌ Base64解码失败: {e}"
    
    @staticmethod
    def base64_url_encode(text: str) -> str:
        return base64.urlsafe_b64encode(text.encode('utf-8')).decode('utf-8').rstrip('=')
    
    @staticmethod
    def base64_url_decode(text: str) -> str:
        try:
            text = text.strip()
            if len(text) % 4:
                text += '=' * (4 - len(text) % 4)
            return base64.urlsafe_b64decode(text.encode('utf-8')).decode('utf-8', errors='replace')
        except Exception as e:
            return f"❌ URL-Safe Base64解码失败: {e}"
    
    @staticmethod
    def hex_encode(text: str) -> str:
        return binascii.hexlify(text.encode('utf-8')).decode('utf-8')
    
    @staticmethod
    def hex_decode(text: str) -> str:
        try:
            return binascii.unhexlify(text).decode('utf-8', errors='replace')
        except Exception as e:
            return f"❌ Hex解码失败: {e}"
    
    @staticmethod
    def url_encode(text: str) -> str:
        return quote(text, safe='')
    
    @staticmethod
    def url_decode(text: str) -> str:
        try:
            return unquote(text)
        except Exception as e:
            return f"❌ URL解码失败: {e}"
    
    @staticmethod
    def unicode_escape(text: str) -> str:
        return text.encode('unicode_escape').decode('utf-8')
    
    @staticmethod
    def unicode_unescape(text: str) -> str:
        try:
            return codecs.decode(text, 'unicode_escape')
        except Exception as e:
            return f"❌ Unicode反转义失败: {e}"
    
    @staticmethod
    def html_escape(text: str) -> str:
        return (text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                   .replace('"', '&quot;').replace("'", '&#39;'))
    
    @staticmethod
    def html_unescape(text: str) -> str:
        return (text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
                   .replace('&quot;', '"').replace('&#39;', "'"))
    
    @staticmethod
    def morse_encode(text: str) -> str:
        result = []
        for c in text.upper():
            if c in MORSE_MAP:
                result.append(MORSE_MAP[c])
            else:
                result.append('?')
        return ' '.join(result)
    
    @staticmethod
    def morse_decode(text: str) -> str:
        result = []
        for code in text.split():
            if code in MORSE_REVERSE:
                result.append(MORSE_REVERSE[code])
            else:
                result.append('?')
        return ''.join(result)
    
    # ---------- 键盘密码 ----------
    @staticmethod
    def keyboard_shift(text: str, direction: str = 'right') -> str:
        result = []
        for char in text.lower():
            if char in KEYBOARD_NEIGHBORS:
                neighbors = KEYBOARD_NEIGHBORS[char]
                if direction == 'right':
                    result.append(neighbors[0] if neighbors else char)
                elif direction == 'left':
                    result.append(neighbors[-1] if neighbors else char)
                elif direction == 'random':
                    import random
                    result.append(random.choice(neighbors) if neighbors else char)
                else:
                    result.append(char)
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def keyboard_shift_bruteforce(text: str) -> List[Tuple[str, str]]:
        results = []
        for direction in ['right', 'left']:
            result = CryptEngine.keyboard_shift(text, direction)
            results.append((direction, result))
        return results
    
    @staticmethod
    def keyboard_coords_encode(text: str) -> str:
        result = []
        for char in text.lower():
            if char in KEYBOARD_COORDS:
                row, col = KEYBOARD_COORDS[char]
                result.append(f"{row}{col}")
            else:
                result.append(f"?")
        return ' '.join(result)
    
    @staticmethod
    def keyboard_coords_decode(text: str) -> str:
        result = []
        coords = re.findall(r'\d', text)
        reverse_coords = {v: k for k, v in KEYBOARD_COORDS.items()}
        for i in range(0, len(coords) - 1, 2):
            try:
                key = (int(coords[i]), int(coords[i+1]))
                if key in reverse_coords:
                    result.append(reverse_coords[key])
                else:
                    result.append('?')
            except:
                result.append('?')
        return ''.join(result)
    
    @staticmethod
    def qwerty_to_azerty(text: str) -> str:
        qwerty_to_azerty_map = {
            'q': 'a', 'w': 'z', 'e': 'e', 'r': 'r', 't': 't', 'y': 'y',
            'u': 'u', 'i': 'i', 'o': 'o', 'p': 'p', 'a': 'q', 's': 's',
            'd': 'd', 'f': 'f', 'g': 'g', 'h': 'h', 'j': 'j', 'k': 'k',
            'l': 'l', 'z': 'w', 'x': 'x', 'c': 'c', 'v': 'v', 'b': 'b',
            'n': 'n', 'm': 'm'
        }
        result = []
        for char in text.lower():
            if char in qwerty_to_azerty_map:
                result.append(qwerty_to_azerty_map[char])
            else:
                result.append(char)
        return ''.join(result)
    
    @staticmethod
    def azerty_to_qwerty(text: str) -> str:
        azerty_to_qwerty_map = {
            'a': 'q', 'z': 'w', 'e': 'e', 'r': 'r', 't': 't', 'y': 'y',
            'u': 'u', 'i': 'i', 'o': 'o', 'p': 'p', 'q': 'a', 's': 's',
            'd': 'd', 'f': 'f', 'g': 'g', 'h': 'h', 'j': 'j', 'k': 'k',
            'l': 'l', 'w': 'z', 'x': 'x', 'c': 'c', 'v': 'v', 'b': 'b',
            'n': 'n', 'm': 'm'
        }
        result = []
        for char in text.lower():
            if char in azerty_to_qwerty_map:
                result.append(azerty_to_qwerty_map[char])
            else:
                result.append(char)
        return ''.join(result)
    
    # ---------- 哈希 ----------
    @staticmethod
    def md5(text: str) -> str:
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha1(text: str) -> str:
        return hashlib.sha1(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha256(text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha512(text: str) -> str:
        return hashlib.sha512(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha3_256(text: str) -> str:
        return hashlib.sha3_256(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sha3_512(text: str) -> str:
        return hashlib.sha3_512(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def blake2b(text: str) -> str:
        return hashlib.blake2b(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def bcrypt_hash(text: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(text.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def bcrypt_verify(text: str, hash_val: str) -> bool:
        try:
            return bcrypt.checkpw(text.encode('utf-8'), hash_val.encode('utf-8'))
        except:
            return False
    
    @staticmethod
    def hmac_sha256(key: str, text: str) -> str:
        h = hmac.HMAC(key.encode('utf-8'), hashes.SHA256(), backend=default_backend())
        h.update(text.encode('utf-8'))
        return h.finalize().hex()
    
    @staticmethod
    def file_md5(file_path: str) -> str:
        h = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    
    @staticmethod
    def file_sha256(file_path: str) -> str:
        h = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    
    @staticmethod
    def file_sha512(file_path: str) -> str:
        h = hashlib.sha512()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    
    # ---------- 经典密码 ----------
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
        return CryptEngine.caesar_encrypt(text, -shift)
    
    @staticmethod
    def caesar_bruteforce(text: str) -> List[Tuple[int, str]]:
        return [(i, CryptEngine.caesar_decrypt(text, i)) for i in range(1, 26)]
    
    @staticmethod
    def rot13(text: str) -> str:
        return CryptEngine.caesar_encrypt(text, 13)
    
    @staticmethod
    def vigenere_encrypt(text: str, key: str) -> str:
        result, key_idx = [], 0
        key = key.upper()
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
        result, key_idx = [], 0
        key = key.upper()
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
    def atbash(text: str) -> str:
        result = []
        for c in text:
            if c.isupper():
                result.append(chr(ord('Z') - (ord(c) - ord('A'))))
            elif c.islower():
                result.append(chr(ord('z') - (ord(c) - ord('a'))))
            else:
                result.append(c)
        return ''.join(result)
    
    @staticmethod
    def affine_encrypt(text: str, a: int, b: int) -> str:
        result = []
        for c in text:
            if c.isupper():
                x = ord(c) - ord('A')
                result.append(chr((a * x + b) % 26 + ord('A')))
            elif c.islower():
                x = ord(c) - ord('a')
                result.append(chr((a * x + b) % 26 + ord('a')))
            else:
                result.append(c)
        return ''.join(result)
    
    @staticmethod
    def affine_decrypt(text: str, a: int, b: int) -> str:
        def mod_inv(a, m):
            for i in range(1, m):
                if (a * i) % m == 1:
                    return i
            return None
        
        a_inv = mod_inv(a, 26)
        if a_inv is None:
            return "❌ a与26不互质，无法解密"
        
        result = []
        for c in text:
            if c.isupper():
                y = ord(c) - ord('A')
                result.append(chr((a_inv * (y - b)) % 26 + ord('A')))
            elif c.islower():
                y = ord(c) - ord('a')
                result.append(chr((a_inv * (y - b)) % 26 + ord('a')))
            else:
                result.append(c)
        return ''.join(result)
    
    # ---------- AES ----------
    @staticmethod
    def aes_cbc_encrypt(text: str, key: str) -> str:
        try:
            key_bytes = hashlib.sha256(key.encode()).digest()
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            padder = padding.PKCS7(128).padder()
            padded = padder.update(text.encode()) + padder.finalize()
            encrypted = encryptor.update(padded) + encryptor.finalize()
            return base64.b64encode(iv + encrypted).decode()
        except Exception as e:
            return f"❌ AES-CBC加密失败: {e}"
    
    @staticmethod
    def aes_cbc_decrypt(text: str, key: str) -> str:
        try:
            data = base64.b64decode(text.encode())
            iv, encrypted = data[:16], data[16:]
            key_bytes = hashlib.sha256(key.encode()).digest()
            cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(encrypted) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            unpadded = unpadder.update(decrypted) + unpadder.finalize()
            return unpadded.decode('utf-8', errors='replace')
        except Exception as e:
            return f"❌ AES-CBC解密失败: {e}"
    
    @staticmethod
    def aes_gcm_encrypt(text: str, key: str) -> str:
        try:
            key_bytes = hashlib.sha256(key.encode()).digest()
            iv = os.urandom(12)
            cipher = Cipher(algorithms.AES(key_bytes), modes.GCM(iv), backend=default_backend())
            encryptor = cipher.encryptor()
            encrypted = encryptor.update(text.encode()) + encryptor.finalize()
            return base64.b64encode(iv + encryptor.tag + encrypted).decode()
        except Exception as e:
            return f"❌ AES-GCM加密失败: {e}"
    
    @staticmethod
    def aes_gcm_decrypt(text: str, key: str) -> str:
        try:
            data = base64.b64decode(text.encode())
            iv, tag, encrypted = data[:12], data[12:28], data[28:]
            key_bytes = hashlib.sha256(key.encode()).digest()
            cipher = Cipher(algorithms.AES(key_bytes), modes.GCM(iv, tag), backend=default_backend())
            decryptor = cipher.decryptor()
            decrypted = decryptor.update(encrypted) + decryptor.finalize()
            return decrypted.decode('utf-8', errors='replace')
        except Exception as e:
            return f"❌ AES-GCM解密失败: {e}"
    
    # ---------- RSA ----------
    @staticmethod
    def rsa_generate_keypair() -> Tuple[str, str]:
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_pem, public_pem
    
    @staticmethod
    def rsa_encrypt(text: str, public_key_pem: str) -> str:
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
            encrypted = public_key.encrypt(
                text.encode('utf-8'),
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            return f"❌ RSA加密失败: {e}"
    
    @staticmethod
    def rsa_decrypt(text: str, private_key_pem: str) -> str:
        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8'),
                password=None,
                backend=default_backend()
            )
            encrypted = base64.b64decode(text.encode())
            decrypted = private_key.decrypt(
                encrypted,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return decrypted.decode('utf-8', errors='replace')
        except Exception as e:
            return f"❌ RSA解密失败: {e}"
    
    # ---------- JWT ----------
    @staticmethod
    def jwt_encode(payload: Dict, secret: str, algorithm: str = 'HS256') -> str:
        try:
            return jwt.encode(payload, secret, algorithm=algorithm)
        except Exception as e:
            return f"❌ JWT编码失败: {e}"
    
    @staticmethod
    def jwt_decode(token: str, secret: str = None, verify: bool = True) -> Dict:
        try:
            if secret:
                return jwt.decode(token, secret, algorithms=['HS256', 'HS384', 'HS512'])
            else:
                return jwt.decode(token, options={'verify_signature': False})
        except jwt.ExpiredSignatureError:
            return {'error': 'Token已过期'}
        except jwt.InvalidTokenError as e:
            return {'error': f'无效Token: {e}'}
    
    # ---------- 哈希破解 ----------
    @staticmethod
    def hash_collision_detect(hash_value: str, wordlist: List[str], hash_func: str = 'md5') -> Optional[Tuple[str, str]]:
        hash_funcs = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }
        
        if hash_func not in hash_funcs:
            return None
        
        for word in wordlist:
            h = hash_funcs[hash_func](word.encode('utf-8')).hexdigest()
            if h.lower() == hash_value.lower():
                return (word, h)
        return None
    
    @staticmethod
    def rainbow_table_lookup(hash_value: str) -> Optional[str]:
        common_passwords = [
            'password', '123456', '123456789', '12345', '12345678',
            'qwerty', 'abc123', 'football', 'monkey', 'letmein',
            'shadow', 'master', '666666', 'qwertyuiop', '123321',
            'mustang', '1234567890', 'michael', '654321', 'superman',
            '1qaz2wsx', 'baseball', 'dragon', 'fuckyou', '000000',
            'lovely', 'iloveyou', 'test', 'admin', 'password123'
        ]
        
        for word in common_passwords:
            for algo in ['md5', 'sha1', 'sha256', 'sha512']:
                h = getattr(hashlib, algo)(word.encode('utf-8')).hexdigest()
                if h.lower() == hash_value.lower():
                    return f"{word} ({algo})"
        return None
    
    # ---------- 编码检测 ----------
    @staticmethod
    def detect_encoding(data: bytes) -> Dict:
        try:
            result = chardet.detect(data)
            return {'encoding': result['encoding'], 'confidence': result['confidence'], 
                    'language': result.get('language', '')}
        except:
            return {'encoding': 'utf-8', 'confidence': 0.0, 'language': ''}
    
    @staticmethod
    def smart_decode(text: str) -> Dict[str, Any]:
        results = {}
        text_stripped = text.strip()
        
        try:
            decoded = CryptEngine.base64_decode(text_stripped)
            if decoded and not decoded.startswith('❌'):
                results['base64'] = decoded
        except:
            pass
        
        try:
            decoded = CryptEngine.hex_decode(text_stripped)
            if decoded and not decoded.startswith('❌'):
                results['hex'] = decoded
        except:
            pass
        
        try:
            decoded = CryptEngine.url_decode(text_stripped)
            if decoded != text_stripped:
                results['url'] = decoded
        except:
            pass
        
        if '\\u' in text_stripped:
            try:
                decoded = CryptEngine.unicode_unescape(text_stripped)
                if decoded != text_stripped:
                    results['unicode_escape'] = decoded
            except:
                pass
        
        if '&' in text_stripped:
            try:
                decoded = CryptEngine.html_unescape(text_stripped)
                if decoded != text_stripped:
                    results['html'] = decoded
            except:
                pass
        
        return results

# ==================== 工作线程 ====================
class WorkerThread(QThread):
    progress = Signal(int)
    finished = Signal(object)
    error = Signal(str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

# ==================== 面板基类 ====================
class BasePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

# ==================== 参考面板 ====================
REFERENCE_TEXT = """
📖 编解码速查手册 v3.0

━━━ 进制转换 ━━━
二进制: 0-1, 前缀0b, 如 0b1010 = 10
八进制: 0-7, 前缀0o, 如 0o12 = 10
十进制: 0-9, 如 10
十六进制: 0-9 A-F, 前缀0x, 如 0xA = 10

常见转换:
- 文本 → Hex: Hello → 48 65 6C 6C 6F
- Hex → 文本: 48 65 6C 6C 6F → Hello
- 文本 → Bin: Hello → 01001000 01100101...
- 十进制序列: 72 101 108 108 111 → Hello

━━━ Base家族 ━━━
Base64: A-Z a-z 0-9 + / =
Base32: A-Z 2-7
Base58: 比特币风格, 去掉了0OIl

━━━ 键盘密码 ━━━
1. 键盘移位: q→w, a→s, z→x
2. 键盘坐标: a=(2,0), s=(2,1)
3. QWERTY↔AZERTY转换

━━━ 经典密码 ━━━
凯撒: 偏移3, HELLO→KHOOR
维吉尼亚: 密钥KEY, HELLO→RIJVS
Atbash: HELLO→SVOOL
仿射: C=(a*P+b) mod 26

━━━ 哈希算法 ━━━
MD5(32), SHA-1(40), SHA-256(64)
SHA-512(128), SHA-3, BLAKE2b
bcrypt, HMAC

━━━ AES ━━━
CBC: 需要IV填充, PKCS7
GCM: 认证加密, 更安全

━━━ RSA ━━━
2048位, 公钥加密, 私钥解密
OAEP填充, SHA-256

━━━ JWT ━━━
Header.Payload.Signature
HS256/HS384/HS512
"""

class ReferencePanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel("📖 编解码参考")
        title.setStyleSheet(f"color: {CyberTheme.NEON_PURPLE}; font-size: 16pt; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        self.text_display = QTextEdit()
        self.text_display.setStyleSheet(f"""
            QTextEdit {{
                background: {CyberTheme.INPUT_BG};
                color: {CyberTheme.TEXT};
                border: 1px solid {CyberTheme.INPUT_BORDER};
                border-radius: 6px;
                padding: 12px;
                font-family: "Consolas", monospace;
                font-size: 10pt;
            }}
        """)
        self.text_display.setPlainText(REFERENCE_TEXT)
        self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)

# ==================== 进制转换面板 ====================
class BaseConvertPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel("🔢 进制转换")
        title.setStyleSheet(f"color: {CyberTheme.NEON_PURPLE}; font-size: 16pt; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        # 输入选择
        input_group = CyberGroupBox("🔹 输入设置")
        input_layout = QHBoxLayout(input_group)
        
        input_layout.addWidget(QLabel("输入类型:"))
        self.input_type = QComboBox()
        self.input_type.addItems(["文本 (自动转换)", "二进制", "八进制", "十进制", "十六进制", "Base64", "Base32", "Base58"])
        self.input_type.setStyleSheet(input_style())
        self.input_type.currentIndexChanged.connect(self.on_input_type_changed)
        input_layout.addWidget(self.input_type)
        
        input_layout.addStretch()
        layout.addWidget(input_group)
        
        # 输入区域
        self.input_text = QTextEdit()
        self.input_text.setStyleSheet(input_style())
        self.input_text.setMaximumHeight(80)
        self.input_text.setPlaceholderText("输入要转换的内容...")
        layout.addWidget(QLabel("输入:"))
        layout.addWidget(self.input_text)
        
        # 转换按钮
        btn_layout = QHBoxLayout()
        convert_btn = FlatButton("🔄 转换全部", color=CyberTheme.NEON_GREEN)
        convert_btn.clicked.connect(self.convert_all)
        btn_layout.addWidget(convert_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # 输出区域 - 使用表格布局显示多种进制
        output_group = CyberGroupBox("📊 转换结果")
        output_layout = QVBoxLayout(output_group)
        
        self.result_text = QTextEdit()
        self.result_text.setStyleSheet(input_style())
        self.result_text.setMaximumHeight(200)
        self.result_text.setReadOnly(True)
        output_layout.addWidget(self.result_text)
        layout.addWidget(output_group)
        
        # 单独转换按钮
        single_group = CyberGroupBox("🔹 单步转换 (快速)")
        single_layout = QGridLayout(single_group)
        single_layout.setSpacing(4)
        
        conversions = [
            ("2→10", "bin_to_dec"), ("2→16", "bin_to_hex"), ("2→8", "bin_to_oct"),
            ("10→2", "dec_to_bin"), ("10→16", "dec_to_hex"), ("10→8", "dec_to_oct"),
            ("16→2", "hex_to_bin"), ("16→10", "hex_to_dec"), ("16→8", "hex_to_oct"),
            ("8→2", "oct_to_bin"), ("8→10", "oct_to_dec"), ("8→16", "oct_to_hex"),
            ("字符→16", "char_to_hex"), ("字符→2", "char_to_bin"), ("字符→8", "char_to_oct"),
            ("16→字符", "hex_to_char"), ("2→字符", "bin_to_char"), ("8→字符", "oct_to_char"),
        ]
        
        for i, (name, method) in enumerate(conversions):
            btn = FlatButton(name, color=CyberTheme.NEON_CYAN)
            btn.clicked.connect(lambda checked, m=method: self.single_convert(m))
            single_layout.addWidget(btn, i//6, i%6)
        
        layout.addWidget(single_group)
        
        # 操作按钮
        action_layout = QHBoxLayout()
        copy_btn = FlatButton("📋 复制", color=CyberTheme.NEON_GREEN)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.result_text.toPlainText()))
        action_layout.addWidget(copy_btn)
        clear_btn = FlatButton("🗑️ 清空", color=CyberTheme.NEON_ORANGE)
        clear_btn.clicked.connect(lambda: (self.input_text.clear(), self.result_text.clear()))
        action_layout.addWidget(clear_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
    
    def on_input_type_changed(self):
        """根据输入类型更新placeholder"""
        types = {
            0: "输入文本 (如: Hello World)",
            1: "输入二进制 (如: 01001000)",
            2: "输入八进制 (如: 110)",
            3: "输入十进制 (如: 72)",
            4: "输入十六进制 (如: 48)",
            5: "输入Base64 (如: SGVsbG8=)",
            6: "输入Base32 (如: JBSWY3DP)",
            7: "输入Base58 (如: 6oX7f)"
        }
        self.input_text.setPlaceholderText(types.get(self.input_type.currentIndex(), ""))
    
    def convert_all(self):
        """转换所有格式"""
        text = self.input_text.toPlainText().strip()
        if not text:
            self.result_text.setText("⚠️ 请先输入内容")
            return
        
        input_type = self.input_type.currentIndex()
        output = []
        separator = "=" * 50
        
        try:
            # 先根据输入类型解码
            decoded_text = text
            
            if input_type == 0:  # 文本
                decoded_text = text
                output.append(f"📝 原始文本: {text}")
                output.append("")
                output.append("━━━ 文本 → 进制 ━━━")
                output.append(f"十六进制: {CryptEngine.text_to_hex(text)}")
                output.append(f"二进制: {CryptEngine.text_to_bin(text)}")
                output.append(f"八进制: {CryptEngine.text_to_oct(text)}")
                output.append(f"十进制序列: {CryptEngine.text_to_decimal(text)}")
                
                # Base系列
                output.append("")
                output.append("━━━ Base家族 ━━━")
                output.append(f"Base64: {CryptEngine.base64_encode(text)}")
                output.append(f"Base32: {CryptEngine.base32_encode(text)}")
                output.append(f"Base58: {CryptEngine.base58_encode(text)}")
            
            elif input_type == 1:  # 二进制
                # 先转为文本
                decoded_text = CryptEngine.bin_to_text(text)
                if decoded_text.startswith("❌"):
                    output.append(f"❌ 转换失败: {decoded_text}")
                else:
                    output.append(f"📝 解码文本: {decoded_text}")
                    output.append("")
                    output.append("━━━ 进制转换 ━━━")
                    output.append(f"十进制: {CryptEngine.bin_to_dec(text)}")
                    output.append(f"十六进制: {CryptEngine.bin_to_hex(text)}")
                    output.append(f"八进制: {CryptEngine.bin_to_oct(text)}")
            
            elif input_type == 2:  # 八进制
                decoded_text = CryptEngine.oct_to_text(text)
                if decoded_text.startswith("❌"):
                    output.append(f"❌ 转换失败: {decoded_text}")
                else:
                    output.append(f"📝 解码文本: {decoded_text}")
                    output.append("")
                    output.append("━━━ 进制转换 ━━━")
                    output.append(f"二进制: {CryptEngine.oct_to_bin(text)}")
                    output.append(f"十进制: {CryptEngine.oct_to_dec(text)}")
                    output.append(f"十六进制: {CryptEngine.oct_to_hex(text)}")
            
            elif input_type == 3:  # 十进制
                # 尝试作为ASCII码
                try:
                    nums = text.split()
                    if len(nums) > 1:
                        decoded_text = CryptEngine.decimal_to_text(text)
                        if not decoded_text.startswith("❌"):
                            output.append(f"📝 解码文本: {decoded_text}")
                            output.append("")
                except:
                    pass
                
                output.append("━━━ 进制转换 ━━━")
                output.append(f"二进制: {CryptEngine.dec_to_bin(text)}")
                output.append(f"十六进制: {CryptEngine.dec_to_hex(text)}")
                output.append(f"八进制: {CryptEngine.dec_to_oct(text)}")
            
            elif input_type == 4:  # 十六进制
                decoded_text = CryptEngine.hex_to_text(text)
                if decoded_text.startswith("❌"):
                    output.append(f"❌ 转换失败: {decoded_text}")
                else:
                    output.append(f"📝 解码文本: {decoded_text}")
                    output.append("")
                    output.append("━━━ 进制转换 ━━━")
                    output.append(f"二进制: {CryptEngine.hex_to_bin(text)}")
                    output.append(f"十进制: {CryptEngine.hex_to_dec(text)}")
                    output.append(f"八进制: {CryptEngine.hex_to_oct(text)}")
            
            elif input_type == 5:  # Base64
                decoded_text = CryptEngine.base64_decode(text)
                if decoded_text.startswith("❌"):
                    output.append(f"❌ {decoded_text}")
                else:
                    output.append(f"📝 Base64解码: {decoded_text}")
                    output.append("")
                    output.append("━━━ 编码转换 ━━━")
                    output.append(f"十六进制: {CryptEngine.text_to_hex(decoded_text)}")
                    output.append(f"二进制: {CryptEngine.text_to_bin(decoded_text)}")
                    output.append(f"URL-Safe Base64: {CryptEngine.base64_url_encode(decoded_text)}")
            
            elif input_type == 6:  # Base32
                decoded_text = CryptEngine.base32_decode(text)
                if decoded_text.startswith("❌"):
                    output.append(f"❌ {decoded_text}")
                else:
                    output.append(f"📝 Base32解码: {decoded_text}")
                    output.append("")
                    output.append("━━━ 编码转换 ━━━")
                    output.append(f"Base64: {CryptEngine.base64_encode(decoded_text)}")
                    output.append(f"十六进制: {CryptEngine.text_to_hex(decoded_text)}")
            
            elif input_type == 7:  # Base58
                try:
                    decoded_text = CryptEngine.base58_decode(text)
                    output.append(f"📝 Base58解码: {decoded_text}")
                    output.append("")
                    output.append("━━━ 编码转换 ━━━")
                    output.append(f"Base64: {CryptEngine.base64_encode(decoded_text)}")
                    output.append(f"十六进制: {CryptEngine.text_to_hex(decoded_text)}")
                except:
                    output.append("❌ Base58解码失败")
            
            self.result_text.setText("\n".join(output))
            
        except Exception as e:
            self.result_text.setText(f"❌ 转换失败: {e}")
    
    def single_convert(self, method):
        """单步转换"""
        text = self.input_text.toPlainText().strip()
        if not text:
            self.result_text.setText("⚠️ 请先输入内容")
            return
        
        try:
            func = getattr(CryptEngine, method)
            result = func(text)
            self.result_text.setText(f"🔹 {method.replace('_', '→').upper()}\n\n{result}")
        except Exception as e:
            self.result_text.setText(f"❌ {e}")

# ==================== 编码面板 ====================
class EncodingPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel("📝 编码转换")
        title.setStyleSheet(f"color: {CyberTheme.NEON_PURPLE}; font-size: 16pt; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        self.input_text = QTextEdit()
        self.input_text.setStyleSheet(input_style())
        self.input_text.setMaximumHeight(100)
        layout.addWidget(QLabel("输入:"))
        layout.addWidget(self.input_text)
        
        ops = [
            ("Base64编码", "base64_encode"), ("Base64解码", "base64_decode"),
            ("URL-Safe Base64编码", "base64_url_encode"), ("URL-Safe Base64解码", "base64_url_decode"),
            ("Hex编码", "hex_encode"), ("Hex解码", "hex_decode"),
            ("URL编码", "url_encode"), ("URL解码", "url_decode"),
            ("Unicode转义", "unicode_escape"), ("Unicode反转义", "unicode_unescape"),
            ("HTML转义", "html_escape"), ("HTML反转义", "html_unescape"),
            ("摩斯编码", "morse_encode"), ("摩斯解码", "morse_decode"),
        ]
        
        grid = QGridLayout()
        grid.setSpacing(4)
        for i, (name, method) in enumerate(ops):
            btn = FlatButton(name, color=CyberTheme.NEON_CYAN)
            btn.clicked.connect(lambda checked, m=method: self.run_op(m))
            grid.addWidget(btn, i//4, i%4)
        layout.addLayout(grid)
        
        self.output_text = QTextEdit()
        self.output_text.setStyleSheet(input_style())
        self.output_text.setMaximumHeight(100)
        self.output_text.setReadOnly(True)
        self.output_text.setAcceptRichText(False)
        layout.addWidget(QLabel("输出:"))
        layout.addWidget(self.output_text)
        
        action_layout = QHBoxLayout()
        copy_btn = FlatButton("📋 复制", color=CyberTheme.NEON_GREEN)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.output_text.toPlainText()))
        action_layout.addWidget(copy_btn)
        clear_btn = FlatButton("🗑️ 清空", color=CyberTheme.NEON_ORANGE)
        clear_btn.clicked.connect(lambda: (self.input_text.clear(), self.output_text.clear()))
        action_layout.addWidget(clear_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
    
    def run_op(self, method):
        text = self.input_text.toPlainText()
        if not text:
            self.output_text.setText("⚠️ 请先输入文本")
            return
        try:
            func = getattr(CryptEngine, method)
            self.output_text.setText(func(text))
        except Exception as e:
            self.output_text.setText(f"❌ {e}")

# ==================== 键盘密码面板 ====================
class KeyboardPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel("⌨️ 键盘密码")
        title.setStyleSheet(f"color: {CyberTheme.NEON_PURPLE}; font-size: 16pt; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        self.input_text = QTextEdit()
        self.input_text.setStyleSheet(input_style())
        self.input_text.setMaximumHeight(100)
        layout.addWidget(QLabel("输入:"))
        layout.addWidget(self.input_text)
        
        shift_group = CyberGroupBox("🔹 键盘移位密码")
        shift_layout = QHBoxLayout(shift_group)
        
        shift_layout.addWidget(QLabel("方向:"))
        self.shift_dir = QComboBox()
        self.shift_dir.addItems(["向右 (加密)", "向左 (解密)", "随机"])
        self.shift_dir.setStyleSheet(input_style())
        shift_layout.addWidget(self.shift_dir)
        
        shift_btn = FlatButton("键盘移位", color=CyberTheme.NEON_CYAN)
        shift_btn.clicked.connect(self.keyboard_shift)
        shift_layout.addWidget(shift_btn)
        
        brute_btn = FlatButton("暴力破解", color=CyberTheme.NEON_ORANGE)
        brute_btn.clicked.connect(self.keyboard_bruteforce)
        shift_layout.addWidget(brute_btn)
        shift_layout.addStretch()
        layout.addWidget(shift_group)
        
        coord_group = CyberGroupBox("🔹 键盘坐标密码")
        coord_layout = QHBoxLayout(coord_group)
        
        coord_enc_btn = FlatButton("坐标编码", color=CyberTheme.NEON_BLUE)
        coord_enc_btn.clicked.connect(self.coords_encode)
        coord_layout.addWidget(coord_enc_btn)
        
        coord_dec_btn = FlatButton("坐标解码", color=CyberTheme.NEON_BLUE)
        coord_dec_btn.clicked.connect(self.coords_decode)
        coord_layout.addWidget(coord_dec_btn)
        coord_layout.addStretch()
        layout.addWidget(coord_group)
        
        layout_group = CyberGroupBox("🔹 键盘布局转换")
        layout_layout = QHBoxLayout(layout_group)
        
        qwerty_to_azerty_btn = FlatButton("QWERTY → AZERTY", color=CyberTheme.NEON_PINK)
        qwerty_to_azerty_btn.clicked.connect(lambda: self.layout_convert('qwerty_to_azerty'))
        layout_layout.addWidget(qwerty_to_azerty_btn)
        
        azerty_to_qwerty_btn = FlatButton("AZERTY → QWERTY", color=CyberTheme.NEON_PINK)
        azerty_to_qwerty_btn.clicked.connect(lambda: self.layout_convert('azerty_to_qwerty'))
        layout_layout.addWidget(azerty_to_qwerty_btn)
        layout_layout.addStretch()
        layout.addWidget(layout_group)
        
        self.output_text = QTextEdit()
        self.output_text.setStyleSheet(input_style())
        self.output_text.setMaximumHeight(120)
        self.output_text.setReadOnly(True)
        layout.addWidget(QLabel("输出:"))
        layout.addWidget(self.output_text)
        
        action_layout = QHBoxLayout()
        copy_btn = FlatButton("📋 复制", color=CyberTheme.NEON_GREEN)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.output_text.toPlainText()))
        action_layout.addWidget(copy_btn)
        clear_btn = FlatButton("🗑️ 清空", color=CyberTheme.NEON_ORANGE)
        clear_btn.clicked.connect(lambda: (self.input_text.clear(), self.output_text.clear()))
        action_layout.addWidget(clear_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        info = QLabel("💡 QWERTY键盘布局: 1234567890/qwertyuiop/asdfghjkl/zxcvbnm")
        info.setStyleSheet(f"color: {CyberTheme.TEXT_DIM}; font-size: 8pt; background: transparent;")
        layout.addWidget(info)
    
    def keyboard_shift(self):
        text = self.input_text.toPlainText()
        if not text:
            self.output_text.setText("⚠️ 请先输入文本")
            return
        direction_map = {
            "向右 (加密)": "right",
            "向左 (解密)": "left",
            "随机": "random"
        }
        direction = direction_map[self.shift_dir.currentText()]
        self.output_text.setText(CryptEngine.keyboard_shift(text, direction))
    
    def keyboard_bruteforce(self):
        text = self.input_text.toPlainText()
        if not text:
            self.output_text.setText("⚠️ 请先输入文本")
            return
        results = CryptEngine.keyboard_shift_bruteforce(text)
        output = "\n".join([f"{d}: {r}" for d, r in results])
        self.output_text.setText(output)
    
    def coords_encode(self):
        text = self.input_text.toPlainText()
        if not text:
            self.output_text.setText("⚠️ 请先输入文本")
            return
        self.output_text.setText(CryptEngine.keyboard_coords_encode(text))
    
    def coords_decode(self):
        text = self.input_text.toPlainText()
        if not text:
            self.output_text.setText("⚠️ 请先输入文本")
            return
        self.output_text.setText(CryptEngine.keyboard_coords_decode(text))
    
    def layout_convert(self, method):
        text = self.input_text.toPlainText()
        if not text:
            self.output_text.setText("⚠️ 请先输入文本")
            return
        func = getattr(CryptEngine, method)
        self.output_text.setText(func(text))

# ==================== 经典密码面板 ====================
class ClassicCipherPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel("🏛️ 经典密码")
        title.setStyleSheet(f"color: {CyberTheme.NEON_PURPLE}; font-size: 16pt; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        self.input_text = QTextEdit()
        self.input_text.setStyleSheet(input_style())
        self.input_text.setMaximumHeight(80)
        layout.addWidget(QLabel("输入:"))
        layout.addWidget(self.input_text)
        
        caesar_group = CyberGroupBox("🔹 凯撒密码")
        caesar_layout = QHBoxLayout(caesar_group)
        
        caesar_layout.addWidget(QLabel("偏移:"))
        self.shift_spin = QSpinBox()
        self.shift_spin.setRange(1, 25)
        self.shift_spin.setValue(3)
        self.shift_spin.setStyleSheet(input_style())
        caesar_layout.addWidget(self.shift_spin)
        
        for name, method in [("加密", "caesar_encrypt"), ("解密", "caesar_decrypt"), ("暴力破解", "caesar_bruteforce")]:
            btn = FlatButton(name, color=CyberTheme.NEON_CYAN)
            btn.clicked.connect(lambda checked, m=method: self.run_caesar(m))
            caesar_layout.addWidget(btn)
        caesar_layout.addStretch()
        layout.addWidget(caesar_group)
        
        quick_group = CyberGroupBox("🔸 快速密码")
        quick_layout = QHBoxLayout(quick_group)
        
        rot13_btn = FlatButton("ROT13", color=CyberTheme.NEON_PINK)
        rot13_btn.clicked.connect(self.run_rot13)
        quick_layout.addWidget(rot13_btn)
        
        atbash_btn = FlatButton("Atbash (字母反转)", color=CyberTheme.NEON_PINK)
        atbash_btn.clicked.connect(self.run_atbash)
        quick_layout.addWidget(atbash_btn)
        quick_layout.addStretch()
        layout.addWidget(quick_group)
        
        vig_group = CyberGroupBox("🔹 维吉尼亚密码")
        vig_layout = QVBoxLayout(vig_group)
        
        key_row = QHBoxLayout()
        key_row.addWidget(QLabel("密钥:"))
        self.vigenere_key = QLineEdit()
        self.vigenere_key.setStyleSheet(input_style())
        self.vigenere_key.setPlaceholderText("输入密钥，如 KEY")
        key_row.addWidget(self.vigenere_key)
        key_row.addStretch()
        vig_layout.addLayout(key_row)
        
        btn_row = QHBoxLayout()
        vig_enc_btn = FlatButton("维吉尼亚加密", color=CyberTheme.NEON_BLUE)
        vig_enc_btn.clicked.connect(self.vigenere_encrypt)
        btn_row.addWidget(vig_enc_btn)
        vig_dec_btn = FlatButton("维吉尼亚解密", color=CyberTheme.NEON_BLUE)
        vig_dec_btn.clicked.connect(self.vigenere_decrypt)
        btn_row.addWidget(vig_dec_btn)
        btn_row.addStretch()
        vig_layout.addLayout(btn_row)
        layout.addWidget(vig_group)
        
        affine_group = CyberGroupBox("🔹 仿射密码")
        affine_layout = QHBoxLayout(affine_group)
        
        affine_layout.addWidget(QLabel("a:"))
        self.affine_a = QSpinBox()
        self.affine_a.setRange(1, 25)
        self.affine_a.setValue(5)
        self.affine_a.setStyleSheet(input_style())
        affine_layout.addWidget(self.affine_a)
        
        affine_layout.addWidget(QLabel("b:"))
        self.affine_b = QSpinBox()
        self.affine_b.setRange(0, 25)
        self.affine_b.setValue(8)
        self.affine_b.setStyleSheet(input_style())
        affine_layout.addWidget(self.affine_b)
        
        aff_enc_btn = FlatButton("仿射加密", color=CyberTheme.NEON_ORANGE)
        aff_enc_btn.clicked.connect(self.affine_encrypt)
        affine_layout.addWidget(aff_enc_btn)
        
        aff_dec_btn = FlatButton("仿射解密", color=CyberTheme.NEON_ORANGE)
        aff_dec_btn.clicked.connect(self.affine_decrypt)
        affine_layout.addWidget(aff_dec_btn)
        affine_layout.addStretch()
        layout.addWidget(affine_group)
        
        self.output_text = QTextEdit()
        self.output_text.setStyleSheet(input_style())
        self.output_text.setMaximumHeight(120)
        self.output_text.setReadOnly(True)
        layout.addWidget(QLabel("输出:"))
        layout.addWidget(self.output_text)
        
        action_layout = QHBoxLayout()
        copy_btn = FlatButton("📋 复制", color=CyberTheme.NEON_GREEN)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.output_text.toPlainText()))
        action_layout.addWidget(copy_btn)
        clear_btn = FlatButton("🗑️ 清空", color=CyberTheme.NEON_ORANGE)
        clear_btn.clicked.connect(lambda: (self.input_text.clear(), self.output_text.clear()))
        action_layout.addWidget(clear_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
    
    def run_caesar(self, method):
        text = self.input_text.toPlainText()
        if not text:
            self.output_text.setText("⚠️ 请先输入文本")
            return
        shift = self.shift_spin.value()
        try:
            if method == "caesar_encrypt":
                self.output_text.setText(CryptEngine.caesar_encrypt(text, shift))
            elif method == "caesar_decrypt":
                self.output_text.setText(CryptEngine.caesar_decrypt(text, shift))
            else:
                results = CryptEngine.caesar_bruteforce(text)
                self.output_text.setText("\n".join([f"偏移 {s}: {r}" for s, r in results]))
        except Exception as e:
            self.output_text.setText(f"❌ {e}")
    
    def run_rot13(self):
        text = self.input_text.toPlainText()
        if not text:
            self.output_text.setText("⚠️ 请先输入文本")
            return
        self.output_text.setText(CryptEngine.rot13(text))
    
    def run_atbash(self):
        text = self.input_text.toPlainText()
        if not text:
            self.output_text.setText("⚠️ 请先输入文本")
            return
        self.output_text.setText(CryptEngine.atbash(text))
    
    def vigenere_encrypt(self):
        text = self.input_text.toPlainText()
        key = self.vigenere_key.text().strip()
        if not text or not key:
            self.output_text.setText("⚠️ 请输入文本和密钥")
            return
        self.output_text.setText(CryptEngine.vigenere_encrypt(text, key))
    
    def vigenere_decrypt(self):
        text = self.input_text.toPlainText()
        key = self.vigenere_key.text().strip()
        if not text or not key:
            self.output_text.setText("⚠️ 请输入文本和密钥")
            return
        self.output_text.setText(CryptEngine.vigenere_decrypt(text, key))
    
    def affine_encrypt(self):
        text = self.input_text.toPlainText()
        if not text:
            self.output_text.setText("⚠️ 请先输入文本")
            return
        a = self.affine_a.value()
        b = self.affine_b.value()
        self.output_text.setText(CryptEngine.affine_encrypt(text, a, b))
    
    def affine_decrypt(self):
        text = self.input_text.toPlainText()
        if not text:
            self.output_text.setText("⚠️ 请先输入文本")
            return
        a = self.affine_a.value()
        b = self.affine_b.value()
        self.output_text.setText(CryptEngine.affine_decrypt(text, a, b))

# ==================== 哈希面板 ====================
class HashPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel("🔐 哈希计算")
        title.setStyleSheet(f"color: {CyberTheme.NEON_PURPLE}; font-size: 16pt; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        self.input_text = QTextEdit()
        self.input_text.setStyleSheet(input_style())
        self.input_text.setMaximumHeight(80)
        layout.addWidget(QLabel("输入:"))
        layout.addWidget(self.input_text)
        
        hash_layout = QGridLayout()
        hash_layout.setSpacing(4)
        hash_funcs = [
            ("MD5", "md5"), ("SHA-1", "sha1"), ("SHA-256", "sha256"),
            ("SHA-512", "sha512"), ("SHA3-256", "sha3_256"), ("SHA3-512", "sha3_512"),
            ("BLAKE2b", "blake2b"), ("bcrypt", "bcrypt_hash")
        ]
        for i, (name, method) in enumerate(hash_funcs):
            btn = FlatButton(name, color=CyberTheme.NEON_BLUE)
            btn.clicked.connect(lambda checked, m=method: self.run_hash(m))
            hash_layout.addWidget(btn, i//4, i%4)
        layout.addLayout(hash_layout)
        
        hmac_layout = QHBoxLayout()
        hmac_layout.addWidget(QLabel("HMAC密钥:"))
        self.hmac_key = QLineEdit()
        self.hmac_key.setStyleSheet(input_style())
        self.hmac_key.setPlaceholderText("输入HMAC密钥")
        hmac_layout.addWidget(self.hmac_key)
        hmac_btn = FlatButton("HMAC-SHA256", color=CyberTheme.NEON_ORANGE)
        hmac_btn.clicked.connect(self.run_hmac)
        hmac_layout.addWidget(hmac_btn)
        hmac_layout.addStretch()
        layout.addLayout(hmac_layout)
        
        self.output_text = QTextEdit()
        self.output_text.setStyleSheet(input_style())
        self.output_text.setMaximumHeight(80)
        self.output_text.setReadOnly(True)
        layout.addWidget(QLabel("哈希:"))
        layout.addWidget(self.output_text)
        
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("文件:"))
        self.file_path = QLineEdit()
        self.file_path.setStyleSheet(input_style())
        file_layout.addWidget(self.file_path)
        browse_btn = FlatButton("📂", color=CyberTheme.NEON_ORANGE)
        browse_btn.setFixedWidth(40)
        browse_btn.clicked.connect(self.select_file)
        file_layout.addWidget(browse_btn)
        file_hash_btn = FlatButton("计算MD5+SHA256+SHA512", color=CyberTheme.NEON_GREEN)
        file_hash_btn.clicked.connect(self.file_hash)
        file_layout.addWidget(file_hash_btn)
        layout.addLayout(file_layout)
        
        self.progress = QProgressBar()
        self.progress.setStyleSheet(input_style())
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        action_layout = QHBoxLayout()
        copy_btn = FlatButton("📋 复制", color=CyberTheme.NEON_GREEN)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.output_text.toPlainText()))
        action_layout.addWidget(copy_btn)
        clear_btn = FlatButton("🗑️ 清空", color=CyberTheme.NEON_ORANGE)
        clear_btn.clicked.connect(lambda: (self.input_text.clear(), self.output_text.clear()))
        action_layout.addWidget(clear_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
    
    def run_hash(self, method):
        text = self.input_text.toPlainText()
        if not text:
            self.output_text.setText("⚠️ 请先输入文本")
            return
        try:
            func = getattr(CryptEngine, method)
            result = func(text)
            self.output_text.setText(f"{method.upper()}: {result}")
        except Exception as e:
            self.output_text.setText(f"❌ {e}")
    
    def run_hmac(self):
        text = self.input_text.toPlainText()
        key = self.hmac_key.text().strip()
        if not text or not key:
            self.output_text.setText("⚠️ 请输入文本和HMAC密钥")
            return
        self.output_text.setText(f"HMAC-SHA256: {CryptEngine.hmac_sha256(key, text)}")
    
    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if path:
            self.file_path.setText(path)
    
    def file_hash(self):
        path = self.file_path.text()
        if not path or not os.path.exists(path):
            self.output_text.setText("⚠️ 请选择有效的文件")
            return
        try:
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)
            QApplication.processEvents()
            
            md5 = CryptEngine.file_md5(path)
            sha256 = CryptEngine.file_sha256(path)
            sha512 = CryptEngine.file_sha512(path)
            
            self.progress.setVisible(False)
            self.output_text.setText(
                f"MD5: {md5}\n"
                f"SHA-256: {sha256}\n"
                f"SHA-512: {sha512}"
            )
        except Exception as e:
            self.progress.setVisible(False)
            self.output_text.setText(f"❌ {e}")

# ==================== AES面板 ====================
class AesPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel("🔑 AES 加密/解密")
        title.setStyleSheet(f"color: {CyberTheme.NEON_PURPLE}; font-size: 16pt; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        self.key_input = QLineEdit()
        self.key_input.setStyleSheet(input_style())
        self.key_input.setPlaceholderText("密钥 (任意字符串)")
        layout.addWidget(QLabel("密钥:"))
        layout.addWidget(self.key_input)
        
        self.content_input = QTextEdit()
        self.content_input.setStyleSheet(input_style())
        self.content_input.setMaximumHeight(100)
        layout.addWidget(QLabel("内容:"))
        layout.addWidget(self.content_input)
        
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("模式:"))
        self.aes_mode = QComboBox()
        self.aes_mode.addItems(["CBC", "GCM (认证加密)"])
        self.aes_mode.setStyleSheet(input_style())
        mode_layout.addWidget(self.aes_mode)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        btn_layout = QHBoxLayout()
        enc_btn = FlatButton("🔒 加密", color=CyberTheme.NEON_PINK)
        enc_btn.clicked.connect(self.aes_encrypt)
        btn_layout.addWidget(enc_btn)
        dec_btn = FlatButton("🔓 解密", color=CyberTheme.NEON_CYAN)
        dec_btn.clicked.connect(self.aes_decrypt)
        btn_layout.addWidget(dec_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.result_text = QTextEdit()
        self.result_text.setStyleSheet(input_style())
        self.result_text.setMaximumHeight(100)
        self.result_text.setReadOnly(True)
        layout.addWidget(QLabel("结果:"))
        layout.addWidget(self.result_text)
        
        action_layout = QHBoxLayout()
        copy_btn = FlatButton("📋 复制", color=CyberTheme.NEON_GREEN)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.result_text.toPlainText()))
        action_layout.addWidget(copy_btn)
        clear_btn = FlatButton("🗑️ 清空", color=CyberTheme.NEON_ORANGE)
        clear_btn.clicked.connect(lambda: (self.content_input.clear(), self.key_input.clear(), self.result_text.clear()))
        action_layout.addWidget(clear_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
    
    def aes_encrypt(self):
        text = self.content_input.toPlainText()
        key = self.key_input.text().strip()
        if not text or not key:
            self.result_text.setText("⚠️ 请输入内容和密钥")
            return
        if self.aes_mode.currentIndex() == 0:
            self.result_text.setText(CryptEngine.aes_cbc_encrypt(text, key))
        else:
            self.result_text.setText(CryptEngine.aes_gcm_encrypt(text, key))
    
    def aes_decrypt(self):
        text = self.content_input.toPlainText()
        key = self.key_input.text().strip()
        if not text or not key:
            self.result_text.setText("⚠️ 请输入内容和密钥")
            return
        if self.aes_mode.currentIndex() == 0:
            self.result_text.setText(CryptEngine.aes_cbc_decrypt(text, key))
        else:
            self.result_text.setText(CryptEngine.aes_gcm_decrypt(text, key))

# ==================== RSA面板 ====================
class RsaPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel("🔐 RSA 非对称加密")
        title.setStyleSheet(f"color: {CyberTheme.NEON_PURPLE}; font-size: 16pt; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        gen_layout = QHBoxLayout()
        gen_btn = FlatButton("🔄 生成RSA密钥对 (2048位)", color=CyberTheme.NEON_GREEN)
        gen_btn.clicked.connect(self.generate_keys)
        gen_layout.addWidget(gen_btn)
        gen_layout.addStretch()
        layout.addLayout(gen_layout)
        
        layout.addWidget(QLabel("公钥 (PEM):"))
        self.public_key = QTextEdit()
        self.public_key.setStyleSheet(input_style())
        self.public_key.setMaximumHeight(80)
        self.public_key.setPlaceholderText("公钥将显示在这里")
        layout.addWidget(self.public_key)
        
        layout.addWidget(QLabel("私钥 (PEM):"))
        self.private_key = QTextEdit()
        self.private_key.setStyleSheet(input_style())
        self.private_key.setMaximumHeight(80)
        self.private_key.setPlaceholderText("私钥将显示在这里")
        layout.addWidget(self.private_key)
        
        self.rsa_input = QTextEdit()
        self.rsa_input.setStyleSheet(input_style())
        self.rsa_input.setMaximumHeight(80)
        layout.addWidget(QLabel("要加密/解密的内容:"))
        layout.addWidget(self.rsa_input)
        
        rsa_btn_layout = QHBoxLayout()
        rsa_enc_btn = FlatButton("🔒 公钥加密", color=CyberTheme.NEON_PINK)
        rsa_enc_btn.clicked.connect(self.rsa_encrypt)
        rsa_btn_layout.addWidget(rsa_enc_btn)
        rsa_dec_btn = FlatButton("🔓 私钥解密", color=CyberTheme.NEON_CYAN)
        rsa_dec_btn.clicked.connect(self.rsa_decrypt)
        rsa_btn_layout.addWidget(rsa_dec_btn)
        rsa_btn_layout.addStretch()
        layout.addLayout(rsa_btn_layout)
        
        self.rsa_result = QTextEdit()
        self.rsa_result.setStyleSheet(input_style())
        self.rsa_result.setMaximumHeight(80)
        self.rsa_result.setReadOnly(True)
        layout.addWidget(QLabel("结果:"))
        layout.addWidget(self.rsa_result)
        
        action_layout = QHBoxLayout()
        copy_btn = FlatButton("📋 复制", color=CyberTheme.NEON_GREEN)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.rsa_result.toPlainText()))
        action_layout.addWidget(copy_btn)
        clear_btn = FlatButton("🗑️ 清空", color=CyberTheme.NEON_ORANGE)
        clear_btn.clicked.connect(lambda: (self.rsa_input.clear(), self.rsa_result.clear()))
        action_layout.addWidget(clear_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
    
    def generate_keys(self):
        private, public = CryptEngine.rsa_generate_keypair()
        self.public_key.setText(public)
        self.private_key.setText(private)
    
    def rsa_encrypt(self):
        text = self.rsa_input.toPlainText()
        pub_key = self.public_key.toPlainText()
        if not text or not pub_key:
            self.rsa_result.setText("⚠️ 请输入内容和公钥")
            return
        self.rsa_result.setText(CryptEngine.rsa_encrypt(text, pub_key))
    
    def rsa_decrypt(self):
        text = self.rsa_input.toPlainText()
        priv_key = self.private_key.toPlainText()
        if not text or not priv_key:
            self.rsa_result.setText("⚠️ 请输入内容和私钥")
            return
        self.rsa_result.setText(CryptEngine.rsa_decrypt(text, priv_key))

# ==================== JWT面板 ====================
class JwtPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel("🎫 JWT 处理")
        title.setStyleSheet(f"color: {CyberTheme.NEON_PURPLE}; font-size: 16pt; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        self.jwt_input = QTextEdit()
        self.jwt_input.setStyleSheet(input_style())
        self.jwt_input.setMaximumHeight(80)
        self.jwt_input.setPlaceholderText("JWT Token 或 Payload JSON")
        layout.addWidget(QLabel("输入:"))
        layout.addWidget(self.jwt_input)
        
        encode_group = CyberGroupBox("🔹 JWT 编码 (生成Token)")
        encode_layout = QHBoxLayout(encode_group)
        
        encode_layout.addWidget(QLabel("密钥:"))
        self.jwt_secret = QLineEdit()
        self.jwt_secret.setStyleSheet(input_style())
        self.jwt_secret.setPlaceholderText("JWT密钥")
        encode_layout.addWidget(self.jwt_secret)
        
        encode_layout.addWidget(QLabel("算法:"))
        self.jwt_algo = QComboBox()
        self.jwt_algo.addItems(["HS256", "HS384", "HS512"])
        self.jwt_algo.setStyleSheet(input_style())
        encode_layout.addWidget(self.jwt_algo)
        
        jwt_enc_btn = FlatButton("生成JWT", color=CyberTheme.NEON_GREEN)
        jwt_enc_btn.clicked.connect(self.jwt_encode)
        encode_layout.addWidget(jwt_enc_btn)
        encode_layout.addStretch()
        layout.addWidget(encode_group)
        
        decode_group = CyberGroupBox("🔹 JWT 解码")
        decode_layout = QHBoxLayout(decode_group)
        
        jwt_dec_btn = FlatButton("解码 (不验证签名)", color=CyberTheme.NEON_CYAN)
        jwt_dec_btn.clicked.connect(self.jwt_decode)
        decode_layout.addWidget(jwt_dec_btn)
        
        decode_layout.addWidget(QLabel("验证密钥:"))
        self.jwt_verify_secret = QLineEdit()
        self.jwt_verify_secret.setStyleSheet(input_style())
        self.jwt_verify_secret.setPlaceholderText("验证签名 (可选)")
        decode_layout.addWidget(self.jwt_verify_secret)
        
        verify_btn = FlatButton("验证解码", color=CyberTheme.NEON_ORANGE)
        verify_btn.clicked.connect(self.jwt_verify_decode)
        decode_layout.addWidget(verify_btn)
        decode_layout.addStretch()
        layout.addWidget(decode_group)
        
        self.jwt_result = QTextEdit()
        self.jwt_result.setStyleSheet(input_style())
        self.jwt_result.setMaximumHeight(120)
        self.jwt_result.setReadOnly(True)
        layout.addWidget(QLabel("结果:"))
        layout.addWidget(self.jwt_result)
        
        action_layout = QHBoxLayout()
        copy_btn = FlatButton("📋 复制", color=CyberTheme.NEON_GREEN)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.jwt_result.toPlainText()))
        action_layout.addWidget(copy_btn)
        clear_btn = FlatButton("🗑️ 清空", color=CyberTheme.NEON_ORANGE)
        clear_btn.clicked.connect(lambda: (self.jwt_input.clear(), self.jwt_result.clear()))
        action_layout.addWidget(clear_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
    
    def jwt_encode(self):
        payload_text = self.jwt_input.toPlainText().strip()
        secret = self.jwt_secret.text().strip()
        if not payload_text or not secret:
            self.jwt_result.setText("⚠️ 请输入Payload JSON和密钥")
            return
        try:
            payload = json.loads(payload_text)
            algo = self.jwt_algo.currentText()
            token = CryptEngine.jwt_encode(payload, secret, algo)
            self.jwt_result.setText(token)
        except json.JSONDecodeError:
            self.jwt_result.setText("❌ 无效的JSON Payload")
        except Exception as e:
            self.jwt_result.setText(f"❌ {e}")
    
    def jwt_decode(self):
        token = self.jwt_input.toPlainText().strip()
        if not token:
            self.jwt_result.setText("⚠️ 请输入JWT Token")
            return
        try:
            result = CryptEngine.jwt_decode(token)
            self.jwt_result.setText(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            self.jwt_result.setText(f"❌ {e}")
    
    def jwt_verify_decode(self):
        token = self.jwt_input.toPlainText().strip()
        secret = self.jwt_verify_secret.text().strip()
        if not token:
            self.jwt_result.setText("⚠️ 请输入JWT Token")
            return
        if not secret:
            self.jwt_result.setText("⚠️ 请输入验证密钥")
            return
        try:
            result = CryptEngine.jwt_decode(token, secret)
            self.jwt_result.setText(json.dumps(result, indent=2, ensure_ascii=False))
        except Exception as e:
            self.jwt_result.setText(f"❌ {e}")

# ==================== 破解面板 ====================
class CrackPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel("💥 哈希破解 & 智能识别")
        title.setStyleSheet(f"color: {CyberTheme.NEON_PURPLE}; font-size: 16pt; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        crack_group = CyberGroupBox("🔹 哈希破解 (字典查找)")
        crack_layout = QVBoxLayout(crack_group)
        
        hash_row = QHBoxLayout()
        hash_row.addWidget(QLabel("哈希值:"))
        self.crack_hash = QLineEdit()
        self.crack_hash.setStyleSheet(input_style())
        self.crack_hash.setPlaceholderText("输入哈希值 (MD5/SHA1/SHA256/SHA512)")
        hash_row.addWidget(self.crack_hash)
        crack_layout.addLayout(hash_row)
        
        algo_row = QHBoxLayout()
        algo_row.addWidget(QLabel("算法:"))
        self.crack_algo = QComboBox()
        self.crack_algo.addItems(["自动检测", "md5", "sha1", "sha256", "sha512"])
        self.crack_algo.setStyleSheet(input_style())
        algo_row.addWidget(self.crack_algo)
        
        crack_btn = FlatButton("🔍 查找", color=CyberTheme.NEON_ORANGE)
        crack_btn.clicked.connect(self.hash_crack)
        algo_row.addWidget(crack_btn)
        
        rainbow_btn = FlatButton("🌈 彩虹表查找", color=CyberTheme.NEON_PINK)
        rainbow_btn.clicked.connect(self.rainbow_lookup)
        algo_row.addWidget(rainbow_btn)
        algo_row.addStretch()
        crack_layout.addLayout(algo_row)
        layout.addWidget(crack_group)
        
        detect_group = CyberGroupBox("🔹 智能编码识别")
        detect_layout = QHBoxLayout(detect_group)
        
        self.detect_input = QTextEdit()
        self.detect_input.setStyleSheet(input_style())
        self.detect_input.setMaximumHeight(60)
        self.detect_input.setPlaceholderText("输入要识别的编码文本")
        detect_layout.addWidget(self.detect_input)
        
        detect_btn = FlatButton("🔍 智能识别", color=CyberTheme.NEON_GREEN)
        detect_btn.clicked.connect(self.smart_detect)
        detect_layout.addWidget(detect_btn)
        layout.addWidget(detect_group)
        
        self.crack_result = QTextEdit()
        self.crack_result.setStyleSheet(input_style())
        self.crack_result.setMaximumHeight(150)
        self.crack_result.setReadOnly(True)
        layout.addWidget(QLabel("结果:"))
        layout.addWidget(self.crack_result)
        
        action_layout = QHBoxLayout()
        copy_btn = FlatButton("📋 复制", color=CyberTheme.NEON_GREEN)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.crack_result.toPlainText()))
        action_layout.addWidget(copy_btn)
        clear_btn = FlatButton("🗑️ 清空", color=CyberTheme.NEON_ORANGE)
        clear_btn.clicked.connect(lambda: (self.crack_result.clear(), self.crack_hash.clear(), self.detect_input.clear()))
        action_layout.addWidget(clear_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
    
    def hash_crack(self):
        hash_val = self.crack_hash.text().strip()
        if not hash_val:
            self.crack_result.setText("⚠️ 请输入哈希值")
            return
        
        algo = self.crack_algo.currentText()
        if algo == "自动检测":
            if len(hash_val) == 32:
                algo = "md5"
            elif len(hash_val) == 40:
                algo = "sha1"
            elif len(hash_val) == 64:
                algo = "sha256"
            elif len(hash_val) == 128:
                algo = "sha512"
            else:
                self.crack_result.setText("❌ 无法自动检测算法，请手动选择")
                return
        
        wordlist = [
            'password', '123456', '123456789', '12345', '12345678',
            'qwerty', 'abc123', 'football', 'monkey', 'letmein',
            'shadow', 'master', '666666', 'qwertyuiop', '123321',
            'mustang', '1234567890', 'michael', '654321', 'superman',
            '1qaz2wsx', 'baseball', 'dragon', 'fuckyou', '000000',
            'lovely', 'iloveyou', 'test', 'admin', 'password123',
            'admin123', 'root', 'toor', 'secret', 'hello', 'world'
        ]
        
        self.crack_result.setText(f"🔍 正在查找 {algo} 哈希...\n")
        QApplication.processEvents()
        
        result = CryptEngine.hash_collision_detect(hash_val, wordlist, algo)
        if result:
            self.crack_result.setText(f"✅ 找到!\n原文: {result[0]}\n哈希: {result[1]}")
        else:
            self.crack_result.setText("❌ 未在字典中找到匹配")
    
    def rainbow_lookup(self):
        hash_val = self.crack_hash.text().strip()
        if not hash_val:
            self.crack_result.setText("⚠️ 请输入哈希值")
            return
        result = CryptEngine.rainbow_table_lookup(hash_val)
        if result:
            self.crack_result.setText(f"✅ 彩虹表命中!\n{result}")
        else:
            self.crack_result.setText("❌ 彩虹表中未找到匹配")
    
    def smart_detect(self):
        text = self.detect_input.toPlainText().strip()
        if not text:
            self.crack_result.setText("⚠️ 请输入要识别的文本")
            return
        
        results = CryptEngine.smart_decode(text)
        if not results:
            self.crack_result.setText("❌ 未识别出任何编码格式")
            return
        
        output = "🔍 智能识别结果:\n\n"
        for encoding, decoded in results.items():
            output += f"━━━ {encoding.upper()} ━━━\n{decoded}\n\n"
        self.crack_result.setText(output)

# ==================== 检测面板 ====================
class DetectPanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title = QLabel("🔍 编码检测")
        title.setStyleSheet(f"color: {CyberTheme.NEON_PURPLE}; font-size: 16pt; font-weight: bold; background: transparent;")
        layout.addWidget(title)
        
        self.input_text = QTextEdit()
        self.input_text.setStyleSheet(input_style())
        self.input_text.setMaximumHeight(150)
        layout.addWidget(QLabel("输入:"))
        layout.addWidget(self.input_text)
        
        detect_btn = FlatButton("🔍 检测编码", color=CyberTheme.NEON_GREEN)
        detect_btn.clicked.connect(self.detect)
        layout.addWidget(detect_btn)
        
        self.result_text = QTextEdit()
        self.result_text.setStyleSheet(input_style())
        self.result_text.setMaximumHeight(150)
        self.result_text.setReadOnly(True)
        layout.addWidget(QLabel("结果:"))
        layout.addWidget(self.result_text)
        
        action_layout = QHBoxLayout()
        copy_btn = FlatButton("📋 复制", color=CyberTheme.NEON_GREEN)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.result_text.toPlainText()))
        action_layout.addWidget(copy_btn)
        clear_btn = FlatButton("🗑️ 清空", color=CyberTheme.NEON_ORANGE)
        clear_btn.clicked.connect(lambda: (self.input_text.clear(), self.result_text.clear()))
        action_layout.addWidget(clear_btn)
        action_layout.addStretch()
        layout.addLayout(action_layout)
    
    def detect(self):
        text = self.input_text.toPlainText()
        if not text:
            self.result_text.setText("⚠️ 请先输入文本")
            return
        try:
            data = text.encode('utf-8', errors='ignore')
            result = CryptEngine.detect_encoding(data)
            self.result_text.setText(
                f"编码: {result['encoding']}\n"
                f"置信度: {result['confidence']:.2f}\n"
                f"语言: {result['language'] if result['language'] else '未知'}"
            )
        except Exception as e:
            self.result_text.setText(f"❌ {e}")

# ==================== 主窗口 ====================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 MikanLock v3.0 · 专业加密工具箱")
        self.setMinimumSize(1050, 800)
        self.resize(1150, 850)
        self.setStyleSheet(f"background: {CyberTheme.BG};")
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        sidebar = QWidget()
        sidebar.setFixedWidth(150)
        sidebar.setStyleSheet(f"background: {CyberTheme.BG2}; border-right: 1px solid {CyberTheme.BORDER};")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(8, 12, 8, 12)
        sidebar_layout.setSpacing(4)
        
        title = QLabel("🔐\nMikanLock")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {CyberTheme.NEON_PURPLE}; font-size: 16pt; font-weight: bold; background: transparent; padding: 8px 0;")
        sidebar_layout.addWidget(title)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"background: {CyberTheme.BORDER}; max-height: 1px;")
        sidebar_layout.addWidget(line)
        
        panels = [
            ("📝 编码", EncodingPanel, CyberTheme.NEON_CYAN),
            ("🔢 进制", BaseConvertPanel, CyberTheme.NEON_YELLOW),
            ("⌨️ 键盘", KeyboardPanel, CyberTheme.NEON_ORANGE),
            ("🏛️ 经典", ClassicCipherPanel, CyberTheme.NEON_PINK),
            ("🔐 哈希", HashPanel, CyberTheme.NEON_BLUE),
            ("🔑 AES", AesPanel, CyberTheme.NEON_PURPLE),
            ("🔐 RSA", RsaPanel, CyberTheme.NEON_RED),
            ("🎫 JWT", JwtPanel, CyberTheme.NEON_GREEN),
            ("💥 破解", CrackPanel, CyberTheme.NEON_GREEN),
            ("🔍 检测", DetectPanel, CyberTheme.NEON_CYAN),
            ("📖 参考", ReferencePanel, CyberTheme.NEON_ORANGE),
        ]
        
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        
        for name, panel_class, color in panels:
            btn = FlatButton(name, color=color)
            btn.clicked.connect(lambda checked, pc=panel_class, n=name: self.switch_panel(pc, n))
            sidebar_layout.addWidget(btn)
            
            panel = panel_class()
            self.stack.addWidget(panel)
            panel.setProperty("panel_name", name)
        
        sidebar_layout.addStretch()
        version = QLabel("v3.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet(f"color: {CyberTheme.TEXT_DIM}; font-size: 8pt; background: transparent;")
        sidebar_layout.addWidget(version)
        
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack, 1)
        
        self.switch_panel(EncodingPanel, "📝 编码")
    
    def switch_panel(self, panel_class, name):
        for i in range(self.stack.count()):
            if self.stack.widget(i).property("panel_name") == name:
                self.stack.setCurrentIndex(i)
                return

# ==================== 启动 ====================
def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()