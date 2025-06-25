import os
from roboflow import Roboflow
from dotenv import load_dotenv

load_dotenv()

def baixar_modelo():
    api_key = os.getenv("ROBOFLOW_API_KEY")
    if not api_key:
        raise ValueError("API key do Roboflow não encontrada no .env")

    rf = Roboflow(api_key=api_key)

    project = rf.workspace("roboflow-100").project("vehicles-q0x2v")
    version = project.version(2)
    
    dataset = version.download("yolov8")
    model_path = dataset.location

    print(f"Modelo baixado em: {model_path}")
    return model_path
