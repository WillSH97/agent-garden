import os, requests, gradio as gr

URL = os.environ.get("FASTAPI_URL", "http://localhost:8000")

def make_friend(name, likes, dislikes, personality):
    if not all(x.strip() for x in (name, likes, dislikes, personality)):
        raise gr.Error("fill out all traits!")
    r = requests.get(URL + "/friendlist"); r.raise_for_status()
    if name in r.json():
        raise gr.Error("that friend (or their name) already exists!")
    requests.post(URL + "/makefriend", json={"name": name, "likes": likes, "dislikes": dislikes, "personality": personality}).raise_for_status()
    return "you've made a friend!"

gr.Interface(make_friend, [gr.Textbox(label=l) for l in ("Enter your friend's name", "list what they like", "list what they dislike", "describe their personality")], "text", title="make a friend!", flagging_mode="never").launch(share=True)