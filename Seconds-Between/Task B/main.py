from flask import Flask,request
from Seconds_between import seconds_between

app = Flask(__name__)


@app.route('/seconds_btwn')
def main():
    # data = str(request.args.get("data"))
    date1 = str(request.args.get("date1"))
    date2 = str(request.args.get("date2"))
    print(date1, date2)
    return seconds_between(date1, date2)


if __name__ == "__main__":
    app.run()
