# HelloDSH —— 在 Windows 上产出可自签的 iOS IPA

一个**纯手写、零第三方依赖**的 SwiftUI 工程。Windows 电脑不可能本地编译 iOS，
所以这里用 **GitHub Actions 的免费 macOS 机器**把工程编译成**未签名 IPA**，
再由你用**全能签**签名安装到手机。

```
Windows 写代码  →  GitHub Actions (macOS) 编译  →  未签名 .ipa  →  全能签签名  →  iPhone
```

---

## 一、最快路径：三个动作

### 动作 1：拿一个 GitHub Token

打开（只勾 `repo`，30 天有效期就够用了）：

```
https://github.com/settings/tokens/new?scopes=repo&description=dsh-ios-build
```

点最下方 **Generate token**，把 `ghp_...` 那串复制下来（**只显示一次**）。

### 动作 2：双击运行

打开 `D:\dsh-scratch\ios-app\`，双击 **`一键出包.bat`**。

把 Token 粘进去回车。脚本会自己完成：

1. 校验 Token，取回你的用户名
2. 建一个**私有**仓库 `ios-hello-dsh`
3. 把工程 9 个文件全部上传（走 GitHub API，**不需要你装 git**）
4. 触发编译工作流
5. 轮询等编译完成（一般 3–6 分钟）
6. 把 IPA 下载到 `D:\dsh-scratch\ios-app\out\`

> 想建公开仓库：`pwsh -File ship.ps1 -Token "ghp_xxx" -Public`

### 动作 3：用全能签签名安装

1. 把 `D:\dsh-scratch\ios-app\out\*.ipa` 传到手机（微信/QQ/隔空投送/数据线都行）
2. 全能签 → **导入 IPA** → 选中这个文件
3. 签名时 Bundle ID 用 `com.dsh.hellodsh`（或全能签自动分配）
4. 签名完成 → 安装 → 首次打开如果提示"不受信任"，去
   **设置 → 通用 → VPN与设备管理** 里信任对应证书

---

## 二、验证点：怎么确认它真的成功了

装好后 App 长这样，看到这些就说明链路完全打通：

| 现象 | 说明什么 |
|---|---|
| 主屏出现带渐变图标的 **HelloDSH** | IPA 结构正确、图标资源被编译进包了 |
| 打开显示 `Hello, iPhone` + `自签链路已打通` | SwiftUI 正常运行 |
| 显示 `iOS xx.x · iPhone` | 系统 API 可调用 |
| 点按钮数字会涨 | 原生交互生效，不是网页套壳 |

---

## 三、工程结构

```
HelloDSH/
├─ .github/workflows/build-ipa.yml          # 云端编译流程（macOS 上跑 xcodebuild）
├─ .gitignore
├─ HelloDSH.xcodeproj/
│  ├─ project.pbxproj                       # 手写的工程文件
│  └─ xcshareddata/xcschemes/HelloDSH.xcscheme
└─ HelloDSH/
   ├─ HelloDSHApp.swift                     # @main 入口
   ├─ ContentView.swift                     # 界面
   ├─ Assets.xcassets/AppIcon.appiconset/   # 1024×1024 图标
   ├─ Info.plist
   └─ HelloDSH.entitlements
```

关键编译参数（都在 `build-ipa.yml` 里）：

```
CODE_SIGN_IDENTITY=""          关闭签名
CODE_SIGNING_REQUIRED=NO       不要求签名证书
CODE_SIGNING_ALLOWED=NO        连 ad-hoc 签名都不做
CODE_SIGN_ENTITLEMENTS=""      不带 entitlements
DEVELOPMENT_TEAM=""            不需要开发者账号
```

出来的包**故意不带 `_CodeSignature`**，这样全能签会走它自己的签名流程，
不会被残留签名干扰。

---

## 四、手动改工程时注意

- 部署目标 `IPHONEOS_DEPLOYMENT_TARGET = 16.0`，想支持更老系统就调低它。
- Bundle ID `com.dsh.hellodsh`，改这里要同步改签名工具里的 ID。
- 加新的 `.swift` 文件时，**必须同时**在 `project.pbxproj` 里加
  `PBXFileReference` + `PBXBuildFile` + `PBXSourcesBuildPhase` 三处引用，
  否则编译不进包。（这是手写工程的唯一门槛）
- 本地自检脚本：`python D:\dsh-scratch\ios-app\verify_project.py`
  会检查对象引用完整性、plist 格式、scheme XML、工作流 YAML。

---

## 五、常见故障

| 现象 | 原因 | 处理 |
|---|---|---|
| 工作流报 `No profiles for 'com.dsh.hellodsh' were found` | 签名没关干净 | 确认命令里四个 `CODE_SIGN*` 参数都在 |
| 工作流报 `xcodebuild: error: The project does not contain a scheme named` | scheme 目录名写错 | 必须是 `xcshareddata/xcschemes/`（不是 `xschemes`） |
| 上传时 403 | Token 没勾 `repo` | 重新生成 Token |
| 上传时 404 on contents | 仓库是空的、没默认分支 | 脚本已自动建 `main` 分支，正常不会遇到 |
| 全能签签名后装不上 | Bundle ID 与证书不匹配 / 证书掉签 | 换证书，或让全能签自动分配 Bundle ID |
| 装上了点开闪退 | 极少见，通常是证书问题 | 换证书重签 |
| 工件下载 404 | artifact 过期（30 天） | 重新跑一次工作流 |
