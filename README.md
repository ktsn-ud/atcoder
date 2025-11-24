# AtCoder環境（C++, Python）

このリポジトリは AtCoder のコンテストを快適に進めるためのワークスペースです。VS Code Dev Container を前提に、C++ (GCC 15.2.0 + ac-library 1.6) と Python (CPython 3.13 / PyPy 3.11) をまとめて導入し、ac-companion 拡張と連携するシンプルなビルド・実行フローを提供します。

## 推奨環境: Dev Container

### 前提条件
- Docker Desktop / nerdctl などコンテナ実行環境
- Visual Studio Code
- VS Code 拡張: Remote - Containers (Dev Containers)

### 使い方
1. このリポジトリをクローンし、VS Code でフォルダーを開く。
2. コマンドパレットで「Dev Containers: Reopen in Container」を実行。
3. `.devcontainer/devcontainer.json` に基づきコンテナがビルドされると、自動的にセットアップ用スクリプトが順番に実行されます（`updateContentCommand`）。

### 自動で導入される主なツール
- CPython 3.13（Dev Container feature）
- PyPy 7.3.16（`.devcontainer/scripts/install_pypy`）
- GCC 15.2.0 + ac-library 1.6（`.devcontainer/scripts/install_cpp`）
- `python3 -m pip install --user -r requirements.txt`
- ac-companion-python 拡張 v1.1.3（`.devcontainer/scripts/install_ac_extension`）

> Dev Container 内では `/workspaces/atcoder/` がワークスペース直下の絶対パスになります。`WORKSPACE_DIR` を参照するスクリプトもこのパスを前提にしています。


## ローカル環境で再現する場合

Dev Container を使わない場合は、以下を参考にホスト OS 上で同等環境を用意できます。

1. 依存ツールを用意する  
   - build-essential / curl / zlib など Python ソースビルドに必要なパッケージ  
   - GCC ビルドに必要なツール (git, cmake, lld, ninja-build, bison, flex, gmp/mpfr/mpc 系ライブラリなど)  
   - Node.js (v22 目安)
2. リポジトリ直下でスクリプトを順に実行する
   ```bash
   bash .devcontainer/scripts/install_pypy          # 非 root ユーザーで実行
   sudo AC_INSTALL_DIR=/opt/atcoder/gcc bash .devcontainer/scripts/install_cpp
   python3 -m pip install --user -r requirements.txt
   ```
3. シェルの再読み込み後、`python3`, `pypy3`, `g++` がパスに通っていることを確認する。

`WORKSPACE_DIR` が `/workspaces/atcoder/` と異なる場合は、必要に応じてスクリプト内のデフォルトを上書きしてください。

## リポジトリ構成

- `cpp_compile` / `cpp_run`：C++ のビルド・実行スクリプト（ac-companion から呼び出し可能）
- `.config/templates/main.cpp` / `.config/templates/main.py`：提出用テンプレート
- `.devcontainer/`：Dev Container 定義とセットアップスクリプト群
- `ac-library/`：AtCoder Library ソース（コンテナ構築時に `/opt/atcoder/gcc/include` へコピー）
- `requirements.txt`：Python 依存パッケージ

## `contest` コマンドの使い方

1. ルートディレクトリで実行  
   ```bash
   ./contest
   ```
   パスを通している場合は単に `contest` と入力すれば起動します。

2. メニューの概要
   - `1. Start new contest`  
     コンテスト ID（例: `abc370`）を入力すると `acc new <contest_id>` を実行し、所定時刻まで待機してから問題を生成します。開始時刻はデフォルト `21:00`、任意に上書き可能です。
   - `2. Resume ongoing contest`  
     現在の `contest_id` を維持したまま操作メニュー（後述）に入ります。
   - `3. Resume existing contest`  
     既存ディレクトリからコンテスト ID を指定し直して再開できます。
   - `0. Exit`  
     終了します。

3. コンテスト中メニュー（`during_contest()`）
   - 初回は `acc new` で生成された問題一覧が表示され、対象問題を入力すると VS Code がそのファイルを開きます。
   - 入力プロンプトでは以下のショートカットが利用できます:
     - `n`：`acc add` を実行して次の問題を取得し、自動的に開きます。
     - `c`：既存問題一覧から移動したい問題名を入力します。
     - `t`：言語設定に応じてサンプルテストを実行します（Python は `pypy3 ./main.py`、C++ は `cpp_compile` → `cpp_run`）。
     - `d`：提出前の実行確認（Python はインタプリタ実行、C++ はビルド済みバイナリを実行）。
     - `l`：使用する実行環境の切り替え（例: PyPy / CPython / C++）。
     - `h`：ヘルプ（`exit`, `n`, `t` などの説明）。
     - `exit`：このメニューを抜けて最初の画面に戻ります。

4. テストと提出
   - テンプレートから生成した `tests/` ディレクトリ内の入出力を使い、`t` コマンドや ac-companion で検証します。
   - 必要に応じて `acc submit` などで提出してください（自動提出は行いません）。

## C++ 用コマンド

- `cpp_compile <contest_id> <task_id>`  
  `main.cpp` を `g++ -std=gnu++23 -O2 -march=native` でコンパイルし、`a.out` を生成します。
- `cpp_run <contest_id> <task_id> [input_file]`  
  `a.out` を実行します。`input_file` を渡した場合はその内容を標準入力に流し込みます。

どちらもデフォルトで `/workspaces/atcoder/<contest>/<task>` を参照し、ac-companion から直接呼び出すことを前提にしています。

## トラブルシューティング

- `g++` のバージョンが 15.2.0 になっていない  
  PATH が `/opt/atcoder/gcc/bin` を指しているか確認し、必要ならコンテナを再構築してください。
- ac-library が参照できない  
  `/opt/atcoder/gcc/include/atcoder` が存在するか確認し、`install_cpp` を再実行します。
- `pypy3` が見つからない  
  シェルの初期化ファイルに PyPy の PATH 追加が入っているか、`install_pypy` 実行後にシェルを再読み込みしてください。
- VS Code が C++ インテリセンスを解決できない  
  Dev Container の設定で includePath が `/opt/atcoder/gcc/include` を指しているか確認してください。

この README を参考に、事前にログイン・テンプレート確認を済ませ、コンテストに集中できる環境を整えてください。
