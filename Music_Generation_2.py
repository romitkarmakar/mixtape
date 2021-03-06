#!/usr/bin/env python
# coding: utf-8

# ### Imports

# In[1]:


from music21 import converter, instrument, note, chord, stream
import glob
import pickle
import numpy as np
from keras.utils import np_utils


# ## Read a Midi File

# In[2]:


#midi = converter.parse("midi_songs/EyesOnMePiano.mid")


# In[3]:


#midi


# In[4]:


#midi.show('midi')


# In[5]:


#midi.show('text')


# In[6]:


# Flat all the elements
#elements_to_parse = midi.flat.notes


# In[7]:


#len(elements_to_parse)


# In[8]:


#for e in elements_to_parse:
    #print(e, e.offset)


# In[ ]:





# In[9]:


"""
notes_demo = []

for ele in elements_to_parse:
    # If the element is a Note,  then store it's pitch
    if isinstance(ele, note.Note):
        notes_demo.append(str(ele.pitch))
    
    # If the element is a Chord, split each note of chord and join them with +
    elif isinstance(ele, chord.Chord):
        notes_demo.append("+".join(str(n) for n in ele.normalOrder))
        
"""


# In[10]:


#len(notes_demo)


# In[11]:


#isinstance(elements_to_parse[68], chord.Chord)


# # Preprocessing all Files

# In[12]:


'''
notes = []

for file in glob.glob("midi_songs/*.mid"):
    midi = converter.parse(file) # Convert file into stream.Score Object
    
    print("parsing %s"%file)
    
    elements_to_parse = midi.flat.notes
    
    
    for ele in elements_to_parse:
        # If the element is a Note,  then store it's pitch
        if isinstance(ele, note.Note):
            notes.append(str(ele.pitch))

        # If the element is a Chord, split each note of chord and join them with +
        elif isinstance(ele, chord.Chord):
            notes.append("+".join(str(n) for n in ele.normalOrder))
'''


# In[ ]:





# In[13]:


#len(notes)


# In[14]:


#with open("notes", 'wb') as filepath:
    #pickle.dump(notes, filepath)


# In[15]:


with open("notes", 'rb') as f:
    notes= pickle.load(f)


# In[16]:


n_vocab = len(set(notes))


# In[17]:


#print("Total notes- ", len(notes))
#print("Unique notes- ",  n_vocab)


# In[18]:


#print(notes[100:200])


# # Prepare Sequential Data for LSTM

# In[19]:


# Hoe many elements LSTM input should consider
sequence_length = 100


# In[20]:


# All unique classes
pitchnames = sorted(set(notes))


# In[21]:


# Mapping between ele to int value
ele_to_int = dict( (ele, num) for num, ele in enumerate(pitchnames) )


# In[22]:


#network_input = []
#network_output = []


# In[23]:


"""
for i in range(len(notes) - sequence_length):
    seq_in = notes[i : i+sequence_length] # contains 100 values
    seq_out = notes[i + sequence_length]
    
    network_input.append([ele_to_int[ch] for ch in seq_in])
    network_output.append(ele_to_int[seq_out])
"""


# In[24]:


# No. of examples
#n_patterns = len(network_input)
#print(n_patterns)


# In[25]:


# Desired shape for LSTM
#network_input = np.reshape(network_input, (n_patterns, sequence_length, 1))
#print(network_input.shape)


# In[26]:


#normalised_network_input = network_input/float(n_vocab)


# In[27]:


# Network output are the classes, encode into one hot vector
#network_output = np_utils.to_categorical(network_output)


# In[28]:


#network_output.shape


# In[29]:


#print(normalised_network_input.shape)
#print(network_output.shape)


# # Create Model

# In[30]:


from keras.models import Sequential, load_model
from keras.layers import *
from keras.callbacks import ModelCheckpoint, EarlyStopping


# In[31]:


"""
model = Sequential()
model.add( LSTM(units=512,
               input_shape = (normalised_network_input.shape[1], normalised_network_input.shape[2]),
               return_sequences = True) )
model.add( Dropout(0.3) )
model.add( LSTM(512, return_sequences=True) )
model.add( Dropout(0.3) )
model.add( LSTM(512) )
model.add( Dense(256) )
model.add( Dropout(0.3) )
model.add( Dense(n_vocab, activation="softmax") )
"""


# In[32]:


#model.compile(loss="categorical_crossentropy", optimizer="adam")


# In[33]:


#model.summary()


# In[34]:


#checkpoint = ModelCheckpoint("model.hdf5", monitor='loss', verbose=0, save_best_only=True, mode='min')

#model_his = model.fit(normalised_network_input, network_output, epochs=100, batch_size=64, callbacks=[checkpoint])


# In[35]:


model = load_model("new_weights.hdf5")


# # Predictions

# In[36]:


sequence_length = 100
network_input = []

for i in range(len(notes) - sequence_length):
    seq_in = notes[i : i+sequence_length] # contains 100 values
    network_input.append([ele_to_int[ch] for ch in seq_in])


# In[37]:


# Any random start index
start = np.random.randint(len(network_input) - 1)

# Mapping int_to_ele
int_to_ele = dict((num, ele) for num, ele in enumerate(pitchnames))

# Initial pattern 
pattern = network_input[start]
prediction_output = []

# generate 200 elements
for note_index in range(200):
    prediction_input = np.reshape(pattern, (1, len(pattern), 1)) # convert into numpy desired shape 
    prediction_input = prediction_input/float(n_vocab) # normalise
    
    prediction =  model.predict(prediction_input, verbose=0)
    
    idx = np.argmax(prediction)
    result = int_to_ele[idx]
    prediction_output.append(result) 
    
    # Remove the first value, and append the recent value.. 
    # This way input is moving forward step-by-step with time..
    pattern.append(idx)
    pattern = pattern[1:]


# In[38]:


print(prediction_output)


# # Create Midi File

# In[ ]:





# In[39]:


offset = 0 # Time
output_notes = []

for pattern in prediction_output:
    
    # if the pattern is a chord
    if ('+' in pattern) or pattern.isdigit():
        notes_in_chord = pattern.split('+')
        temp_notes = []
        for current_note in notes_in_chord:
            new_note = note.Note(int(current_note))  # create Note object for each note in the chord
            new_note.storedInstrument = instrument.Piano()
            temp_notes.append(new_note)
            
        
        new_chord = chord.Chord(temp_notes) # creates the chord() from the list of notes
        new_chord.offset = offset
        output_notes.append(new_chord)
    
    else:
            # if the pattern is a note
        new_note = note.Note(pattern)
        new_note.offset = offset
        new_note.storedInstrument = instrument.Piano()
        output_notes.append(new_note)
        
    offset += 0.5


# In[ ]:





# In[40]:


# create a stream object from the generated notes
midi_stream = stream.Stream(output_notes)
midi_stream.write('midi', fp = "test_output.mid")


# In[41]:


midi_stream.show('midi')


# In[ ]:




