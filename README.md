# AtCoder環境（PyPy, Codon）

このリポジトリは AtCoder のコンテストを快適に進めるためのワークスペースです。VS Code Dev Container を前提に、PyPy・Codon・online-judge-tools・atcoder-cli などのツールをまとめて構築できるようになっています。ここでは開発環境の整え方から、コンテスト中に利用する `contest` コマンド（実装は `contest.py`）の操作フローまでをまとめています。

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
- Python 3.13 系（`.devcontainer/scripts/install_python` がソースビルド）
- PyPy 7.3.16（`.devcontainer/scripts/install_pypy.sh`）
- Codon 0.19.3（`.devcontainer/scripts/install_codon.sh`）
- pipx / online-judge-tools / atcoder-cli（`.devcontainer/scripts/setup_oj_acc.sh`）
- `pip install --user -r requirements.txt`（現在は `termcolor` のみ）

> Dev Container 内では `/workspaces/atcoder/` がワークスペース直下の絶対パスになります。`contest.py` もこのパスを前提にしています。

### ホストと共有される設定
- `${repo}/.config/atcoder-cli-nodejs` → `/home/vscode/.config/atcoder-cli-nodejs`
- `${repo}/.config/online-judge-tools` → `/home/vscode/.local/share/online-judge-tools`

それぞれ AtCoder CLI (`acc`) と online-judge-tools (`oj`) の設定ディレクトリです。ホスト側でファイルを置いておくとコンテナ再構築後もログイン情報などを引き継げます。

## ローカル環境で再現する場合

Dev Container を使わない場合は、以下を参考にホスト OS 上で同等環境を用意できます。全て非 root ユーザーで実行してください。

1. 依存ツールを用意する  
   - build-essential / curl / zlib など Python ソースビルドに必要なパッケージ  
   - Node.js (v22 目安)  
   - pipx（`python3 -m pip install --user pipx`）
2. リポジトリ直下でスクリプトを順に実行する
   ```bash
   bash .devcontainer/scripts/install_python
   bash .devcontainer/scripts/install_pypy.sh
   bash .devcontainer/scripts/install_codon.sh
   bash .devcontainer/scripts/setup_oj_acc.sh
   python3 -m pip install --user -r requirements.txt
   ```
3. シェルの再読み込み後、`python3`, `pypy3`, `codon`, `oj`, `acc` がパスに通っていることを確認する。

`contest.py` の `WORKSPACE_DIR` はデフォルトで `/workspaces/atcoder/` になっています。ローカルでパスが異なる場合は環境に合わせて書き換えてください。

## ツールの初回設定

1. `acc` のログイン  
   ```bash
   acc login
   ```
   ブラウザが開かない場合はコンテナのターミナルでワンタイムトークンを入力します。

2. `oj` のログイン  
   ```bash
   oj login https://atcoder.jp/
   ```

3. 必要に応じて `~/.config/atcoder-cli-nodejs` や `~/.local/share/online-judge-tools` にアカウント情報が保存されるので、Dev Container 再構築前にバックアップしておくと便利です。

## リポジトリ構成

- `contest`：コンテスト進行 CLI の実行ファイル（リポジトリ直下から `contest` で起動）
- `contest.py`：`contest` コマンドの Python 実装
- `contest/`：`acc new` や `acc add` で取得した問題が配置されるディレクトリ
- `.devcontainer/`：Dev Container 定義とセットアップスクリプト群
- `requirements.txt`：Python 依存パッケージ（現在は `termcolor` のみ）

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
   - 初回は `acc new` で生成された問題一覧が表示され、対象問題を入力すると VS Code がその `main.py` を開きます。
   - 入力プロンプトでは以下のショートカットが利用できます:
     - `n`：`acc add` を実行して次の問題を取得し、自動的に開きます。
     - `c`：既存問題一覧から移動したい問題名を入力します。
     - `t`：言語設定に応じてサンプルテストを実行します（`oj t` / `pypy3 ./main.py` など）。
     - `d`：提出前の実行確認（Codon はビルド後 `./main`、PyPy は `pypy3 ./main.py` を起動）。
     - `l`：`pypy` / `codon` の切り替え。
     - `h`：ヘルプ（`exit`, `n`, `t` などの説明）。
     - `exit`：このメニューを抜けて最初の画面に戻ります。

4. テストと提出
   - `t` コマンドは `oj t` を用いてサンプルケースを検証します。Codon 選択時は `codon build` → `oj t -c ./main` を行います。
   - 必要に応じて `oj submit` や `acc submit` を手動で実行してください（自動化はしていません）。

## トラブルシューティング

- `acc` / `oj` が認証エラーになる  
  - 設定ディレクトリの権限や保存内容を確認し、再ログインしてください。
- `contest` コマンドがワークスペースを見つけられない  
  - `WORKSPACE_DIR` の定数が実際のパスと一致しているかを確認し、必要なら環境に合わせて書き換えます。
- Codon ビルドが失敗する  
  - 依存する `CODON_PYTHON` のパスがシェルに設定されているか、`install_python` スクリプトを再実行して `.bashrc` が読み込まれているかを確認します。

## 補足

- コンテスト前に `acc session` や `acc config` でテンプレート・提出言語を設定しておくとスムーズに開始できます。
- Dev Container 上では `editor.formatOnSave = true` と Ruff フォーマッタが設定されています。不要な場合は `.vscode/settings.json` などで上書きしてください。
- 新しいツールを追加したい場合は `.devcontainer/Dockerfile` または各スクリプトを編集して再ビルドします。

この README を参考に、事前にログイン・テンプレート確認を済ませ、コンテストに集中できる環境を整えてください。
