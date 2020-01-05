from flask import Flask, render_template, redirect, url_for, send_from_directory
import datetime
from json import load, dumps, loads
from requests import get, post, put
from commonmark import commonmark
from pathlib import Path

app = Flask(__name__)
global_path = Path(app.root_path)
####### Globals #############

my_list = ["5", "13", "22", "foo",]
ref_server =  ("HAPI UHN R4","http://hapi.fhir.org/baseR4/") # base_url for ref server

############################

# *********************** Fetch Resource ********************
def fetch(Type,**kwargs):
    '''
    fetch resource by search parameters e.g. _id
    return resource as fhirclient model
    '''
    headers = {
    'Accept':'application/fhir+json',
    'Content-Type':'application/fhir+json'
    }
    r_url = f'{ref_server[1]}/{Type.capitalize()}'
    with get(r_url, headers=headers, params=kwargs) as r:
        # return r.status_code--  always 200 for search
        # view  output
        # return (r.json()["text"]["div"])
        app.logger.info(f'***** r.status_code={ r.status_code}***')
        app.logger.info(f'***** r.json()["total"]={r.json()["total"]}***')
        if r.status_code <300 and r.json()["total"] > 0: # >0
            return r.json()["entry"][0]["resource"] # just the first for now
        else:
            return None

@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    """convert a datetime to a different format."""
    return value.strftime(format)

@app.template_filter()
def markdown(text, *args, **kwargs):
    return commonmark(text, *args, **kwargs)

app.jinja_env.filters['datetimefilter'] = datetimefilter
app.jinja_env.filters['markdown'] = markdown

@app.route("/")
def template_test():
    return render_template(
        'template.html',
         my_string="**Get Resource from Reference Implementation**",
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
    my_string='''
this is a simple Flask template for:

-  creating FHIR Facades to get stuff from the **{ref_server}** Reference Server
-  display the Resource
'''.format(ref_server=ref_server[0])
    return render_template('sub_template1.html',
                           my_string=my_string,
                           title="About",
                           current_time=datetime.datetime.now(),
                           )

@app.route("/contact")
def contact():
    return render_template('sub_template2.html'
                           , my_string="Contact Information",
                            title="Contact Us",
                            current_time=datetime.datetime.now(),
                            )

@app.route("/not_found/<r_id>")
def page_not_found(r_id):
    my_string='''
>Woops, that resource {r_id} doesn't exist! (0 search results)

-  Click on the home button in the nav bar and try a different id
'''.format(r_id=r_id)
    return render_template('sub_template1.html',
                           my_string=my_string,
                           title="Resource not found error",
                           current_time=datetime.datetime.now(),
                           )


@app.route("/<string:p_id>")
def p_id(p_id):
    app.logger.info(f'************p_id={p_id}*************')
    r_dict=fetch("Patient",_id=p_id)
    app.logger.info(f'******type r_dict={type(r_dict)}***')
    #r_dict = {"foo":"bar"}
    if r_dict:
        local_path = global_path / "downloads" / f"Patient_{p_id}.json"
        local_path.write_text(dumps(r_dict,indent=4))
        return render_template('sub_template3.html',
                               my_string=f"Getting Resource...for p_id={p_id}",
                               title=f"Patient: {p_id}", current_time=datetime.datetime.now(),
                               p_id=p_id,
                               r_dict=r_dict,
                               )
    else:
        return redirect(url_for('page_not_found',  r_id=p_id))

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    directory= global_path / "downloads"
    return send_from_directory(directory= directory, filename=f'{filename}.json', as_attachment=True, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
