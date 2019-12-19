from flask import Flask, render_template, redirect
import datetime
from json import load, dumps, loads
from requests import get, post, put


app = Flask(__name__)

####### Globals #############

my_list = ["5", "13", "22",]
ref_server =  ("HAPI UHN R4","http://hapi.fhir.org/baseR4/") # base_url for ref server

############################

# *********************** Fetch Resource ********************
def fetch(r_type,r_id):
    headers = {
    'Accept':'application/fhir+json',
    'Content-Type':'application/fhir+json'
    }
    # profile = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient' # The official URL for this profile is: http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient
    params = dict(
      # profile = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient' # The official URL for this profile is: http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient
        )
    r = get(f'{ref_server[1]}/{r_type}/{r_id}', params = params, headers = headers)
    # return r.status_code
    # view  output
    # return (r.json()["text"]["div"])
    return r.json()

@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    """convert a datetime to a different format."""
    return value.strftime(format)

@app.template_filter()
def to_json(value):
    return (dumps(value,indent=4))

app.jinja_env.filters['datetimefilter'] = datetimefilter
app.jinja_env.filters['tojson_pretty'] = to_json

@app.route("/")
def template_test():
    return render_template(
        'template.html',
         my_string="Get Resource from Reference Implementation",
        my_list=my_list,
         title="Index",
         current_time=datetime.datetime.now(),
         ref_server= ref_server[0],
         )

@app.route("/home")  # reroute to "/"
def home():
    return redirect('/')

@app.route("/about")
def about():
    return render_template('sub_template1.html',
                           my_string="this is a simple Flask template for creating FHIR Facades to get stuff from FHIR Reference Servers",
                           title="About",
                           current_time=datetime.datetime.now()
                           )

@app.route("/contact")
def contact():
    return render_template('sub_template2.html'
                           , my_string="Contact Information",
                            my_list=[18,19,20,21,22,23], title="Contact Us", current_time=datetime.datetime.now()
                            )

@app.route("/<string:p_id>")
def p_id(p_id):
    app.logger.info(f'************p_id={p_id}*************')
    r_dict=fetch("Patient",p_id)
    app.logger.info(f'******type r_dict={type(r_dict)}***')
    #r_dict = {"foo":"bar"}
    return render_template('sub_template3.html',
                           my_string=f"Getting Resource...for p_id={p_id}",
                           title=f"Patient: {p_id}", current_time=datetime.datetime.now(),
                           p_id=p_id,
                           r_dict=r_dict,
                           )


if __name__ == '__main__':
    app.run(debug=True)
