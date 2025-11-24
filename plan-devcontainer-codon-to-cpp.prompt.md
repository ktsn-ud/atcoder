# Plan: devcontainer環境のCodon削除とC++環境構築

Codon関連を削除し、C++（GCC 15.2.0）とPython（CPython 3.13 + PyPy 3.11）を導入するdevcontainer環境を構築します。ac-companion-python拡張機能のC++対応に向けたインターフェーススクリプトも作成します。

## Steps

### 1. Codon関連の削除と基本設定の変更

**ファイル**: `.devcontainer/devcontainer.json`

- コンテナ名を `atcoder-ubuntu24-python313-codon` から `atcoder-ubuntu24-cpp-python` に変更
- `containerEnv` から `CODON_VERSION` を削除
- `containerEnv` の `PYPY_VERSION` を `7.3.16` のまま維持（PyPy 3.11相当）
- `updateContentCommand` から `install_codon` を削除
- `updateContentCommand` に `install_cpp` を追加
- Python関連の設定は維持

**ファイル**: `.devcontainer/scripts/install_codon` (削除)

**ファイル**: `.devcontainer/scripts/install_python` (削除)

### 2. Python環境の公式feature化

**ファイル**: `.devcontainer/devcontainer.json`

- `features` セクションの `ghcr.io/devcontainers/features/python:1` で `version: "3.13"` を維持
- これにより公式featureからCPython 3.13がインストールされる

**ファイル**: `.devcontainer/scripts/install_pypy`

- バージョンを `PYPY_VERSION="${PYPY_VERSION:-7.3.16}"` のまま維持
- これはPyPy 3.11 (v7.3.16) をインストール
- シンボリックリンクの作成処理は維持

**ファイル**: `.devcontainer/Dockerfile`

- `ENV PATH=/workspaces/atcoder:${PIPX_BIN_DIR}:/home/vscode/.codon/bin:${PATH}` から `:/home/vscode/.codon/bin` を削除
- C++環境用のPATH追加: `ENV PATH=/opt/atcoder/gcc/bin:/workspaces/atcoder:${PIPX_BIN_DIR}:${PATH}`
- `LD_LIBRARY_PATH` を追加: `ENV LD_LIBRARY_PATH=/opt/atcoder/gcc/lib64:/opt/atcoder/gcc/lib:${LD_LIBRARY_PATH:-}`

### 3. C++環境構築スクリプトの作成

**ファイル**: `.devcontainer/scripts/install_cpp` (新規作成)

`cpp.toml` の `install` スクリプトをベースに、以下のライブラリをインストール:

**インストールライブラリ**:
- GCC 15.2.0 (コンパイラ)
- ac-library 1.6 (ワークスペースから `/opt/atcoder/gcc/include` へコピー)

**インストール先**: `/opt/atcoder/gcc`

**環境変数**:
- `AC_VARIANT=gcc` (GCCのみ)
- `AC_INSTALL_DIR=/opt/atcoder/gcc`
- `AC_TEMP_DIR=/tmp/atcoder/gcc`

**最適化**:
- ccacheが利用可能な場合は有効化
- ビルドの並列度: `$(nproc)+2`
- sudoで実行（rootユーザーとして）

**スクリプト構造**:
```bash
#!/usr/bin/env bash
set -euo pipefail

# cpp.tomlのinstallスクリプトから以下のみを抽出:
# - 基本変数設定とディレクトリ作成
# - 必要ツールのインストール (git, cmake, lld, ninja-build, pigz)
# - GCCビルド (VERSION="15.2.0")
# - ac-libraryのコピー (ワークスペース /workspaces/atcoder/ac-library から)
# - /etc/atcoder/install_dir.txt への記録
# - 最小限の依存パッケージのみ
```

### 4. C++用インターフェーススクリプトの作成

ac-companion拡張機能から呼び出されるシェルスクリプトを作成します。ojは使用せず、ac-companionがテストケース作成・実行を担当します。

**ファイル**: `cpp_compile` (新規作成、ワークスペース直下)

