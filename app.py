from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard', methods=['POST'])
def device():
    return render_template('dashboard.html', device_id=request.form['device_id'])

if __name__ == '__main__':
    app.run()