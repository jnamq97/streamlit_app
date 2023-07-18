from ultralytics import YOLO

# Load a model
model = YOLO("yolov8n.yaml")  # build a new model from scratch
model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)

# Use the model
model.train(data="/opt/ml/final_project/data.yaml", epochs=100)  # train the model
metrics = model.val()  # evaluate model performance on the validation set
# results = model("https://ultralytics.com/images/bus.jpg")  # predict on an image
# im = '/opt/ml/final_project/datasets/data/images/ZED3_KSC_047442_L_P009367_png.rf.d96c2b97f43448b522ae5b407ca31eba.jpg'
# results = model(im)
path = model.export()  # export the model to pytorch(default) format