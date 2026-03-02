# プロンプト
ハンズオンで使用するプロンプトを記載しています。
コピー&ペーストでご利用ください。

1. Streamlitを使用して、Open-MeteoのAPIを活用した東京の1週間分の天気予報を確認できるコードを生成してほしい。
2. /explain bash: streamlit: command not found
3. 東京の天気予報ではなく大阪の天気予報に変えてほしい
4. @workspace /explain 概要図とシーケンス図をmermaid記法を用いて生成して
5. @vscode Markdownのプレビューでmermaid記法がVScode上で図として正しく表示されない
6. /explain このAPIで現在取得している項目の情報説明と他に取れる項目がないか教えてほしい
7. 晴れ予報なのか曇り予報なのか雨予報なのかもデータフレームに表示したい
8. 東京と大阪をセレクトボックスで切り替えられるように変更します
9. 地名情報が重複している箇所などリファクタリングしてほしい
10. vision.py ファイルを新規作成し、以下の機能を含むアプリをstreamlitを用いて開発してください
　1. Azure AI Visionサービスを利用
　2. 環境変数（endpoint, api key）は.envから読み取る
　3. envファイルも値はdummyで作成する
　4. 写真を送付と送付された画像の解析
　5. 解析結果のリストを画面上に表示

# azure ai visionのインストールコマンド
```
pip install azure-ai-vision-imageanalysis
```