# Import libraries
import cv2 # for reading images, draw bounding boxes
from ultralytics import YOLO 
import gradio as gr

# Define constants
ENTITIES_COLORS = {
    "Caption": (191, 100, 21),
    "Footnote": (2, 62, 115),
    "Formula": (140, 80, 58),
    "List-item": (168, 181, 69),
    "Page-footer": (2, 69, 84),
    "Page-header": (83, 115, 106),
    "Picture": (255, 72, 88),
    "Section-header": (0, 204, 192),
    "Table": (116, 127, 127),
    "Text": (0, 153, 221),
    "Title": (196, 51, 2)
}
BOX_PADDING = 2

# Load models
DETECTION_MODEL = YOLO("models/dla-model.pt") 

def detect(image_path):
    """
    Output inference image with bounding box

    Args:
    - image: to check for checkboxes

    Return: image with bounding boxes drawn 
    """
    image = cv2.imread(image_path)
    if image is None:
        return image
    
    # Predict on image
    results = DETECTION_MODEL.predict(source=image, conf=0.2, iou=0.8) # Predict on image
    boxes = results[0].boxes # Get bounding boxes

    if len(boxes) == 0:
        return image

    # Get bounding boxes
    for box in boxes:
        detection_class_conf = round(box.conf.item(), 2)
        cls = list(ENTITIES_COLORS)[int(box.cls)]
        # Get start and end points of the current box
        start_box = (int(box.xyxy[0][0]), int(box.xyxy[0][1]))
        end_box = (int(box.xyxy[0][2]), int(box.xyxy[0][3]))

        
        # 01. DRAW BOUNDING BOX OF OBJECT
        line_thickness = round(0.002 * (image.shape[0] + image.shape[1]) / 2) + 1
        image = cv2.rectangle(img=image, 
                              pt1=start_box, 
                              pt2=end_box,
                              color=ENTITIES_COLORS[cls], 
                              thickness = line_thickness) # Draw the box with predefined colors
        
        # 02. DRAW LABEL
        text = cls + " " + str(detection_class_conf)
        # Get text dimensions to draw wrapping box
        font_thickness =  max(line_thickness - 1, 1)
        (text_w, text_h), _ = cv2.getTextSize(text=text, fontFace=2, fontScale=line_thickness/3, thickness=font_thickness)
        # Draw wrapping box for text
        image = cv2.rectangle(img=image,
                              pt1=(start_box[0], start_box[1] - text_h - BOX_PADDING*2),
                              pt2=(start_box[0] + text_w + BOX_PADDING * 2, start_box[1]),
                              color=ENTITIES_COLORS[cls],
                              thickness=-1)
        # Put class name on image
        start_text = (start_box[0] + BOX_PADDING, start_box[1] - BOX_PADDING)
        image = cv2.putText(img=image, text=text, org=start_text, fontFace=0, color=(255,255,255), fontScale=line_thickness/3, thickness=font_thickness)
        
    return image

iface = gr.Interface(fn=detect, 
                     inputs=gr.inputs.Image(label="Upload scanned document", type="filepath"), 
                     outputs="image")
iface.launch()