```bash
#!/usr/bin/env bash
# C++コンパイルスクリプト (ac-companion用)
# Usage: cpp_compile <contest_id> <task_id>

set -euo pipefail

if [ $# -ne 2 ]; then
    echo "Usage: cpp_compile <contest_id> <task_id>" >&2
    exit 1
fi

CONTEST_ID="$1"
TASK_ID="$2"
WORKSPACE_DIR="${WORKSPACE_DIR:-/workspaces/atcoder}"
TASK_DIR="$WORKSPACE_DIR/$CONTEST_ID/$TASK_ID"

if [ ! -f "$TASK_DIR/main.cpp" ]; then
    echo "Error: main.cpp not found in $TASK_DIR" >&2
    exit 1
fi

cd "$TASK_DIR"

# コンパイルフラグ (最小限)
INSTALL_DIR="/opt/atcoder/gcc"
COMPILE_FLAGS=(
    "-DATCODER"
    "-DONLINE_JUDGE"
    "-I$INSTALL_DIR/include"
    "-O2"
    "-std=gnu++23"
    "-march=native"
)

echo "[cpp_compile] Compiling main.cpp in $TASK_DIR"
g++ main.cpp -o a.out "${COMPILE_FLAGS[@]}"

if [ -f "./a.out" ]; then
    echo "[cpp_compile] Compilation successful: a.out"
    exit 0
else
    echo "[cpp_compile] Compilation failed" >&2
    exit 1
fi
```

**ファイル**: `cpp_run` (新規作成、ワークスペース直下)

```bash
#!/usr/bin/env bash
# C++実行スクリプト (ac-companion用)
# Usage: cpp_run <contest_id> <task_id> [input_file]
# input_file: 省略時は標準入力から、指定時はファイルから読み込む

set -euo pipefail

if [ $# -lt 2 ]; then
    echo "Usage: cpp_run <contest_id> <task_id> [input_file]" >&2
    exit 1
fi

CONTEST_ID="$1"
TASK_ID="$2"
INPUT_FILE="${3:-}"
WORKSPACE_DIR="${WORKSPACE_DIR:-/workspaces/atcoder}"
TASK_DIR="$WORKSPACE_DIR/$CONTEST_ID/$TASK_ID"

if [ ! -f "$TASK_DIR/a.out" ]; then
    echo "Error: a.out not found. Run cpp_compile first." >&2
    exit 1
fi

cd "$TASK_DIR"

if [ -n "$INPUT_FILE" ]; then
    if [ ! -f "$INPUT_FILE" ]; then
        echo "Error: Input file $INPUT_FILE not found" >&2
        exit 1
    fi
    exec ./a.out < "$INPUT_FILE"
else
    exec ./a.out
fi
```

**ファイル**: `cpp_test` は削除 (ac-companionがテスト実行を担当)

**実行権限**: 2つのスクリプトに実行権限を付与 (`chmod +x`)

### 5. VSCode設定の更新

**ファイル**: `.devcontainer/devcontainer.json`

**VSCode拡張機能の追加**:
```jsonc
"extensions": [
    // Python (既存)
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    // C++ (新規)
    "ms-vscode.cpptools",
    "ms-vscode.cmake-tools"
]
```

**VSCode設定の追加**:
```jsonc
"settings": {
    // 既存のPython設定は維持
    "terminal.integrated.defaultProfile.linux": "bash",
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "github.copilot.nextEditSuggestions.enabled": false,
    
    // C++設定 (新規)
    "[cpp]": {
        "editor.defaultFormatter": "ms-vscode.cpptools"
    },
    "C_Cpp.default.cppStandard": "c++23",
    "C_Cpp.default.includePath": [
        "/opt/atcoder/gcc/include",
        "${workspaceFolder}/**"
    ],
    "C_Cpp.default.compilerPath": "/opt/atcoder/gcc/bin/g++"
}
```

**環境変数の更新**:
```jsonc
"containerEnv": {
    "PIPX_BIN_DIR": "/home/vscode/.local/bin",
    "PIPX_HOME": "/home/vscode/.local/pipx",
    "PYPY_VERSION": "7.3.16",
    "AC_EXT_VERSION": "1.1.3",
    "ATCODER_CPP_INSTALL_DIR": "/opt/atcoder/gcc"
}
```

**updateContentCommand**:
```jsonc
"updateContentCommand": "bash .devcontainer/scripts/install_pypy && bash .devcontainer/scripts/install_cpp && python3 -m pip install --user --no-cache-dir -r requirements.txt && chmod +x cpp_compile cpp_run"
```

### 6. ドキュメントとテンプレートの更新

**ファイル**: `README.md`

- タイトルを「AtCoder環境（PyPy, Codon）」から「AtCoder環境（C++, Python）」に変更
- Dev Container説明を更新:
  - CPython 3.13 (公式feature)
  - PyPy 3.11 (v7.3.16)
  - GCC 15.2.0 + ac-library (最小限)
