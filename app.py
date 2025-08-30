from flask import Flask, render_template, request, send_file
from xhtml2pdf import pisa
from io import BytesIO
from flask import Flask, request, render_template
import pickle
import pandas as pd

app = Flask(__name__)

# Load data
medicines_dict = pickle.load(open('medicine_dict.pkl', 'rb'))
medicines = pd.DataFrame(medicines_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Recommendation function
def recommend(medicine):
    if medicine not in medicines['Drug_Name'].values:
        return None  # Handle unknown medicine
    medicine_index = medicines[medicines['Drug_Name'] == medicine].index[0]
    distances = similarity[medicine_index]
    medicines_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:9]
    return [medicines.iloc[i[0]].Drug_Name for i in medicines_list]

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    selected_medicine_name = None
    error = None

    if request.method == 'POST':
        selected_medicine_name = request.form.get('medicine')
        if selected_medicine_name in medicines['Drug_Name'].values:
            recommendations = recommend(selected_medicine_name)
        else:
            error = f"Medicine '{selected_medicine_name}' not found in our database."

    return render_template('index.html',
                           medicines=medicines['Drug_Name'].tolist(),
                           recommendations=recommendations,
                           selected_medicine_name=selected_medicine_name,
                           error=error)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    selected_medicine = request.form.get('selected_medicine')
    recommendations = request.form.getlist('recommendations')

    html = render_template('pdf_template.html', selected_medicine=selected_medicine, recommendations=recommendations)
    result = BytesIO()
    pisa.CreatePDF(html, dest=result)
    result.seek(0)
    return send_file(result, download_name='recommendations.pdf', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
