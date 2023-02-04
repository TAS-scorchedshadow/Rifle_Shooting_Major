import json
from datetime import datetime

from app.api.api import num_shots
from app.models import Club, User

from app import create_app


def run_generate_usage_report():
    app = create_app()

    club_name = str(input("Enter club name: "))

    start = str(input("Please enter start date (yyyy-mm-dd): "))
    end = str(input("Please enter end date (yyyy-mm-dd): "))

    num_free_stages = int(input("Enter minimum number of stages for an active user: "))

    with app.app_context():
        generate_usage_report(club_name, start, end, num_free_stages)
    return app


def generate_usage_report(club_name: str, start: str, end: str, num_free_stages: int):

    club = Club.query.filter_by(name=club_name).first()
    if not club:
        raise ValueError("No club of that name was found")

    try:
        start_time = datetime.strptime(start, "%Y-%m-%d")
        end_time = datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Incorrect format given for dates. Must be given in dd-mm-yyyy")

    if start_time > end_time:
        raise ValueError("Start time must be smaller than start time")
    # Used for charging customers

    users = User.query.filter_by(clubID=club.id).all()
    data = {
        "club_info": {
            "club_name": club.name,
            "start": start,
            "end": end,
            "active_threshold": f'At least {num_free_stages} stages',
            "num_active_users": 0,
            "num_inactive_users": 0,
        },
        "active_users": [],
        "inactive_users": []
    }

    num_users = len(users)
    searched = 0
    for user in users:
        u_num_shots = num_shots(user.id, start_time, end_time)
        u_usage_data = {
            "name": f"{user.fName} {user.sName}",
            "userID": user.id,
            "username": user.username,
            "data": u_num_shots
        }

        if u_num_shots["num_stages"] >= num_free_stages:
            data["active_users"].append(u_usage_data)
            data["club_info"]["num_active_users"] += 1
        else:
            data["inactive_users"].append(u_usage_data)
            data["club_info"]["num_inactive_users"] += 1

        print(f"{searched}/{num_users}  {int(searched/num_users * 100)}%")
        searched += 1
    json_object = json.dumps(data, indent=4)

    output_name = f'{club.name} {start} to {end}.txt'
    print(f"Writing to {output_name}")
    with open(output_name, "w") as outfile:
        outfile.write(json_object)


if __name__ == "__main__":
    run_generate_usage_report()
