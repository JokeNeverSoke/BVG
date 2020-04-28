# BVG

全自动营销号视频生成器，通过一个主语和一个动词来生成。

稿子生成来源于[这个](https://iamazing.cn/page/baidu-style-generator)模版

**此项目还在开发中，欢迎积极提issue**

## 安装

**建议使用venv**

~~以此目前只能在mac上跑，未来会增加跨平台`tts`~~ 

### 下载至本地

```bash
git clone https://github.com/JokeNeverSoke/BVG.git
```

### 安装dependencies

```bash
cd BVG # 换到项目主目录
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

此外需根据操作系统安装[ffmpeg](https://ffmpeg.org/)

## 运行

在文件目录跑`./run.py 名词 动词`

```
Usage: run.py [OPTIONS] NOUN ACTION

Options:
  --bgm TEXT  BGM used for the video
  --help      Show this message and exit.
```

## TODO

- [ ] 增加跨平台tts脚本
- [ ] 增加懒人一键安装
- [ ] setup py
