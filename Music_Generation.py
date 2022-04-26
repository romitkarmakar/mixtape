#!/usr/bin/env python
# coding: utf-8
from music21 import converter, instrument, note, chord, stream
import glob
import pickle
import numpy as np
from keras.utils import np_utils
from keras.models import Sequential, load_model
from keras.layers import *
from keras.callbacks import ModelCheckpoint, EarlyStopping
from flask import Flask, render_template, request

def generate():
    with open("notes", 'rb') as f:
        notes= pickle.load(f)

    n_vocab = len(set(notes))

    sequence_length = 100
    pitchnames = sorted(set(notes))
    ele_to_int = dict( (ele, num) for num, ele in enumerate(pitchnames) )
    model = load_model("new_weights.hdf5")



    sequence_length = 100
    network_input = []

    for i in range(len(notes) - sequence_length):
        seq_in = notes[i : i+sequence_length] # contains 100 values
        network_input.append([ele_to_int[ch] for ch in seq_in])


  
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





    print(prediction_output)

    offset = 0 
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

    # create a stream object from the generated notes
    midi_stream = stream.Stream(output_notes)
    midi_stream.write('midi', fp = "static/test_output.mid")


    # In[41]:


   # midi_stream.show('midi')








    