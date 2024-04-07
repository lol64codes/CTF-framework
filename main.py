from flask import *
import bcrypt
app = Flask(__name__)

# GET
@app.route("/challenge_frame", methods=["GET"])
def challenge_frame():
    with open("databases/challenges.txt", "r") as f2:
        challenges = f2.readlines()
    challenges_string = ""
    for i in challenges:
        temp = i.split("|")[:2]
        temp2 = temp[0] + "<br>" + temp[1] + " points<br><hr><br>"
        challenges_string += temp2
    return render_template("./challenge_frame.html", challenges_text=challenges_string), 200

@app.route("/scoreboard", methods=["GET"])
def scoreboard():
    with open("databases/users.txt", "r") as f2:
        users = f2.readlines()
    users2 = []
    for i in users:
        users2.append(i.replace("\n", "").split("|"))
    users2.sort(reverse=True, key=lambda x: int(x[2]))
    users_string = ""
    for j in users2:
        temp = j[0] + " " + j[2] + " points<br><hr><br>"
        users_string += temp
    return render_template("./scoreboard.html", scoreboard_text = users_string), 200

@app.route("/challenge", methods=["GET"])
def challenge():
    return send_file("./challenge.html", mimetype="text/html"), 200

@app.route("/", methods=["GET"]) 
def main():
    return send_file("./index.html", mimetype="text/html"), 200

# POST
@app.route("/NewAccountRequest", methods=["POST"])
def new_account_request():
    try:
        with open("databases/users.txt", "r") as f:
            users = f.readlines()
        processed_list = []
        for i in users:
            processed_list.append(i.replace("\n", "").split("|"))
        all_users = [processed_list[i][0] for i in range(len(processed_list))]
        if (not request.form["username"].replace(" ", "").isalnum()) or (not len(request.form["username"]) > 0) or (not len(request.form["username"]) < 31):
            return render_template("error.html", message="Team name can only contain letters, numbers, and spaces; team name must be between 1 and 30 characters long"), 400
        if (not len(request.form["password"]) > 7) or (not len(request.form["username"]) < 41):
            return render_template("error.html", message="Password must be between 8 and 40 characters long"), 400
        if request.form["username"] not in all_users:
            with open("databases/users.txt", "a") as f2:
                f2.write("|".join([request.form["username"], bcrypt.hashpw(request.form["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8"), "0", "[]"]) + "\n")
            return render_template("info.html", message="Account creation successful"), 200
        else:
            return render_template("error.html", message="Team name already taken"), 400
    except Exception as e:
        print("Server Error: " + str(e))
        return render_template("error.html", message="Server Error: " + str(e)), 500

@app.route("/FlagSubmitRequest", methods=["POST"]) 
def flag():
    try:
        with open("databases/users.txt", "r") as f:
            users = f.readlines()
        processed_list = []
        for a in users:
            temp = a.replace("\n", "").split("|")
            temp[-1] = eval(temp[-1])
            processed_list.append(temp)
        all_users = [processed_list[b][0] for b in range(len(processed_list))]
        try:
            user_index = all_users.index(request.form["username"])
        except ValueError:
            return render_template("error.html", message="Team name not found"), 401
        if not bcrypt.checkpw(request.form["password"].encode("utf-8"), processed_list[user_index][1].encode("utf-8")):
            return render_template("error.html", message="Incorrect password"), 403

        with open("databases/challenges.txt", "r") as f2:
            challenges = f2.readlines()
        processed_challenges_list = []
        for c in challenges:
            processed_challenges_list.append(c.replace("\n", "").split("|"))
        all_flags = [processed_challenges_list[d][2] for d in range(len(processed_challenges_list))]
        try:
            flag_index = all_flags.index(request.form["flag"])
        except ValueError:
            return render_template("error.html", message="Incorrect flag"), 403
        
        if request.form["flag"] not in processed_list[user_index][3]:
            processed_list[user_index][2] = str(int(processed_list[user_index][2]) + int(processed_challenges_list[flag_index][1]))
            processed_list[user_index][3].append(processed_challenges_list[flag_index][2])
            final = []
            for e in range(len(processed_list)):
                processed_list[e][3] = str(processed_list[e][3])
                final.append("|".join(processed_list[e]))
            with open("databases/users.txt", "w") as f3:
                f3.write("\n".join(final) + "\n")
            return render_template("info.html", message="Challenge solved successfully!!!!!!"), 200
        else:
            return render_template("info.html", message="Your team has already solved this challenge before"), 200
    except Exception as e:
        print("Server Error: " + str(e))
        return render_template("error.html", message="Server Error: " + str(e)), 500

if __name__ == "__main__":
    app.run("0.0.0.0")
