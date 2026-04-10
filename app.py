from flask import Flask, render_template, request, send_file, session
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os

app = Flask(__name__)
app.secret_key = 'secret123'  # required for session


# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Upload + Process
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']

    if file:
        df = pd.read_csv(file)

        revenue = df['Revenue'].sum()
        expenses = df['Expenses'].sum()
        profit = revenue - expenses

        # Save in session (for PDF)
        session['revenue'] = revenue
        session['expenses'] = expenses
        session['profit'] = profit

        # Create Chart
        plt.figure()
        labels = ['Revenue', 'Expenses', 'Profit']
        values = [revenue, expenses, profit]
        plt.bar(labels, values)
        plt.savefig('static/chart.png')
        plt.close()

        table = df.head().to_html(classes='table-auto w-full')

        return render_template(
            'dashboard.html',
            revenue=revenue,
            expenses=expenses,
            profit=profit,
            table=table
        )

    return "No file uploaded"


# PDF Download
@app.route('/download')
def download():
    file_path = "report.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []

    content.append(Paragraph("SmartFinance AI Report", styles['Title']))
    content.append(Paragraph(f"Revenue: ₹{session.get('revenue', 0)}", styles['Normal']))
    content.append(Paragraph(f"Expenses: ₹{session.get('expenses', 0)}", styles['Normal']))
    content.append(Paragraph(f"Profit: ₹{session.get('profit', 0)}", styles['Normal']))

    doc.build(content)

    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)