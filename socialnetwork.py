from __future__ import division
import math
from PIL import Image, ImageDraw


people = ['Charlie', 'Augustus', 'Veruca', 'Violet', 'Mike', 'Joe', 'Willy', 'Miranda']

links = [('Augustus', 'Willy'),
         ('Mike', 'Joe'),
         ('Miranda', 'Mike'),
         ('Violet', 'Augustus'),
         ('Miranda', 'Willy'),
         ('Charlie', 'Mike'),
         ('Veruca', 'Joe'),
         ('Miranda', 'Augustus'),
         ('Willy', 'Augustus'),
         ('Joe', 'Charlie'),
         ('Veruca', 'Augustus'),
         ('Miranda', 'Joe')]


def norm(vector):
    """ :param vector: Return norm of a vector. Vector is a tuple of coordinates. """

    return math.sqrt((sum((k**2 for k in vector))))


def make_unit_vector(vector):
    """ :param vector: Return unit vector obtained by dividing vector to its norm. """

    v_norm = norm(vector)
    if v_norm < 1e-9:
        raise ValueError("Vector with 0 norm.")
    return tuple((k / v_norm for k in vector))


def cos_angle(v1, v2):
    """ Given two vectors, return the cosine of the angle between them. """

    unit_v1, unit_v2 = make_unit_vector(v1), make_unit_vector(v2)
    dot_product = sum((c1 * c2 for c1, c2 in zip(unit_v1, unit_v2)))
    return dot_product


# solution representation: list of coordinates of points
def cross_count(v):
    # convert the number list into dict as person: (x, y)
    locations = {people[i]: (v[i*2], v[i*2+1]) for i in range(len(people))}

    connections = {name: [] for name in people}  # connections graph to be used in angle penalization
    for link in links:
        connections[link[0]].append(link[1])
        connections[link[1]].append(link[0])

    total = 0
    for i in range(len(links)):  # loop through every link
        for j in range(i+1, len(links)):
            # get the locations
            (x1,y1), (x2,y2) = locations[links[i][0]], locations[links[i][1]]
            (x3, y3), (x4, y4) = locations[links[j][0]], locations[links[j][1]]

            den = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)  # slopes are the same
            if den == 0:
                continue  # lines are parallel

            ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / den
            ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / den

            # if the fraction is between 0 and 1 for both lines, they cross each other
            if 0 < ua < 1 and 0 < ub < 1:
                total += 1

                # also add the line angle penalization for intersecting lines
                v1 = (x2 - x1, y2 - y1)
                v2 = (x4 - x3, y4 - y3)
                total += cos_angle(v1, v2) / 10

    # now we add the line angle penalization for non-intersecting lines
    for point in connections:
        other_points = connections[point]
        this_position = locations[point]
        x1, y1 = this_position[0], this_position[1]
        for i in xrange(len(other_points)):
            x2, y2 = locations[other_points[i]][0], locations[other_points[i]][1]
            for j in xrange(i+1, len(other_points)):
                # calculate the angle, if below 90 degrees, penalize by cos()/10
                x3, y3 = locations[other_points[j]][0], locations[other_points[j]][1]
                v1 = (x2 - x1, y2 - y1)
                v2 = (x3 - x1, y3 - y1)

                cos = cos_angle(v1, v2)
                if cos > 0:
                    total += cos / 10

    for i in range(len(people)):
        for j in range(i+1, len(people)):
            (x1,y1), (x2,y2) = locations[people[i]], locations[people[j]]

            dist = math.sqrt(math.pow(x1-x2,2) + math.pow(y1-y2,2))
            total += 1./(dist+0.1)

    return total


domain = [(10, 370)] * len(people)*2  # 400 x 400, but with a margin


def draw_network(sol):
    img = Image.new('RGB', (400, 400), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # create the position dict
    pos = {people[i]: (sol[i*2], sol[i*2+1]) for i in range(len(people))}

    # draw links
    for a, b in links:
        draw.line((pos[a], pos[b]), fill=(255,0,0))

    # draw people
    for n, p in pos.items():
        draw.text(p, n, (0,0,0))

    img.show()