'''
Neural Network for detecting the BPM of a 4 second clip of music
'''

from matplotlib import pyplot as plt
import numpy as np
import cPickle
from vec_to_bpm import vec_to_bpm
np.random.seed(1)  # for reproducibility

from keras.callbacks import EarlyStopping
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation, Reshape, Flatten
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.layers.wrappers import TimeDistributed
from keras.optimizers import SGD, Adam, RMSprop, Adadelta

print("Loading training data...")
X_train, y_train, bpms_train, fnames_train = cPickle.load(open('Xy_pulse3.dump', 'rb'))
print("Loading validation data...")
X_val, y_val, bpms_val, fnames_val = cPickle.load(open('Xy_vali_pulse3.dump', 'rb'))

input_time_dim = X_train.shape[2]
input_freq_dim = X_train.shape[3]
output_length = y_train.shape[1]

drop_hid = 0.25
num_filters = 32
dense_widths = [output_length*2, output_length]

early = EarlyStopping(monitor='val_loss', patience=1, verbose=1, mode='auto')

model = Sequential()

model.add(Convolution2D(num_filters, 3, 3, border_mode='same', 
                        input_shape=(1, input_time_dim, input_freq_dim)))
model.add(Activation('relu'))

model.add(Convolution2D(num_filters, 5, 5, border_mode='same'))
model.add(Activation('relu'))

model.add(Reshape((input_time_dim, input_freq_dim * num_filters)))

model.add(TimeDistributed(Dense(256)))
model.add(Activation('relu'))
model.add(TimeDistributed(Dense(128)))
model.add(Activation('relu'))
model.add(TimeDistributed(Dense(8)))
model.add(Activation('relu'))

model.add(Flatten())
if drop_hid:
    model.add(Dropout(drop_hid))

for w in dense_widths:
    model.add(Dense(w))
    model.add(Activation('relu'))
    if drop_hid:
        model.add(Dropout(drop_hid))
model.add(Dense(output_length))
model.add(Activation('relu'))

model.summary()

#opt = Adadelta()
#opt = SGD(lr=0.001)
opt = Adam()

model.compile(loss='mse',
              optimizer=opt,
              metrics=[])

batch_size = 1536
nb_epoch = 2
history = model.fit(X_train, y_train,
                    batch_size=batch_size, nb_epoch=nb_epoch,
                    verbose=1, validation_data=(X_val, y_val),
                    shuffle=True, callbacks=[early])

model.save('convnet_aws.kerasmodel')

