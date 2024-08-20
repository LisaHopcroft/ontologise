#!/usr/bin/env python

import os
from os import path
from wordcloud import WordCloud


text = open("/media/michael/Files/Dropbox/workspace/2.research/01.Primary/01.Manuscripts/01.Archives/01.SCOTLAND/NRAS, National Register of Archives Scotland/2696, FRASER of Reelig/B007, Letters - E.S.FRASER, 1803-7 [25pp]/02_TXT/17, 18040115, (Demerara).txt").read()

# Generate a word cloud image
wordcloud = WordCloud().generate(text)

# Display the generated image:
# the matplotlib way:
import matplotlib.pyplot as plt
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")

# lower max_font_size
wordcloud = WordCloud(max_font_size=40).generate(text)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
