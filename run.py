#!/usr/bin/env python
"""
A cli to create bad videos from a noun and a verb
"""

import os
import random
import re
import subprocess
from typing import List, Tuple

import click
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def generate_sound(scr: str) -> int:
    """Returns a path to file with sound outputed"""
    path = "voices/" + str(random.randrange(10000000, 99999999)) + ".aiff"
    subprocess.run(["say", "-v", "Ting-Ting", "-o", path, scr], check=True)
    return path


def get_length(path: str) -> int:
    """Get the length of `path` file using ffmpeg"""
    # write to a temporary mp3 to regex output

    completed = subprocess.run(
        ["ffmpeg", "-i", path, "tmp.mp3"], capture_output=True, encoding='utf-8')
    if completed.returncode != 0:
        click.echo("Error, stdout: {}\n stderr: {}".format(
            completed.stdout, completed.stderr))
    os.remove("tmp.mp3")
    out: str = completed.stderr
    pattern = r"Duration: (\S+),"
    duration = re.search(pattern, out).group(1)
    [hourstr, minutestr, secondstr] = duration.split(":")
    hour = int(hourstr)
    minute = int(minutestr)
    second = float(secondstr)
    totaltime: float = hour * 3600 + minute * 60 + second
    return totaltime


def get_images(keywords: Tuple[str], amount: int = 10) -> List[str]:
    """Get images using `keyword` from Bing and return a list of paths"""
    url = "http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word={}".format(
        keywords[0])
    click.echo("Starting webdriver to get image urls")
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    imagelinks = driver.find_elements_by_css_selector('.imgitem')
    image_files = []
    counter = 0
    while len(image_files) < amount:
        click.echo("{} images left".format(amount - len(image_files)))
        try:
            element: webdriver.remote.webelement.WebElement = imagelinks.pop()
        except IndexError:
            click.echo("Current images not enough, switching to fallback verb")
            url = "http://image.baidu.com/search/index?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&ie=utf-8&word={}".format(
                keywords[1])
            driver.get(url)
            imagelinks = driver.find_elements_by_css_selector('.imgitem')
            continue
        try:
            link = element.get_attribute('data-objurl')
        except:
            click.echo("FAILED Cannot get attribute data-objurl")
            continue
        # link = attr_m['murl']
        click.echo("Downloading image from url {}".format(link))
        filename = link.split("/")[-1].split("?")[0]
        if len(filename.split(".")) <= 1:
            click.echo("FAILED FILENAME")
            continue
        extension = "." + filename.split('.')[-1]
        file_name = "images/" + str(counter) + extension
        try:
            stuff = requests.get(link, timeout=2).content
        except requests.exceptions.ConnectionError:
            click.echo("FAILED TIMEOUT")
            continue
        except requests.exceptions.ReadTimeout:
            click.echo("FAILED TIMEOUT")
            continue
        except Exception as e:
            click.echo("Error when downloading image: {}".format(e))
            continue
        else:
            with open(str(file_name), 'wb') as file:
                file.write(stuff)
        image_files.append(file_name)
        click.echo("SUCCESS")
        counter += 1
    driver.quit()
    return image_files


def return_article(noun: str, action: str) -> str:
    return f"""\
{noun}{action}是怎么回事呢？
{noun}相信大家都很熟悉， 但是{action}是怎么回事呢？
下面就让小编带大家一起了解吧。
{noun}{action}，其实就是{action}了。
那么{noun}为什么会{action}，相信大家都很好奇是怎么回事。
大家可能会感到很惊讶，{noun}怎么会{action}呢？
但事实就是这样，小编也感到非常惊讶。
那么这就是关于{noun}{action}的事情了，大家有没有觉得很神奇呢？
看了今天的内容，大家有什么想法呢？
欢迎在评论区告诉小编一起讨论哦。"""


