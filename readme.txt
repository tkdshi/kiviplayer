概要
    『イコライザ機能付き音楽プレーヤー』
    おもに、kivyを用いて、音楽プレーヤーの実装を行った。


プログラムの実行方法（コマンド）
    "python main.py"のコマンドにより実行できる。
    おもに、simpleplayerディレクトリ配下のmusicplayer.pyに、プレーヤーを動作されるための関数を記述している。

操作方法
    上部の「Choose File」ボタンにより、
    エクスプローラー上で音楽ファイル(waveファイル)を選択する。
    ファイルを選択すると、自動で再生が開始される。

    main.pyと同ディレクトリに、20秒程度の音楽(samplemusic.wav)と、
    ホワイトノイズ(whiteNoise.wav)のサンプル音源を用意している。
    これを読み込むことによって、エフェクト処理後の音源ファイル(out.wav)が
    出力され、out.wavから音声を再生するしくみとなっている。

    「Low」「Mid」「High」のゲージを調整することにより、
    周波数帯域ごとの周波数音量を変更することができる。
    また、「Picth」のゲージを調節することにより、
    曲の音階が変更される。

    ファイル選択前にパラメーターを変更することで、
    そのエフェクトが反映される。

    曲再生中にパラメーターを変更しても、
    動的にwaveファイルの編集が行われる。


工夫した点
    フィルタ関数を用いて、実際にGUIとも連動させて
    イコライザやピッチの調節を行う機能を作成することができた点。

参考資料
    『PythonのKivyで音楽プレイヤー』 https://qiita.com/mkgask/items/dcd0f173998168fe5614
