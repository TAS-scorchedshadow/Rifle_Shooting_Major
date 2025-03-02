import random
from datetime import datetime, timedelta
import numpy as np

from app import db
from app.models import Shot, Stage


def generate_rand_stage(num_shots: int, x_center: float, y_center: float, x_spread: float, y_spread: float,
                        distance: str, start_time: datetime) -> Stage:
    """
    Creates a stage with shots placed at a given spread and center
    (Spread should be around 0.1 for more realistic results)
    All shots created will NOT be sighters

    :param start_time:
    :param num_shots: number
    :param x_center: number
    :param y_center: number
    :param x_spread: number
    :param y_spread: number
    :param distance: string
    :return: Stage
    """
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
    x_poses = np.random.normal(size=num_shots, loc=x_center, scale=d[0]*x_spread)
    y_poses = np.random.normal(size=num_shots, loc=y_center, scale=d[0]*y_spread)
    time = start_time
    times = np.random.normal(size=num_shots, loc=20, scale=5)

    stage_id = random.randint(0, 1000)
    while Stage.query.filter_by(id=stage_id).all():
        stage_id = random.randint(0, 1000)

    new_stage = Stage(id=stage_id, distance=distance, timestamp=time, userID=2)
    db.session.add(new_stage)
    db.session.commit()

    for i in range(0, num_shots):
        v_score = 0
        dist = (x_poses[i] ** 2 + y_poses[i] ** 2) ** 0.5
        idx = 0
        while dist < d[idx]/2 and idx < len(d) - 1:
            idx += 1
        score = idx
        if score == 6:
            score = 5
            v_score = 1

        new_shot = Shot(score=score, xPos=x_poses[i], yPos=y_poses[i], vScore=v_score, stageID=stage_id)
        time += timedelta(seconds=int(times[i]))
        new_shot.timestamp = time
        new_shot.sighter = False
        db.session.add(new_shot)
    db.session.commit()

    return new_stage


def in_circle(x: float, y: float, radius: float) -> bool:
    dist = (x**2+y**2)**0.5
    return dist < radius
