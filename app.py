from flask import Flask, render_template, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField, SelectField
from wtforms.validators import DataRequired
from wtforms.widgets import PasswordInput
from functions import scrap_url_list, all_intersections
import json
import os
import openpyxl
import pandas as pd


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

project_folder = os.path.dirname(os.path.abspath(__file__))


class KeywordsForm(FlaskForm):
    report_name = StringField("Name of report", validators=[DataRequired()])
    keywords = TextAreaField("Put list of keywords (one keyword on the line)", validators=[DataRequired()])
    country = SelectField("Country", choices=[('CZ,cs_CZ', 'CZ'), ('SK,sk_SK', 'SK'), ('US,en_US', 'US'), ('DE,de_DE', 'DE')])
    api_key = StringField("Api-key for Serpsbot API", widget=PasswordInput(hide_value=False), validators=[DataRequired()])
    accuracy = RadioField("Accuracy:",
                          choices=[('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8')],
                          validators=[DataRequired()])
    submit = SubmitField("Submit")


class OpenreportForm(FlaskForm):
    report_name = StringField("Name of report", validators=[DataRequired()])
    accuracy = RadioField("Accuracy:",choices=[('2','2'),('3','3'), ('4','4'),('5','5'),('6','6'),('7','7'),('8','8')],
                          validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/', methods=["GET", "POST"])
def inputform():

    keywords = None
    api_key = None
    form = KeywordsForm()
    form.country.data = 'CZ,cs_CZ'
    if form.validate_on_submit():
        report_name = form.report_name.data
        keywords = form.keywords.data
        api_key = form.api_key.data
        accuracy = form.accuracy.data
        keywords_list = keywords.split("\r\n")
        serp_results_dic = {}
        for query in keywords_list:
            if query != "":
                url_list = scrap_url_list(query, api_key)
                serp_results_dic[query] = url_list
            else:
                pass
        if not os.path.exists(report_name):
            file = open(report_name, "w")
            file.write(json.dumps(serp_results_dic))
            file.close()
        else:
            for i in range(100):
                new_name = f'{report_name} ({i})'
                if not os.path.exists(new_name):
                    file = open(new_name, "w")
                    file.write(json.dumps(serp_results_dic))
                    file.close()
                    report_name = new_name
                    break
                else:
                    pass
        results = all_intersections(report_name, int(accuracy))
        pd_data = pd.DataFrame.from_dict(results, orient='index')
        export_filename = f"{report_name}.xlsx"
        pd_data.to_excel(os.path.join(project_folder,export_filename))
        return render_template("openreport.html",
                               nalezeno=True,
                               form=form,
                               results=results,
                               export_filename=export_filename)
    return render_template("inputform.html", keywords = keywords, form = form)

@app.route('/open-report', methods=["GET", "POST"])
def openreport():
    form = OpenreportForm()
    nalezeno = None
    results = None
    export_filename = None
    if form.validate_on_submit():
        report_name = form.report_name.data
        accuracy = form.accuracy.data
        if os.path.exists(report_name):
            nalezeno = True
            results = all_intersections(report_name, int(accuracy))
            pd_data = pd.DataFrame.from_dict(results, orient='index')
            export_filename = f"{report_name}.xlsx"
            pd_data.to_excel(export_filename)

        else:
            nalezeno = False
    return render_template("openreport.html",
                           nalezeno = nalezeno,
                           form = form,
                           results = results,
                           export_filename = export_filename)


@app.route('/download/<path:filename>')
def download(filename):
    return send_file(os.path.join(project_folder, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
