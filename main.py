import cv2
import mediapipe as mp
from deepface import DeepFace
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Inicializa MediaPipe
mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

VIDEO_PATH = 'videos/triste.mp4'

# Função para rodar análise com parâmetros configuráveis
def analisar_video(path, min_det_conf=0.95, limiar_conf=0.95, janela="Análise"):
    cap = cv2.VideoCapture(path) # troque aqui para 0 para abrir a webcam
    frame_num = 0
    dados_emocoes = []

    with mp_face_detection.FaceDetection(
        model_selection=1, min_detection_confidence=min_det_conf
    ) as face_detection:

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(img_rgb)

            if results.detections:
                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = frame.shape
                    x, y, w, h = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                                 int(bboxC.width * iw), int(bboxC.height * ih)

                    x, y = max(0, x), max(0, y)
                    w, h = max(1, w), max(1, h)

                    face_crop = frame[y:y + h, x:x + w]

                    try:
                        analysis = DeepFace.analyze(
                            face_crop,
                            actions=['emotion'],
                            enforce_detection=False
                        )
                        expressao = analysis[0]['dominant_emotion']
                        score = analysis[0]['emotion'][expressao]
                        timestamp = datetime.now().strftime("%H:%M:%S")

                        if score >= limiar_conf:
                            dados_emocoes.append({
                                'tempo': timestamp,
                                'frame': frame_num,
                                'expressao': expressao,
                                'confianca': score
                            })

                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            cv2.putText(frame, f"{expressao} ({score:.2f})", (x, y - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                            mp_drawing.draw_detection(frame, detection)

                    except Exception as e:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        cv2.putText(frame, "Detectado", (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.imshow(janela, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            frame_num += 1

    cap.release()
    cv2.destroyAllWindows()
    return pd.DataFrame(dados_emocoes)



# Execução da Análise 
print(">>> Rodando análise com min_det_conf=0.95 e limiar_conf=0.95")
df = analisar_video(VIDEO_PATH, min_det_conf=0.95, limiar_conf=0.95)

# Salva CSV
df.to_csv("emocoes_configB.csv", index=False)
print(">>> Resultados salvos em emocoes_configB.csv")

# Gráficos
if not df.empty:
    # Gráfico de barras por emoção
    contagem = df['expressao'].value_counts()

    plt.figure(figsize=(8, 5))
    contagem.plot(kind='bar', color='skyblue')
    plt.title("Emoções Detectadas – Configuração B")
    plt.xlabel("Expressão")
    plt.ylabel("Ocorrências")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("grafico_emocoes_configB.png")
    plt.show()

    print("Gráfico salvo: grafico_emocoes.png")

    # Gráfico temporal por hora real
    plt.figure(figsize=(12, 4))
    plt.plot(df['tempo'], df['expressao'], marker='o', linestyle='-', color='green')
    plt.xticks(rotation=45)
    plt.title("Linha do Tempo de Emoções – Horário Real")
    plt.xlabel("Horário")
    plt.ylabel("Expressão")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("linha_tempo_emocoes.png")
    plt.show()

    print("Linha do tempo salva: linha_tempo_emocoes.png")

else:
    print("DataFrame vazio, nenhum gráfico gerado.")