- `contest`コマンドの説明は維持
- C++用コマンド (`cpp_compile`, `cpp_run`) の説明を追加
- ojの説明は削除（使用しないため）
- Codon関連の説明を削除

**ファイル**: `.config/templates/main.cpp` (新規作成)

最小限のテンプレート:
```cpp
#include <bits/stdc++.h>
using namespace std;

int main() {
    
    return 0;
}
```

**注意**: ファイル名は `Main.cpp` ではなく `main.cpp` で統一します。

**ファイル**: `.config/templates/main.py` (既存、変更なし)

Pythonテンプレートは既存のまま維持

## Further Considerations

### 1. ビルド時間とコンテナサイズ

GCC 15.2.0のビルドには30-60分程度かかる可能性があります（ライブラリを最小限にしたため、以前の1時間以上から大幅に短縮）。初回ビルド後はキャッシュが効きます:

- **Option A (推奨)**: そのままビルド - 初回のみ時間がかかるが、以降はキャッシュが効く
- **Option B**: ccache有効化 - `install_cpp`でccacheの検出と有効化は既に実装済み
- **Option C**: プリビルドイメージ使用 - Docker Hubなどで事前ビルドしたイメージを配布

**推奨**: Option A (ccacheは自動検出で有効化される)

### 2. C++テンプレートファイルの内容

`main.cpp`のテンプレートは最小限で実装:

- `#include <bits/stdc++.h>`
- `using namespace std;`
- 空の`main()`関数のみ

ユーザーが好みのマクロやtypedefを追加しやすいシンプルな構成です。

### 3. ac-companion拡張機能のC++対応

ac-companion-python拡張機能のC++対応には以下が必要です（実装は別途）:

1. **設定追加**:
   - `ac-companion-python.cppCompileCommand`: `"${workspaceFolder}/cpp_compile"`
   - `ac-companion-python.cppRunCommand`: `"${workspaceFolder}/cpp_run"`
   - `ac-companion-python.language`: `"python"` | `"cpp"` (言語選択)

2. **テンプレート対応**:
   - `ac-companion-python.templateFilePath` を言語別に分岐
   - Python: `.config/templates/main.py`
   - C++: `.config/templates/main.cpp`

3. **ファイル名対応**:
   - Python: `main.py`
   - C++: `main.cpp` (統一)

4. **実行フロー**:
   - C++選択時: 
     1. `cpp_compile <contest_id> <task_id>` でコンパイル
     2. テストケースごとに `cpp_run <contest_id> <task_id> <input_file>` を実行
     3. 出力を期待値と比較（ac-companion内部で実施）
   - Python選択時: 既存の動作を維持

5. **テスト実行の詳細**:
   - ac-companionが `tests/` ディレクトリ内の `.in` ファイルを検出
   - 各 `.in` ファイルに対して `cpp_run` を実行し、標準出力を取得
   - 対応する `.out` ファイルと比較して AC/WA を判定
   - タイムアウト処理も ac-companion 側で実装

## Installation Order

1. Dockerfile (基本パッケージ)
2. devcontainer.json の features (CPython 3.13)
3. install_pypy (PyPy 3.11)
4. install_cpp (GCC 15.2.0 + ac-library、30-60分程度)
5. Python requirements.txt
6. C++スクリプトに実行権限付与

## Testing Checklist

初回ビルド後の確認項目:

- [ ] `g++ --version` で GCC 15.2.0 が表示される
- [ ] `/opt/atcoder/gcc/include/atcoder/` に ac-library が存在する
- [ ] `python3 --version` で Python 3.13.x が表示される
- [ ] `pypy3 --version` で PyPy 7.3.16 (Python 3.11.x) が表示される
- [ ] `cpp_compile`, `cpp_run` が実行可能
- [ ] サンプルC++コード (`main.cpp`) がコンパイル・実行できる
- [ ] VSCode C++ IntelliSenseが `/opt/atcoder/gcc/include` を認識する

## File Summary

### 削除
- `.devcontainer/scripts/install_codon`
- `.devcontainer/scripts/install_python`

### 変更
- `.devcontainer/devcontainer.json`
- `.devcontainer/Dockerfile`
- `.devcontainer/scripts/install_pypy`
- `README.md`

### 新規作成
- `.devcontainer/scripts/install_cpp`
- `cpp_compile`
- `cpp_run`
- `.config/templates/main.cpp`
