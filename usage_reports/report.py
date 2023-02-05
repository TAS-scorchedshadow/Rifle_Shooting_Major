import json
import os
from datetime import datetime

from app.api.api import num_shots
from app.models import Club, User

from app import create_app

from fpdf import FPDF

from config import ROOT_DIR


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
    """
    Generates a json.txt file. File contains stage & shot data for all members in a club
    :param club_name: Club name must match database
    :param start: YYYY-MM-DD
    :param end: YYYY-MM-DD
    :param num_free_stages: Minimum number of stages for a user to be active
    """
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
            "active_threshold": num_free_stages,
            "num_active_users": 0,
            "num_inactive_users": 0,
            "num_total_shots": 0
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
        data["club_info"]["num_total_shots"] += u_num_shots["num_shots"]

        print(f"{searched}/{num_users}  {int(searched / num_users * 100)}%")
        searched += 1
    data["active_users"].sort(key=lambda x: x["name"])
    data["inactive_users"].sort(key=lambda x: x["name"])
    json_object = json.dumps(data, indent=4)

    output_name = f'{club.name} {start} to {end}'
    print(f"Writing to {output_name}")
    with open(f"{output_name}.txt", "w") as outfile:
        outfile.write(json_object)
    print(f"Generating pdf")
    json_to_pdf(data, f'{output_name}')


def json_to_pdf(data, output_name):
    class PDF(FPDF):
        def header(self):
            # logo
            self.image(os.path.join(ROOT_DIR, 'app/static/logo/logo-text.png'), 10, 8, 25)
            # font
            self.set_font('helvetica', 'B', 20)
            # Padding
            self.cell(80)
            # Title
            self.cell(100, 10, 'Usage Data', border=True, ln=1, align='C')

            self.set_font('times', '', 14)
            self.ln(1)
            self.cell(95)
            self.cell(70, 10, '2022-01-01 to 2022-12-12', border=False, ln=1, align='C')
            # Line Break
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('helvetica', 'I', 8)

            self.set_text_color(169, 169, 169)
            self.cell(0, 10, f'Page {self.page_no()}', align='C')
        def section_title(self, title):
            self.set_font('times', 'B', 15)
            title_w = self.get_string_width(title) + 6
            doc_w = self.w
            self.set_x((doc_w - title_w) / 2)
            self.cell(title_w, 10, title, ln=1, align='C')
            self.ln(2)

        def pretty_print_club_info(self, club_info):
            pdf.section_title(f'{club_info["club_name"]} Club Info')
            self.set_font('times', '', 12)
            self.set_fill_color(211, 211, 211)
            self.cell(80, 10, f'Active Users: {club_info["num_active_users"]}', align='C', fill=1)
            self.cell(0, 10, f'Inactive Users: {club_info["num_inactive_users"]}', ln=1, align='C', fill=1)
            self.cell(80, 10, f'Total Accounts: {club_info["num_active_users"] + club_info["num_inactive_users"]}', align='C', fill=1)
            self.cell(0, 10, f'Total Shots: {club_info["num_total_shots"]}', ln=1, align='C', fill=1)
            self.ln(5)

        def pretty_print_user_data(self, user_data):
            self.set_font('times', 'B', 14)
            title = f'{ user_data["name"] } ({user_data["username"]})'
            self.cell(0, 10, title, ln=1)

            self.ln(1)
            self.set_font('times', '', 12)

            self.set_fill_color(211,211,211)
            self.cell(80, 10, f'Total Shots: {user_data["data"]["num_shots"]}', fill=1)
            self.cell(0, 10, f'Total Stages: {user_data["data"]["num_stages"]}', ln=1, fill=1)
            self.cell(80, 10, f'Total Sessions: {user_data["data"]["num_sessions"]}', fill=1)
            self.cell(0, 10, f'Average shots per session: {user_data["data"]["num_shots_per_session"]}', ln=1, fill=1)

            self.ln(5)

    pdf = PDF('P', 'mm', "A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()

    pdf.set_font('times', '', 12)

    pdf.pretty_print_club_info(data["club_info"])

    pdf.section_title(f'Active Users ({data["club_info"]["active_threshold"]}+ stages)')
    for active_user in data["active_users"]:
        pdf.pretty_print_user_data(active_user)

    pdf.add_page()
    pdf.section_title(f"Inactive Users")
    for inactive_user in data["inactive_users"]:
        pdf.pretty_print_user_data(inactive_user)

    pdf.output(f'{output_name}.pdf')


if __name__ == "__main__":
    run_generate_usage_report()
