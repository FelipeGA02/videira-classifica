import streamlit as st
import gdown
import tensorflow as tf
import io
from PIL import Image
import numpy as np
import pandas as pd
import plotly.express as px

@st.cache_resource
def carrega_modelo():
    # https://drive.google.com/file/d/1aDpkyck8huroIcRJ5bRCaHl9N8sqrOfp/view?usp=sharing
    url = 'https://drive.google.com/uc?id=1aDpkyck8huroIcRJ5bRCaHl9N8sqrOfp'

    gdown.download(url, 'modelo_quantizado16bits.tflite', quiet=False)
    interpreter = tf.lite.Interpreter(model_path='modelo_quantizado16bits.tflite')
    interpreter.allocate_tensors()

    return interpreter

def carrega_imagem():
    uploaded_file = st.file_uploader('Arraste e solte uma imagem aqui ou clique para selecionar uma', type=['png', 'jpg', 'jpeg'])

    if uploaded_file is not None:
        image_data = uploaded_file.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")  # Garante 3 canais

        # Redimensiona a imagem para o tamanho esperado pelo modelo
        image = image.resize((256, 256))

        st.image(image, caption="Imagem carregada", use_column_width=True)
        st.success('Imagem foi carregada com sucesso')

        image = np.array(image, dtype=np.float32)
        image = image / 255.0  # Normaliza para [0, 1]
        image = np.expand_dims(image, axis=0)  # (1, 256, 256, 3)

        return image

def previsao(interpreter, image):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], image)
    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])[0]
    classes = ['BlackMeasles', 'BlackRot', 'HealthyGrapes', 'LeafBlight']

    df = pd.DataFrame({
        'classes': classes,
        'probabilidades (%)': 100 * output_data
    })

    fig = px.bar(
        df,
        y='classes',
        x='probabilidades (%)',
        orientation='h',
        text='probabilidades (%)',
        title='Probabilidade de Classes de Doenças em Uvas'
    )

    st.plotly_chart(fig)

def main():
    st.set_page_config(
        page_title="Classifica Folhas de Videira",
        page_icon="🍇",
        layout="centered"
    )
    st.title("🍇 Classifica Folhas de Videira")
    st.markdown("Este app identifica **doenças em folhas de videira** com base em uma imagem.")

    interpreter = carrega_modelo()
    image = carrega_imagem()

    if image is not None:
        previsao(interpreter, image)

if __name__ == "__main__":
    main()
