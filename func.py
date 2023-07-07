from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
from bs4 import BeautifulSoup


def get_transcription(headers, url):
    response = requests.get(url, headers=headers)
    html = response.content
    # Используем BeautifulSoup для парсинга HTML-кода страницы
    soup = BeautifulSoup(html, 'html.parser')
    # Ищем определение слова на странице
    middle = soup.find("div", {"class": "page"})
    transcription = middle.find("span", {"class": "ipa dipa lpr-2 lpl-1"}).text.strip()
    return transcription


def create_image(translater, transcription):
    weight, height = (270, 200)
    image = Image.new('RGB', (weight, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    w = draw.textlength(translater.encode('utf-8'))
    w1 = draw.textlength(transcription.encode('utf-8'))
    font_path = 'arial.ttf'
    font_size = 28
    font = ImageFont.truetype(font_path, font_size)
    h1 = font.getlength(transcription)
    h = font.getlength(translater)
    draw.text(((weight-w)/2, (height-h)/2), translater, fill=(0, 0, 0), font=font)
    draw.text(((weight-w1)/2, (height-h)/2 + 30), transcription, fill=(0, 0, 0), font=font)
    image_stream = BytesIO()
    image.save(image_stream, format='PNG')
    image_data = image_stream.getvalue()
    return image_data
