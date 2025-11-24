# AtCoder 環境（C++, Python）

このリポジトリは AtCoder のコンテストに特化した開発環境です。VS Code Dev Container を使用して、C++ (GCC 15.2.0 + ac-library) と Python (CPython 3.13 / PyPy 3.10) の双方を統合し、ac-companion 拡張との連携によるスムーズなビルド・実行フローを提供します。

## 推奨環境: Dev Container

### 前提条件

- Docker Desktop または同等のコンテナ実行環境
- Visual Studio Code
- VS Code 拡張: [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

### セットアップ

1. このリポジトリをクローンし、VS Code でフォルダを開く
   ```bash
   git clone <repository-url>
   code atcoder
   ```

2. コマンドパレット（Cmd/Ctrl + Shift + P）で「Dev Containers: Reopen in Container」を実行

3. コンテナ構築中に自動実行されるセットアップスクリプト（`updateContentCommand`）で以下がインストールされます:
   - PyPy 3.10 (v7.3.16)
   - GCC 15.2.0 + ac-library
   - Python 依存パッケージ
   - ac-companion 拡張 v2.0.0

> Dev Container 内では `/workspaces/atcoder/` がワークスペース根となります。スクリプトはこのパスを前提に動作します。

## リポジトリ構成

```
.devcontainer/          # Dev Container 設定
  ├── Dockerfile        # コンテナイメージ定義
  ├── devcontainer.json # Dev Container メタデータ
  └── scripts/
      ├── install_pypy        # PyPy インストール
      ├── install_cpp         # GCC + ac-library インストール
      └── install_ac_extension # ac-companion 拡張インストール

ac-library/             # AtCoder Library (ヘッダファイル)

atcoder/                # Python atcoder ライブラリ

cpp_compile             # C++ コンパイルスクリプト
cpp_run                 # C++ 実行スクリプト

abc431/, abc432/, ...   # コンテスト問題ディレクトリ

requirements.txt        # Python 依存パッケージ
```

## 開発フロー

### Python での開発

```bash
# 通常実行（CPython 3.13）
python3 main.py < tests/1.in

# PyPy での高速実行
pypy3 main.py < tests/1.in
```

### C++ での開発

```bash
# コンパイル（ac-companion から自動実行）
./cpp_compile abc431 abc431_a

# 実行
./cpp_run abc431 abc431_a tests/1.in
```

コンパイルフラグ: `-I/opt/atcoder/gcc/include -O2 -std=gnu++23 -march=native`

## スクリプト詳細

### `cpp_compile <contest_id> <task_id>`

- `<contest_id>/<task_id>/main.cpp` をコンパイル
- `a.out` を生成
- ac-companion が問題実行時に自動呼び出し

### `cpp_run <contest_id> <task_id> [input_file]`

- `a.out` を実行
- `input_file` が指定されれば標準入力として使用
- ac-companion のテスト実行に対応

## Python 環境

- **CPython 3.13**: 標準 Python インタプリタ（開発・デバッグ用）
- **PyPy 3.10**: 高速実行用（本番テスト向け）

両者は同じ `requirements.txt` に基づいて依存パッケージがインストールされます:
- `sortedcontainers`

### 依存パッケージの追加

```bash
# requirements.txt に追加
echo "package_name" >> requirements.txt

# インストール
python3 -m pip install --user -r requirements.txt
```

## ローカル環境での構築（Dev Container 不使用）

Dev Container を使わない場合は、以下の手順で同等の環境をホスト OS 上に構築できます。

### 必要なツール

```bash
# Ubuntu/Debian の場合
sudo apt-get update
sudo apt-get install -y build-essential git cmake lld ninja-build \
    bison flex libgmp-dev libmpfr-dev libmpc-dev libisl-dev \
    curl wget ca-certificates xz-utils ccache
```

### インストール手順

```bash
# 1. PyPy をインストール（非 root ユーザーで実行）
bash .devcontainer/scripts/install_pypy

# 2. GCC 15.2.0 + ac-library をインストール
sudo AC_INSTALL_DIR=/opt/atcoder/gcc \
     WORKSPACE_DIR="$(pwd)" \
     bash .devcontainer/scripts/install_cpp

# 3. Python 依存パッケージをインストール
python3 -m pip install --user -r requirements.txt

# 4. スクリプトに実行権限を付与
chmod +x cpp_compile cpp_run

# 5. シェルを再読み込み
exec $SHELL
```

### PATH の設定

`~/.bashrc` または `~/.zshrc` に以下を追加:

```bash
export PATH="$HOME/.local/pypy3/bin:$PATH"
export PATH="/opt/atcoder/gcc/bin:$PATH"
export LD_LIBRARY_PATH="/opt/atcoder/gcc/lib64:/opt/atcoder/gcc/lib:$LD_LIBRARY_PATH"
```

### 動作確認

```bash
g++ --version          # GCC 15.2.0 であることを確認
pypy3 --version        # PyPy 3.10 であることを確認
python3 -m pip list    # sortedcontainers がリストに含まれることを確認
```

## トラブルシューティング

### `g++` が見つからない / バージョンが異なる

```bash
# PATH 確認
which g++
g++ --version

# Dev Container の場合: コンテナを再構築
# Dev Containers: Rebuild Container を実行

# ローカルの場合: install_cpp を再実行
sudo AC_INSTALL_DIR=/opt/atcoder/gcc bash .devcontainer/scripts/install_cpp
```

### ac-library が参照できない

```bash
# ヘッダファイルの確認
ls /opt/atcoder/gcc/include/atcoder

# 見つからない場合は再インストール
sudo rm -rf /opt/atcoder/gcc/include/atcoder
sudo AC_INSTALL_DIR=/opt/atcoder/gcc \
     WORKSPACE_DIR="$(pwd)" \
     bash .devcontainer/scripts/install_cpp
```

### `pypy3` が見つからない

```bash
# PyPy インストール位置確認
ls ~/.local/pypy3/bin/pypy3

# PATH 確認
echo $PATH | grep pypy3

# PATH に追加されていない場合: シェルを再起動
exec $SHELL

# それでも見つからない場合は再インストール
bash .devcontainer/scripts/install_pypy
```

### VS Code で C++ インテリセンス（IntelliSense）が機能しない

Dev Container の場合、`.devcontainer/devcontainer.json` で以下を確認:

```json
"C_Cpp.default.includePath": ["/opt/atcoder/gcc/include", "${workspaceFolder}/**"],
"C_Cpp.default.compilerPath": "/opt/atcoder/gcc/bin/g++"
```

ローカル環境の場合は、VS Code の C/C++ 拡張設定（`.vscode/settings.json` など）で同等の設定を手動で追加してください。

### コンテナ構築に失敗する

```bash
# コンテナイメージをリセット
docker system prune -a

# コンテナを再構築
# Dev Containers: Rebuild Container を実行
```

## ac-companion 拡張との連携

[ac-companion](https://github.com/ktsn-ud/ac-companion) は、AtCoder 問題の自動生成・テスト実行に対応した VS Code 拡張です。

- 問題ファイルの自動生成
- サンプルテスト（input/output）の自動化
- `cpp_compile` / `cpp_run` との統合実行

詳細は [ac-companion ドキュメント](https://github.com/ktsn-ud/ac-companion) を参照してください。

## 参考

- [AtCoder](https://atcoder.jp/)
- [ac-library](https://atcoder.jp/documents/ac-library/)
- [ac-companion](https://github.com/ktsn-ud/ac-companion)
