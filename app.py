from flask import Flask, render_template, request, redirect, make_response, session, Blueprint
# from flask_session import Session
import json
import pymysql.cursors
import os
import csv
import logging
from collections import Counter
import datetime
import random
from werkzeug.security import generate_password_hash, check_password_hash
from io import StringIO
import re

app = Flask(__name__)
bp = Blueprint("mp", __name__, template_folder="templates", static_folder="static")

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WEBSITE_URL = "https://mit-surveyor.com/mp/"

with open("secrets.json", "r") as secrets_file:
    SECRETS = json.loads(secrets_file.read())

app.config.update(
    TEMPLATES_AUTO_RELOAD = True,
    SESSION_PERMANENT = False,
    SESSION_TYPE = "filesystem",
    SECRET_KEY = SECRETS["SECRET_KEY"]
)

## Experiment information
GITHUB_PREFIX = "https://github.com/mpoliak/noise_priming/blob/main/"
GITHUB_SUFFIX = "?raw=true"
ITEMS = 32
CONDITIONS = 4
LANGUAGES = ["en", "fi"]
PRIME = ["same", "different"]
NOISE_LEVELS = ["-12", "-9", "-6", "-3", "3", "6", "9", "12"]


# health route - used by AWS target group to route traffic to the instance
@bp.route("/health")
def health():
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@bp.route("/")
def index():
   return render_template("index.html")

@bp.route("/initials")
def initials():
    return render_template("initials.html")

@bp.route("/experiment/wnp")
def experiment():
    stimuli = get_stimuli()
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(list(stimuli[0].keys()))

    for item in stimuli:
        cw.writerow(item.values())

    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y_%m_%d-%H_%M")
    export_name = "data_" + timestamp
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = \
        "attachment; filename=" + export_name + ".csv"
    output.headers["Contenty-type"] = "text/csv"

    return output
    return render_template("white_noise_priming_experiment.html", items = stimuli)

def get_stimuli():
    experimental_list = []
    for item in range(ITEMS):
        language = LANGUAGES[item % 2]
        if item < ITEMS / 2:
            prime = PRIME[0]
        else:
            prime = PRIME[1]
        noise_level = NOISE_LEVELS[item % len(NOISE_LEVELS)]
        experimental_list.append(
                {"item":item+1,
                "language":language,
                "prime":prime,
                "prime_id":-1,
                "noise_level":noise_level}
            )
    ## Randomize pairings with sentences
    item_order = list(range(ITEMS))
    random.shuffle(item_order)
    for i in range(len(experimental_list)):
        experimental_list[i]["item"] = item_order[i]+1
    random.shuffle(experimental_list)

    for i in range(len(experimental_list)):
        experimental_list[i]["presentation_order"] = i+1


    different_primes_en = [i for i in range(CONDITIONS*2)]
    random.shuffle(different_primes_en)
    different_primes_fi = [i for i in range(CONDITIONS*2)]
    random.shuffle(different_primes_en)
    different_primes = {
            "en":different_primes_en,
            "fi":different_primes_fi
            }

    for item in experimental_list:
        if item["prime"] == "same":
            prime_link = f"primes/{item['language']}_{item['item']}_prime_same.mp3"
        else:
            different_prime_id = different_primes[item["language"]].pop()
            prime_link = f"primes/{item['language']}_{different_prime_id+1}_prime_different.mp3"
        
        experimental_list[item["presentation_order"]-1]["prime_link"] = GITHUB_PREFIX + prime_link + GITHUB_SUFFIX
        critical_link = f"noise_{item['noise_level']}/{item['language']}_{item['item']}_noise_{item['noise_level']}.mp3"
        experimental_list[item["presentation_order"]-1]["critical_link"] = GITHUB_PREFIX + critical_link + GITHUB_SUFFIX
        if item["prime"] != "same":
            experimental_list[item["presentation_order"]-1]["prime_id"] = different_prime_id

    return experimental_list

    
@bp.route("/completion")
def completion():
    return render_template("completion.html")

@bp.route("/getdata/wnp")
def getdata():
    ## Get connection
    connection = pymysql.connect(
        host=SECRETS["DB_HOST"],
        user=SECRETS["DB_USER"],
        database=SECRETS["DB_NAME"],
        password=SECRETS["DB_PASS"],
        cursorclass = pymysql.cursors.DictCursor
    )
    ## Extract all data
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                *
                FROM 
                data_priming_white_noise_eng_smallsnr
                """
            )
            result = cursor.fetchall()
            si = StringIO()
            cw = csv.writer(si)
            cw.writerow(list(result[0].keys()))

            for item in result:
                cw.writerow(item.values())

            timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y_%m_%d-%H_%M")
            export_name = "data_" + timestamp
            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = \
                "attachment; filename=" + export_name + ".csv"
            output.headers["Contenty-type"] = "text/csv"

            return output

@bp.route("/submitdata/", methods=["POST"])
def submitdata():
    request_data = request.json
    connection = pymysql.connect(
            host=SECRETS["DB_HOST"],
            user=SECRETS["DB_USER"],
            database=SECRETS["DB_NAME"],
            password=SECRETS["DB_PASS"],
            cursorclass = pymysql.cursors.DictCursor
        )
    timestamp = datetime.datetime.now()
    with connection:
        with connection.cursor() as cursor:
            for datum in request_data:
                cursor.execute(
                        """
                        INSERT INTO data_priming_white_noise_eng_smallsnr
                            (prolific_id,
                            item,
                            noise_level,
                            prime,
                            prime_id,
                            language,
                            presentation_order,
                            rating,
                            timestamp
                            )
                        VALUES
                            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            datum["prolific_id"],
                            datum["item"],
                            datum["noise_level"],
                            datum["prime"],
                            datum["prime_id"],
                            datum["language"],
                            datum["presentation_order"],
                            datum["rating"],
                            timestamp
                        )
                )
            connection.commit()
    return "success"


app.register_blueprint(bp, url_prefix="/aux")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)