def timecode(code: float) -> str:
    """Return the formated timecode from imputed float `code`"""
    hour = int(code // 3600)
    minute = int(code % 3600) // 60
    second = int(code % 60)
    millisecond = int((code % 1) * 1000)
    shour: str = "0" * (2 - len(str(hour))) + str(hour)
    sminute: str = "0" * (2 - len(str(minute))) + str(minute)
    ssecond: str = "0" * (2 - len(str(second))) + str(second)
    smilli: str = "0" * (3 - len(str(millisecond))) + str(millisecond)
    return f"{shour}:{sminute}:{ssecond},{smilli}"


def return_srt_caption(sentences: List[Tuple[str, float]],
                       offset: float = 0.0,
                       padding: float = 0.0) -> str:
    """Generate a srt formatted srt file part"""
    srt_sections = []
    current_timecode = offset
    sequence = 1
    for text, length in sentences:
        starttime = timecode(current_timecode + padding)
        current_timecode += length
        endtime = timecode(current_timecode - padding)
        srt_sections.append(f"""{sequence}
{starttime} --> {endtime}
{text}""")
        sequence += 1
    return "\n\n".join(srt_sections)


@click.command()
@click.argument("noun")
@click.argument("action")
@click.option("--bgm", default=None, help="BGM used for the video")
def main(noun: str, action: str, bgm: str):
    if "__cache__" not in os.listdir():  # change dir stuff to cache
        os.mkdir("__cache__")
    os.chdir("__cache__")
    cache_dir = str(random.randrange(10000000, 99999999))
    os.mkdir(cache_dir)
    os.chdir(cache_dir)
    click.echo("Cache root at {}".format(os.getcwd()))
    os.mkdir('images')
    os.mkdir('voices')
    click.echo("Directories `images` and `voices` created")

    click.echo("BGM: {}".format(bgm))
    # get formated sentences
    article: str = return_article(noun, action)
    # split into smaller for subtitles
    sentences = article.split('\n')
    # generate audio files using 'say'
    audios: Tuple[str, float, str] = []
    for sentence in sentences:
        file = generate_sound(sentence)
        click.echo("Voice file created at {} for '{}'".format(file, sentence))
        length = get_length(file)
        audios.append((file, length, sentence))

    # generate .srt subtitle file
    srt_filename = "subtitle.srt"
    with open(srt_filename, 'w') as filestream:
        filestream.write(return_srt_caption(
            [(part[2], part[1]) for part in audios]))
    # download and get the image locations
    image_files = get_images((noun, action), len(sentences))

    # calculate total time
    totaltime = 0.0
    for _, length, _ in audios:
        totaltime += length
    click.echo("Video length: {}".format(totaltime))

    # create a file for joining audio
    with open('audiopath.txt', 'w') as filestream:
        for file, _, _ in audios:
            filestream.write("file '{}'\n".format(file))

    # merge the autio files
    click.echo("Merging autio files")
    os.system("ffmpeg -f concat -i audiopath.txt -c copy output.aiff")

    # subprocess.run([
    #     'cat', 'images/*', '|', 'ffmpeg', '-i', '-', '-vcodec', 'mpeg4', 'test.avi'
    # ], check=True, shell=True)
    # os.system(" ".join([
    #     'ffmpeg', '-i', 'images/*', '-r 60', 'test.avi'
    # ]))
    click.echo("Batch converting images to png")
    os.mkdir("new")
    for counter in range(len(image_files)):
        os.system(
            "ffmpeg -i {} new/{}.png".format(image_files[counter], counter))
    click.echo("Generating low-rate video")
    os.system(r"ffmpeg -framerate 1/{} -i new/%d.png -i output.aiff -vcodec libx264 -s 1920x1080 -pix_fmt yuv420p test1.mp4".format(totaltime // 10 + 1))
    # os.system(r"ffmpeg -framerate 1/5 -i new/*.png -r 30 test.mp4")
    os.system(r"ffmpeg -i test1.mp4 -r 20 -max_muxing_queue_size 9999 test.mp4")
    if bgm is not None:
        subprocess.run(['ffmpeg',
                        '-i',
                        'test.mp4',
                        '-i',
                        "../../" + bgm,
                        "-filter_complex",
                        "[0]volume=1[a0];[1]volume=0.3[a1];[a0][a1]amix=inputs=2[a]",
                        "-map",
                        "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", "-b:a", "192k", "-ac", "2", "-shortest",
                        '-r',
                        '20',
                        '-max_muxing_queue_size',
                        '9999',
                        'test2.mp4'],
                       check=True)
    else:
        subprocess.run(['ffmpeg',
                        '-i',
                        'test.mp4',
                        '-vf',
                        'subtitles=subtitle.srt',
                        '-r',
                        '20',
                        '-max_muxing_queue_size',
                        '9999',
                        'test2.mp4'],
                       check=True)
    subprocess.run(['ffmpeg', '-i', 'test2.mp4', '-vf','subtitles=subtitle.srt', '-max_muxing_queue_size', '9999', 'out.mp4'], check=True)
    os.rename("out.mp4", "../../out.mp4")


if __name__ == "__main__":
    main()
