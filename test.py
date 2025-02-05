# import tensorflow as tf
# from tensorflow.keras.preprocessing.image import load_img, img_to_array

# # model = tf.keras.models.load_model("Cataract-Model")
# filename = "static/images/test_cat.png"

# img = load_img(filename, target_size=(224, 224))
# img = img_to_array(img)
# img = img.reshape(1, 224, 224, 3)

# img = img.astype('float32')
# # img = img/255.0

# # print(model.predict(img))
# # print(tf.__version__)

# for i in range(1):
#     print(i)

classes = ["cataract", "normal"]
result = [[0.9, 0.1]]
dict_result = {}
for i in range(2):
    # dict_result[result[0][i]] = classes[i]
    print(i)

# print(dict_result)