# discord-pigeon
![](https://i.imgur.com/d7cG5Fq.png)

内々で使う日程調整用のDiscord Botです

# このBotがやること
参加可能日の一覧を投稿 → 一番リアクションの多かった日程で告知 → 予定15分前にチャンネルに通知

# セットアップ

dockerが必要です.

1. このリポジトリをクロン
```
$ git clone git@github.com:106-/discord-pigeon.git
$ cd discord-pigeon
```

2. 環境変数の設定

こんな感じのファイルを`.env`という名前で保存します.
```
MONGODB_USER=hoge
MONGODB_PASSWORD=hoge # 推測しにくい文字列なら何でもOK
DISCORD_CHANNEL_ID=hoge
DISCORD_TOKEN=hoge # botのトークン
```

3. 起動
```
$ make run-all
```