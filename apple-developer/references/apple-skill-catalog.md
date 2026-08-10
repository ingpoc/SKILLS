# Apple Skill Catalog

Use this catalog to route Apple-platform work without loading or installing a
large skill bundle. Apple documentation and the project's canonical owners
remain authoritative.

## Installed locally

Invoke an installed skill by name when its scope fits the task.

| Skill | Refer for | Local path | Upstream |
| --- | --- | --- | --- |
| `apple-developer` | Signing, certificates, profiles, capabilities, App Groups, App Store Connect, TestFlight, Developer ID, and notarization | `~/.codex/skills/apple-developer` | Local owner |
| `xcode-cloud` | Apple-native CI/CD, clean-clone bootstrap, compute controls, TestFlight delivery, and cloud proof gates | `~/.codex/skills/xcode-cloud` | Local owner |
| `widgetkit` | Timeline providers, refresh budgets, App Group data sharing, widget families, and extension review | `~/.codex/skills/widgetkit` | [Source](https://github.com/dpearson2699/swift-ios-skills/tree/main/skills/widgetkit) |
| `swiftui-pro` | Modern SwiftUI design, state, navigation, accessibility, performance, and API review | `~/.codex/skills/swiftui-pro` | [Source](https://github.com/twostraws/swiftui-agent-skill/tree/main/swiftui-pro) |
| `macos-widget-reinstall` | Local macOS WidgetKit reinstall, registration recovery, and visible verification | `~/.codex/skills/macos-widget-reinstall` | Local owner |

Check the live skill inventory supplied to the agent before assuming a local
path is installed. A newly installed global skill becomes available on the
next agent turn or session.

## Available from the web

The upstream [Swift iOS Skills catalog](https://github.com/dpearson2699/swift-ios-skills#skills)
currently provides 86 independent skills. The project explicitly says each
skill is self-contained, so select only the narrow skill needed. This index is
a discovery snapshot from 2026-07-25; check the live catalog for additions,
renames, removals, and license changes.

### SwiftUI

`focus-engine`, `swiftui-animation`, `swiftui-gestures`,
`swiftui-layout-components`, `swiftui-liquid-glass`, `swiftui-navigation`,
`swiftui-patterns`, `swiftui-performance`, `swiftui-uikit-interop`,
`swiftui-webkit`

### Core Swift

`swift-api-design-guidelines`, `swift-architecture`, `swift-codable`,
`swift-charts`, `swift-concurrency`, `swift-formatstyle`, `swift-language`,
`swift-testing`, `core-data`, `swiftdata`

### App experience frameworks

`activitykit`, `adattributionkit`, `alarmkit`, `app-clips`, `app-intents`,
`avkit`, `carplay`, `mapkit`, `paperkit`, `pdfkit`, `photokit`,
`push-notifications`, `storekit`, `tipkit`, `widgetkit`

### Data and service frameworks

`cloudkit`, `contacts-framework`, `eventkit`, `financekit`, `healthkit`,
`musickit`, `passkit`, `weatherkit`

### AI and machine learning

`apple-on-device-ai`, `coreml`, `natural-language`, `speech-recognition`,
`vision-framework`

### iOS engineering

`app-store-optimization`, `app-store-review`, `authentication`,
`background-processing`, `cryptokit`, `debugging-instruments`,
`device-integrity`, `ios-accessibility`, `ios-ettrace-performance`,
`ios-localization`, `ios-memgraph-analysis`, `ios-networking`,
`swift-security`, `ios-simulator`, `metrickit`, `swiftlint`

### Hardware and device integration

`accessorysetupkit`, `core-bluetooth`, `core-motion`, `core-nfc`, `dockkit`,
`pencilkit`, `realitykit`, `sensorkit`

### Platform integration

`appmigrationkit`, `audioaccessorykit`, `browserenginekit`, `callkit`,
`cryptotokenkit`, `energykit`, `homekit`, `permissionkit`, `relevancekit`,
`shareplay-activities`

### Gaming

`gamekit`, `scenekit`, `spritekit`, `tabletopkit`

SwiftUI Pro is maintained separately at
[twostraws/swiftui-agent-skill](https://github.com/twostraws/swiftui-agent-skill).

## Install one skill

Before installing, confirm the skill is absent from the live agent inventory
and `~/.codex/skills`. Read its `SKILL.md`, repository license, and recent
source history. The Swift iOS Skills repository currently uses the PolyForm
Perimeter License; SwiftUI Pro currently uses MIT. Recheck rather than relying
on this snapshot.

Install one Swift iOS Skills entry:

```sh
installer="${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer"
/usr/bin/python3 "$installer/scripts/install-skill-from-github.py" \
  --repo dpearson2699/swift-ios-skills \
  --path skills/<skill-name>
```

Install SwiftUI Pro:

```sh
installer="${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer"
/usr/bin/python3 "$installer/scripts/install-skill-from-github.py" \
  --repo twostraws/swiftui-agent-skill \
  --path swiftui-pro
```

Do not install the complete 86-skill collection. After installation, inspect
the created folder and use the new skill on the next agent turn or session.
