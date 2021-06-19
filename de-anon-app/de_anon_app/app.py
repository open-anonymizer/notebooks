import ast
from datetime import datetime
from pickle import FALSE

import pandas as pd
import streamlit as st
import streamlit.components.v1

import pickledb
from htbuilder import HtmlElement, div, span, styles
from htbuilder.units import em, px, rem


def annotation(body, label="", background="#ddd", color="#333", **style):

    if "font_family" not in style:
        style["font_family"] = "sans-serif"

    return span(
        style=styles(
            background=background,
            border_radius=rem(0.33),
            color=color,
            padding=(rem(0.17), rem(0.67)),
            display="inline-flex",
            justify_content="center",
            align_items="center",
            **style,
        )
    )(
        body,
        span(
            style=styles(
                color=color,
                font_size=em(0.67),
                opacity=0.5,
                padding_left=rem(0.5),
                text_transform="uppercase",
                margin_bottom=px(-2),
            )
        )(label),
    )


def annotated_text(list_text, *args, **kwargs):
    out = div(style=styles(font_family="sans-serif", line_height="1.5", font_size=px(16)))

    for arg in list_text:
        if isinstance(arg, str):
            out(arg)

        elif isinstance(arg, HtmlElement):
            out(arg)

        elif isinstance(arg, tuple):
            out(annotation(*arg))

        else:
            raise Exception("Oh noes!")

    streamlit.components.v1.html(str(out), **kwargs)


@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_csv("data/anonymized_only.csv")
    return df


def skip_faster(i, counted):
    if "XXX" in i:
        pass
    else:
        counted += 1
        with open("state_file.txt", "w") as f:
            f.truncate()
            f.write(f"{counted}")
        st.experimental_rerun()


def save_data(df):
    date_string = datetime.now()
    df.to_csv(f"data/{date_string}-anon-bearbeitet.csv", index=False)


######
df = load_data()

with open("state_file.txt", "r") as f:
    counted = f.readline()
    counted = 0 if counted == "" else int(counted)

st.sidebar.progress(counted / df.shape[0])
st.sidebar.text(f"{counted}/{df.shape[0]}")

col_1, col_2, col_3, col_4, col_5, col_6 = st.beta_columns(6)

button_person = col_1.button("PERSON")
button_date = col_2.button("DATE")
button_org = col_3.button("ORGANISATION")
button_location = col_4.button("LOCATION")
button_remove = col_5.button("REMOVE")
text_custom_ent = col_6.text_input("custom entity")
button_custom = col_6.button("CUSTOM")

st.markdown("----")

try:
    input_text = df.iloc[counted]["open_nps_reason"]
except Exception as e:
    print(e)
    input_text = "SKIP"

skip_faster(input_text, counted)

a = input_text.replace("XXX", '#SPLIT ("XXX", "UNK", "#faa") #SPLIT')
b = a.split("#SPLIT")
b = [e.lstrip() for e in b]
c = []
try:
    for e in b:
        if e.startswith("("):
            temp = ast.literal_eval(e)
        else:
            temp = e
        c.append(temp)
except Exception as e:
    print(e)

annotated_text(c)

st.markdown("----")

if button_person:
    new_text = input_text.replace("XXX", "PERSON", 1)
    df.iloc[counted]["open_nps_reason"] = new_text
    st.experimental_rerun()

if button_date:
    new_text = input_text.replace("XXX", "DATE", 1)
    df.iloc[counted]["open_nps_reason"] = new_text
    st.experimental_rerun()

if button_org:
    new_text = input_text.replace("XXX", "ORGANISATION", 1)
    df.iloc[counted]["open_nps_reason"] = new_text
    st.experimental_rerun()

if button_location:
    new_text = input_text.replace("XXX", "LOCATION", 1)
    df.iloc[counted]["open_nps_reason"] = new_text
    st.experimental_rerun()

if button_remove:
    new_text = input_text.replace("XXX", "", 1)
    df.iloc[counted]["open_nps_reason"] = new_text
    st.experimental_rerun()

if button_custom:
    new_text = input_text.replace("XXX", text_custom_ent, 1)
    df.iloc[counted]["open_nps_reason"] = new_text
    st.experimental_rerun()

st.write(df.iloc[counted]["open_nps_reason"])

if st.button("Export"):
    save_data(df)
