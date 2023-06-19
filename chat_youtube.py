# -*- coding: utf-8 -*-

import os
from langchain.document_loaders import YoutubeLoader
from langchain.indexes import VectorstoreIndexCreator

loader = YoutubeLoader.from_youtube_url("https://www.youtube.com/watch?v=9rVOwPLNHnE&ab_channel=DoisDedosdeTeologia", add_video_info=True, language="pt")
index = VectorstoreIndexCreator().from_loaders([loader])
query = "Oque nicodemos confessa?"
response = index.query(query)

print()
print("###################")
print(response)
print("###################")
print()