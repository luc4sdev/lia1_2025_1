import os
import cv2
from ultralytics import YOLO
from collections import defaultdict

def contar_veiculos(model_path: str, video_path: str) -> dict:
    model_file = os.path.join(model_path, "yolov8n.pt")
    model = YOLO(model_file)

    CLASSES_INTERESSE = {'car', 'truck', 'bus', 'motorcycle', 'bicycle'}

    cap = cv2.VideoCapture(video_path)
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # Largura do vídeo
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) # Altura do vídeo
    fps    = cap.get(cv2.CAP_PROP_FPS) # Frames por segundo
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) # Total de frames
    duration = total_frames / fps   # Duração total do vídeo em segundos

    os.makedirs("static", exist_ok=True)
    saida_path = os.path.join("static", "video_saida_detectado.mp4")

    writer = cv2.VideoWriter(saida_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    veiculos_rastreados = set() # Guarda os IDs únicos dos veículos detectados
    posicoes = defaultdict(list)  # tracking_id -> [lista de posições (x, y)]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.track(frame, persist=True, verbose=False) # Detecta e rastreia veículos no frame atual

        if not results or not results[0].boxes:
            writer.write(frame) # Se não detectou nada, só escreve o frame no vídeo
            continue

        for box in results[0].boxes:
            cls_id = int(box.cls[0]) # ID da classe detectada (inteiro)
            nome = model.names[cls_id].lower()  # Nome da classe, ex: "car"

            if nome in CLASSES_INTERESSE:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Coordenadas da caixa delimitadora
                cx = (x1 + x2) // 2 # Centro X da caixa
                cy = (y1 + y2) // 2 # Centro Y da caixa

                tracking_id = int(box.id[0]) if box.id is not None else None
                if tracking_id is not None:
                    veiculos_rastreados.add(tracking_id)  # Guarda o ID único do veículo
                    posicoes[tracking_id].append((cx, cy))  # Armazena o centro para análise de velocidade

                label = f"{nome} #{tracking_id}"  # Exemplo: "car #12"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2) # Desenha a caixa verde
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        writer.write(frame) # Escreve o frame anotado no vídeo de saída

    cap.release()
    writer.release()

    # Análise de velocidade média (deslocamento euclidiano médio por frame)
    velocidades = []
    # Para cada veículo rastreado (com um tracking_id)
    for trajetoria in posicoes.values():
        if len(trajetoria) < 2:
            continue # Não tem como calcular velocidade com só uma posição
        d = 0
        # Soma das distâncias entre cada par de posições consecutivas
        for i in range(1, len(trajetoria)):
            dx = trajetoria[i][0] - trajetoria[i-1][0] # deslocamento em X
            dy = trajetoria[i][1] - trajetoria[i-1][1] # deslocamento em Y
            d += (dx**2 + dy**2)**0.5 # Soma as distâncias euclidianas (teorema de Pitágoras)
        velocidade_media = d / len(trajetoria) # Média de deslocamento por frame
        velocidades.append(velocidade_media)

    # Estatísticas
    pixels_por_metro = 40  # ajuste conforme sua referência real
    velocidades_kmh = [v * fps / pixels_por_metro * 3.6 for v in velocidades]
    media_kmh = sum(velocidades_kmh) / len(velocidades_kmh) if velocidades_kmh else 0
    total_veiculos = len(veiculos_rastreados)
    veiculos_por_segundo = total_veiculos / duration
    #media_velocidade_px = sum(velocidades) / len(velocidades) if velocidades else 0

    return {
        "total": total_veiculos,
        "duracao_s": round(duration, 1),
        "veiculos_por_segundo": round(veiculos_por_segundo, 2),
        "media_velocidade_kmh": round(media_kmh, 2)
    }
