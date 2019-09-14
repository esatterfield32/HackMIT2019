from flask import Flask, escape, request, render_template

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        userInput = request.form['userInput']
        return render_template('index.html', hasInput = True, userInput = userInput)
    return render_template('index.html', hasInput = False)
    

if __name__ == '__main__':
    app.run(debug=True)