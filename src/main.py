import os
import streamlit as st
import pandas as pd
from glob import glob
from tabulate import tabulate
import matplotlib.pyplot as plt
from janome.tokenizer import Tokenizer
from wordcloud import WordCloud
from io import BytesIO



st.set_page_config(
    page_title="create WordCloud",
    page_icon="./Jellyfish-icon.png",
    layout="wide",
    initial_sidebar_state="auto",
)

class Comment2WordCloud:
    def __init__(self, csv_path, header=None):
        self.__data = pd.read_csv(csv_path, header=None, encoding='utf-8')
        self.__data_string = tabulate(self.__data,tablefmt='simple', showindex=False)

        self.fpath =  glob('/Library/Fonts//*.ttf')[0] if os.name=="posix" else glob('C:\Windows\Fonts\*.ttf')[0]

        # カウントしない文節をsetで用意
        self.non_count = set(["/", "", " ", "　", "、", "。", ".",  "せる", "まし", "まし","ます","てる","たら"])
        for i in range(12353, 12439):
            self.non_count.add(chr(i))

    def get_data(self):
        return self.__data_string

    def get_wordcloud(self):
        try:
            return self.__wordcloud.to_image()
        except Exception("wordcloud not created"):
            return None

    def wakati_count(self):
        # MeCabのTaggerオブジェクトを作成
        tokenizer=Tokenizer()

        # 各文節をカウントするための辞書を用意する
        self.count_text = {}

        # 各行を処理する
        for col_name,item in self.__data.items():
            # MeCabを使用して日本語の文字列を分かち書きにする

            for sentence in item:

                nodes = tokenizer.tokenize(str(sentence).replace('\u3000',''),wakati=True)

                # 分かち書きされた文字列から各文節をカウントする
                for node in nodes:

                    if node not in self.non_count:  # 不要な文字列はカウントしない
                        # まだ辞書に登録されていない文節の場合は、新しく辞書に登録する
                        if node not in self.count_text:
                            self.count_text[node] = 1
                        # 既に登録されている文節の場合は、カウントを1増やす
                        else:
                            self.count_text[node] += 1

        # カウント数の降順に並び替える
        self.count_sorted_text = sorted([[str(k), v] for (k, v) in self.count_text.items()], key=lambda x: -x[1])
        self.count_words_text = str(self.count_sorted_text).replace(' ', '')

    def save_count(self, save_path):
        # 保存する
        with open(save_path, mode='w',  encoding="utf-8-sig") as f:
            f.write(self.count_words_text)
        return self.count_sorted_text

    def create_wordcloud(self, width=1600, height=900):
        self.__wordcloud = WordCloud(background_color="white", font_path=self.fpath,stopwords=self.non_count,width=width, height=height, regexp=r"[0-9a-zA-Zぁ-んァ-ヶｱ-ﾝﾞﾟ一-龠ー]+").generate(self.count_words_text)

    def show_wordcloud(self, width=16, height=9):
        plt.figure(figsize=(width, height))
        plt.imshow(self.__wordcloud)
        plt.axis("off")

    def save_wordcloud(self):
        self.path="./wordcloud.png"
        self.__wordcloud.to_file(self.path)


st.header('CSVファイルからワードクラウドを作成しよう')

uploaded_file=st.file_uploader("ファイルアップロード", type='csv')
if uploaded_file is not None:
    try:
        base_name=uploaded_file.name.split('.')[0]
        w2c=Comment2WordCloud(uploaded_file)
        w2c.wakati_count()
        w2c.create_wordcloud(900,600)
        img=w2c.get_wordcloud()
        st.image(img,caption = '生成画像')
        # byte=img.tobytes()
        buf = BytesIO()
        img.save(buf, format="JPEG")
        byte_im = buf.getvalue()
        if img is not None:
            st.download_button(
                '画像をダウンロード',
                data=byte_im,
                file_name=base_name+"_wordcloud.png",
                mime="image/png"
            )
    except:
        st.text("処理に失敗しました")