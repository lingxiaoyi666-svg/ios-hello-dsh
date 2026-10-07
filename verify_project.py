#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""静态自检：pbxproj 对象引用完整性 + plist 格式（无需 Xcode）"""
import re, sys, plistlib, pathlib

ROOT = pathlib.Path(r"D:\dsh-scratch\ios-app\HelloDSH")
pbx_path = ROOT / "HelloDSH.xcodeproj" / "project.pbxproj"
text = pbx_path.read_text(encoding="utf-8")

fails = []

# ---- 1. 括号/花括号/引号平衡 ----
for open_c, close_c, label in (("{", "}", "花括号"), ("(", ")", "圆括号")):
    n_o, n_c = text.count(open_c), text.count(close_c)
    status = "OK " if n_o == n_c else "FAIL"
    if n_o != n_c:
        fails.append(f"{label}不平衡 {n_o} vs {n_c}")
    print(f"[{status}] {label}平衡: {n_o} / {n_c}")

# ---- 2. 所有被引用的对象 ID 都必须被定义 ----
# 定义形式: \t\tID /* comment */ = {  或  \t\tID = {
# 也支持 "ID /* ... */ = {"  以及无注释
defined = set(re.findall(r"^\t\t([A-F0-9]{24})\b[^\n]*=\s*\{", text, re.M))
defined |= set(re.findall(r"^\t\t([A-F0-9]{24})\s*=", text, re.M))
# 根对象也是定义
root = re.search(r"rootObject\s*=\s*([A-F0-9]{24})", text)
defs = set(defined)
if root:
    defs.add(root.group(1))

all_ids = set(re.findall(r"\b([A-F0-9]{24})\b", text))
missing = sorted(all_ids - defs)
orphan = sorted(defs - all_ids)

print(f"\n[{'OK ' if not missing else 'FAIL'}] 定义 {len(defs)} 个对象 / 引用 {len(all_ids)} 个 ID")
if missing:
    fails.append(f"引用了未定义的 ID: {missing}")
    for m in missing:
        for i, line in enumerate(text.splitlines(), 1):
            if m in line:
                print(f"  MISSING {m} -> 第 {i} 行: {line.strip()[:120]}")
                break
else:
    print("  所有引用都有定义")
if orphan:
    print(f"  (提示) 只定义未被引用的 ID: {orphan}")

# ---- 3. 关键 build settings 抽查 ----
need = [
    "PRODUCT_BUNDLE_IDENTIFIER = com.dsh.hellodsh",
    "IPHONEOS_DEPLOYMENT_TARGET = 16.0",
    "SDKROOT = iphoneos",
    "SWIFT_VERSION = 5.0",
    "INFOPLIST_FILE = HelloDSH/Info.plist",
    'CODE_SIGN_IDENTITY = ""',
]
print()
for n in need:
    hit = n in text
    if not hit:
        fails.append(f"缺少 build setting: {n}")
    print(f"[{'OK ' if hit else 'FAIL'}] {n}")

# ---- 4. Sources 构建阶段必须包含两个 .swift ----
src_block = re.search(r"PBXSourcesBuildPhase section \*/(.*?)/\* End PBXSourcesBuildPhase", text, re.S)
if src_block:
    swift_refs = re.findall(r"([A-F0-9]{24}) /\* ([^*]+?) in Sources \*/", src_block.group(1))
    names = [n.strip() for _, n in swift_refs]
    ok = "HelloDSHApp.swift" in names and "ContentView.swift" in names
    if not ok:
        fails.append(f"Sources 阶段文件异常: {names}")
    print(f"[{'OK ' if ok else 'FAIL'}] Sources 阶段: {names}")
else:
    fails.append("找不到 PBXSourcesBuildPhase")
    print("[FAIL] 找不到 PBXSourcesBuildPhase")

# ---- 5. plist 解析 ----
print()
for p in ("HelloDSH/Info.plist", "HelloDSH/HelloDSH.entitlements"):
    fp = ROOT / p
    try:
        data = plistlib.loads(fp.read_bytes())
        print(f"[OK ] {p} 可解析，{len(data)} 个键: {list(data)[:4]}...")
    except Exception as e:
        fails.append(f"{p} 解析失败: {e}")
        print(f"[FAIL] {p} 解析失败: {e}")

# ---- 6. xcscheme XML ----
import xml.etree.ElementTree as ET
for p in ("HelloDSH.xcodeproj/xcshareddata/xcschemes/HelloDSH.xcscheme",
          ".github/workflows/build-ipa.yml"):
    fp = ROOT.joinpath(*p.split("/"))
    if p.endswith(".xcscheme"):
        try:
            ET.parse(fp); print(f"[OK ] {p} XML 合法")
        except Exception as e:
            fails.append(f"{p} XML 错误: {e}"); print(f"[FAIL] {p} XML 错误: {e}")
    else:
        try:
            import yaml
            yaml.safe_load(fp.read_text(encoding="utf-8")); print(f"[OK ] {p} YAML 合法")
        except ImportError:
            print(f"[SKIP] {p} 无 pyyaml，跳过")
        except Exception as e:
            fails.append(f"{p} YAML 错误: {e}"); print(f"[FAIL] {p} YAML 错误: {e}")

# ---- 7. 文件清单 ----
print("\n=== 工程文件清单 ===")
for f in sorted(ROOT.rglob("*")):
    if f.is_file():
        rel = f.relative_to(ROOT)
        print(f"  {f.stat().st_size:>7} B  {rel}")

print("\n" + "=" * 46)
if fails:
    print(f"结果: {len(fails)} 项失败")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("结果: 全部通过")
