import numpy as np

def _dist_to_segment_sq(px, py, ax, ay, bx, by):
    abx, aby = bx - ax, by - ay
    apx, apy = px - ax, py - ay
    ab_len_sq = abx**2 + aby**2
    ab_len_sq = np.where(ab_len_sq == 0, 1, ab_len_sq)
    dot_p = apx * abx + apy * aby
    t = np.clip(dot_p / ab_len_sq, 0, 1)
    proj_x, proj_y = ax + t * abx, ay + t * aby
    return (px - proj_x)**2 + (py - proj_y)**2