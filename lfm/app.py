import os
import requests
from email import utils
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory, abort
from config import Config

app = Flask(__name__)
config = Config()


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/", methods=["GET", "POST"])
def hello_readers():
    if request.method == "GET":
        payload = {"user": "thexiffy", "title": "Example URLs"}
    else:
        payload = {"user": request.form["user"], "title": "Your URLs"}
    payload["base_url"] = config.base_url
    return render_template("home.html", context=payload)


@app.route("/<user>")
def recent_tracks(user):
    # /2.0/?method=user.getrecenttracks&user=rj&api_key=YOUR_API_KEY&format=json
    payload = {
        "api_key": config.api_key,
        "method": "user.getrecenttracks",
        "user": user,
        "format": "json",
    }
    response = requests.get(config.api_base_url, params=payload)
    try:
        json = response.json()
        if "recenttracks" in json:
            context = {"user": user, "tracks": json["recenttracks"], "type": "recent"}
            return (
                render_template("recent.html", context=context),
                200,
                {
                    "Content-type": "text/xml; charset=utf-8",
                    "Cache-Control": "max-age=600",
                },
            )
        else:
            abort(response.status_code)
    except ValueError:
        return response.content


@app.route("/<user>/loved")
def loved_tracks(user):
    payload = {
        "api_key": config.api_key,
        "method": "user.getlovedtracks",
        "user": user,
        "format": "json",
    }
    response = requests.get(config.api_base_url, params=payload)
    try:
        json = response.json()
        if "lovedtracks" in json:
            context = {"user": user, "tracks": json["lovedtracks"], "type": "loved"}
            return (
                render_template("loved.html", context=context),
                200,
                {
                    "Content-type": "text/xml; charset=utf-8",
                    "Cache-Control": "max-age=600",
                },
            )
        else:
            abort(response.status_code)
    except ValueError:
        return response.content


@app.route("/<user>/toptracks")
def toptracks(user):
    payload = {
        "api_key": config.api_key,
        "method": "user.gettoptracks",
        "user": user,
        "format": "json",
        "period": valid_period(request.args),
    }
    response = requests.get(config.api_base_url, params=payload)
    try:
        json = response.json()
        if "toptracks" in json:
            context = {
                "user": user,
                "tracks": json["toptracks"],
                "type": f"toptracks?period={valid_period(request.args)}",
                "title": f"Top tracks [{valid_period(request.args)}]",
            }
            return (
                render_template("toptracks.html", context=context),
                200,
                {
                    "Content-type": "text/xml; charset=utf-8",
                    "Cache-Control": "max-age=600",
                },
            )
        else:
            return json
    except ValueError:
        return response.content


@app.route("/<user>/topartists")
def topartists(user):
    payload = {
        "api_key": config.api_key,
        "method": "user.gettopartists",
        "user": user,
        "format": "json",
        "period": valid_period(request.args),
    }
    response = requests.get(config.api_base_url, params=payload)
    try:
        json = response.json()
        if "topartists" in json:
            context = {
                "user": user,
                "artists": json["topartists"],
                "type": f"topartists?period={valid_period(request.args)}",
                "title": f"Top artists [{valid_period(request.args)}]",
            }
            return (
                render_template("topartists.html", context=context),
                200,
                {
                    "Content-type": "text/xml; charset=utf-8",
                    "Cache-Control": "max-age=600",
                },
            )
        else:
            return json

    except ValueError:
        return response.content


@app.route("/<user>/weeklytracks")
def get_weeklytracks(user):
    payload = {
        "api_key": config.api_key,
        "method": "user.getweeklytrackchart",
        "user": user,
        "format": "json",
    }
    weeks = None
    if "weeks" in request.args:
        weeks = request.args.get("weeks")
        period = from_to(user, weeks)
        payload["from"] = period[0]
        payload["to"] = period[1]

    response = requests.get(config.api_base_url, params=payload)

    try:
        json = response.json()
        if "weeklytrackchart" in json:
            to_dt = datetime.fromtimestamp(int(json["weeklytrackchart"]["@attr"]["to"]))
            title = "Weekly top tracks."
            if period:
                title += f" (period: {weeks} weeks)"
            context = {
                "user": user,
                "tracks": json["weeklytrackchart"]["track"],
                "type": f"weeklytracks",
                "title": title,
                "track_dt": str(to_dt),
            }
            return (
                render_template("weekly.html", context=context),
                200,
                {
                    "Content-type": "text/xml; charset=utf-8",
                    "Cache-Control": "max-age=600",
                },
            )
        else:
            return json
    except ValueError as e:
        print(e)
        return response.content


def valid_period(args):
    periods = ["overall", "7day", "1month", "3month", "6month", "12month"]
    alternatives = {"week": "7day", "year": "12month"}
    arg = args.get("period")
    if arg in periods:
        return arg
    if arg in alternatives:
        return alternatives[arg]
    else:
        return "1month"


def from_to(user, weeks: int = None):
    if weeks is None:
        return [None, None]
    payload = {
        "api_key": config.api_key,
        "method": "user.getweeklychartlist",
        "user": user,
        "format": "json",
    }
    response = requests.get(config.api_base_url, params=payload)
    json = response.json()
    weeks = int(weeks)
    charts = json["weeklychartlist"]["chart"][-weeks:]
    return [charts[0]["from"], charts[weeks - 1]["to"]]


@app.template_filter("artistlink")
def make_artistlink(url):
    return "/".join(url.split("/")[:-2])


@app.template_filter("rfc822_date")
def rfc822_date(datestring):
    if not datestring:
        nowdt = datetime.utcnow()
        return utils.format_datetime(nowdt)
    dt = datetime.strptime(datestring, "%d %b %Y, %H:%M")
    return utils.format_datetime(dt)


@app.template_filter("image_url")
def find_image_url(images):
    if not images:
        return ""
    else:
        for image in images:
            if image["size"] == "large":
                return image["#text"]
    return ""


if __name__ == "__main__":
    app.run()
