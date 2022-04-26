from flask import Flask, render_template, request
import Music_Generation
import Guitar_Music_Generation
app=Flask('Music_Generation')
@app.route('/')
def show_home():
    return render_template('index.html')
@app.route('/instrument')
def show_instrument():
    return render_template('Instrument.html') 
@app.route('/piano')
def play_piano():
    #render_template('loader.html')
    Music_Generation.generate()
    return render_template('piano.html')
@app.route('/guitar')
def play_guitar():
    #render_template('loader.html')
    Guitar_Music_Generation.generate()
    return render_template('guitar.html')
@app.route('/buy_piano')
def buy_piano():
    return render_template('payment_piano.html')
@app.route('/buy_guitar')
def buy_guitar():
    return render_template('payment_guitar.html')

app.run("localhost", "9999", debug=True)
