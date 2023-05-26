from skimage import io
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import cv2

class FeatureExtractor():
  def __init__(self,model_url,IMAGE_SHAPE=(224,224)):

    self.IMAGE_SHAPE = IMAGE_SHAPE
    self.INPUT_SHAPE = IMAGE_SHAPE+(3,)
    layer = hub.KerasLayer(model_url, input_shape=self.INPUT_SHAPE)
    self.model = tf.keras.Sequential([layer])
  
  def url_to_img(self, url):
    # print(url)
    try:
        image_np = io.imread( url )
    except:
        image_np = np.zeros((self.INPUT_SHAPE))
    image = np.asarray(image_np, dtype="uint8")
    if format=='BGR' :
      image = image[...,[2,1,0]]
    np_img = cv2.resize(image,self.IMAGE_SHAPE)
    return np_img

  def get_feature_extraction(self, urls):
    np_list = [self.url_to_img(url) for url in urls]
    inputs = np.stack(np_list)
    outputs = self.model.predict(inputs)
    return outputs