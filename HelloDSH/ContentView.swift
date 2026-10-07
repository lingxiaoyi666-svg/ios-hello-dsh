import SwiftUI

struct ContentView: View {
    @State private var tappedCount = 0

    /// 应用版本号，取自 Bundle（与 Xcode 工程里的 MARKETING_VERSION 一致）
    private var appVersion: String {
        let v = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "?"
        let b = Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "?"
        return "\(v) (\(b))"
    }

    var body: some View {
        VStack(spacing: 22) {
            Image(systemName: "iphone.gen3.radiowaves.left.and.right")
                .font(.system(size: 72))
                .foregroundStyle(.tint)

            Text("Hello, iPhone")
                .font(.largeTitle.bold())

            Text("自签链路已打通")
                .font(.title3)
                .foregroundStyle(.secondary)

            Text("iOS \(UIDevice.current.systemVersion)  ·  \(UIDevice.current.model)")
                .font(.footnote)
                .foregroundStyle(.tertiary)

            Text("App 版本 \(appVersion)")
                .font(.footnote)
                .foregroundStyle(.tertiary)

            Button {
                tappedCount += 1
            } label: {
                Label("点我一下（\(tappedCount)）", systemImage: "hand.tap")
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)

            Text(tappedCount == 0 ? "按钮能动，说明 native 代码在跑" : "交互正常，这不是网页套壳")
                .font(.caption)
                .foregroundStyle(.secondary)

            Spacer()
        }
        .padding(28)
        .animation(.default, value: tappedCount)
    }
}
