import random
from datetime import datetime, timedelta
import numpy as np

from app import db
from app.models import Shot, Stage


def generate_rand_stages(num_shots, distance):
    time = datetime.now()
    times = np.random.normal(size=num_shots, loc=20, scale=5)
    stage_id = random.randint(0, 1000)
    while Stage.query.filter_by(id=stage_id).all():
        stage_id = random.randint(0, 1000)

    new_stage = Stage(id=stage_id, distance=distance)
    db.session.add(new_stage)
    db.session.commit()
    for i in range(0, num_shots):
        shot = generate_rand_shot(distance)
        shot.stageID = stage_id
        time += timedelta(seconds=int(times[i]))
        shot.timestamp = time
        db.session.add(shot)
    db.session.commit()
    return new_stage


def generate_rand_shot(distance, score=None):
    target_details = {
        # ['1', '2', '3', '4', '5', 'V', 'Range],
        "300m": [1200, 600, 420, 280, 140, 70, 300],
        "400m": [1800, 800, 560, 375, 185, 95, 400],
        "500m": [1800, 1320, 1000, 660, 290, 145, 500],
        "600m": [1800, 1320, 1000, 660, 320, 160, 600],
        "700m": [2400, 1830, 1120, 815, 510, 255, 700],
        "800m": [2400, 1830, 1120, 815, 510, 255, 800],
        "900m": [2400, 1830, 1120, 815, 510, 255, 900],
        "300y": [560, 390, 260, 130, 65, 274.32],
        "400y": [745, 520, 350, 175, 85, 365.76],
        "500y": [1320, 915, 600, 260, 130, 457.20],
        "600y": [1320, 915, 600, 290, 145, 548.64],
        "800y": [2400, 1830, 1120, 815, 510, 255, 731.52],
        "900y": [2400, 1830, 1120, 815, 510, 255, 822.96],
        "1000y": [2400, 1120, 815, 510, 255, 914.4]
    }
    d = target_details[distance]
    if score is None:
        score = random.randint(1, 6)
    v_score = 0
    if score == 6:
        flag = True
        while flag or not check_in_circle(x_pos, y_pos, d[5]/2):
            flag = False
            x_pos = random.uniform(-d[5]/2, d[5]/2)
            y_pos = random.uniform(-d[5]/2, d[5]/2)
        v_score = 1
        score = 5
    else:
        outer_bound = d[score-1]/2
        inner_bound = d[score]/2
        print(score,outer_bound,inner_bound)
        flag2 = True
        while flag2 or not check_in_circle(x_pos, y_pos, outer_bound):
            flag2 = False
            x_pos = random.uniform(inner_bound,  outer_bound)
            y_pos = random.uniform(inner_bound,  outer_bound)
            if random.choice([True, False]):
                x_pos *= -1
            if random.choice([True, False]):
                y_pos *= -1
        print(score, outer_bound, x_pos, y_pos)
    print(f"New Shot:\n    Score: {score}\n    xPos:{x_pos}\n    yPos:{y_pos}")
    new_shot = Shot(score=score, xPos=x_pos, yPos=y_pos, vScore=v_score)
    return new_shot


def check_in_circle(x,y,radius):
    dist = (x**2+y**2)**0.5
    return dist < radius
