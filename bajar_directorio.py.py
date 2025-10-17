from roboflow import Roboflow 
rf = Roboflow(api_key="OQyzBfxk67CZFkmoHPG8") 
project = rf.workspace("prueba-wd7ts").project("ocr-e7e5v-kzvsb") 
version = project.version(1) 
dataset = version.download("yolov8")
